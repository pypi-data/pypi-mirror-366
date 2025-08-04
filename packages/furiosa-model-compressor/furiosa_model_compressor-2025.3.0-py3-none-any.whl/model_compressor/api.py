from functools import wraps
import inspect
import logging
import os
from pathlib import Path
import sys
import types
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Type, Union

import model_compressor_impl as _impl
import torch
from torch import fx
from transformers.modeling_utils import PreTrainedModel

logger = logging.getLogger("api")

MAP_LOCATION = Optional[
    Union[Callable[[torch.Tensor, str], torch.Tensor], torch.device, str, Dict[str, str]]
]

TENSOR_NAMES_WITH_BATCH_DIM: List[str] = [
    'input_ids',
    'attention_mask',
    'causal_mask',
    'position_ids',
]

__all__ = [
    "create_quantsim_model",
    "calibrate",
    "export",
    "save_tracing_guide",
    "create_pipeline_parallelism_model",
    "load_on_multi_gpus_from_cpu",
    # e2e_verfication
    "set_model_to_dump_golden_model",
    "enable_qlv4_skip_output_rounding",
    "check_conformance",
    # immigrate_qparam 사용하는 경우를 위해서 추가됨. API정리 후 한번에 깔끔히 제거 필요합니다.
    # https://github.com/furiosa-ai/model-compressor-private/pull/697
    "save_qformat_qparam",
    # NOTE: 아래 함수들은 모두 제거해도 되지 않을까요?
    "load_qckpt",
    "save_qformat",
    # "ptq_auto_optimize",
    "extract_qformat_and_qparam",
    # "mc_impl.helper"
    "FXGraphCausalLM",
    "setup_tracing_dataloaders_for_prefill_decode",
    "llama_custom_symbolic_trace",
    "trace_model",
]


