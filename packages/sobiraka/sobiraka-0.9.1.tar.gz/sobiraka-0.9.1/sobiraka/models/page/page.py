from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence, TYPE_CHECKING

from sobiraka.utils import Location, MISSING
from ..issues import Issue
from ..status import ObjectWithStatus
from ..syntax import Syntax
from ..version import TranslationStatus, Version

if TYPE_CHECKING:
    from sobiraka.models import Document, Project, Source


class Page(ObjectWithStatus):
    """
    A page is a unit of addressing used in the navigation.
    It represents a piece of output documentation (not necessarily the full Source).
    For example, in the HTML output format, a page is literally a single HTML page.

    Each page is located at a unique Location (basically, a URI) within its Document.
    Its relation to other pages in the hierarchy is stored in the `parent` and `children` fields.
    Note that the Location does not necessarily reflect the real hierarchy.
    """

    def __init__(self, source: Source, location: Location, syntax: Syntax, meta: PageMeta, text: str):
        self.source: Source = source
        self.location: Location = location
        self.syntax: Syntax = syntax
        self.meta: PageMeta = meta
        self.text: str = text

        # Fields for traversing the hierarchy
        self.parent: Page = None if location.is_root else MISSING
        self.children: list[Page] = MISSING

        # Fields for collecting bad results
        self.issues: list[Issue] = []
        self.exception: Exception | None = None

    @property
    def document(self) -> Document:
        return self.source.document

    @property
    def project(self) -> Project:
        return self.source.document.project

    def __repr__(self):
        return f'<{self.__class__.__name__}: {str(self.location)!r}>'

    def __lt__(self, other):
        assert isinstance(other, Page), TypeError
        assert self.document.project == other.document.project

        if self.document is not other.document:
            return self.document < other.document

        self_breadcrumbs_as_indexes = []
        for crumb in self.breadcrumbs[1:]:
            self_breadcrumbs_as_indexes.append(crumb.parent.children.index(crumb))

        other_breadcrumbs_as_indexes = []
        for crumb in other.breadcrumbs[1:]:
            other_breadcrumbs_as_indexes.append(crumb.parent.children.index(crumb))

        return self_breadcrumbs_as_indexes < other_breadcrumbs_as_indexes

    @property
    def breadcrumbs(self) -> Sequence[Page]:
        """
        A sequence that includes the current page after all its parents, including the root page.
        This may or may not look similar to the corresponding `Source.breadcrumbs`.
        """
        breadcrumbs: list[Page] = [self]
        while breadcrumbs[0].parent not in (None, MISSING):
            breadcrumbs.insert(0, breadcrumbs[0].parent)
        return tuple(breadcrumbs)

    # ------------------------------------------------------------------------------------------------------------------
    # region Translation-related properties

    @property
    def original(self) -> Page:
        project = self.document.project
        return project.get_translation(self, project.primary_language)

    @property
    def translation_status(self) -> TranslationStatus:
        this_version = self.meta.version
        orig_version = self.original.meta.version

        if this_version == orig_version:
            return TranslationStatus.UPTODATE
        if this_version.major == orig_version.major:
            return TranslationStatus.MODIFIED
        return TranslationStatus.OUTDATED

    # endregion


@dataclass(kw_only=True)
class PageMeta:
    permalink: Location = None
    title: str = None
    version: Version = None
    toc_title: str = None
    toc_collapse: bool = None

    def __post_init__(self):
        if self.permalink is not None:
            if not isinstance(self.permalink, Location):
                self.permalink = Location(self.permalink)

        if self.version is not None:
            if not isinstance(self.version, Version):
                self.version = Version.parse(str(self.version))

    def __add__(self, other: PageMeta) -> PageMeta:
        data = asdict(self)
        if other is not None:
            for key, value in other.__dict__.items():
                if value is not None:
                    data[key] = value
        return PageMeta(**data)
