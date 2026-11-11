"""OpenAI-compatible provider.

Responsibility:
    Implement the provider interface for any endpoint that speaks the
    OpenAI chat completions API (hosted or local), configured by base URL,
    API key and model name.

Must NOT:
    - Retry or switch providers on its own (that is the router's job);
      it should surface rate-limit errors clearly instead.
    - Log request bodies, headers or API keys.
"""

# TODO(augusto): implement the OpenAI-compatible provider.
