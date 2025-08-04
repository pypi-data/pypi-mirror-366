from enum import Enum


class KVDType(Enum):
    """
    Enum for different kv data type used in model quantization.

    Attributes:
        BF16 (str): The kv dtype is specified as 'bf16'.
        INT8 (str): the kv dtype is specified as 'int8'.

    """

    BF16 = 'bf16'
    INT8 = 'int8'


class WeightDType(Enum):
    """
    Enum for the weight dtype according to the supported quantization scheme.

    Attributes:
        W16A16 (str): For W16A16, the weight data type is specified as 'bf16'.
        W8A16 (str): For W8A16, the weight data type is specified as 'int8'.
        W8A8 (str): For W8A8, the weight data type is specified as 'int8'.

    """

    W16A16 = 'bf16'
    W8A16 = 'int8'
    W8A8 = 'int8'


class WeightBitPrecision(Enum):
    """
    Enum for the weight bit precision according to the supported quantization scheme.

    Attributes:
        W16A16 (int): For W16A16, the weight bit precision is specified as 16.
        W8A16 (int): For W8A16, the weight bit precision is specified as 8.
        W8A8 (int): For W8A8, the weight bit precision is specified as 8.
    """

    W16A16 = 16
    W8A16 = 8
    W8A8 = 8


class WeightCalibrationMethod(Enum):
    """
    Enum for different weight calibration methods supported in model quantization.

    Attributes:
        AMAX_SYM (str): Symmetric AMAX method. Quantizes weights symmetrically based on the maximum absolute value.
                        This approach ensures that positive and negative weights are represented with equal range and precision.
        ENTROPY_SYM (str): Symmetric Entropy method. Optimizes quantization levels by maximizing the entropy of weight distributions.
                           Aims to minimize information loss while maintaining quantization efficiency.
        PERCENTILE_SYM (str): Symmetric Percentile method. Utilizes weight value percentiles to determine quantization ranges.
                              Less sensitive to extreme values or outliers, providing a more uniform representation of the entire weight distribution.
    """

    AMAX_SYM = "AMAX_SYM"
    ENTROPY_SYM = "ENTROPY_SYM"
    PERCENTILE_SYM = "PERCENTILE_SYM"


class WeightGranularity(Enum):
    """
    Enum for specifying the granularity of weight quantization supported in model quantization.

    Attributes:
        CHANNEL (str): Channel-wise quantization. Quantizes weights independently for each channel,
                       considering the unique distribution of each channel to minimize information loss and optimize performance.
        TENSOR (str): Tensor-wise quantization. Applies quantization uniformly across the entire tensor.
                      While simpler to implement and computationally less expensive, it may not fully account for the characteristics of individual channels.
    """

    CHANNEL = "channel"
    TENSOR = "tensor"


class ActivationDType(Enum):
    """
    Enum for the activation dtype according to the supported quantization scheme.

    Attributes:
        W16A16 (str):  For W16A16, the activation data type is specified as 'bf16'.
        W8A16 (str): For W8A16, the activation data type is specified as 'bf16'.
        W8A8 (str): For W8A8, the activation data type is specified as 'int8'.

    """

    W16A16 = 'bf16'
    W8A16 = 'bf16'
    W8A8 = 'int8'


class ActivationBitPrecision(Enum):
    """
    Enum for the activation bit precision according to the supported quantization scheme.

    Attributes:
        W16A16 (int): For W16A16, the activation bit precision is specified as 16.
        W8A16 (int): For W8A16, the activation bit precision is specified as 16.
        W8A8 (int): For W8A8, the activation bit precision is specified as 8.
    """

    W16A16 = 16
    W8A16 = 16
    W8A8 = 8


class ActivationCalibrationMethod(Enum):
    """
    Enum for different activation calibration methods supported in model quantization.

    Attributes:
        MINMAX_ASYM (str): Asymmetric Min-Max method. Quantizes activations using an asymmetric approach
                           by scaling based on the minimum and maximum values. This method is suitable for data
                           that is not symmetrically distributed around zero.
        ENTROPY_ASYM (str): Asymmetric Entropy method. Optimizes quantization levels for activations by maximizing
                            the entropy, which helps in retaining the information content in the activation distribution
                            while quantizing.
        PERCENTILE_ASYM (str): Asymmetric Percentile method. Determines quantization ranges using percentiles of
                               the activation values, making it robust to outliers and extreme values in the activation distribution.
    """

    MINMAX_ASYM = "MINMAX_ASYM"
    ENTROPY_ASYM = "ENTROPY_ASYM"
    PERCENTILE_ASYM = "PERCENTILE_ASYM"


class ActivationGranularity(Enum):
    """
    Enum for specifying the granularity of activation quantization supported in model quantization.

    Attributes:
        CHANNEL (str): Channel-wise quantization for activations. Each channel of the activations is quantized independently,
                       allowing the quantization process to adapt to the specific statistical distribution of each channel.
        TENSOR (str): Tensor-wise quantization for activations. Applies a uniform quantization across the entire tensor.
                      This approach is simpler but might not capture the unique characteristics of activations in different channels.
    """

    CHANNEL = "channel"
    TENSOR = "tensor"


class AdvancedPTQ(Enum):
    """
    Enum for specifying the advanced PTQ algorithm supported in model quantization.

    Attributes:
        DISABLED (str): Default.
        SMOOTHQUANT (str): ["SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models"](https://arxiv.org/pdf/2211.10438)
        AWQ (str): ["AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration."](https://arxiv.org/pdf/2306.00978) [alpha-release 이후에 반영될 예정]
        GPTQ (str): ["GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers."](https://arxiv.org/pdf/2210.17323) [alpha-release 이후에 반영될 예정]
    """

    DISABLED = 'disabled'
    SMOOTHQUANT = 'SmoothQuant'


__all__ = [
    "WeightDType",
    "WeightBitPrecision",
    "WeightCalibrationMethod",
    "WeightGranularity",
    "ActivationDType",
    "ActivationBitPrecision",
    "ActivationCalibrationMethod",
    "ActivationGranularity",
    "AdvancedPTQ",
    "KVDType",
]
