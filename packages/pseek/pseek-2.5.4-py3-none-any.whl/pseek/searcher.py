import mmap, click, io
from pathlib import Path
from .utils import compile_regex, get_archive_path_size, try_decode, get_path_suffix
from .parser import parse_query_expression, TermNode, highlight_text
from concurrent.futures import ThreadPoolExecutor
# Archive modules
import zipfile, py7zr, tarfile, gzip, bz2, lzma, rarfile

# Archive extensions that are allowed
ARCHIVE_EXTS = ('zip', 'rar', '7z', 'tar', 'tar.gz', 'tar.bz2', 'tar.xz', 'gz', 'bz2', 'xz')

# Extensions that are not suitable for content search (binary, media, etc.)
EXCLUDED_EXTENSIONS = (
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg',
    'mp4', 'mov', 'avi', 'mkv', 'webm', 'flv', 'm4v', 'mpg', 'wmv',
    'mp3', 'wav', 'ogg', 'flac', 'aac', 'wma', 'opus',
    'exe', 'dll', 'bin', 'iso', 'img', 'dat', 'dmg', 'class', 'so', 'o', 'obj',
    'ttf', 'otf', 'woff', 'woff2', 'eot',
    'db', 'sqlite', 'mdf', 'bak', 'log', 'jsonl', 'dat',
    'apk', 'ipa', 'deb', 'rpm', 'pkg', 'appimage', 'jar', 'war',
    'pyc', 'ps1', 'pem', 'pyd', 'whl'
)


