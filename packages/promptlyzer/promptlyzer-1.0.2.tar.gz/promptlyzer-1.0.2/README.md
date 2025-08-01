# Promptlyzer Python Client

The official Python client for [Promptlyzer](https://promptlyzer.com) - manage and version your prompts, run them across multiple LLM providers.

**Key Features:**
- **Prompt Management**: Version control, environments (dev/staging/prod), and centralized storage
- **Multi-Provider Inference**: Single API for OpenAI, Anthropic, and Together AI models
- **Streaming Support**: Real-time streaming responses for all providers
- **Cost & Performance Tracking**: Monitor usage, costs, and latency across providers
- **A/B Testing**: Compare different prompts and models side-by-side
- **Auto-reload**: Automatically fetch latest prompt versions

## Installation

```bash
pip install promptlyzer
```

## Quick Start

### 1. Get Your API Key

Log in to [Promptlyzer](https://promptlyzer.com) and generate an API key from Settings → API Keys.

### 2. Set Up Client

```python
from promptlyzer import PromptlyzerClient

# Option 1: Direct API key
client = PromptlyzerClient(api_key="pk_live_YOUR_API_KEY")

# Option 2: Environment variable (recommended)
# Set: export PROMPTLYZER_API_KEY=pk_live_YOUR_API_KEY
client = PromptlyzerClient()
```

### 3. Basic Usage

```python
# Configure LLM provider
client.configure_inference_provider("openai", "sk-...")

# Use a prompt from Promptlyzer
response = client.inference.infer(
    prompt={"project_id": "your-project-id", "prompt_name": "assistant"},
    model="gpt-4o"
)

print(response.content)
print(f"Cost: ${response.metrics.cost:.4f}")
```

## Features

- **Prompt Management**: Version control, centralized repository, environment-based deployments
- **Multi-Provider Inference**: OpenAI, Anthropic, Together AI support
- **Streaming Responses**: Real-time streaming for all providers
- **Cost Tracking**: Monitor usage and costs across providers
- **Auto-reload**: Automatically fetch latest prompt versions

## Usage

### Prompt Management

#### Get Prompts

```python
# Get a specific prompt
prompt = client.get_prompt("project-id", "customer-support")
print(f"Content: {prompt['content']}")
print(f"Version: {prompt['version']}")

# Use prompt with variables
custom_prompt = prompt['content'].format(
    customer_name="Sarah Johnson",
    issue="refund request"
)
```

#### List Prompts

```python
# List all prompts in a project
prompts = client.list_prompts("your-project-id")
for prompt in prompts["prompts"]:
    print(f"- {prompt['name']}: v{prompt['current_version']}")
```

#### Caching

```python
# Disable cache for real-time updates
prompt = client.get_prompt("project-id", "prompt-name", use_cache=False)

# Clear cache
client.clear_prompt_cache("project-id")
```

#### Auto-reload with PromptManager

```python
from promptlyzer import PromptManager

manager = PromptManager(
    client=client,
    project_id="your-project-id",
    update_interval=60  # Check every minute
)

manager.start()

# Always get latest version
prompt = manager.get_prompt("greeting")
```

### Inference

#### Configure Providers

```python
# Add your LLM provider API keys
client.configure_inference_provider("openai", "sk-...")
client.configure_inference_provider("anthropic", "sk-ant-...")
client.configure_inference_provider("together", "together-api-key...")
```

#### Run Inference

```python
# Direct text prompt
response = client.inference.infer(
    prompt="Explain quantum computing in simple terms",
    model="gpt-4o"
)

# Use a Promptlyzer prompt
response = client.inference.infer(
    prompt={"project_id": "your-project", "prompt_name": "assistant"},
    model="claude-3-5-sonnet-20241022"
)

# Get prompt and customize before inference
prompt = client.get_prompt("your-project", "email-template")
custom_prompt = prompt['content'].format(
    customer_name="Sarah Johnson",
    product="Premium Plan",
    discount="20%"
)
response = client.inference.infer(prompt=custom_prompt, model="gpt-4o")

print(response.content)
print(f"Cost: ${response.metrics.cost:.4f}")
print(f"Latency: {response.metrics.latency_ms}ms")
```

#### Streaming Responses

```python
# Stream the response in real-time
for chunk in client.inference.infer(
    prompt="Write a story about a robot",
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    stream=True
):
    if not chunk.is_final:
        print(chunk.content, end='', flush=True)
    else:
        # Final chunk contains metrics
        print(f"\n\nTotal cost: ${chunk.metrics.cost:.4f}")
        print(f"Tokens: {chunk.metrics.total_tokens}")

# Async streaming
async for chunk in await client.inference.infer_async(
    prompt="Explain AI",
    model="claude-3-5-sonnet-20241022",
    stream=True
):
    print(chunk.content, end='')
```

#### Compare Models

```python
# Compare different models
models = ["gpt-4o", "claude-3-5-sonnet-20241022", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"]

for model in models:
    response = client.inference.infer(
        prompt="What is 2+2? Answer in one word.",
        model=model
    )
    print(f"{model}: {response.content} (${response.metrics.cost:.4f})")
```

#### A/B Testing

```python
# Test different prompt versions
prompt_a = "Summarize this text in 3 sentences"
prompt_b = "Provide a 3-sentence summary of the following text"

text = "Your long text here..."

# Test both versions
for version, prompt in [("A", prompt_a), ("B", prompt_b)]:
    response = client.inference.infer(
        prompt=f"{prompt}: {text}",
        model="gpt-4o"
    )
    print(f"Version {version}:")
    print(f"  Response: {response.content[:100]}...")
    print(f"  Cost: ${response.metrics.cost:.4f}")
    print(f"  Latency: {response.metrics.latency_ms}ms")
    print()

# Or use Promptlyzer's prompt versions
for version in ["v1", "v2"]:
    response = client.inference.infer(
        prompt={"project_id": "your-project", "prompt_name": f"summary-{version}"},
        model="gpt-4o"
    )
    # Compare metrics...
```

#### View Metrics

```python
# Get metrics from API (last 7 days)
metrics = client.get_inference_metrics(days=7)

# Simple summary
for provider, data in metrics.items():
    print(f"{provider}:")
    print(f"  Total requests: {data.get('total_requests', 0)}")
    print(f"  Total cost: ${data.get('total_cost', 0):.2f}")
    print(f"  Success rate: {data.get('uptime_percentage', 0):.1f}%")

# For detailed analytics and visualizations, visit the Promptlyzer dashboard
```

## Environment Variables

- `PROMPTLYZER_API_KEY` - Your API key (recommended)
- `PROMPTLYZER_API_URL` - API endpoint (default: https://api.promptlyzer.com)
- `OPENAI_API_KEY` - For inference features
- `ANTHROPIC_API_KEY` - For inference features
- `TOGETHER_API_KEY` - For inference features

## Support

- Email: contact@promptlyzer.com

## License

MIT