from pathlib import Path
from typing import Dict, List, Optional, Tuple, Type, Union

from furiosa_llm_models.generators.generator import BaseGenerator
import torch
from torch import fx, nn
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast
from transformers.modeling_utils import PreTrainedModel

import model_compressor

from .typing import (
    ActivationCalibrationMethod,
    ActivationDType,
    ActivationGranularity,
    KVDType,
    TargetMachine,
    WeightCalibrationMethod,
    WeightDType,
    WeightGranularity,
    WeightOpEmulDtype,
)


def trace_model(
    model: torch.nn.Module,
    dataloader: torch.utils.data.DataLoader,
    generator_cls: Optional[Type] = None,
    generate_kwargs: Optional[Dict] = None,
    reduced_layer_sample_model: Optional[torch.nn.Module] = None,
):
    """
    This function traces a given model using provided data and configuration options.
    It is optimized for use with model classes provided in "furiosa-llm-models".

    To execute generation, the function requires `generator_cls` and `generate_kwargs`,
    where a generator is instantiated with the statement `generator = generator_cls(model)`.

    Args:
        model (torch.nn.Module): The PyTorch model to be traced.
        dataloader (torch.utils.data.DataLoader): DataLoader providing the necessary input data for tracing the model.
            A dataloader for calibration can also be used if applicable.
        generator_cls (Optional[Type], optional): A class to instantiate a generator object. Defaults to None.
        generate_kwargs (Optional[Dict], optional): A dictionary of keyword arguments to be passed to the generation function. Defaults to None.
        reduced_layer_sample_model (Optional[torch.nn.Module], optional): A model with reduced layers used for generating
            sample inputs for tracing. Typically, this should be a 1-layer sample model (full weight model) loaded using the
            standard model loading method, especially in multi-GPU scenarios to optimize tracing processes. Defaults to None.

    Returns:
        Tuple[fx.GraphModule,  fx.GraphModule]: A tuple containing the `prefill_graph` and `decode_graph`.
            - prefill_graph: The graph module for prefill operations.
            - decode_graph: The graph module for decode operations.
    """


def create_quantsim_model(
    model: torch.nn.Module,
    dataloader: Optional[torch.utils.data.DataLoader],
    target_machine: Union[str, TargetMachine] = TargetMachine.RNGD,
    weight_calib_method: Union[str, WeightCalibrationMethod] = WeightCalibrationMethod.AMAX_SYM,
    weight_dtype: Union[str, WeightDType] = WeightDType.W8A8,
    weight_granularity: Union[str, WeightGranularity] = WeightGranularity.CHANNEL,
    act_calib_method: Union[
        str, ActivationCalibrationMethod
    ] = ActivationCalibrationMethod.AMAX_SYM,
    act_dtype: Union[str, ActivationDType] = ActivationDType.W8A8,
    act_granularity: Union[str, ActivationGranularity] = ActivationGranularity.CHANNEL,
    kv_dtype: Union[str, KVDType] = KVDType.INT8,
    qformat_path: Union[str, dict, None] = None,
    qparam_path: Union[str, dict, None] = None,
    disable_inout: Tuple[bool, bool] = (False, False),
    weighted_op_emul_dtype: Union[str, WeightOpEmulDtype] = WeightOpEmulDtype.FP32,
    output_path: str = './',
) -> model_compressor.FXGraphCausalLM:
    """Converts a full-precision PyTorch model into a quantization simulation model (*quantsim model*).

    This function generates a quantsim model from a full-precision PyTorch model, preparing it for deployment on NPUs. The quantsim model simulates quantization effects and includes nodes that specify quantization operations.

    Once the quantsim model is created and calibrated, it can be transformed, along with its quantization metadata, into an Executable NPU Format (ENF) file using the Furiosa SDK, making it ready for execution on NPUs.

    For more detailed options, please refer to `typing.py`.

    Args:
        model (torch.nn.Module): The PyTorch model.
        dataloader (Optional[torch.utils.data.DataLoader]): DataLoader for calibration.
        target_machine (Union[str, TargetMachine], optional): Target machine type. Defaults to TargetMachine.RNGD.
        weight_calib_method (Union[str, WeightCalibrationMethod], optional): Weight calibration method.
        weight_dtype (Union[str, WeightDType], optional): Weight data type. Defaults to WeightDType.W8A8.
        weight_granularity (Union[str, WeightGranularity], optional): Weight quantization granularity.
        act_calib_method (Union[str, ActivationCalibrationMethod], optional): Activation calibration method.
        act_dtype (Union[str, ActivationDType], optional): Activation data type.
        act_granularity (Union[str, ActivationGranularity], optional): Activation quantization granularity.
        kv_dtype (Union[str, KVDType], optional): Key/value data type for quantization.
        qformat_path (Union[str, dict, None], optional): Path to quantization format file or dict.
        qparam_path (Union[str, dict, None], optional): Path to quantization parameters file or dict.
        disable_inout (Tuple[bool, bool], optional): Flags for disabling input/output quantization. Defaults to (False, False). This option will be removed in a future release.
        weighted_op_emul_dtype (Union[str, WeightOpEmulDtype], optional): Emulation dtype for weighted operations.
        output_path (str, optional): Path to save output files. Defaults to './'.

    Returns:
        model_compressor.FXGraphCausalLM: Quantized simulation model.
    """


