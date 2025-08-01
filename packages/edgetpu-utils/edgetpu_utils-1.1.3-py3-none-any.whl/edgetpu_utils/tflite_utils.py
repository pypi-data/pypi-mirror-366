"""TensorFlow Lite utilities for EdgeTPU models."""

import shutil
import struct
from pathlib import Path
import tempfile

import numpy as np
from edgetpu_utils.partition import partition_with_num_ops
from edgetpu_utils.path_utils import generate_segments_names

import flexbuffers
from platforms.darwinn import Executable, MultiExecutable, Package
from tflite import Model


def read_buf(path: Path) -> bytearray:
    """Read binary file into bytearray."""
    with open(path, "rb") as f:
        buf = f.read()
        buf = bytearray(buf)
    return buf


def save_buf(buf, path):
    """Save bytearray to file."""
    with open(path, "wb") as f:
        f.write(bytes(buf))


def get_num_ops(model_path: Path) -> int:
    """Get number of operations in TensorFlow Lite model."""
    buf_cpu = read_buf(model_path)
    model_cpu = Model.Model.GetRootAsModel(buf_cpu)
    subgraph_cpu = model_cpu.Subgraphs(0)
    num_nodes_cpu = subgraph_cpu.OperatorsLength()
    return num_nodes_cpu


def calculate_first_output_node_exe_idx(model_path):
    """Calculate execution index of first output node."""
    first_output_node_exe_idx = 0
    model_content = read_buf(model_path)
    model = Model.Model.GetRootAsModel(model_content)
    exe_order_to_node_idx = topological_sort(model)

    edges = build_edge_list(model)
    graph = build_graph(edges, len(exe_order_to_node_idx))
    out_degree = calculate_out_degree(graph)

    while first_output_node_exe_idx < len(exe_order_to_node_idx):
        first_output_node_exe_idx += 1
        if out_degree[exe_order_to_node_idx[first_output_node_exe_idx]] == 0:
            break
    return first_output_node_exe_idx


def build_edge_list(model: Model) -> list:
    """Build edge list from TensorFlow Lite model."""
    subgraph = model.Subgraphs(0)

    tensor_consumers = {}
    tensor_producers = {}
    all_tensor_indices = set()

    for i in range(subgraph.OperatorsLength()):
        op = subgraph.Operators(i)
        input_length = op.InputsLength()
        output_length = op.OutputsLength()
        for j in range(input_length):
            in_tensor_idx = op.Inputs(j)
            if in_tensor_idx not in tensor_consumers.keys():
                tensor_consumers[in_tensor_idx] = []
            tensor_consumers[in_tensor_idx].append(i)
            all_tensor_indices.add(in_tensor_idx)

        for j in range(output_length):
            out_tensor_idx = op.Outputs(j)
            if out_tensor_idx not in tensor_producers.keys():
                tensor_producers[out_tensor_idx] = []
            tensor_producers[out_tensor_idx].append(i)
            all_tensor_indices.add(out_tensor_idx)

    result = []
    for tensor_idx in all_tensor_indices:
        if (tensor_idx in tensor_consumers.keys()) and (
            tensor_idx in tensor_producers.keys()
        ):
            consumer_iter = tensor_consumers[tensor_idx]
            producer_iter = tensor_producers[tensor_idx]
        else:
            continue

        if consumer_iter and producer_iter:
            for consumer_op_idx in consumer_iter:
                for producer_op_idx in producer_iter:
                    result.append((producer_op_idx, consumer_op_idx))

    return result


def build_graph(edges: list, num_nodes: int) -> dict:
    """Build adjacency list graph from edges."""
    graph = {}
    for i in range(num_nodes):
        graph[i] = []

    for edge in edges:
        graph[edge[0]].append(edge[1])
    return graph


def build_reverse_graph(graph: dict) -> dict:
    """Build reverse graph from adjacency list."""
    reverse_graph = {}
    for i in range(len(graph)):
        reverse_graph[i] = []

    for i in range(len(graph)):
        for child_node in graph[i]:
            reverse_graph[child_node].append(i)
    return reverse_graph


