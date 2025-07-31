## 🤖 Saptiva Agents

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/saptiva-agents.svg)](https://pypi.org/project/saptiva-agents/)
[![License](https://img.shields.io/github/license/saptiva/saptiva-agents)](https://github.com/saptiva-ai/saptiva-agents/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-online-blue)](https://app.gitbook.com/o/YD7tmPjNuCJPBtMoeymU/s/1Xeu6KDnv2A0dUxoQDDU/saptiva-agents/)

**Saptiva-Agents** es un potente framework para construir aplicaciones de IA multiagente que pueden actuar de forma autónoma o colaborar con humanos.

---

## ⚙️ Instalación

**Saptiva-Agents** requiere **Python 3.10 o superior**. Para instalar desde [**PyPI**](https://pypi.org/project/saptiva-agents/):

```bash
pip install -U saptiva-agents
```

---

## 🚀 Inicio rápido

## 👋 Hola, Mundo

Crea un agente asistente usando `Saptiva Legacy` con **Saptiva-Agents**:


```python


import asyncio

from saptiva_agents import SAPTIVA_LEGACY
from saptiva_agents.base import SaptivaAIChatCompletionClient
from saptiva_agents.agents import AssistantAgent

async def main() -> None:
    model_client = SaptivaAIChatCompletionClient(
        model=SAPTIVA_LEGACY, 
        api_key="TU_SAPTIVA_API_KEY"
    )
    agent = AssistantAgent("assistant", model_client=model_client)
    print(await agent.run(task="Di '¡Hola Mundo!'"))
    await model_client.close()

asyncio.run(main())
```

```bash
python hello_world.py
```

---

## 🌐 Equipo de Agentes para Navegación Web

Create a browser-based agent team using Playwright:

```python
# pip install saptiva-agents
# playwright install --with-deps chromium

import asyncio

from saptiva_agents import SAPTIVA_OPS
from saptiva_agents.agents import UserProxyAgent
from saptiva_agents.base import SaptivaAIChatCompletionClient
from saptiva_agents.conditions import TextMentionTermination
from saptiva_agents.teams import RoundRobinGroupChat
from saptiva_agents.web_surfer import MultimodalWebSurfer
from saptiva_agents.ui import Console

async def main() -> None:
    model_client = SaptivaAIChatCompletionClient(
        model=SAPTIVA_OPS, 
        api_key="TU_SAPTIVA_API_KEY"
    )
    web_surfer = MultimodalWebSurfer(
        "web_surfer", 
        model_client, 
        headless=False, 
        animate_actions=True, 
        start_page="https://www.google.com"
    )
    user_proxy = UserProxyAgent("user_proxy")
    termination = TextMentionTermination("exit", sources=["user_proxy"])
    team = RoundRobinGroupChat([web_surfer, user_proxy], termination_condition=termination)

    try:
        await Console(team.run_stream(task="Navega a saptiva.com y consigue información sobre Saptiva AI."))
    finally:
        await web_surfer.close()
        await model_client.close()

asyncio.run(main())
```

```bash
python web_surfer.py
```

---

## 📚 Modelos Disponibles

**Saptiva-Agents** soporta una variedad de modelos para tareas tanto de texto como multi-modales. En caso de requerir implementación de herramientas (tools) te recomendamos usar los siguientes modelos que soportan dicha caracteristica:

## 🧠 Modelos de texto

| Nombre           | Modelo Base         | Mejor para                                   | Caso de Uso                                             |
|------------------|----------------------|-----------------------------------------------|----------------------------------------------------------|
| `Saptiva Cortex` | qwen3:30b            | Tareas de razonamiento                        | Agentes con lógica, comprensión profunda                |
| `Saptiva Ops`    | qwen2.5:72b-instruct | Casos complejos con tools y SDK              | Agentes autónomos, RAG, websearch                      |
| `Saptiva Legacy` | llama3.3:70b         | Compatibilidad con herramientas legacy        | SDK avanzado, pruebas, compatibilidad técnica          |

---

## 🖼️ Modelos multi-modal

| Nombre              | Modelo Base   | Mejor para                                                                 | Caso de Uso                                                                 |
|---------------------|----------------|------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| `Saptiva Multimodal`| gemma3:27b     | Procesamiento combinado de texto e imágenes, largos contextos multilingües. | Visual Q&A, OCR + extracción y estructuración de contenido, asistencia técnica con apoyo visual, análisis multimedia. |

> 🔗 [Ver lista completa de modelos disponibles en Saptiva](https://saptiva.gitbook.io/saptiva-docs/basicos/modelos-disponibles)

---

## 🧰 Custom Tools

Junto a la SDK viene un grupo de tools pre-determinadas con funcionalidades que puedes adherir en la fase de inicialización de tus agentes, estas tools dan acceso a funcionalidades tales como extracción de documentos, consultas CURP, CFDI y demás.

Haz clic en el siguiente link para más información:

💼 [**Custom Tools**](https://saptiva.gitbook.io/saptiva-docs/saptiva-agents/custom-tools)

> **Nota:**  
> La lista de tools pre-determinadas está disponible a partir de la versión **0.1.3** de nuestro **SDK**.

## 📄 Licencia

Este proyecto está licenciado bajo la [Licencia MIT](https://github.com/saptiva-ai/saptiva-agents/blob/main/LICENSE).

---

## 🌐 Enlaces

- 🔗 [Documentación Oficial](https://saptiva.gitbook.io/saptiva-docs/)