def calibrate(
    model: model_compressor.FXGraphCausalLM,
    model_type: Optional[str] = None,
    enable_multi_gpu: bool = False,
    ckpt_folder_path: Optional[Path] = None,
) -> model_compressor.FXGraphCausalLM:
    """Performs quantization calibration for a quantsim model using the calibration dataloader.

    This function uses the provided dataloader to calibrate the quantization parameters of a quantsim model. Calibration adjusts the model's quantization parameters based on the data distribution observed in the calibration dataset. This step is crucial for ensuring the accuracy and performance of the quantized model, especially when working with reduced precision formats.

    Calibrates a quantization simulation model using the calibration dataloader.

    Args:
        model (model_compressor.FXGraphCausalLM): Quantsim model instance.
        model_type (Optional[str], optional): Type of model returned by type(torch_model). This option will be removed in a future release.
        enable_multi_gpu (bool, optional): Enable multi-GPU calibration. When enabled, the model is distributed across multiple GPUs. Defaults to False.
        ckpt_folder_path (Optional[Path], optional):  Model checkpoint file location. Required if init_with_empty_weight mode is used.

    Returns:
        model_compressor.FXGraphCausalLM: Calibrated quantsim model instance
    """


def create_pipeline_parallelism_model(
    model: Union[model_compressor.FXGraphCausalLM, fx.GraphModule],
    ckpt_folder_path: str,
    subgraph_ir: str = 'MCM',
    shared_param_dict: Optional[Dict] = None,
):
    """
    Distributes a model across multiple GPUs for pipeline parallelism.

    This function distributes a given model (Llama-based or FXGraph CausalLM model) across
    multiple GPUs using pre-saved sharded checkpoint weights. It handles the dividing of
    the model’s layers into multiple subgraphs (IR representation) and manages any shared parameters.

    Args:
        model (Union[FXGraphCausalLM, fx.GraphModule]): The empty input model to be distributed across GPUs.
        ckpt_folder_path (str): Path to the folder containing the sharded model checkpoints.
        subgraph_ir (str, optional): The intermediate representation (IR) of the subgraphs.
                                     The default is 'MCM' (Model Comprssor Module) and we only guarantee the operations for MCM IR.
        shared_param_dict (Optional[Dict], optional): Dictionary of shared parameters across chips to be loaded.
                                                      The default is None if no shared parameters are provided.

    Returns:
        Union[FXGraphCausalLM, fx.GraphModule]: The model distributed across multiple GPUs for pipeline parallelism.

    Example usage:
        model = create_pipeline_parallelism_model(
                    my_model,
                    ckpt_folder_path='path/to/checkpoints'
                )
    """


