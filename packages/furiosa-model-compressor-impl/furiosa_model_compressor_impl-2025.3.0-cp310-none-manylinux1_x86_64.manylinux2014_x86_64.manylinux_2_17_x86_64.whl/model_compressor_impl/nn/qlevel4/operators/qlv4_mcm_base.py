import pickle
from typing import Dict

from torch import float32, float64, nn

from ..modeling.qlv4_output_modeling import QLV4_Output_MOD

__all__ = [
    "QLV4_ModelCompressorModule",
]


class QLV4_ModelCompressorModule(nn.Module):
    def __init__(self, org_target=None):
        super().__init__()
        self._skip_output_rounding = False
        self._run_dumping = False
        self._dump_file_path = None
        self._dumped = False
        self._dumping_mode = 'only-in-out'
        self._dumping_before_rounding = False
        self._dump_in_append_mode = False
        self.org_target = org_target

    def enable_skip_output_rounding(self):
        self._skip_output_rounding = True
        qlv4_output_mod = self._find_qlv4_output_mod()
        if qlv4_output_mod:
            output_module = qlv4_output_mod.pop()
            output_module.skip_rounding = True

    def disable_skip_output_rounding(self):
        self._skip_output_rounding = False
        qlv4_output_mod = self._find_qlv4_output_mod()
        if qlv4_output_mod:
            output_module = qlv4_output_mod.pop()
            output_module.skip_rounding = False

    def enable_dumping_mode(
        self,
        dump_file_path,
        dumping_mode,
        module_name,
        dumping_before_rounding,
        dump_in_append_mode,
    ):
        self._run_dumping = True
        self._dumped = False
        self._dump_file_path = dump_file_path
        self._name = module_name
        self._dumping_mode = dumping_mode
        self._dumping_before_rounding = dumping_before_rounding
        self._dump_in_append_mode = dump_in_append_mode

    def configure_output_dump_mode(self, output_module, dump_in_append_mode):
        if self._dump_in_append_mode:
            output_module.dump_in_append_mode = True

        if self._skip_output_rounding:
            output_module.skip_rounding = True

        if self._run_dumping and not self._dumped:
            output_module.run_dumping = True
            output_module.dumping_before_rounding = self._dumping_before_rounding
        else:
            output_module.run_dumping = False

    def dump(self, inputs, output_module=None, qerr_ub=-1):
        # [Data to dump]
        # 1. inputs (List)
        # 2. ouputs (Dict) containing output_dtype and output(or _before_rounding)
        # 3. qerr_ub
        # 4. dumping_before_rounding flag
        # 5. skip_output_rounding flag

        _data = {
            'inputs': [_input.to('cpu') if hasattr(_input, 'to') else _input for _input in inputs]
        }
        if output_module is not None:
            _dumped_data = output_module.dumped_data

            _dumped_data = {
                k: v.to('cpu') if hasattr(v, 'to') else v for k, v in _dumped_data.items()
            }
            _data.update(_dumped_data)

            # reset
            output_module.dumped_data = None

        _data.update(
            {
                'qerr_ub': qerr_ub,
                'dumping_before_rounding': self._dumping_before_rounding,
                'skip_output_rounding': self._skip_output_rounding,
            }
        )

        filename = self._dump_file_path

        # Open the file in binary append mode
        with open(filename, 'ab') as file:
            # Serialize and append the data to the file
            pickle.dump({self._name: _data}, file)

        self._dumped = True

        # Free Memory
        if output_module is not None:
            output_module.dumped_data = None

    def _calculate_qerr_ub(self, *args, **kwargs):
        # Overrided at each module
        return -1

    def _find_qlv4_output_mod(self):

        return [mod for mod in self._modules.values() if isinstance(mod, QLV4_Output_MOD)]

    def __call__(self, *args, **kwargs):
        output = self.forward(*args, **kwargs)

        if self._run_dumping and (not self._dumped or self._dump_in_append_mode):
            # 첫번째 sample seq에 대해서만 dump.
            if self._dump_file_path is None:
                raise ValueError("The file path for dumping data has not been assigned.")

            if self._dumping_mode != 'only-in-out':
                if self._dumping_mode == 'all_with_qerr_fp32':
                    emulation_dtype = float32
                elif self._dumping_mode == 'all_with_qerr_fp64':
                    emulation_dtype = float64
                else:
                    raise ValueError(f"Invalid dumpgint mode: {self._dumping_mode}.")

                qerr_ub = self._calculate_qerr_ub(*args, emulation_dtype=emulation_dtype)
            else:
                qerr_ub = -1

            qlv4_output_mod = self._find_qlv4_output_mod()
            self.dump(
                list(args),
                output_module=qlv4_output_mod.pop() if qlv4_output_mod else None,
                qerr_ub=qerr_ub,
            )

        return output

    def get_qmeta(self) -> Dict:
        QUANT_CONFIG_KEYS = [
            'real_dtype',
            'num_bits',
            'dtype',
            'weight_real_dtype',
            "dequant",
            "dequant_output_dtype",
        ]

        qmeta = {}

        for child_name, child in self.named_children():
            tq_meta = {}
            for key in QUANT_CONFIG_KEYS:
                if hasattr(child, key):
                    tq_meta[key] = getattr(child, key)

            qmeta[child_name] = tq_meta

        return qmeta
