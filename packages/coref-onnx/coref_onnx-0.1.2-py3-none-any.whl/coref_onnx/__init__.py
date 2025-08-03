"""
coref_onnx
~~~~~~~~~~

Lightweight crosslingual coreference resolution using ONNX Runtime
and distilled transformer models.
"""

__version__ = "0.1.2"
__author__ = "Tal Almagor"
__license__ = "MIT"
__email__ = "almagoric@gmail.com"

from coref_onnx.coref_resolver import (  # noqa: F401
    CoreferenceResolver,
    decode_clusters,
)
from coref_onnx.spacy_component import (  # noqa: F401
    SpaCyCorefComponent,
    create_coref_minilm_component,
)
