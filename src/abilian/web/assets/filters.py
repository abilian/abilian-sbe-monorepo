# Copyright (c) 2012-2024, Abilian SAS

""""""

from __future__ import annotations

import json
import os
import re
import shutil
from functools import partial
from io import StringIO
from os.path import isabs
from pathlib import Path

from devtools import debug
from flask import current_app
from loguru import logger
from webassets.filter import ExternalTool, Filter, get_filter, register_filter
from webassets.filter.closure import ClosureJS as BaseClosureJS
from webassets.utils import working_directory


class ImportCSSFilter(Filter):
    """This filter searches (recursively) '@import' rules and replaces them by
    content of target file."""

    name = "cssimporter"
    max_debug_level = None

    _IMPORT_RE = re.compile(
        r"""@import ("|')(?P<filename>(/?[-a-zA-Z0-9_\.]+)+\.css)("|');"""
    )

    def input(self, _in, out, **kwargs) -> None:
        filepath = kwargs["source_path"]
        source = kwargs.get("source")

        if not source:
            # this happens when this filters is not used as a "source" filter, i.e _in
            # is a webasset hunk instance
            source = filepath
        # output = kwargs['output']
        base_dir = Path(filepath).parent
        rel_dir = Path(source).parent

        logger.debug('process "{filepath}"', filepath=filepath)

        for line in _in.readlines():
            import_match = self._IMPORT_RE.search(line)
            if import_match is None:
                out.write(line)
                continue

            filename = import_match.group("filename")
            abs_filename = os.path.abspath(base_dir / filename)
            rel_filename = os.path.normpath(rel_dir / filename)

            start, end = import_match.span()
            if start > 0:
                out.write(line[:start])
                out.write("\n")

            with open(abs_filename) as included:
                # rewrite url() statements
                buf = StringIO()
                url_rewriter = get_filter("cssrewrite")
                url_rewriter.set_context(self.ctx)
                url_rewriter.setup()
                url_rewriter.input(
                    included,
                    buf,
                    source=rel_filename,
                    source_path=abs_filename,
                    output=source,
                    output_path=filepath,
                )
            buf.seek(0)
            # now process '@includes' directives in included file
            self.input(
                buf,
                out,
                source=rel_filename,
                source_path=abs_filename,
                output=source,
                output_path=filepath,
            )

            if end < len(line):
                out.write(line[end:])
            else:
                out.write("\n")


class LessImportFilter(Filter):
    """This filter outputs `@import` statements for listed files.

    This allows to generate a single less file for application, where
    abilian properties can be overridden by application.
    """

    name = "less_import"
    options = {"run_in_debug": "LESS_RUN_IN_DEBUG"}  # use same option as less filter
    max_debug_level = None

    def setup(self) -> None:
        super().setup()
        if self.run_in_debug is False:
            # Disable running in debug mode for this instance.
            self.max_debug_level = False

    def input(self, _in, out, source_path, output_path, **kwargs) -> None:
        if not Path(source_path).is_file():
            # we are not processing files but webassets intermediate hunks
            out.write(_in.read())
            return

        out_dir = os.path.dirname(output_path)
        rel_path = os.path.relpath(source_path, out_dir)

        # note: when import as CSS, import statement is put at the top of the
        # generated file (order of import is not preserved, less content will be
        # after pure css one). If we use "inline" the lessc will not rewrite
        # url(). So we better have all our css imported as less content.
        import_mode = "less"  # if not rel_path.endswith('css') else 'css'
        out.write(f'@import ({import_mode}) "{rel_path}";')


