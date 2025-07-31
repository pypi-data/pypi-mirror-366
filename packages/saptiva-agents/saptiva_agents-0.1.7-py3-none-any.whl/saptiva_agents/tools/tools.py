import asyncio
import json
import os
import aiohttp
import io
from typing import Any
import base64

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from saptiva_agents import DEFAULT_LANG, CONTENT_CHARS_MAX


async def get_weather(city: str) -> str: # Async tool is possible too.
    """
    Get weather from a city.
    :param city: City name
    :return: Weather information
    """
    return f"The weather in {city} is 72 degree and sunny."


async def wikipedia_search(query: str) -> Any:
    """
    Function for searching information on Wikipedia without using `BaseTool`.

    Make sure to install Wikipedia:
        pip install wikipedia
    """
    try:
        api_wrapper = WikipediaAPIWrapper(doc_content_chars_max=CONTENT_CHARS_MAX, lang=DEFAULT_LANG, wiki_client="wikipedia")
        tool = WikipediaQueryRun(api_wrapper=api_wrapper)
        result = tool.invoke({"query": query})

        return result

    except Exception as e:
        raise e
    

# CSV Functions
async def upload_csv(uniqueID: str, file: str) -> Any:
    """
    Upload a CSV file to the Saptibank analyzer service.
    
    :param uniqueID: A string identifier
    :param file: Base64-encoded CSV file
    :return: JSON response from the API or error message
    """
    response = None
    try:
        decoded_file = base64.b64decode(file)
        file_obj = io.BytesIO(decoded_file)

        form_data = aiohttp.FormData()
        form_data.add_field('file', file_obj, filename='upload.csv', content_type='text/csv')
        form_data.add_field('uniqueID', uniqueID)

        async with aiohttp.ClientSession() as session:
            async with session.post('https://analizador.saptibank.vulcanics.mx/process_csv', data=form_data) as response:
                if response.status != 200:
                    raise Exception(f"API call failed with status {response.status}: {await response.text()}")
                data = await response.json()
                if 'error' in data:
                    raise Exception(f"API returned error: {data['error']}")
                response = data

    except Exception as e:
        response = e
        raise

    return response

# CFDI/CURP Functions
async def consultar_cfdi(url: str) -> Any:
    """
    Consume CFDI through the Vulcanics API with retry logic.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("The CFDI URL is required & must be a valid string.")

    payload = {"operation": "cfdi", "url": url}
    retries = 10
    wait_seconds = 1
    endpoint = "https://api-portal-saptibank.saptiva.com/"

    async with aiohttp.ClientSession() as session:
        for attempt in range(1, retries + 1):
            async with session.post(endpoint, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "error" not in data:
                        return data
                else:
                    if attempt < retries:
                        await asyncio.sleep(wait_seconds)
                    else:
                        raise Exception(f"Failed after {retries} attempts. Last status: {response.status}")
        
async def consultar_curp_post(curp: str) -> str:
    """
    Send a CURP via POST y and return ID.
    """
    if not isinstance(curp, str) or not curp.strip():
        raise ValueError("CURP is required and must be a valid string.")

    payload = {"operation": "curp", "curp": curp}
    async with aiohttp.ClientSession() as session:
        async with session.post("https://portalesrpa.vulcanics.mx/", json=payload) as response:
            if response.status not in [200, 201, 202]:
                raise Exception(f"Error in API request: {response.status}")
            data = await response.json()
            if "error" in data:
                raise Exception(f"Error in API response: {data['error']}")
            return data
        
async def consultar_curp_get(curp_id: str) -> Any:
    """
    Get CURP details via GET.
    """
    if not isinstance(curp_id, str) or not curp_id.strip():
        raise ValueError("The CURP ID is required and must be a valid string.")

    async with aiohttp.ClientSession() as session:
        async with session.get("https://portalesrpa.vulcanics.mx/curp", headers={"curp": curp_id}) as response:
            if response.status not in [200, 201, 202]:
                raise Exception(f"Error in API Request: {response.status}")
            data = await response.json()
            if "error" in data:
                raise Exception(f"Error in API Response: {data['error']}")
            return data

async def get_verify_sat(url: str) -> Any:
    """
    Verify SAT via API.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("La URL del SAT es requerida y debe ser una cadena válida.")

    payload = {"operation": "sat", "url": url}
    async with aiohttp.ClientSession() as session:
        async with session.post("https://portalesrpa.vulcanics.mx/", json=payload) as response:
            if response.status not in [200, 201, 202]:
                raise Exception(f"Error in API request: {response.status}")
            data = await response.json()
            if "error" in data:
                raise Exception(f"Error in API response: {data['error']}")
            return data

# PDF Extractor functions
async def obtener_texto_en_documento(doc_type: str, document: str, key: str="") -> Any:
    """
    Extract document data using Extractor service

    :param doc_type: Document type
    :param document: Document coded in base64
    :return: API response
    """
    if not isinstance(doc_type, str) or not doc_type.strip():
        raise ValueError("Field 'doc_type' must be a valid string.")

    try:
        if key == "":
            key = os.getenv("SAPTIVA_API_KEY")

        bearer_tkn = key
        base64_str = document.strip()  # remove leading/trailing whitespace/newlines
        decoded_file = base64.b64decode(base64_str, validate=True)
        file_obj = io.BytesIO(decoded_file)
        form_data = aiohttp.FormData()
        
        form_data.add_field(
            "file",
            file_obj,
            filename=f"document.{doc_type}",  
            content_type=f'application/{doc_type}'
        )
        form_data.add_field('system_prompt', "Eres un experto en convertir pdf a texto, tu tarea es llanamente convertir todo el pdf en texto, y devolverlo en json format. Sólo devuelve el contenido del PDF.")
        form_data.add_field('fields_to_extract', json.dumps({"text": "texto encontrado en el pdf"}))
        
        headers = {
            "Authorization": f"Bearer {bearer_tkn}"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post('https://api-extractor.saptiva.com/', data=form_data) as response:
                if response.status != 200:
                    raise Exception(f"Error in API request: {response} ({response.status})")
                data = await response.json()
                if 'error' in data and data['error']:
                    raise Exception(f"Error in API response: {data['error']}")
                return data

    except Exception as e:
        raise e

# Saptiva function
async def saptiva_bot_query(userMessage: str) -> Any:
    """
    Send a simple query to saptiva bot and get a response.

    :param userMessage: query.
    :return: bot's response.
    """
    if not isinstance(userMessage, str) or not userMessage.strip():
        raise ValueError("User message must be a valid string.")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://bot.saptibank.vulcanics.mx/query',
            json={"userMessage": userMessage},
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status != 200:
                raise Exception(f"Error getting saptiva bot request: {response.statusText}")
            data = await response.json()
            return data
