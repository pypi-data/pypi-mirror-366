import enum
from enum import auto
from typing import List, Mapping, Optional, Sequence, Tuple, Union

from torch.fx import GraphModule

__all__ = [
    "full_version",
    "compiler_version",
    "compiler_git_short_hash",
    "compile",
    "CompiledGraph",
]

__version__: str = ...
__full_version__: str = ...
__git_short_hash__: str = ...
__build_timestamp__: str = ...

class CompiledGraph:
    def is_edf(self) -> bool: ...
    def serialize(self) -> bytes: ...
    @staticmethod
    def deserialize(b: bytes, tag: str) -> "CompiledGraph": ...

class CompileResult:
    graphs: List[CompiledGraph]
    graph_metadata: Optional[str]

def full_version() -> str: ...
def compiler_version() -> str: ...
def compiler_git_short_hash() -> str: ...
def compile(
    model,
    input_args: Sequence,
    target_npu: str = "renegade",
    *,
    input_kwargs: Optional[Mapping] = None,
    target_ir: str = "edf",
    config: Optional[Mapping] = None,
    verbose: bool = False,
    enable_cache: bool = True,
    ignore_compile_error=False,
    skip_trace=False,
    skip_preprocess=False,
    print_fx_graph=False,
    only_cpu_tasks=False,
    experimental_lower_only_einsum_by_dpe=None,
    graph_metadata: Optional[str] = None,
    dump_tag: Optional[str] = None,
    dump_path: Optional[str] = None,
    dump_lir: bool = True,
    cache_dir: Optional[str] = None,
    cache_id: Optional[str] = None,
    extra_args_for_hash: Optional[Mapping] = None,
    **kwargs,
) -> Union[CompileResult, GraphModule]: ...
def compile_from_path(
    model_path: str,
    target_npu: str = "renegade",
    target_ir: str = "edf",
    *,
    config: Optional[Mapping] = None,
    verbose: bool = False,
    enable_cache: bool = True,
    only_cpu_tasks=False,
    experimental_lower_only_einsum_by_dpe=None,
    dump_tag: Optional[str] = None,
    dump_path: Optional[str] = None,
    dump_lir: bool = True,
) -> CompiledGraph: ...
def check_furiosa_ir(model, ir_kind: str) -> bool: ...
def create_llm_compiler_config(
    pretrained_id: str,
    num_chip: int,
    num_pe: int,
    batch_size: int,
    attention_size: int,
    input_ids_size: int,
    layers: Optional[Sequence[Tuple[LayerType, int]]],
    is_quantized: bool,
    enable_bf16_partial_sum_for_split: bool,
    has_valid_length_tensor: bool,
) -> str: ...
def create_vision_compiler_config() -> str: ...
def create_default_compiler_config() -> str: ...

class GraphMetadataBuilder:
    def __init__(self) -> None: ...
    @staticmethod
    def from_yaml(yaml: str) -> GraphMetadataBuilder: ...
    def set_valid_length(
        self,
        target_input_index: int,
        valid_length_input_index: int,
        valid_length_axis: int,
        sparse_key_axis: int,
        sparse_ratio_mean: float,
        sparse_ratio_sigma: float,
        sparse_ratio_sorted: bool,
    ) -> None:
        """Set valid length for builder. Valid length is used to determine the length of the input sequence in the batch."""
        ...

    def set_dram_shape_guide_with_guide_generator(
        self,
        pretrained_id: str,
        qtype: str,
        layers: Optional[Sequence[Tuple[LayerType, int]]],
        batch_size: int,
        kv_cache_size: int,
        attention_size: int,
        num_chips: int,
        kv_cache_shape: List[int],
    ) -> None:
        """Set dram shape guide for builder. Dram shape guide is generated
        by guide generator based on given parameters.
        """
        ...

    def set_io_category(
        self,
        input_categories: Sequence[IoCategory],
        output_categories: Sequence[IoCategory],
    ) -> None:
        """Set input/output category for builder."""
        ...

    def build(self) -> str:
        """Generate serialized graph metadata."""
        ...

class IoCategory:
    """Represents an category for input/output tensors in the graph."""

    @staticmethod
    def model_input() -> "IoCategory":
        """Represents a model input."""
        ...

    @staticmethod
    def intermediate(named_axes: Sequence[Optional[AxisName]]) -> "IoCategory":
        """Represents an intermediate tensor with optional named axes. Special names are "batch_size","""
        ...

    @staticmethod
    def weight() -> "IoCategory":
        """Represents a weight."""
        ...

    @staticmethod
    def model_output() -> "IoCategory":
        """Represents a model output."""

class AxisName:
    """Represents an axis name for intermediate tensors."""

    @staticmethod
    def batch() -> "AxisName":
        """Represents the batch axis."""
        ...

    @staticmethod
    def sequence() -> "AxisName":
        """Represents the sequence axis."""
        ...

    @staticmethod
    def embedding() -> "AxisName":
        """Represents the embedding axis."""
        ...

    @staticmethod
    def custom(name: str) -> "AxisName":
        """Represents a custom axis with the given name."""
        ...

class LayerType(enum.Enum):
    """Represents the type of a layer in the block (graph)."""

    EMBEDDING = auto()
    TRANSFORMER_BLOCK = auto()
    OUTPUT_HEAD_AND_POST_PROCESS = auto()
