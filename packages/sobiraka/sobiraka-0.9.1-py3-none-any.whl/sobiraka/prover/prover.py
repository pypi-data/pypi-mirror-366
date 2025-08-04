import re
from functools import cached_property

from more_itertools import unique_everseen
from panflute import Element
from typing_extensions import override

from sobiraka.models import Document, Page, PageHref, Status
from sobiraka.models.issues import MisspelledWords
from sobiraka.processing.abstract import DocumentBuilder
from sobiraka.processing.txt import PlainTextDispatcher, TextModel, clean_lines, clean_phrases
from .checks import phrases_must_begin_with_capitals
from .hunspell import run_hunspell
from .quotationsanalyzer import QuotationsAnalyzer


class ProverProcessor(PlainTextDispatcher):
    def __init__(self, document: Document):
        super().__init__()
        self.document: Document = document

    @override
    def _new_text_model(self) -> TextModel:
        return TextModel(exceptions_regexp=self.exceptions_regexp)

    @override
    async def must_skip(self, elem: Element, page: Page) -> bool:
        return isinstance(elem, self.document.config.prover.skip_elements)

    @cached_property
    def exceptions_regexp(self) -> re.Pattern | None:
        """
        Prepare a regular expression that matches any exception.
        If the document declares no exceptions, returns `None`.
        """
        dictionaries = self.document.config.prover.dictionaries
        fs = self.document.project.fs

        regexp_parts: list[str] = []

        for dictionary in dictionaries.plaintext_dictionaries:
            lines = fs.read_text(dictionary).splitlines()
            for line in lines:
                regexp_parts.append(r'\b' + re.escape(line.strip()) + r'\b')

        for dictionary in dictionaries.regexp_dictionaries:
            lines = fs.read_text(dictionary).splitlines()
            for line in lines:
                regexp_parts.append(line.strip())

        if regexp_parts:
            return re.compile('|'.join(regexp_parts))
        return None


class Prover(DocumentBuilder[ProverProcessor]):
    def __init__(self, document: Document, variables: dict = None):
        super().__init__(document)
        self.waiter.target_status = Status.PROCESS1
        self._variables: dict = variables or {}

    @override
    def additional_variables(self) -> dict:
        return self._variables or dict(
            HTML=True,
            LATEX=True,
            PDF=True,
            PROVER=True,
            WEASYPRINT=True,
            WEB=True,
        )

    @override
    def init_processor(self) -> ProverProcessor:
        return ProverProcessor(self.document)

    @override
    def make_internal_url(self, href: PageHref, *, page: Page = None) -> str:
        raise NotImplementedError

    @override
    async def run(self):
        await self.waiter.wait_all()

    @override
    async def do_process1(self, page: Page):
        await super().do_process1(page)
        tm = self.processor.tm[page]

        phrases = tm.phrases()

        fs = self.document.project.fs
        config = self.document.config.prover

        if config.dictionaries.hunspell_dictionaries:
            words: list[str] = []
            for phrase in clean_phrases(phrases, tm.exceptions()):
                words += phrase.split()
            words = list(unique_everseen(words))
            misspelled_words: list[str] = []
            for word in await run_hunspell(words, fs, config.dictionaries.hunspell_dictionaries):
                if word not in misspelled_words:
                    misspelled_words.append(word)
            if misspelled_words:
                page.issues.append(MisspelledWords(page.source.path_in_project, tuple(misspelled_words)))

        if config.phrases_must_begin_with_capitals:
            page.issues += phrases_must_begin_with_capitals(tm, phrases)

        if config.allowed_quotation_marks:
            lines = tuple(clean_lines(tm.lines, tm.exceptions()))
            quotation_analyzer = QuotationsAnalyzer(lines,
                                                    config.allowed_quotation_marks,
                                                    config.allowed_apostrophes)
            page.issues += quotation_analyzer.issues
