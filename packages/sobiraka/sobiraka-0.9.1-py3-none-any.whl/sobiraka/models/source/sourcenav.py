from functools import cached_property
from importlib.resources import files
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from more_itertools import one
from typing_extensions import override

from sobiraka.utils import RelativePath
from .indexsourcefile import IndexSourceFile
from .source import IdentifierResolutionError, Source
from ..filesystem import FileSystem
from ..href import PageHref
from ..issues import IndexFileInNav, NonExistentFileInNav
from ..page import Page, PageMeta
from ..syntax import Syntax

NAV_FILENAME = '_nav.yaml'
SCHEMA = yaml.safe_load((files('sobiraka') / 'files' / 'sobiraka-nav.yaml').read_text())


class SourceNav(Source):

    @override
    async def generate_child_sources(self):
        from . import make_source
        fs = self.document.project.fs
        naming_scheme = self.document.config.paths.naming_scheme

        child_sources = []
        for subpath, options in self._data['items']:

            # Make sure the specified file exists
            if not fs.exists(self.path_in_project / subpath):
                self.issues.append(NonExistentFileInNav(subpath))
                continue

            # Make sure the specified file is not the index file
            if naming_scheme.parse(subpath).is_main:
                self.issues.append(IndexFileInNav(subpath))
                continue

            # Generate the child
            child = make_source(self.document, self.path_in_project / subpath, parent=self)
            child_sources.append(child)

            # Provide base options for the child, if specified in the item
            if options:
                child.base_meta = PageMeta(**options)

        # Now look for the actual files in the directory:
        # if there is an index file there, use it
        for index_path in fs.iterdir(self.path_in_project):
            if not fs.is_dir(index_path):
                if naming_scheme.parse(index_path).is_main:
                    child_sources.insert(0, IndexSourceFile(self.document, index_path, parent=self))
                    break

        # Done
        self.child_sources = tuple(child_sources)

    @override
    async def generate_pages(self):
        naming_scheme = self.document.naming_scheme
        location = naming_scheme.make_location(self.path_in_document, as_dir=True)

        # If we've already found a Source that will generate an index page, do nothing
        for child in self.child_sources:
            if isinstance(child, IndexSourceFile):
                self._set_index_page(child.page)
                self.pages = ()
                return

        # Otherwise, proceed to generate a simple index page
        meta = PageMeta(**self._metadata)
        index_page = Page(self, location, Syntax.MD, meta, f'# {meta.title}\n@toc')
        self._set_index_page(index_page)
        self.pages = index_page,

    @override
    def href(self, identifier: str = None) -> PageHref:
        if identifier is not None:
            raise IdentifierResolutionError

        assert self.index_page is not None
        return PageHref(self.index_page, default_label=self.index_page.meta.title)

    # region Reading from YAML

    @cached_property
    def _data(self) -> dict:
        fs: FileSystem = self.document.project.fs
        nav_path: RelativePath = self.path_in_project / NAV_FILENAME
        with fs.open_text(nav_path) as index_file:
            data = yaml.safe_load(index_file) or {}
            Draft202012Validator(data).validate(SCHEMA)

        data.setdefault('items', [])
        data['items'] = list(map(self._parse_item, data['items']))

        return data

    @cached_property
    def _metadata(self) -> dict:
        data = self._data
        del data['items']
        return data

    @staticmethod
    def _parse_item(item) -> tuple[RelativePath, dict[str, Any]]:

        # - page.md
        if isinstance(item, str):
            return RelativePath(item), {}

        assert isinstance(item, dict)
        key, value = one(item.items())

        # - page.md: My Page
        if isinstance(value, str):
            return RelativePath(key), {'title': value}

        # - page.md: { ...meta... }
        if isinstance(value, dict):
            return RelativePath(key), value

        raise ValueError({key: value})

    # endregion
