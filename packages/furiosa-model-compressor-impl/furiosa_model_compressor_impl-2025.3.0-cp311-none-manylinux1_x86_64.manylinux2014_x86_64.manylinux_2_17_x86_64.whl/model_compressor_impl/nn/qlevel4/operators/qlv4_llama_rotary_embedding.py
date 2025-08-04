from ..modeling.qlv4_llama_rotary_embedding_modeling import QLV4_LlamaRotaryEmbedding_MOD
from .qlv4_mcm_base import QLV4_ModelCompressorModule

__all__ = ["QLV4_LlamaRotaryEmbedding"]


class QLV4_LlamaRotaryEmbedding(QLV4_ModelCompressorModule):
    def __init__(
        self,
        dim,
        emul_dtype,
        org_target,
        max_position_embeddings=2048,
        base=10000,
        **org_target_kwargs,
    ):
        super().__init__(org_target)
        self.QLV4_llama_rotary_embedding = QLV4_LlamaRotaryEmbedding_MOD(
            dim,
            emul_dtype,
            org_target,
            max_position_embeddings=max_position_embeddings,
            base=base,
        )

    def forward(self, input, seq_len=None):
        output = self.QLV4_llama_rotary_embedding(input, seq_len=seq_len)

        return output
