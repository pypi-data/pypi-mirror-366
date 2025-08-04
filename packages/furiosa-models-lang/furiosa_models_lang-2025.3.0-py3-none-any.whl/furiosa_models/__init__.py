from furiosa_models.architecture.models.llama import LlamaForCausalLM
from furiosa_models.architecture.models.qwen2 import Qwen2ForCausalLM
from furiosa_models.version import get_version

__version__ = get_version()

__all__ = [
    "__version__",
    "LlamaForCausalLM",
    "Qwen2ForCausalLM",
]