class Search:
    def __init__(self, base_path, query, case_sensitive, ext, exclude_ext, regex, include, exclude, re_include,
                 re_exclude, whole_word, expr, fuzzy, fuzzy_level, max_size, min_size, archive, depth, arc_ext, arc_ee,
                 arc_inc, arc_exc, arc_max, arc_min, full_path, no_content):
        """Initialize search parameters"""
        self.base_path = Path(base_path)
        self.query = query
        self.case_sensitive = case_sensitive
        self.ext = set(ext)
        self.exclude_ext = set(exclude_ext) | {''} if exclude_ext else set() # To exclude directories from search result
        self.regex = regex
        self.include = {Path(p).resolve() for p in include}
        self.exclude = {Path(p).resolve() for p in exclude}
        self.re_include = compile_regex(re_include)
        self.re_exclude = compile_regex(re_exclude)
        self.whole_word = whole_word
        self.expr = expr
        self.fuzzy = fuzzy
        self.fuzzy_level = fuzzy_level
        self.max_size = max_size
        self.min_size = min_size
        self.archive = archive
        self.depth = depth
        self.arc_ext = set(arc_ext)
        self.arc_ee = set(arc_ee) | {''} if arc_ee else set()
        self.arc_inc = {Path(p) for p in arc_inc}
        self.arc_exc = {Path(p) for p in arc_exc}
        self.arc_max = arc_max
        self.arc_min = arc_min
        self.full_path = full_path
        self.no_content = no_content
        self.result = None

    def should_skip(self, p_resolved: Path, search_type: str) -> bool:
        """
        Check whether the file/directory should be skipped based on various filters.
        Returns True if the path should be skipped.
        """
        try:
            p_size_mb = p_resolved.stat().st_size / 1_048_576  # Convert size to MB
        except OSError:
            # If path is inaccessible, skip it.
            return True

        file_ext = get_path_suffix(p_resolved)

        # Ignore some filters for archive files when archive is enabled
        if (not self.archive or file_ext not in ARCHIVE_EXTS[:-3]) and \
                ((search_type in ('file', 'content') and not p_resolved.is_file())
                 or (search_type == 'directory' and not p_resolved.is_dir())):
            return True

        if (self.include and not any(p_resolved.is_relative_to(inc) for inc in self.include)) \
                or (self.exclude and any(p_resolved.is_relative_to(exc) for exc in self.exclude)) \
                or (self.ext and file_ext not in self.ext) \
                or (self.exclude_ext and file_ext in self.exclude_ext) \
                or (search_type == 'content' and file_ext in EXCLUDED_EXTENSIONS) \
                or (self.max_size and p_size_mb > self.max_size) \
                or (self.min_size and p_size_mb < self.min_size):
            return True

        # Filter by regex include and exclude
        if self.re_include:
            return not self.re_include.search(str(p_resolved))
        if self.re_exclude:
            return self.re_exclude.search(str(p_resolved)) is not None

        return False

    def archive_should_skip(self, path_info: Path, search_type: str, is_file: bool, is_dir: bool, p_size: float):
        """Check whether the file/directory inside archive files should be skipped based on various filters"""

        file_ext = get_path_suffix(path_info)

        if (search_type in ('file', 'content') and not is_file) \
                or (search_type == 'directory' and not is_dir):
            return True

        if (self.arc_inc and not any(path_info.is_relative_to(inc) for inc in self.arc_inc)) \
                or (self.arc_exc and any(path_info.is_relative_to(exc) for exc in self.arc_exc)) \
                or (self.arc_ext and file_ext not in self.arc_ext) \
                or (self.arc_ee and file_ext in self.arc_ee) \
                or (search_type == 'content' and file_ext in EXCLUDED_EXTENSIONS) \
                or (self.arc_max and p_size > self.arc_max) \
                or (self.arc_min and p_size < self.arc_min):
            return True

        if self.re_include:
            return not self.re_include.search(str(path_info))
        if self.re_exclude:
            return self.re_exclude.search(str(path_info)) is not None

        return False

    def extract_names_from_archive(self, file_path: Path, search_type: str,
                                   file_bytes: bytes = None, parent_label: str = '',
                                   depth: int = None):
        """
        Recursively extract files and directories name from archive files.
        Supports nested archives like a.zip::b.7z::c.txt.

        Parameters:
            file_path (Path): the archive file path
            search_type (str): search type ( file / directory )
            file_bytes (bytes | None): optional byte data if already read (for recursion)
            parent_label (str): string for nested archive tracking like a.zip::b.7z::file.txt
            depth (int): the depth value that is returned recursively

        Yields:
            (str, Path): tuple of parent label and file or directory name
        """

        file_ext = get_path_suffix(file_path)
        label_prefix = (parent_label + str(file_path) + '::') if parent_label else '::'
        if depth is None:
            depth = self.depth

        try:
            # Decide the stream source: from disk or memory
            file_stream = io.BytesIO(file_bytes) if file_bytes is not None else open(file_path, 'rb')

            # Handle ZIP and RAR archives
            if file_ext in ('zip', 'rar'):
                opener = {'zip': zipfile.ZipFile, 'rar': rarfile.RarFile}[file_ext]
                with opener(file_stream) as f:
                    for info in f.infolist():
                        name = Path(info.filename)
                        if not self.archive_should_skip(
                                name,
                                search_type,
                                not info.is_dir(),
                                info.is_dir(),
                                get_archive_path_size(info, file_ext)
                        ):
                            yield label_prefix, name

                        # At each recursion, subtract 1 from depth if it's set
                        new_depth = None if depth is None else depth - 1
                        # Check if this is a nested archive
                        if get_path_suffix(name) in ARCHIVE_EXTS[:-3] and (new_depth is None or new_depth >= 0):
                            yield from self.extract_names_from_archive(
                                name,
                                search_type,
                                f.read(info),
                                label_prefix,
                                new_depth
                            )
            # Handle 7Z archives
            elif file_ext == '7z':
                with py7zr.SevenZipFile(file_stream, mode='r') as z:
                    for info in z.list():
                        name = Path(info.filename)
                        if not self.archive_should_skip(
                                name,
                                search_type,
                                not info.is_directory,
                                info.is_directory,
                                get_archive_path_size(info, '7z')
                        ):
                            yield label_prefix, name

                        new_depth = None if depth is None else depth - 1
                        if get_path_suffix(name) in ARCHIVE_EXTS[:-3] and (new_depth is None or new_depth >= 0):
                            file_data = z.read([info.filename]).get(info.filename)
                            if file_data is None:
                                continue

                            yield from self.extract_names_from_archive(
                                name,
                                search_type,
                                file_data.read(),
                                label_prefix,
                                new_depth
                            )
            # Handle TAR and compressed TAR formats
            elif file_ext in ('tar', 'tar.gz', 'tar.bz2', 'tar.xz'):
                # Specify the mode based on the file ext to open it
                mode = {
                    'tar': 'r',
                    'tar.gz': 'r:gz',
                    'tar.bz2': 'r:bz2',
                    'tar.xz': 'r:xz'
                }[file_ext]

                with tarfile.open(fileobj=file_stream, mode=mode) as tf:
                    for member in tf.getmembers():
                        name = Path(member.name)
                        if not self.archive_should_skip(
                                name,
                                search_type,
                                member.isfile(),
                                member.isdir(),
                                get_archive_path_size(member, file_ext)
                        ):
                            yield label_prefix, name

                        new_depth = None if depth is None else depth - 1
                        if get_path_suffix(name) in ARCHIVE_EXTS[:-3] and (new_depth is None or new_depth >= 0):
                            f = tf.extractfile(member)
                            if f is None:
                                continue

                            yield from self.extract_names_from_archive(
                                name,
                                search_type,
                                f.read(),
                                label_prefix,
                                new_depth
                            )
        except Exception:
            return  # silently skip invalid archives

    def extract_text_from_archive(self, file_path: Path, file_bytes: bytes = None,
                                  parent_label: str = '', depth: int = None):
        """
        Recursively extract (path_label, text_content) from any archive file.
        Supports nested archives like a.zip::b.7z::c.txt.

        Parameters:
            file_path (Path): the archive file path
            file_bytes (bytes | None): optional byte data if already read (for recursion)
            parent_label (str): string for nested archive tracking like a.zip::b.7z::file.txt
            depth (int): the depth value that is returned recursively

        Yields:
            (str, str): tuple of full virtual path and decoded content text
        """

        file_ext = get_path_suffix(file_path)
        label_prefix = (parent_label + str(file_path) + '::') if parent_label else '::'
        if depth is None:
            depth = self.depth

        try:
            # Decide the stream source: from disk or memory
            file_stream = io.BytesIO(file_bytes) if file_bytes is not None else open(file_path, 'rb')

            # Handle ZIP and RAR archives
            if file_ext in ('zip', 'rar'):
                opener = {'zip': zipfile.ZipFile, 'rar': rarfile.RarFile}[file_ext]
                with opener(file_stream) as f:
                    for info in f.infolist():
                        file_name = Path(info.filename)
                        data = f.read(info)
                        # At each recursion, subtract 1 from depth if it's set
                        new_depth = None if depth is None else depth - 1

                        # Check if this is a nested archive
                        if get_path_suffix(file_name) in ARCHIVE_EXTS and (new_depth is None or new_depth >= 0):
                            yield from self.extract_text_from_archive(file_name, data, label_prefix, new_depth)
                        else:
                            if self.archive_should_skip(
                                    file_name,
                                    'content',
                                    not info.is_dir(),
                                    info.is_dir(),
                                    get_archive_path_size(info, file_ext)
                            ):
                                continue

                            text = try_decode(data)
                            if text is not None:
                                yield label_prefix + str(file_name), text
            # Handle 7Z archives
            elif file_ext == '7z':
                with py7zr.SevenZipFile(file_stream, mode='r') as archive:
                    for info in archive.list():
                        file_data = archive.read([info.filename]).get(info.filename)
                        if file_data is None:
                            continue

                        file_name = Path(info.filename)
                        data = file_data.read()
                        new_depth = None if depth is None else depth - 1

                        if get_path_suffix(file_name) in ARCHIVE_EXTS and (new_depth is None or new_depth >= 0):
                            yield from self.extract_text_from_archive(file_name, data, label_prefix, new_depth)
                        else:
                            if self.archive_should_skip(
                                    file_name,
                                    'content',
                                    not info.is_directory,
                                    info.is_directory,
                                    get_archive_path_size(info, '7z')
                            ):
                                continue

                            text = try_decode(data)
                            if text is not None:
                                yield label_prefix + str(file_name), text
            # Handle TAR and compressed TAR formats
            elif file_ext in ('tar', 'tar.gz', 'tar.bz2', 'tar.xz'):
                mode = {
                    'tar': 'r',
                    'tar.gz': 'r:gz',
                    'tar.bz2': 'r:bz2',
                    'tar.xz': 'r:xz'
                }[file_ext]

                with tarfile.open(fileobj=file_stream, mode=mode) as tf:
                    for member in tf.getmembers():
                        f = tf.extractfile(member)
                        if f is None:
                            continue

                        file_name = Path(member.name)
                        data = f.read()
                        new_depth = None if depth is None else depth - 1

                        if get_path_suffix(file_name) in ARCHIVE_EXTS and (new_depth is None or new_depth >= 0):
                            yield from self.extract_text_from_archive(file_name, data, label_prefix, new_depth)
                        else:
                            if self.archive_should_skip(
                                    file_name,
                                    'content',
                                    member.isfile(),
                                    member.isdir(),
                                    get_archive_path_size(member, file_ext)
                            ):
                                continue

                            text = try_decode(data)
                            if text is not None:
                                yield label_prefix + str(file_name), text
            # Handle single compressed files like .gz, .bz2, .xz
            elif file_ext in ARCHIVE_EXTS[-3:]:
                opener = {'gz': gzip.open, 'bz2': bz2.open, 'xz': lzma.open}[file_ext]
                with opener(file_stream, 'rb') as f:
                    data = f.read()
                    text = try_decode(data)
                    if text is not None:
                        yield file_ext, text
        except Exception:
            return

    def search(self, search_type: str):
        """Main search function. search_type can be 'file', 'directory' or 'content'"""
        pattern = parse_query_expression(self.query, self.expr, self.regex, self.whole_word, self.case_sensitive,
                                         self.fuzzy, self.fuzzy_level)

        if search_type in ('file', 'directory'):
            matches = []
            for p in self.base_path.rglob('*'):
                try:
                    p_resolved = p.resolve()
                except Exception:
                    continue
                # Skip if conditions fail
                if self.should_skip(p_resolved, search_type):
                    continue

                # Choose parent path based on full_path flag
                p_parent = p_resolved.parent if self.full_path else p.parent
                p_ext = get_path_suffix(p_resolved)

                if pattern.evaluate(p.name) and not (search_type == 'directory' and p_resolved.is_file()):
                    # Highlight matched query in the name
                    highlighted_name = highlight_text(pattern, p.name, self.fuzzy)
                    matches.append(f'{p_parent}\\{highlighted_name}')

                # Search for files and directories name inside archive files if archive is active
                if self.archive and p_ext in ARCHIVE_EXTS[:-3]:
                    for label, name in self.extract_names_from_archive(p_resolved, search_type):
                        if pattern.evaluate(name.name):
                            highlighted_name = highlight_text(pattern, name.name, self.fuzzy)
                            matches.append(f'{p_parent}\\{p.name}{label}{name.parent}\\{highlighted_name}')
        else:  # content search
            # Use dictionary: key: file path (colored), value: list of line matches
            matches = {} if not self.no_content else set()

            # If expression is simple and is a single TermNode, we can use binary pattern
            binary_pattern = None
            if isinstance(pattern, TermNode):
                try:
                    binary_pattern = pattern.get_binary_pattern()
                except Exception:
                    binary_pattern = None

            def process_file(file_path: Path):
                """Process a single file for content search"""
                try:
                    # Avoid empty files for mmap
                    if file_path.stat().st_size == 0:
                        return

                    # Choose the file path format based on the full_path setting
                    file_label = str(file_path.resolve()) if self.full_path else str(file_path)

                    # First, check if the file is an archive, extract it from the archive and perform a search
                    if self.archive and get_path_suffix(file_path) in ARCHIVE_EXTS:
                        for fname, content in self.extract_text_from_archive(file_path):
                            if not pattern.evaluate(content) and not self.expr:
                                continue

                            # Change file_label for archive files (zip, rar, 7z, tar)
                            if fname not in ARCHIVE_EXTS[-3:]:
                                file_label += fname

                            if self.no_content and not self.expr:
                                matches.add(click.style(file_label, fg='cyan'))
                                continue

                            lines = []
                            for num, line in enumerate(content.splitlines(), 1):
                                if not pattern.evaluate(line):
                                    continue

                                if self.no_content and self.expr:
                                    matches.add(click.style(file_label, fg='cyan'))
                                    continue

                                count = pattern.count_matches(line) if isinstance(pattern, TermNode) else 0
                                # Highlight the matching parts in green
                                highlighted = highlight_text(pattern, line.strip(), self.fuzzy)
                                # Show a note if the pattern repeats 3 or more times
                                count_query = f' - Repeated {count} times' if count >= 3 else ''
                                # Format the output line with line number and highlighted matches
                                lines.append(
                                    click.style(f'Line {num}{count_query}: ', fg='magenta') + highlighted
                                )

                            if lines:
                                matches[click.style(file_label, fg='cyan')] = lines

                    # Open the file in binary read mode
                    with open(file_path, 'rb') as f:
                        # Memory-map the file for efficient access
                        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                            if binary_pattern is not None:
                                if not binary_pattern.search(mm):
                                    return
                            else:
                                # fallback: decode whole file for complex expressions
                                try:
                                    content = mm.read().decode('utf-8')
                                except UnicodeDecodeError:
                                    return

                                if not pattern.evaluate(content) and not self.expr:
                                    return

                            # Avoid searching through the entire file content if the fast-content flag is True
                            if self.no_content and not self.expr:
                                matches.add(click.style(file_label, fg='cyan'))
                                return

                            lines = []
                            mm.seek(0)  # Move the cursor to the beginning of the file

                            # Iterate over each line in the file
                            for num, line in enumerate(iter(mm.readline, b''), 1):
                                try:
                                    # Decode the binary line as UTF-8 and strip whitespace
                                    line_decoded = line.decode('utf-8').strip()
                                except UnicodeDecodeError:
                                    # Skip lines that can't be decoded
                                    continue

                                # If the pattern matches in the decoded line
                                if pattern.evaluate(line_decoded):
                                    if self.no_content and self.expr:
                                        matches.add(click.style(file_label, fg='cyan'))
                                        return
                                    count = pattern.count_matches(line_decoded) if isinstance(pattern, TermNode) else 0
                                    # Highlight the matching parts in green
                                    highlighted = highlight_text(pattern, line_decoded, self.fuzzy)
                                    # Show a note if the pattern repeats 3 or more times
                                    count_query = f' - Repeated {count} times' if count >= 3 else ''
                                    # Format the output line with line number and highlighted matches
                                    lines.append(
                                        click.style(f'Line {num}{count_query}: ', fg='magenta') + highlighted
                                    )

                            # If any matching lines were found
                            if lines:
                                # Add the file and its matching lines to the results
                                matches[click.style(file_label, fg='cyan')] = lines
                except Exception:
                    return

            # Filter files before processing
            files_to_process = {
                p for p in self.base_path.rglob('*') if not self.should_skip(p.resolve(), 'content')
            }

            with ThreadPoolExecutor(max_workers=8) as executor:
                executor.map(process_file, files_to_process)

        self.result = matches
        return self

    def echo(self, title: str, result_name: str) -> int:
        """
        Display the search results with a title.
        Returns the count of results.
        """
        count_result = 0

        if self.result:
            click.echo(click.style(f'\n{title}:\n', fg='yellow'))
            if isinstance(self.result, dict):
                # For content search results
                for key, value in self.result.items():
                    click.echo(key)
                    click.echo('\n'.join(value) + '\n')
                    count_result += len(value)
            else:
                # For file/directory search results
                count_result = len(self.result)
                click.echo('\n'.join(self.result))

            if count_result >= 3:
                click.echo(click.style(f'\n{count_result} results found for {result_name}', fg='blue'))

        return count_result
