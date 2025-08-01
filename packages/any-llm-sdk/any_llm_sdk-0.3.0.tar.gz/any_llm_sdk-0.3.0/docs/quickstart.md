## Quickstart

### Requirements

- Python 3.11 or newer
- API_KEYS to access to whichever LLM you choose to use.

### Installation

In your pip install, include the [supported providers](./providers.md) that you plan on using, or use the `all` option if you want to install support for all `any-llm` supported providers.

```bash
pip install 'any-llm-sdk[mistral,ollama]'
```

Make sure you have the appropriate API key environment variable set for your provider. Alternatively,
you could use the `api_key` parameter when making a completion call instead of setting an environment variable.

```bash
export MISTRAL_API_KEY="YOUR_KEY_HERE"  # or OPENAI_API_KEY, etc
```

### Basic Usage

[`completion`][any_llm.completion] and [`acompletion`][any_llm.acompletion] use a unified interface across all providers.

The provider_id key of the model should be specified according the [provider ids supported by any-llm](./providers.md).
The `model_id` portion is passed directly to the provider internals: to understand what model ids are available for a provider,
you will need to refer to the provider documentation.

```python
from any_llm import completion
import os

# Make sure you have the appropriate environment variable set
assert os.environ.get('MISTRAL_API_KEY')

model = "mistral/mistral-small-latest" # <provider_id>/<model_id>
# Basic completion
response = completion(
    model=model,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

In that above script,
updating to use an ollama hosted mistral model (assuming that you have ollama installed and running)
is as easy as updating the model to specify the ollama provider and using
[ollama model syntax for mistral](https://ollama.com/library/mistral-small3.2)!

```python
model="ollama/mistral-small3.2:latest"
```
