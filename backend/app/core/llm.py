import httpx
import json
import asyncio
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class OllamaLLMClient:
    """Interface to Ollama for local LLM inference"""
    
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.ollama_base_url
        # self.model = model or settings.ollama_model
        self.model = settings.ollama_model
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def generate(
        self,
        query: str,
        context_chunks: list[str],
        max_tokens: int = None
    ) -> str:
        """Generate response using retrieved context"""
        
        max_tokens = max_tokens or settings.llm_max_tokens
        
        # Build context
        context = "\n\n".join([
            f"[Email Excerpt {i+1}]:\n{chunk}"
            for i, chunk in enumerate(context_chunks[:5])
        ])
        
        system_prompt = """You are a helpful assistant that answers questions about personal email history.
IMPORTANT RULES:
1. Only answer using the provided email context below
2. Do NOT invent or assume information
3. If you cannot answer from the context, say: "I don't have enough information in your emails to answer this question."
4. Be concise and direct
5. If relevant, mention the email sender and approximate date
6. Cite sources using [Source: sender | timestamp]"""
        
        user_prompt = f"""Email Context:
{context}

User Question: {query}

Answer (stay within the context provided):"""
        
        # Call Ollama's native generate endpoint and handle responses robustly
        try:
            payload = {
                "model": self.model,
                "prompt": user_prompt,
                "system": system_prompt,
                "stream": False,
                "temperature": settings.llm_temperature,
                "top_p": 0.9,
                "num_predict": max_tokens,
            }

            url = f"{self.base_url}/api/generate"
            logger.info("Calling Ollama generate: %s", url)
            response = await self.client.post(url, json=payload, timeout=120.0)

            # Log non-200 responses with body for easier debugging
            if response.status_code != 200:
                try:
                    body = await response.text()
                except Exception:
                    body = "<unreadable response body>"
                logger.error("Ollama generate failed %s: %s", response.status_code, body)
                return f"Error: LLM generate failed {response.status_code}: {body}"

            # Parse JSON safely
            try:
                data = response.json()
                return data.get("response", "")
            except Exception as e:
                text = await response.text()
                logger.error("Failed to parse JSON from Ollama response: %s", str(e))
                return f"Error: Invalid JSON from LLM: {text}"

            # Try multiple response shapes
            # content = None

            # # OpenAI-like choices -> message.content or text
            # if isinstance(data, dict) and data.get("choices"):
            #     choice = data["choices"][0]
            #     if isinstance(choice, dict):
            #         content = (
            #             choice.get("message", {}).get("content")
            #             or choice.get("text")
            #             or choice.get("content")
            #         )

            # # Ollama may return 'output' or 'result' fields
            # if not content and isinstance(data, dict) and data.get("output"):
            #     out = data.get("output")
            #     if isinstance(out, list):
            #         content = "\n".join([str(x) for x in out])
            #     else:
            #         content = str(out)

            # if not content and isinstance(data, dict) and data.get("result"):
            #     res = data.get("result")
            #     if isinstance(res, list):
            #         # try to extract 'content' keys
            #         parts = []
            #         for item in res:
            #             if isinstance(item, dict):
            #                 parts.append(item.get("content", ""))
            #             else:
            #                 parts.append(str(item))
            #         content = "\n".join(parts)
            #     else:
            #         content = str(res)

            # # Fallback: try to stringify a top-level 'text' or entire body
            # if not content:
            #     if isinstance(data, dict) and data.get("text"):
            #         content = data.get("text")
            #     else:
            #         # last resort: return part of raw JSON for debugging
            #         try:
            #             raw = json.dumps(data)
            #             logger.warning("Ollama returned unexpected schema, raw: %s", raw[:1000])
            #             content = raw
            #         except Exception:
            #             content = ""

            # return (content or "").strip() or "Error: empty response from LLM"

        except httpx.ConnectError:
            logger.exception("Cannot connect to Ollama at %s", self.base_url)
            return "Error: Cannot connect to Ollama. Make sure it's running on " + self.base_url
        except Exception as e:
            logger.exception("Unexpected error while calling Ollama: %s", str(e))
            return f"Error: {str(e)}"
    
    async def health_check(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags", timeout=5.0)
            return response.status_code == 200
        except:
            return False