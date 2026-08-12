import httpx

from config import OLLAMA_MODEL, OLLAMA_URL


async def generate_ai_answer(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "system": (
                    "Ти корисний AI-асистент. "
                    "Відповідай українською мовою, коротко і зрозуміло."
                ),
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 200,
                },
            },
            timeout=120,
        )

    response.raise_for_status()

    data = response.json()

    return data["response"]