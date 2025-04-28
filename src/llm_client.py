import os
from groq import Groq

class LLMClient:
    """
    Groq LLM client for P4 code generation
    """

    def __init__(self):
        # from https://console.groq.com/docs/models
        self.model = os.getenv("GROQ_MODEL")
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def generate(self, prompt: str, max_new_tokens: int = 1500) -> str:
        """
        accepts prompt + budget for generation
        returns generated P4 code as a string
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at writing P4_16 code."},
                {"role": "user",   "content": prompt}
            ],
            max_tokens=max_new_tokens
        )
        return response.choices[0].message.content
