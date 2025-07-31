from saptiva_agents.models import ModelInfo

from fastapi import HTTPException
from langchain_core.tools import BaseTool

from saptiva_agents import TEXT_MODEL_LIST, MULTIMODAL_MODEL_LIST, MODEL_INFO, TOOLS
from saptiva_agents import SYSTEM_PROMPT
from saptiva_agents.models.models import Message
from saptiva_agents.tools.langchain import LangChainToolAdapter


def get_messages(messages):
    """
    Extracts user and system messages from a list of messages.
    Args:
        messages (list): A list of messages, each with a role and content.
    Returns:
        tuple: A tuple containing the user message and the system message.
    Raises:
        HTTPException: If no user message or content is found, or if the system message or content is not found.
    """
    user_message = next((msg for msg in messages if msg.role == "user"), None)
    system_message = next((msg for msg in messages if msg.role == "system"), None)

    if not user_message or not user_message.content:
        raise HTTPException(status_code=400, detail="No se encontró una consulta por parte del usuario.")

    if not system_message or not system_message.content:
        system_message = Message(content=SYSTEM_PROMPT, role="system")

    return user_message, system_message


def get_messages_with_image_urls(messages):
    """
    Extracts user and system messages from a list of messages and validates if it contains images.
    Args:
        messages (list): A list of messages, each with a role and content.
    Returns:
        tuple: A tuple containing the user message and the system message.
    Raises:
        HTTPException: If no user message or content is found, or if the system message or content is not found.
    """
    user_message = next((msg for msg in messages if msg.role == "user"), None)
    system_message = next((msg for msg in messages if msg.role == "system"), None)

    if not user_message or not user_message.content:
        raise HTTPException(status_code=400, detail="No se encontró una consulta por parte del usuario.")

    user_content = user_message.content

    if not isinstance(user_content, list) or len(user_content) < 2 or 'text' not in user_content[0]:
        raise HTTPException(
            status_code=400,
            detail="El campo 'content' debe ser una lista de elementos válidos (texto e imágenes). "
                   "Por favor verifica el formato e intenta nuevamente.")

    if not system_message or not system_message.content:
        system_message = Message(content=SYSTEM_PROMPT, role="system")

    return user_message, system_message


def extract_image_values(image_data):
    """
    Extracts image URLs and paths from a list of dictionaries and stores them in a list.
    """
    image_list = []

    for item in image_data:
        if item["type"] == "image_url":
            image_list.append(item["image_url"]["url"])
        elif item["type"] == "image_path":
            image_list.append(item["image_path"]["path"])

    if not image_list:
        raise HTTPException(status_code=400, detail="No se encontraron imágenes.")

    return image_list


def get_tools(tool_list):
    """
    Retrieves and validates tools based on a list of tool names.
    Args:
        tool_list (list): A list of tool names.
    Returns:
        list: A list of tool instances.
    Raises:
        HTTPException: If a specified tool is not available.
    """
    tools = []

    for item in tool_list:
        if item in TOOLS.keys():
                tools.append(TOOLS[item])
        else:
            raise HTTPException(
                status_code=400,
                detail=f"La herramienta '{item}' no está registrada o no está disponible.")

    return tools


def validate_langchain_instance(tool, tool_list):
    """
    Validate Langchain BaseTool class instance
    """
    if isinstance(tool, BaseTool):
        tool_list.append(LangChainToolAdapter(tool))
    else:
        raise HTTPException(
            status_code=400,
            detail=f"La herramienta '{tool.name}' no es compatible con LangChain."
        )

    return tool_list


def resolve_model_class(model: str) -> str:
    return model.split(":")[0]


def get_model_info(model: str) -> ModelInfo:
    try:
        resolved_model = resolve_model_class(model)
        return MODEL_INFO[resolved_model]
    except KeyError:
        raise KeyError(f"Modelo '{model}' no encontrado. Por favor verifica el modelo e intenta nuevamente.")


def get_text_model_list():
    return TEXT_MODEL_LIST


def get_multimodal_model_list():
    return MULTIMODAL_MODEL_LIST