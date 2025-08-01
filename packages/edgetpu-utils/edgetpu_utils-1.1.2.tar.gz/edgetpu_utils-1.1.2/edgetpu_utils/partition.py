"""Model partitioning utilities for EdgeTPU."""

from pathlib import Path
import subprocess
import tempfile

try:
    from importlib.resources import files
except ImportError:
    # Python < 3.9 fallback
    from importlib_resources import files

import numpy as np

from edgetpu_utils.path_utils import generate_segments_names


def get_partitioner_path():
    """Get the path to the partitioner binary."""
    try:
        # Try to get path from installed package using importlib.resources
        package_files = files("edgetpu_utils")
        partitioner_path = package_files / "partitioner" / "partition_with_num_ops"

        if partitioner_path.is_file():
            return Path(str(partitioner_path))
    except:
        pass

    # Fallback to development environment path
    current_file_dir = Path(__file__).parent
    dev_partitioner_path = (
        current_file_dir.parent / "partitioner" / "partition_with_num_ops"
    )

    if dev_partitioner_path.exists():
        return dev_partitioner_path

    # Last resort: check if it's in the edgetpu_utils directory
    package_partitioner_path = (
        current_file_dir / "partitioner" / "partition_with_num_ops"
    )
    if package_partitioner_path.exists():
        return package_partitioner_path

    raise FileNotFoundError("partition_with_num_ops binary not found")


partitioner_path = get_partitioner_path()


def list_to_str(_list: list) -> str:
    """Convert list to comma-separated string."""
    _list = list(map(str, _list))
    return ",".join(_list)


def partition_with_num_ops(
    model_path: Path,
    num_segments: int,
    num_ops_per_segment: np.ndarray,
    output_dir: Path = None,
    debug=False,
) -> Path:
    """Partition TensorFlow Lite model by number of operations per segment."""
    if output_dir is None:
        tmp_par_dir = Path("/tmp/edgetpu_utils/partition")
        tmp_par_dir.mkdir(parents=True, exist_ok=True)
        output_dir = Path(tempfile.mkdtemp(dir=tmp_par_dir))

    model_stem = model_path.stem
    segment_paths = None

    if num_segments != 1:
        cmd = f"{partitioner_path} --output_dir {output_dir} \
                                   --model_path {str(model_path)} \
                                   --segment_prefix {model_stem} \
                                   --num_ops {list_to_str(num_ops_per_segment)}"
        try:
            result = subprocess.check_output(cmd, shell=True)
        except Exception as e:
            print(f"Error in partition_with_num_ops: {num_ops_per_segment}")
            raise e

        if debug:
            print(result.decode())

        segment_paths = generate_segments_names(
            output_dir / model_stem, num_segments, ".tflite"
        )
    else:
        cmd = f"cp {str(model_path)} {str(output_dir / model_path.name)}"
        try:
            subprocess.check_output(cmd, shell=True)
        except Exception:
            # Source and destination might be the same
            pass
        segment_paths = [output_dir / model_path.name]

    return segment_paths


def partition_with_layer_idxs(
    model_path: Path,
    num_ops: int,
    start: int,
    end: int,
    output_dir: Path = None,
) -> Path:
    """Partition TensorFlow Lite model by layer indices."""

    def calculate_num_ops_per_segment():
        ranges = [(0, start), (start, end + 1), (end + 1, num_ops)]
        num_ops_per_segment = [e - s for s, e in ranges if s != e]
        return num_ops_per_segment

    def determine_segment_to_return():
        if start == 0:
            return 0  # first segment
        elif end == num_ops - 1:
            return -1  # last segment
        else:
            return 1  # middle segment

    if start == num_ops:
        return None, None

    if output_dir is None:
        tmp_par_dir = Path("/tmp/edgetpu_utils/partition")
        tmp_par_dir.mkdir(parents=True, exist_ok=True)
        output_dir = Path(tempfile.mkdtemp(dir=tmp_par_dir))

    model_stem = model_path.stem
    num_ops_per_segment = calculate_num_ops_per_segment()
    num_segments = len(num_ops_per_segment)

    segment_paths = None
    if num_segments > 1:
        cmd = f"{partitioner_path} --output_dir {output_dir} \
                                   --model_path {str(model_path)} \
                                   --segment_prefix {model_stem} \
                                   --num_ops {list_to_str(num_ops_per_segment)}"
        try:
            subprocess.check_output(cmd, shell=True)
        except Exception as e:
            print(f"Error in partition_with_layer_idxs: {num_ops_per_segment}")
            raise e

        segment_paths = generate_segments_names(
            output_dir / model_stem, num_segments, ".tflite"
        )
    else:
        cmd = f"cp {str(model_path)} {str(output_dir / model_path.name)}"
        try:
            subprocess.check_output(cmd, shell=True)
        except Exception:
            # Source and destination might be the same
            pass
        segment_paths = [output_dir / model_path.name]

    return segment_paths, determine_segment_to_return()


def partition_and_compile_with_edgetpu_compiler(model_path, out_dir, num_segments):
    cmd = f"edgetpu_compiler -o {out_dir} --num_segments {num_segments} {model_path}"
    subprocess.check_output(cmd, shell=True)