class Less(ExternalTool):
    """Converts `less <http://lesscss.org/>`_ markup to real CSS.

    This depends on the NodeJS implementation of less, installable via npm.
    To use the old Ruby-based version (implemented in the 1.x Ruby gem), see
    :class:`~.less_ruby.Less`.

    *Supported configuration options*:

    LESS_BIN (binary)
      Path to the less executable used to compile source files. By default,
      the filter will attempt to run ``lessc`` via the system path.

    LESS_LINE_NUMBERS (line_numbers)
      Outputs filename and line numbers. Can be either 'comments', which
      will output the debug info within comments, 'mediaquery' that will
      output the information within a fake media query which is compatible
      with the SASSPath to the less executable used to compile source files.

    LESS_RUN_IN_DEBUG (run_in_debug)
      By default, the filter will compile in debug mode. Since the less
      compiler is written in Javascript and capable of running in the
      browser, you can set this to ``False`` to have your original less
      source files served (see below).

    LESS_PATHS (paths)
      Add include paths for less command line.
      It should be a list of paths relatives to Environment.directory or absolute paths.
      Order matters as less will pick the first file found in path order.

    .. admonition:: Compiling less in the browser

      less is an interesting case because it is written in Javascript and
      capable of running in the browser. While for performance reason you
      should prebuild your stylesheets in production, while developing you
      may be interested in serving the original less files to the client,
      and have less compile them in the browser.

      To do so, you first need to make sure the less filter is not applied
      when :attr:`Environment.debug` is ``True``. You can do so via an
      option::

          env.config['less_run_in_debug'] = False

      Second, in order for the less to identify the  less source files as
      needing to be compiled, they have to be referenced with a
      ``rel="stylesheet/less"`` attribute. One way to do this is to use the
      :attr:`Bundle.extra` dictionary, which works well with the template
      tags that webassets provides for some template languages::

          less_bundle = Bundle(
              '**/*.less',
              filters='less',
              extra={'rel': 'stylesheet/less' if env.debug else 'stylesheet'}
          )

      Then, for example in a Jinja2 template, you would write::

          {% assets less_bundle %}
              <link rel="{{ EXTRA.rel }}" type="text/css" href="{{ ASSET_URL }}">
          {% endassets %}

      With this, the ``<link>`` tag will sport the correct ``rel`` value both
      in development and in production.

      Finally, you need to include the less compiler::

          if env.debug:
              js_bundle.contents += \
                 'http://lesscss.googlecode.com/files/less-1.3.0.min.js'
    """

    name = "less"
    options = {
        "less": ("binary", "LESS_BIN"),
        "run_in_debug": "LESS_RUN_IN_DEBUG",
        "line_numbers": "LESS_LINE_NUMBERS",
        "extra_args": "less_extra_args",
        "paths": "LESS_PATHS",
        "as_output": "less_as_output",
        "source_map_file": "less_source_map_file",
    }
    max_debug_level = None

    def setup(self) -> None:
        super().setup()
        if self.run_in_debug is False:
            # Disable running in debug mode for this instance.
            self.max_debug_level = False

    def input(self, in_, out, **kw) -> None:
        if self.as_output:
            importer = get_filter("less_import")
            importer.input(in_, out, **kw)
        else:
            self._apply_less(in_, out, **kw)

    def output(self, in_, out, **kw) -> None:
        if not self.as_output:
            out.write(in_.read())
        else:
            self._apply_less(in_, out, **kw)

    def _apply_less(self, in_, out, output_path, output, **kw) -> None:
        # Set working directory to the source file so that includes are found

        if self.less and shutil.which(self.less):
            lessc = shutil.which(self.less)
        elif shutil.which("lessc"):
            lessc = shutil.which("lessc")
        else:
            root = Path(current_app.root_path) / ".." / ".."
            debug(root)
            lessc = str(root / "node_modules" / ".bin" / "lessc")

        assert Path(lessc).is_file(), f"lessc not found at {lessc}"
        args = [lessc]

        if self.line_numbers:
            args.append(f"--line-numbers={self.line_numbers}")

        if self.paths:
            paths = [
                path if isabs(path) else self.ctx.resolver.resolve_source(path)
                for path in self.pathsep
            ]
            args.append(f"--include-path={os.pathsep.join(paths)}")

        #
        # Commented out since this doesn't work with the current lessc compiler.
        # (See also just below)
        #
        # source_map = self.source_map_file and self.ctx.debug
        # if source_map:
        #     source_map_dest = os.path.join(self.ctx.directory,
        #                                    self.source_map_file)
        #     self.logger.debug('Generate source map to "%s"', source_map_dest)
        #     args.append('--source-map={}'.format(source_map_dest))
        #     args.append('--source-map-url={}'.format(self.source_map_file))

        if self.extra_args:
            args.extend(self.extra_args)

        args.append("-")
        buf = StringIO()
        with working_directory(filename=output_path):
            self.subprocess(args, buf, in_)

        # if source_map:
        #     self.fix_source_map_urls(source_map_dest)

        # rewrite css url()
        replace_url = partial(self.fix_url, os.path.dirname(output_path))
        buf.seek(0)
        url_rewriter = get_filter("cssrewrite", replace=replace_url)
        url_rewriter.set_context(self.ctx)
        url_rewriter.setup()
        url_rewriter.input(
            buf,
            out,
            source=output,
            source_path=output_path,
            output=output,
            output_path=output_path,
        )

    def fix_url(self, cur_path, url):
        if url.startswith("data:"):
            # base64 embeded
            return url

        src_path = os.path.normpath(os.path.abspath(os.path.join(cur_path, url)))
        possible_paths = [p for p in self.ctx.url_mapping if src_path.startswith(p)]
        if not possible_paths:
            return url

        if len(possible_paths) > 1:
            msg = "Should not happen"
            raise RuntimeError(msg)
            # possible_paths.sort(lambda p: -len(p))

        path = possible_paths[0]
        return self.ctx.url_mapping[path] + src_path[len(path) :]

    def fix_source_map_urls(self, filename) -> None:
        with open(filename) as f:
            data = json.load(f)

        for idx, path in enumerate(data["sources"]):
            if path == "-":
                data["sources"][idx] = "-"
                continue

            # apparently less is stripping first part
            path = os.path.join("..", path)
            data["sources"][idx] = self.fix_url(self.ctx.directory, path)

        with open(filename, "w") as f:
            json.dump(data, f)


