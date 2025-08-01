"""Path utilities for model segment management."""

import re
from typing import List
from pathlib import Path


def sort_segment_files(segment_files: List[Path]) -> List[Path]:
    """Sort segment files by segment number."""
    return sorted(segment_files, key=get_segment_num)


def get_segment_num(s):
    """Extract segment number from filename."""
    pat = re.compile(".*_(\d+)_of_(\d+).*")
    m = pat.match(str(s))
    if m:
        result = int(m.groups()[0])
    else:
        # If there is no segment pattern, return 0
        return 0
    return result


def generate_segments_names(
    base_path: Path, num_segments: int, extension: str
) -> List[Path]:
    """Generate segment file paths."""
    segment_paths = []
    for i in range(num_segments):
        segment_name = f"{base_path}_segment_{i}_of_{num_segments}{extension}"
        segment_paths.append(Path(segment_name))
    return segment_paths
