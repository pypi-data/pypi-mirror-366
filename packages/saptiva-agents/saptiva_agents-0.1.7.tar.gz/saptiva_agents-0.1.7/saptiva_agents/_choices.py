from typing import Dict

from autogen_core.models import ModelInfo, ModelFamily

from saptiva_agents.tools import (
    get_weather, 
    wikipedia_search, 
    upload_csv,
    saptiva_bot_query,
    obtener_texto_en_documento,
    get_verify_sat,
    consultar_curp_get,
    consultar_curp_post,
    consultar_cfdi
)
from saptiva_agents.tools.langchain import WikipediaSearch

# OFICIAL TOOLING OPTIONS
TOOLS = {
    WikipediaSearch.__name__: WikipediaSearch,
    get_weather.__name__: get_weather,
    wikipedia_search.__name__: wikipedia_search,
    upload_csv.__name__: upload_csv,
    saptiva_bot_query.__name__: saptiva_bot_query,
    obtener_texto_en_documento.__name__: obtener_texto_en_documento,
    get_verify_sat.__name__: get_verify_sat,
    consultar_curp_get.__name__: consultar_curp_get,
    consultar_curp_post.__name__: consultar_curp_post,
    consultar_cfdi.__name__: consultar_cfdi,
}

MODEL_INFO: Dict[str, ModelInfo] = {
    # gemma2
    "Saptiva Turbo": {
        "vision": False,
        "function_calling": False,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    # gemma3
    "Saptiva Multimodal": {
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    # deepseek-coder
    "Saptiva Coder": {
        "vision": False,
        "function_calling": False,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    # llama3.3
    "Saptiva Legacy": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    # qwen2.5
    "Saptiva Ops": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    # qwen3
    "Saptiva Cortex": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    # llama-guard
    "Saptiva Guard": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
}