def topological_sort(model: Model) -> list:
    """Perform topological sort on model operations."""
    edges = build_edge_list(model)
    num_nodes = model.Subgraphs(0).OperatorsLength()
    graph = build_graph(edges, num_nodes)
    return _topological_sort(graph)


def _topological_sort(graph: dict) -> list:
    num_nodes = len(graph)

    to_visit = []
    exe_order = []
    in_degree = calculate_in_degree(graph)
    out_degree = calculate_out_degree(graph)
    for i in range(num_nodes):
        if in_degree[i] == 0:
            to_visit.append(i)

    while len(to_visit) != 0:
        node = to_visit[-1]
        to_visit.pop()
        exe_order.append(node)

        for child_node in graph[node]:
            if child_node >= num_nodes:
                continue
            in_degree[child_node] -= 1
            if in_degree[child_node] == 0:
                if out_degree[child_node] == 0:
                    to_visit.insert(0, child_node)
                else:
                    to_visit.append(child_node)
    return exe_order


def calculate_in_degree(graph: dict) -> np.ndarray:
    num_nodes = len(graph)

    in_degree = np.zeros(num_nodes)
    for i in range(num_nodes):
        if i not in graph.keys():
            continue
        for child_node in graph[i]:
            if child_node >= num_nodes:
                continue
            in_degree[child_node] += 1
    return in_degree


def calculate_out_degree(graph: dict) -> np.ndarray:
    return calculate_in_degree(build_reverse_graph(graph))


def get_mem_tran_size(model_path: Path):
    buf_cpu = read_buf(model_path)

    model_cpu = Model.Model.GetRootAsModel(buf_cpu)
    subgraph_cpu = model_cpu.Subgraphs(0)

    total_byte = 0
    inputs_idxs = subgraph_cpu.InputsAsNumpy()
    outputs_idxs = subgraph_cpu.OutputsAsNumpy()
    for inputs_idx in inputs_idxs:
        total_byte += np.prod(subgraph_cpu.Tensors(inputs_idx).ShapeAsNumpy())

    for outputs_idx in outputs_idxs:
        total_byte += np.prod(subgraph_cpu.Tensors(outputs_idx).ShapeAsNumpy())

    return total_byte


def get_total_input_tran_size(model_path: Path):
    """Calculate total input transfer sizes for all operations."""
    tmp_par_dir = Path("/tmp/tflite_utils")
    tmp_par_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(dir=tmp_par_dir))

    num_ops = get_num_ops(model_path)
    num_ops_ones = np.ones([num_ops], dtype=int)
    partition_with_num_ops(
        model_path, sum(num_ops_ones), num_ops_ones, output_dir=tmp_dir
    )
    model_base_name = tmp_dir / model_path.stem
    segment_paths = generate_segments_names(model_base_name, num_ops, ".tflite")
    output_tran_sizes = [
        get_input_tran_size(segment_path) for segment_path in segment_paths
    ]

    shutil.rmtree(tmp_dir)
    return output_tran_sizes


def get_input_tran_size(model_path):
    buf_cpu = read_buf(model_path)

    model_cpu = Model.Model.GetRootAsModel(buf_cpu)
    subgraph_cpu = model_cpu.Subgraphs(0)

    total_byte = 0
    inputs_idxs = subgraph_cpu.InputsAsNumpy()
    for inputs_idx in inputs_idxs:
        total_byte += np.prod(subgraph_cpu.Tensors(inputs_idx).ShapeAsNumpy())

    return total_byte


def get_total_output_tran_size(model_path: Path):
    tmp_par_dir = Path("/tmp/tflite_utils")
    tmp_par_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(dir=tmp_par_dir))

    num_ops = get_num_ops(model_path)
    num_ops_ones = np.ones([num_ops], dtype=int)
    partition_with_num_ops(
        model_path, sum(num_ops_ones), num_ops_ones, output_dir=tmp_dir
    )
    model_base_name = tmp_dir / model_path.stem
    segment_paths = generate_segments_names(model_base_name, num_ops, ".tflite")
    output_tran_sizes = [
        get_output_tran_size(segment_path) for segment_path in segment_paths
    ]

    shutil.rmtree(tmp_dir)

    return output_tran_sizes