def export(
    model: model_compressor.FXGraphCausalLM,
    exported_model_name: str = 'exported_model.qckpt',
    qckpt_output_path: str = './',
    save_qckpt: bool = True,
) -> model_compressor.FXGraphCausalLM:
    """Exports the quantized model and quantization metadata for the Furiosa SDK.

    Args:
        model (model_compressor.FXGraphCausalLM): The calibrated quantsim model instance.
        exported_model_name (str): Name of the file for the exported model. Defaults to 'exported_model.qckpt'.
        qckpt_output_path (str, optional): Path for saving the quantized checkpoint data.
        save_qckpt (bool, optional): Whether to save the quantized checkpoint data. Defaults to True.

    Returns:
        model_compressor.FXGraphCausalLM: Optimized quantsim model instance
    """


def load_qckpt(
    quantized_model: model_compressor.FXGraphCausalLM,
    file_path: str = './',
    enable_multi_gpu: bool = False,
    load_decode_qckpt: bool = True,
) -> None:
    """
    Loads a quantized checkpoint file into a quantized model.

    Args:
        quantized_model (model_compressor.FXGraphCausalLM): The optimized quantsim model instance to load quantized data into.
        file_path (str, optional): Path to the quantized checkpoint file(*.qckpt).
        enable_multi_gpu (bool, optional): Load checkpoint with multi-GPU support. Defaults to False.
        load_decode_qckpt (bool, optional): Load decoding checkpoint, if applicable.

    Returns:
        None
    """


def save_tracing_guide(
    model: model_compressor.FXGraphCausalLM,
    trace_guide_json_path: str = './',
) -> None:
    """
    Saves a JSON guide to aid in compilation process.

    Args:
        model (model_compressor.FXGraphCausalLM): The calibrated quantsim model instance.
        trace_guide_json_path (str, optional): Path to save the tracing guide JSON.

    Returns:
        None
    """


class FXGraphCausalLM:
    """
    FXGraphCausalLM class that includes both `prefill` and `decode` graphs.

    This class defines a large language model that can handle both prefill and decode
    stages. This design can be used for efficient generation in models like Llama or GPT-J.

    Args:
        model_type (Type[nn.Module]): Type of model returned by type(torch_model). This option will be removed in a future release.
        prefill_model (GraphModule): The traced FX graph module for the prefill stage.
        decode_model (GraphModule, optional): The traced FX graph module for the decode stage. Defaults to None.
        return_tensors (bool, optional): Whether to return tensors instead of other output types. Defaults to True.
    """

    def __init__(
        self,
        model_type: Type[nn.Module],
        prefill_model: fx.GraphModule,
        decode_model: fx.GraphModule = None,
        generator_cls: Type[BaseGenerator] = None,
        used_dynamo: bool = False,
    ):
        self.model_type = model_type
        self.prefill_model = prefill_model
        self.decode_model = decode_model
        self.generator_cls = generator_cls
        self.used_dynamo = used_dynamo
        self.generator = None

    def generate(self, *args, **kwargs):
        """
        Generate text from the model.

        This method uses the configured generator to produce text sequences based on the input arguments
        and keyword arguments provided. It can generate text given an initial prompt or sequence.

        Args:
            *args: Positional arguments for text generation.
            **kwargs: Keyword arguments for text generation configuration.

        Returns:
            Generated text sequences from the model.

        Example Usage:
            ```python
            model = FXGraphCausalLM(...)
            model.generate(*args, **kwargs)
            ```
        """

        # If the generator is not initialized, create a new instance.
        if self.generator is None:
            self.generator = self.generator_cls(self)

        return self.generator.generate(*args, **kwargs)


__all__ = [
    "create_quantsim_model",
    "calibrate",
    "export",
    "load_qckpt",
    "save_tracing_guide",
    "FXGraphCausalLM",
]
