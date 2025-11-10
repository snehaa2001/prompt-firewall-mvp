from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from app.core.secrets import get_openai_api_key, get_anthropic_api_key


class LLMService:
    def __init__(self):
        openai_key = get_openai_api_key()
        anthropic_key = get_anthropic_api_key()

        self.openai_client = AsyncOpenAI(api_key=openai_key) if openai_key else None
        self.anthropic_client = AsyncAnthropic(api_key=anthropic_key) if anthropic_key else None

    async def generate_response(self, prompt: str, model: str = "gpt-4o") -> str:
        try:
            if model.startswith("gpt") and self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=500,
                    temperature=0.7,
                )
                return response.choices[0].message.content

            elif model.startswith("claude") and self.anthropic_client:
                response = await self.anthropic_client.messages.create(
                    model=model, max_tokens=500, messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text

            else:
                return "LLM service not configured. Please set API keys in environment variables."

        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def moderate_content(self, text: str) -> dict:
        try:
            if self.openai_client:
                response = await self.openai_client.moderations.create(input=text)
                return response.results[0].model_dump()
            return {"error": "OpenAI client not configured"}
        except Exception as e:
            return {"error": str(e)}