def track_kwargs(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 현재 함수에 대한 인수 정보를 가져옴
        sig = inspect.signature(func)
        bound_args = sig.bind_partial(*args, **kwargs).arguments

        # 사용자가 명시적으로 제공한 인수를 추적
        wrapper._user_provided_args = set(kwargs.keys()).union(bound_args.keys())

        return func(*args, **kwargs)

    wrapper._user_provided_args = set()
    return wrapper


@track_kwargs
def create_quantsim_model(
    model: torch.nn.Module,
    dataloader: Optional[torch.utils.data.DataLoader] = None,
    target_machine: str = 'RGDA0',
    # qformat
    weight_calib_method: str = "AMAX_SYM",
    weight_dtype: str = "int8",
    weight_granularity: str = "channel",
    act_calib_method: str = "PERCENTILE_ASYM",
    act_dtype: str = "int8",
    act_granularity: str = "channel",
    kv_dtype: str = 'bf16',
    v_cache_granularity: str = 'channel',
    disable_inout: Tuple[bool, bool] = (False, False),
    # graph pattern search
    transformer_block_yaml=None,
    # Quant config
    act_zp_equalizing: str = 'disabled',
    outlier_percentile: Optional[int] = None,
    # Advanced Quant confi
    nodes_excluded_from_outlier_compensation: List[str] = None,
    # Other Options
    data_preprocessor: Optional[Callable] = None,
    output_path: str = './',
    # 나머지
    outlier_dtype: str = "int8",
    bcq_iter: int = 10,
    qformat_path: Union[str, dict, None] = None,
    qparam_path: Union[str, dict, None] = None,
    qlv2_calib_graph_skeleton_path: Union[str, dict, None] = None,
    bn_folding: bool = True,
    qlevel: int = 2,
    qlevel3_emul_mode: str = 'normal',
    weighted_op_emul_dtype: str = 'fp64',
    concrete_args: Optional[Dict[str, Any]] = None,
    skipped_methods: List[str] = None,
    decode_phase: bool = False,
    draw_each_gtx_graph=False,
    immigrate_qparams=False,
    unify_inter_pipeline_dtype=True,
    set_pow_dtype_to_bf16=False,
    debug_mode_force_to_int8=False,
    disable_old_node_mapping=False,
    disable_auto_node_mapping=False,
    force_softmax_emul_dtype_to_fp32=False,
    gtx_measure_time=False,
    naive_quantize=False,
) -> fx.GraphModule:

    entire_func_args = dict(locals())
    user_provided_args = {
        x: y for x, y in entire_func_args.items() if x in create_quantsim_model._user_provided_args
    }
    del user_provided_args['model']

    return _impl.create_quantsim_model(
        model,
        user_provided_args,
        dataloader,
        target_machine,
        # qformat
        weight_calib_method,
        weight_dtype,
        weight_granularity,
        act_calib_method,
        act_dtype,
        act_granularity,
        kv_dtype,
        v_cache_granularity,
        disable_inout,
        # graph pattern search
        transformer_block_yaml,
        # Quant config
        act_zp_equalizing,
        outlier_percentile,
        # Advanced Quant confi
        nodes_excluded_from_outlier_compensation,
        # Other Options
        data_preprocessor,
        output_path,
        # 나머지
        outlier_dtype,
        bcq_iter,
        qformat_path,
        qparam_path,
        qlv2_calib_graph_skeleton_path,
        bn_folding,
        qlevel,
        qlevel3_emul_mode,
        weighted_op_emul_dtype,
        concrete_args,
        skipped_methods,
        decode_phase,
        draw_each_gtx_graph,
        immigrate_qparams,
        unify_inter_pipeline_dtype,
        set_pow_dtype_to_bf16,
        debug_mode_force_to_int8,
        disable_old_node_mapping,
        disable_auto_node_mapping,
        force_softmax_emul_dtype_to_fp32,
        gtx_measure_time,
        naive_quantize,
    )


@track_kwargs
def export(
    model: fx.GraphModule,
    exported_model_name: str = 'exported_model.qckpt',
    artifacts_dir_path: str = './',
    qparam_path: Optional[str] = None,
    qformat_path: Optional[str] = None,
    save_qckpt: bool = True,
    target_machine: str = 'RGDA0',
    decode_phase: bool = False,
    disable_old_node_mapping=False,
    disable_auto_node_mapping=False,
    weighted_op_emul_dtype="fp64",
    transformer_block_yaml: Optional[Path] = None,
    gtx_measure_time=False,
):
    """qlevel4단계의 quantized model weight를 저장.

    Args:
        model (fx.GraphModule): MCM IR을 포함한 fx graph module.
        file_path (str)
        qparam_path (str)
        qformat_path (str)
        target_machine (str, optional):Defaults to 'RGDA0'.
    """
    entire_func_args = dict(locals())
    user_provided_args = {
        x: y for x, y in entire_func_args.items() if x in export._user_provided_args
    }
    del user_provided_args['model']

    return _impl.export(
        model,
        user_provided_args,
        exported_model_name,
        artifacts_dir_path,
        qparam_path,
        qformat_path,
        save_qckpt,
        target_machine,
        decode_phase,
        disable_old_node_mapping,
        disable_auto_node_mapping,
        weighted_op_emul_dtype,
        transformer_block_yaml,
        gtx_measure_time,
    )


def load_qckpt(
    quantized_model: fx.GraphModule,
    file_path: str = './',
    enable_multi_gpu: bool = False,
    load_decode_qckpt: bool = True,
    map_location: MAP_LOCATION = None,
):
    """Load weight to quantized model."""
    _impl.load_qckpt(quantized_model, file_path, enable_multi_gpu, load_decode_qckpt, map_location)
    return


def extract_qformat_and_qparam(
    model: fx.GraphModule = None,
):
    return _impl.extract_qformat_and_qparam(model)


def save_qformat(
    model: fx.GraphModule = None,
    qformat_dict: Optional[dict] = None,
    qformat_out_path: Optional[str] = None,
    weight_calib_method: Optional[str] = None,
    weight_granularity: Optional[str] = None,
    weight_dtype: Optional[str] = None,
    act_calib_method: Optional[str] = None,
    act_granularity: Optional[str] = None,
    act_dtype: Optional[str] = None,
    kv_dtype: Optional[str] = None,
    disable_mods: Optional[List[str]] = None,
    disable_inout: Tuple[bool, bool] = (False, False),
    v_cache_granularity: Optional[str] = None,
    qlevel: int = 1,
) -> None:
    _impl.save_qformat(
        model,
        qformat_dict,
        qformat_out_path,
        weight_calib_method,
        weight_granularity,
        weight_dtype,
        act_calib_method,
        act_granularity,
        act_dtype,
        kv_dtype,
        disable_mods,
        disable_inout,
        v_cache_granularity,
        qlevel,
    )
    return


def save_qformat_qparam(
    model: fx.GraphModule = None,
    artifacts_out_dir: Optional[str] = './',
    qformat_dict: Optional[dict] = None,
    qformat_out_path: Optional[str] = None,
    qparam_dict: Optional[dict] = None,
    qparam_out_path: Optional[str] = None,
    weight_calib_method: Optional[str] = None,
    weight_granularity: Optional[str] = None,
    weight_dtype: Optional[str] = None,
    act_calib_method: Optional[str] = None,
    act_granularity: Optional[str] = None,
    act_dtype: Optional[str] = None,
    kv_dtype: Optional[str] = None,
    disable_mods: Optional[List[str]] = None,
    disable_inout: Tuple[bool, bool] = (False, False),
    v_cache_granularity: Optional[str] = None,
    qlevel: Optional[int] = None,
) -> None:

    _impl.save_qformat_qparam(
        model,
        artifacts_out_dir,
        qformat_dict,
        qformat_out_path,
        qparam_dict,
        qparam_out_path,
        weight_calib_method,
        weight_granularity,
        weight_dtype,
        act_calib_method,
        act_granularity,
        act_dtype,
        kv_dtype,
        disable_mods,
        disable_inout,
        v_cache_granularity,
        qlevel,
    )


@track_kwargs
def calibrate(
    model: fx.GraphModule,
    # dataloader: Optional[torch.utils.data.DataLoader],
    model_name: str = None,
    # target_machine: str = 'gpu',
    model_type: Optional[str] = None,
    # qformat
    # weight_calib_method: str = "AMAX_SYM",
    # weight_dtype: str = "int8",
    # weight_granularity: str = "channel",
    # act_calib_method: str = "PERCENTILE_ASYM",
    # act_dtype: str = "int8",
    # act_granularity: str = "channel",
    # kv_dtype: Optional[str] = None,
    # v_cache_granularity: str = 'channel',
    # disable_inout: Tuple[bool, bool] = (False, False),
    group_size: Optional[int] = None,
    # graph pattern search
    # transformer_block_yaml: Optional[Path] = None,
    # Quant config
    # act_zp_equalizing: str = 'disabled',
    percentile: float = 99.9,
    # outlier_percentile: Optional[int] = None,
    # Advancded Quant config
    autoscale: str = 'disabled',
    autoscale_calib_method: str = 'auto',
    autoscale_calib_kwargs: Optional[Dict] = None,
    autoclip: bool = False,  # ??
    outlier_calib_cfg: Optional[Dict] = None,
    ckpt_folder_path: Optional[Path] = None,  # ??
    smoothquant_alpha: float = 0.5,  # SMQ
    unify_smooth_factor: bool = False,  # SMQ
    module_name_to_replace_smooth_factor: Optional[str] = None,  # SMQ
    module_name_for_smooth_factor: Optional[str] = None,  # SMQ
    nodes_excluded_from_auto_scale_calib: Optional[List] = None,
    nodes_excluded_from_auto_clip_calib: Optional[List] = None,
    enable_kv_sep_calib: bool = False,
    max_single_batch_size: Optional[int] = None,
    # Other Options
    # data_preprocessor: Optional[Callable] = None, #??
    is_dynamic_quant: bool = False,  # ??
    disable_mods: Optional[List[str]] = None,  # ??
    enable_multi_gpu: bool = False,
    memory_saving_mode: bool = False,
    # output_path: str = './', #??
    get_prev_autoscale_calib_cfg: bool = False,
    ckpt_to_state_key_map: Optional[Dict] = None,
    use_dynamo_export: bool = False,
) -> None:

    entire_func_args = dict(locals())
    user_provided_args = {
        x: y for x, y in entire_func_args.items() if x in calibrate._user_provided_args
    }
    del user_provided_args['model']

    return _impl.calibrate(
        model,
        user_provided_args,
        model_name,
        model_type,
        group_size,
        percentile,
        autoscale,
        autoscale_calib_method,
        autoscale_calib_kwargs,
        autoclip,
        outlier_calib_cfg,
        ckpt_folder_path,
        smoothquant_alpha,
        unify_smooth_factor,
        module_name_to_replace_smooth_factor,
        module_name_for_smooth_factor,
        nodes_excluded_from_auto_scale_calib,
        nodes_excluded_from_auto_clip_calib,
        enable_kv_sep_calib,
        max_single_batch_size,
        is_dynamic_quant,
        disable_mods,
        enable_multi_gpu,
        memory_saving_mode,
        get_prev_autoscale_calib_cfg,
        ckpt_to_state_key_map,
        use_dynamo_export,
    )


def load_on_multi_gpus_from_cpu(model: fx.GraphModule) -> fx.GraphModule:
    return _impl.multi_chip.load_on_multi_gpus_from_cpu(model)


def create_pipeline_parallelism_model(
    model: fx.GraphModule,
    ckpt_folder_path: str,
    subgraph_ir: str = 'MCM',
    shared_param_dict: Optional[Dict] = None,
    ckpt_to_state_key_map: Optional[Dict] = None,
    use_dynamo_export: bool = False,
):
    return _impl.create_pipeline_parallelism_model(
        model,
        ckpt_folder_path,
        subgraph_ir,
        shared_param_dict,
        ckpt_to_state_key_map,
        use_dynamo_export,
    )


def save_tracing_guide(
    model: fx.GraphModule,
    trace_guide_json_path: str = './',
):
    '''
    model fx.graph에서 trasnformer block들을 찾아서 json파일로 저장합니다.
    '''

    _impl.save_tracing_guide(model, trace_guide_json_path)


# Note: model_compressor_impl.helper 내부 함수들
def llama_custom_symbolic_trace(
    model: PreTrainedModel,
    input_names: Optional[List[str]] = None,
    disable_check: bool = False,
    use_cache: bool = True,
) -> fx.GraphModule:
    """
    Performs custom symbolic tracing on the model.
    """
    return _impl.helper.llama_custom_symbolic_trace(model, input_names, disable_check, use_cache)


class FXGraphCausalLM(_impl.helper.FXGraphCausalLM):
    """
    Inherited FXGraphCausalLM class from `model_compressor_impl.helper`.
    This allows usage as `model_compressor.FXGraphCausalLM`.

     prefill, decode graph를 모두 포함한 FXGraphCausalLM class를 정의합니다.
    """

    pass


def setup_tracing_dataloaders_for_prefill_decode(
    torch_model: torch.nn.Module,
    dataloader: torch.utils.data.DataLoader,
    device: str,
    generator_cls: Optional[Type] = None,
    gen_kwargs: Optional[Dict] = None,
    use_max_length_only=False,
    # inputs_without_batch_axis:Optional[List]=None,
):
    """
    Designed to facilitate extracting of input names for the prefill/decode graph tracing.
    """

    return _impl.helper.dynamo.capture_example_input_for_tracing(
        torch_model, dataloader, device, generator_cls, gen_kwargs, use_max_length_only
    )


def trace_model(
    model: torch.nn.Module,
    dataloader: torch.utils.data.DataLoader,
    generator_cls: Optional[Type] = None,
    generate_kwargs: Optional[Dict] = None,
    reduced_layer_sample_model: Optional[torch.nn.Module] = None,
    tensor_names_with_batch_dim: List[str] = TENSOR_NAMES_WITH_BATCH_DIM,
):
    """
    torch._dynamo.export 함수를 사용하여 모델을 export 합니다.
    """
    return _impl.helper.dynamo.trace_model(
        model,
        dataloader=dataloader,
        generator_cls=generator_cls,
        generate_kwargs=generate_kwargs,
        reduced_layer_sample_model=reduced_layer_sample_model,
        tensor_names_with_batch_dim=tensor_names_with_batch_dim,
    )


# NOTE: 나중에 RNGD에서도 구현해야 하나, 현재 실행가능하지 않으므로  코드를 지우지 말고 주석처리로 보관합니다.
'''
def ptq_auto_optimize(
    model: torch.nn.Module,
    calib_dataloader: Optional[torch.utils.data.DataLoader],
    valid_func: types.FunctionType = None,
    target_machine: str = 'RGDA0',
    data_preprocessor: Optional[Callable] = None,
    weight_dtype: str = 'int8',
    weight_nbits: int = 8,
    act_dtype: str = 'int8',
    act_nbits: int = 8,
    bn_folding: bool = True,
    qlevel: int = 1,
    qlevel3_emul_mode: str = 'normal',
    disable_inout=(False, False),
    concrete_args: Optional[Dict[str, Any]] = None,
    skipped_methods: List[str] = None,
    output_path: str = './',
    kv_dtype: Optional[str] = None,
    disable_mods: Optional[List[str]] = None,
) -> fx.GraphModule:

    if skipped_methods is None:
        skipped_methods = []

    _optcheck_output_dir(output_path, 'output_path')

    if disable_mods is None:
        disable_mods = []

    qparam_out_path = os.path.join(output_path, "qparam.npy")
    qformat_out_path = os.path.join(output_path, "qformat.yaml")

    # Check option values.
    _optcheck_target_machine(target_machine)
    _optcheck_valid_func(valid_func)
    _optcheck_target_machine(target_machine)

    # main function
    if target_machine in ['RGDA0']:
        quantized_model, best_quant_scehem = ptq_auto_optimization.ptq_auto_optimize(
            model,
            calib_dataloader,
            valid_func,
            data_preprocessor,
            weight_dtype,
            weight_nbits,
            act_dtype,
            act_nbits,
            bn_folding,
            qlevel,
            target_machine,
            qlevel3_emul_mode,
            disable_inout,
            concrete_args=concrete_args,
            skipped_methods=skipped_methods,
        )

        qformat_dict = qformat.extract_qformat(
            model,
            disable_mods,
        )

        qformat.save_qformat(
            qformat_dict=qformat_dict,
            qformat_out_path=qformat_out_path,
            weight_calib_method=best_quant_scehem['weight_calib_method'],
            weight_granularity=best_quant_scehem['weight_granularity'],
            weight_dtype=weight_dtype,
            weight_nbits=weight_nbits,
            act_calib_method=best_quant_scehem['act_calib_method'],
            act_granularity=best_quant_scehem['act_granularity'],
            act_dtype=act_dtype,
            act_nbits=act_nbits,
            kv_dtype=kv_dtype,
            disable_inout=disable_inout,
        )
        logger.info(f"Qformat yaml file saved: {qformat_out_path}")
        qformat.save_qparams(qparam_out_path, model=model)
        logger.info(f"Quantization parameters file saved: {qparam_out_path}")

        return quantized_model
    else:
        raise NotImplementedError

    return
'''


def set_model_to_dump_golden_model(
    dump_file_path,
    model: fx.GraphModule,
    dumping_range: str = 'qlv4_linear',
    dumping_mode: str = 'only-in-out',
    qlv4_skip_output_rounding: bool = False,
    dumping_before_rounding: bool = False,
    dump_in_append_mode: bool = False,
):
    _impl.set_model_to_dump_golden_model(
        dump_file_path,
        model,
        dumping_range,
        dumping_mode,
        qlv4_skip_output_rounding,
        dumping_before_rounding,
        dump_in_append_mode,
    )


def enable_qlv4_skip_output_rounding(model: fx.GraphModule, applied_range: str = 'linear'):
    _impl.enable_qlv4_skip_output_rounding(model, applied_range)


def check_conformance(
    comparison_model: Union[fx.GraphModule, str],
    golden_file_path: str,
    dumping_range: str = 'qlv4_linear',
    result_file_path: Optional[str] = None,
    mcm_name_to_check: Optional[str] = None,
    mcm_name_map: Optional[dict] = None,
    compare_rounded_result: bool = False,
):
    """
    주어진 모델과 골든 모델 결과를 비교하는 함수를 실행합니다.

    Args:
        comparison_model(fx.GraphModule or str): MCM으로 변환된 테스트 모델 또는 모델 dump file path
        golden_file_path (str]): 골든 모델 결과를 포함하고 있는 파일 경로.
        dumping_range (str, optional): Test를 진행할 layer 범위 설정. 기본값은 'qlv4_linear'입니다.
        result_file_path (Optional[str], optional): 비교 결과를 저장할 파일 경로.
            지정되지 않을 경우, 현재 시간 정보를 기준으로 파일 이름이 설정됩니다. 기본값은 None입니다.
        mcm_name_to_check (Optional[str], optional): 특정 레이어만 비교할 경우, 설정이 필요한 변수로 테스트를 수행할 모듈 이름을 설정합니다. 기본값은 None입니다.
        mcm_name_map (Optional[dict], optional): 골든 모델과 현재 모델의 레이어 이름이 일치하지 않을 경우,
            {현재_모델_레이어_이름: 골든_모델_레이어_이름} 형식의 매핑 정보를 입력합니다. 기본값은 None입니다.
        compare_rounded_result (bool, optional): 비교할 값을 반올림 전 혹은 후로 할지 설정합니다.
            True로 설정하면 rounding 후로 비교하고, False로 설정하면 rounding 전으로 비교합니다. 기본값은 False입니다.
    """
    _impl.check_conformance(
        comparison_model,
        golden_file_path,
        dumping_range,
        result_file_path,
        mcm_name_to_check,
        mcm_name_map,
        compare_rounded_result,
    )
