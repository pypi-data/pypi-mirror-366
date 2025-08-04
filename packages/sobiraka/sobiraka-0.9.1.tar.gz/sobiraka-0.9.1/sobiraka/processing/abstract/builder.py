from __future__ import annotations

import os
from abc import ABCMeta, abstractmethod
from asyncio import Task, create_subprocess_exec, wait
from collections import defaultdict
from io import BytesIO
from subprocess import PIPE
from typing import Generic, TYPE_CHECKING, TypeVar, final

import jinja2
import panflute
from jinja2 import StrictUndefined

from sobiraka.models import Document, FileSystem, Page, PageHref, Project, Source
from sobiraka.models.config import Config
from sobiraka.runtime import RT
from sobiraka.utils import replace_element
from .waiter import Waiter
from ..directive import parse_directives
from ..numerate import numerate

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from .processor import Processor

P = TypeVar('P', bound='Processor')


class Builder(Generic[P], metaclass=ABCMeta):
    def __init__(self):
        self.waiter = Waiter(self)
        self.jinja: dict[Document, jinja2.Environment] = {}
        self.process2_tasks: dict[Page, list[Task]] = defaultdict(list)
        self.process3_tasks: dict[Document, list[Task]] = defaultdict(list)
        self.process4_tasks: dict[Page, list[Task]] = defaultdict(list)

    def __repr__(self):
        return f'<{self.__class__.__name__} at {hex(id(self))}>'

    @abstractmethod
    async def run(self):
        ...

    @abstractmethod
    def get_project(self) -> Project:
        ...

    @abstractmethod
    def get_documents(self) -> tuple[Document, ...]:
        ...

    @final
    def get_roots(self) -> tuple[Source, ...]:
        return tuple(v.root for v in self.get_documents())

    @abstractmethod
    def get_pages(self) -> tuple[Page, ...]:
        ...

    @abstractmethod
    def get_processor_for_page(self, page: Page) -> P:
        ...

    @abstractmethod
    def additional_variables(self) -> dict:
        ...

    async def prepare(self, page: Page):
        """
        Parse the syntax tree with Pandoc and save its syntax tree into `RT[page].doc`.
        """
        document: Document = page.document
        config: Config = page.document.config
        project: Project = page.document.project
        fs: FileSystem = page.document.project.fs

        default_variables = dict(
            page=page,
            document=document,
            project=project,
            LANG=document.lang,

            # Format-specific variables
            HTML=False,
            LATEX=False,
            PDF=False,
            PROVER=False,
            WEASYPRINT=False,
            WEB=False,

            # Python library
            os=os,
        )
        variables = config.variables | default_variables | self.additional_variables()

        page_text = page.text

        if document not in self.jinja:
            self.jinja[document] = jinja2.Environment(
                comment_start_string='{{#',
                comment_end_string='#}}',
                undefined=StrictUndefined,
                enable_async=True,
                loader=config.paths.partials and jinja2.FileSystemLoader(fs.resolve(config.paths.partials)),
            )
        page_text = await self.jinja[document].from_string(page_text).render_async(variables)

        pandoc = await create_subprocess_exec(
            'pandoc',
            '--from', page.syntax.as_pandoc_format(),
            '--to', 'json',
            stdin=PIPE,
            stdout=PIPE)
        json_bytes, _ = await pandoc.communicate(page_text.encode('utf-8'))
        assert pandoc.returncode == 0

        RT[page].doc = panflute.load(BytesIO(json_bytes))

    async def do_process1(self, page: Page) -> Page:
        """
        The first stage of page processing.

        Internally, this function runs :func:`process_element()` on the :obj:`.Page.doc` root.

        This method is called by :obj:`.Page.processed1`.
        """
        parse_directives(page, self)
        processor = self.get_processor_for_page(page)
        await processor.process_doc(RT[page].doc, page)
        return page

    async def do_process2(self, page: Page):
        """
        The second stage of the processing.
        """
        if self.process2_tasks[page]:
            await wait(self.process2_tasks[page])

    async def do_process3(self, document: Document):
        """
        The third stage of the processing.
        Unlike other stages, this deals with the Document as a whole.
        """
        if document.config.content.numeration:
            numerate(document)

        for page in document.root.all_pages():
            processor = self.get_processor_for_page(page)
            for directive in processor.directives[page]:
                replace_element(directive, directive.postprocess())

        if self.process3_tasks[document]:
            await wait(self.process3_tasks[document])

    async def do_process4(self, page: Page):
        """
        The fourth stage of the processing.
        """
        if self.process4_tasks[page]:
            await wait(self.process4_tasks[page])

    @abstractmethod
    def make_internal_url(self, href: PageHref, *, page: Page = None) -> str:
        ...
