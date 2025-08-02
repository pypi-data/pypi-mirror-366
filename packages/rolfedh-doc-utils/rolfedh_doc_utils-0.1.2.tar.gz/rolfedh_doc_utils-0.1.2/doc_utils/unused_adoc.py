# doc_utils/unused_adoc.py

import os
import re
from .file_utils import collect_files, write_manifest_and_archive

def find_unused_adoc(scan_dirs, archive_dir, archive=False, exclude_dirs=None, exclude_files=None):
    asciidoc_files = collect_files(scan_dirs, {'.adoc'}, exclude_dirs, exclude_files)
    include_pattern = re.compile(r'include::(.+?)\[')
    included_files = set()
    adoc_files = collect_files(['.'], {'.adoc'}, exclude_dirs, exclude_files)
    for file_path in adoc_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                includes = include_pattern.findall(content)
                included_files.update(os.path.basename(include) for include in includes)
        except Exception as e:
            print(f"Warning: could not read {file_path}: {e}")
    unused_files = [f for f in asciidoc_files if os.path.basename(f) not in included_files]
    unused_files = list(dict.fromkeys(unused_files))
    return write_manifest_and_archive(
        unused_files, archive_dir, 'to-archive', 'to-archive', archive=archive
    )
