import os
from openai import OpenAI

import os
import openai

class LLMEngine:
    def __init__(self, model="gpt-4"):
        self.model = model
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise Exception("OPENAI_API_KEY is not set in environment variables.")
        # Set the API key for OpenAI
        openai.api_key = self.api_key

    def generate_response(self, prompt):
        print(f"[DEBUG] Generating response for prompt: {prompt}", flush=True)
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            print(f"[DEBUG] OpenAI API response: {response}", flush=True)
            # Access the generated content using bracket notation
            return response.choices[0]['message']['content']
        except Exception as e:
            print(f"[DEBUG] Error during OpenAI API call: {e}", flush=True)
            raise
