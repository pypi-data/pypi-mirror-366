from typing import Sequence

from typing_extensions import override
from wcmatch.glob import globmatch

from sobiraka.utils import RelativePath
from .indexsourcefile import IndexSourceFile
from .source import Source
from .sourcefile import SourceFile
from ..aggregationpolicy import AggregationPolicy
from ..filesystem import FileSystem
from ..filesystem.filesystem import GLOB_KWARGS
from ..href import PageHref
from ..namingscheme import NamingScheme
from ..page import DirPage


class SourceDirectory(Source):
    aggregation_policy = AggregationPolicy.WAIT_FOR_CHILDREN | AggregationPolicy.WAIT_FOR_ANY_PAGE

    @override
    async def generate_child_sources(self):
        from .make_source import make_source

        document = self.document
        fs: FileSystem = document.project.fs
        include_pattern: Sequence[str] = document.config.paths.include
        exclude_pattern: Sequence[str] = document.config.paths.exclude
        naming_scheme: NamingScheme = document.config.paths.naming_scheme

        child_sources = []
        for child_path in fs.iterdir(self.path_in_project):
            # A directory is being discovered unconditionally
            # (it may or may not generate pages later, depending on the NamingScheme)
            if fs.is_dir(child_path):
                child_sources.append(make_source(self.document, child_path, parent=self))

            # A file is being discovered or not, according to the patterns
            elif globmatch(child_path.relative_to(self.document.root.path_in_project),
                           include_pattern, exclude=exclude_pattern, **GLOB_KWARGS):
                klass = IndexSourceFile if naming_scheme.parse(child_path).is_main else SourceFile
                child_sources.append(klass(self.document, child_path, parent=self))

        child_sources.sort(key=lambda s: naming_scheme.path_sorting_key(s.path_in_document))
        self.child_sources = tuple(child_sources)

    @override
    async def generate_pages(self):
        document = self.document
        include_pattern: Sequence[str] = document.config.paths.include
        exclude_pattern: Sequence[str] = document.config.paths.exclude
        naming_scheme: NamingScheme = document.config.paths.naming_scheme

        # If we've already discovered the index page, use it
        for child in self.child_sources:
            if isinstance(child, IndexSourceFile):
                self._set_index_page(child.page)
                self.pages = self.index_page,
                return

        # The index page should only exist in these two cases:
        #  - there is at least one other page (this is the reason we declare the WAIT_FOR_ANY_PAGE policy)
        #  - the directory itself matches the patterns (this was not tested in our parent's generate_child_sources())
        if not any((self.subtree_has_pages,
                    globmatch(self.path_in_document, include_pattern, exclude=exclude_pattern, **GLOB_KWARGS))):
            self.pages = ()
            return

        # Create an auto-generated index page for the directory
        location = naming_scheme.make_location(self.path_in_document, as_dir=True)
        self._set_index_page(DirPage(self, location))
        self.pages = self.index_page,

    @property
    def path_in_document(self) -> RelativePath:
        return self.path_in_project.relative_to(self.document.root_path)

    @override
    def href(self, identifier: str = None) -> PageHref:
        assert self.index_page is not None
        return PageHref(self.index_page,
                        anchor=identifier,
                        default_label=self.index_page.meta.title)
