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
    try:
        result = int(m.groups()[0])
    except Exception as e:
        print(s)
        raise e
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
