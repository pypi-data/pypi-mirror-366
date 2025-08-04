from ..modeling.qlv4_output_modeling import QLV4_Output_MOD
from ..modeling.qlv4_pooling_modeling import (
    QLV4_AdaptiveAvgPool2d_MOD,
    QLV4_FAdaptiveAvgPool2d_MOD,
    QLV4_MaxPool2d_MOD,
)
from .qlv4_mcm_base import QLV4_ModelCompressorModule

__all__ = [
    "QLV4_AdaptiveAvgPool2d",
    "QLV4_FAdaptiveAvgPool2d",
    "QLV4_MaxPool2d",
]


class QLV4_AdaptiveAvgPool2d(QLV4_ModelCompressorModule):
    def __init__(self, output_size, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_adaptiveavgpool2d = QLV4_AdaptiveAvgPool2d_MOD(output_size, emul_dtype)
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input):
        output = self.QLV4_adaptiveavgpool2d(input)
        output = self.QLV4_output(output)

        return output


class QLV4_FAdaptiveAvgPool2d(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_fadaptiveavgpool2d = QLV4_FAdaptiveAvgPool2d_MOD(emul_dtype)
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input, output_size):
        output = self.QLV4_fadaptiveavgpool2d(input, output_size)
        output = self.QLV4_output(output)

        return output


class QLV4_MaxPool2d(QLV4_ModelCompressorModule):
    def __init__(
        self,
        kernel_size,
        stride,
        padding,
        dilation,
        ceil_mode,
        qlv3_output_quantizer=None,
        **org_target_kwargs,
    ):
        super().__init__()
        self.QLV4_maxpool2d = QLV4_MaxPool2d_MOD(kernel_size, stride, padding, dilation, ceil_mode)
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input):
        output = self.QLV4_maxpool2d(input)
        output = self.QLV4_output(output)

        return output