def get_output_tran_size(model_path: Path):
    buf_cpu = read_buf(model_path)

    model_cpu = Model.Model.GetRootAsModel(buf_cpu)
    subgraph_cpu = model_cpu.Subgraphs(0)

    tran_size = 0
    outputs_idxs = subgraph_cpu.OutputsAsNumpy()

    for outputs_idx in outputs_idxs:
        tran_size += np.prod(subgraph_cpu.Tensors(outputs_idx).ShapeAsNumpy())

    return tran_size


def calculate_parameter_size_list(model_path: Path):
    """Calculate parameter sizes for each operation."""
    buf_cpu = read_buf(model_path)
    model = Model.Model.GetRootAsModel(buf_cpu)

    num_nodes = model.Subgraphs(0).OperatorsLength()

    parameter_size_list = np.zeros([num_nodes], dtype=int)
    for i in range(num_nodes):
        op = model.Subgraphs(0).Operators(i)
        if is_custom_op(model, i):
            parameter_size_list[i] = 0
        else:
            for input_index in [op.Inputs(j) for j in range(op.InputsLength())]:
                tensor = model.Subgraphs(0).Tensors(input_index)
                buffer = model.Buffers(tensor.Buffer())
                if buffer.DataLength():
                    parameter_size_list[i] += buffer.DataLength()

    return parameter_size_list.tolist()


def calculate_parameter_sizes(model_path: Path):
    """Calculate total parameter size of the model."""
    return sum(calculate_parameter_size_list(model_path))


def is_custom_op(model: Model.Model, op_index):
    """Check if operation is a custom operation."""
    op = model.Subgraphs(0).Operators(op_index)
    opcode_index = op.OpcodeIndex()
    opcode = model.OperatorCodes(opcode_index)
    return opcode.BuiltinCode() == 32


def change_param_caching_token(model_path, new_token):
    """Change parameter caching token in EdgeTPU model."""
    old_token = get_caching_token(model_path)
    buf = read_buf(model_path)
    if old_token != new_token:
        while True:
            pointer = find_token_pointer(buf, old_token)
            if pointer == -1:
                break
            change_token(buf, pointer, new_token)

    save_buf(buf, model_path)


def get_caching_token(model_path):
    """Get parameter caching token from EdgeTPU model."""
    return struct.pack("<Q", get_caching_token_binary(model_path))


def get_caching_token_binary(model_path):
    """Get binary parameter caching token from EdgeTPU model."""
    buf = read_buf(model_path)
    model = Model.Model.GetRootAsModel(buf)
    subgraph = model.Subgraphs(0)
    op = subgraph.Operators(0)
    custom_options_data = bytearray(op.CustomOptionsAsNumpy().tobytes())

    flexbuffer_map = flexbuffers.GetRoot(custom_options_data).AsMap
    executable_content = flexbuffer_map["4"].AsString

    package = Package.Package.GetRootAs(executable_content)

    serial_multi_exec_data = bytearray(
        package.SerializedMultiExecutableAsNumpy().tobytes()
    )
    multi_executable = MultiExecutable.MultiExecutable.GetRootAs(serial_multi_exec_data)
    executables = {}
    caching_tokens = []
    for i in range(multi_executable.SerializedExecutablesLength()):
        serial_exec = multi_executable.SerializedExecutables(i)
        executable = Executable.Executable.GetRootAs(serial_exec)
        executables[executable.Type()] = executable
        caching_tokens.append(executable.ParameterCachingToken())

    assert len(set(caching_tokens)) == 1, "More than one unique token found"

    return caching_tokens[0]


def find_token_pointer(buf, token):
    pointer = 0
    while True:
        pointer = buf.find(token, pointer + 1)
        return pointer


def change_token(buf, pointer, new_token, debug=False):
    if debug:
        print("[before change]")
        print(f"pointer: {pointer}, value: {buf[pointer:pointer + 8]}")
    buf[pointer : pointer + 8] = new_token
    if debug:
        print("[after change]")
        print(f"pointer: {pointer}, value: {buf[pointer:pointer + 8]}\n")
