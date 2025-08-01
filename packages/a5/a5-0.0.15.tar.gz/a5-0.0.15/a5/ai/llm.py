# LLM utils

from openai import OpenAI
from os import environ


class LLM:
    def __init__(self, api_key=None, base_url=None, model=None, client=None, **kwargs):
        self.api_key = api_key or environ.get("LLM_API_KEY")
        if not self.api_key:
            raise ValueError("No LLM API key found")
        self.base_url = base_url or environ.get("LLM_BASE_URL") or "https://px.axess-ai.com/v1"
        self.model = model
        self.client = client or OpenAI(base_url=self.base_url, api_key=self.api_key, **kwargs)

    def with_model(self, model):
        return LLM(api_key=self.api_key, base_url=self.base_url, model=model, client=self.client)

    def complete(self, user_prompt, system_prompt=None, model=None, **kwargs):
        use_model = model or self.model
        if not use_model:
            raise ValueError("Model not provided in constructor nor at completion")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        completion = self.client.chat.completions.create(model=use_model, messages=messages, **kwargs)
        return completion.choices[0].message.content

    def json_complete(self, user_prompt, response_format, system_prompt=None, model=None, **kwargs):
        use_model = model or self.model
        if not use_model:
            raise ValueError("Model not provided in constructor nor at completion")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        completion = self.client.beta.chat.completions.parse(
            model=use_model, messages=messages, response_format=response_format, **kwargs
        )
        return completion.choices[0].message.parsed.model_dump()

    def embed(self, content, model=None, **kwargs):
        use_model = model or self.model
        if not use_model:
            raise ValueError("Model not provided in constructor nor at completion")
        embedding = self.client.embeddings.create(model=use_model, input=content, encoding_format="float", **kwargs)
        return embedding.data[0].embedding
