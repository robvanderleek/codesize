import fnmatch
import locale
import os
from os.path import relpath
from pathlib import Path
from typing import Union, Callable

from pygments.lexer import Lexer
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound
from rich.live import Live

from codelimit.common.Codebase import Codebase
from codelimit.common.Configuration import Configuration
from codelimit.common.Location import Location
from codelimit.common.Measurement import Measurement
from codelimit.common.ScanResultTable import ScanResultTable
from codelimit.common.SourceFileEntry import SourceFileEntry
from codelimit.common.Token import Token
from codelimit.common.lexer_utils import lex
from codelimit.common.report.Report import Report
from codelimit.common.scope.Scope import count_lines
from codelimit.common.scope.ScopeExtractor import ScopeExtractor
from codelimit.common.scope.scope_extractor_utils import build_scopes
from codelimit.common.source_utils import filter_tokens
from codelimit.common.utils import (
    calculate_checksum,
    load_scope_extractor_by_name,
    make_count_profile,
)
from codelimit.languages import languages, ignored

locale.setlocale(locale.LC_ALL, "")


def scan_codebase(path: Path, cached_report: Union[Report, None] = None) -> Codebase:
    codebase = Codebase(str(path.absolute()))

    with Live() as live:
        languages = {}

        def add_file_entry(entry: SourceFileEntry):
            profile = make_count_profile(entry.measurements())
            if entry.language not in languages:
                languages[entry.language] = {
                    "files": 1,
                    "loc": entry.loc,
                    "functions": len(entry.measurements()),
                    "hard-to-maintain": profile[2],
                    "unmaintainable": profile[2],
                }
            else:
                language_entry = languages[entry.language]
                language_entry["files"] += 1
                language_entry["loc"] += entry.loc
                language_entry["functions"] += len(entry.measurements())
                language_entry["hard-to-maintain"] += profile[2]
                language_entry["unmaintainable"] += profile[3]
            table = ScanResultTable(path, languages)
            live.update(table)

        _scan_folder(codebase, path, cached_report, add_file_entry)
    return codebase


def _scan_folder(
    codebase: Codebase,
    folder: Path,
    cached_report: Union[Report, None] = None,
    add_file_entry: Union[Callable[[SourceFileEntry], None], None] = None,
):
    for root, dirs, files in os.walk(folder.absolute()):
        files = [f for f in files if not f[0] == "."]
        dirs[:] = [d for d in dirs if not d[0] == "."]
        for file in files:
            rel_path = Path(os.path.join(root, file)).relative_to(folder.absolute())
            if is_excluded(rel_path):
                continue
            try:
                lexer = get_lexer_for_filename(rel_path)
                language = lexer.__class__.name
                if language in languages:
                    file_path = os.path.join(root, file)
                    file_entry = _add_file(
                        codebase, lexer, folder, file_path, cached_report
                    )
                    if add_file_entry:
                        add_file_entry(file_entry)
                elif language in ignored:
                    pass
                else:
                    print(f"Unclassified: {language}")
            except ClassNotFound:
                pass


def _add_file(
    codebase: Codebase,
    lexer: Lexer,
    root: Path,
    path: str,
    cached_report: Union[Report, None] = None,
) -> SourceFileEntry:
    checksum = calculate_checksum(path)
    rel_path = relpath(path, root)
    cached_entry = None
    if cached_report:
        rel_path = relpath(path, root)
        try:
            cached_entry = cached_report.codebase.files[rel_path]
        except KeyError:
            pass
    if cached_entry and cached_entry.checksum() == checksum:
        entry = SourceFileEntry(
            rel_path,
            checksum,
            cached_entry.language,
            cached_entry.loc,
            cached_entry.measurements(),
        )
        codebase.add_file(entry)
        return entry
    else:
        with open(path) as f:
            code = f.read()
        all_tokens = lex(lexer, code, False)
        code_tokens = filter_tokens(all_tokens)
        file_loc = count_lines(code_tokens)
        scope_extractor = load_scope_extractor_by_name(lexer.__class__.name)
        if scope_extractor:
            measurements = scan_file(all_tokens, scope_extractor)
        else:
            measurements = []
        entry = SourceFileEntry(
            rel_path, checksum, lexer.__class__.name, file_loc, measurements
        )
        codebase.add_file(entry)
        return entry


def scan_file(
    tokens: list[Token], scope_extractor: ScopeExtractor
) -> list[Measurement]:
    scopes = build_scopes(tokens, scope_extractor)
    measurements: list[Measurement] = []
    if scopes:
        for scope in scopes:
            length = len(scope)
            start_location = scope.header.token_range[0].location
            last_token = scope.block.tokens[-1]
            end_location = Location(
                last_token.location.line,
                last_token.location.column + len(last_token.value),
            )
            measurements.append(
                Measurement(scope.header.name, start_location, end_location, length)
            )
    return measurements


def is_excluded(path: Path):
    for exclude in Configuration.excludes:
        exclude_parts = exclude.split(os.sep)
        if len(exclude_parts) == 1:
            for part in path.parts:
                if fnmatch.fnmatch(part, exclude):
                    return True
        else:
            if fnmatch.fnmatch(str(path), exclude):
                return True
    return False