class ClosureJS(BaseClosureJS):
    def setup(self) -> None:
        super().setup()
        self.source_files = []

    def input(self, _in, out, source_path, output_path, **kwargs) -> None:
        if not Path(source_path).is_file():
            # we are not processing files but webassets intermediate hunks
            return
        self.source_files.append(source_path)

    def output(self, _in, out, **kw) -> None:
        for source_file in self.source_files:
            self.extra_args.append("--js")
            self.extra_args.append(source_file)

        super().output(_in, out, **kw)
        try:
            smap_idx = self.extra_args.index("--create_source_map")
            smap_path = Path(self.extra_args[smap_idx + 1])
        except (ValueError, IndexError):
            return

        if not smap_path.exists():
            return

        name = smap_path.name
        out.write(f"//# sourceMappingURL={name!s}")
        self.fix_source_map_urls(smap_path)

    def fix_url(self, cur_path, src_path):
        possible_paths = [p for p in self.ctx.url_mapping if src_path.startswith(p)]

        if not possible_paths:
            msg = "Should not happen"
            raise RuntimeError(msg)
            # # FIXME: url is not defined at this point, this can't work.
            # return url

        if len(possible_paths) > 1:
            msg = "Should not happen"
            raise RuntimeError(msg)
            # possible_paths.sort(lambda p: -len(p))

        path = possible_paths[0]
        return self.ctx.url_mapping[path] + src_path[len(path) :]

    def fix_source_map_urls(self, file_path: Path) -> None:
        with file_path.open() as f:
            data = json.load(f)

        for idx, path in enumerate(data["sources"]):
            if path == "-":
                data["sources"][idx] = "-"
                continue

            data["sources"][idx] = self.fix_url(self.ctx.directory, path)

        with file_path.open("w") as f:
            json.dump(data, f)


def register_filters() -> None:
    register_filter(Less)
    register_filter(LessImportFilter)
    register_filter(ImportCSSFilter)
    register_filter(ClosureJS)
