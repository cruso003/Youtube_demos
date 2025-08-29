# SDKs

NexusAI provides official SDKs for JavaScript and Python, making it easy to integrate AI agents into your applications.

## Available SDKs

### JavaScript/Node.js SDK

Perfect for web applications, Node.js backends, and React Native mobile apps.

- **Installation**: `npm install nexusai-sdk`
- **Size**: < 50KB minified
- **Features**: Full API coverage, TypeScript support
- **[npm Package →](https://www.npmjs.com/package/nexusai-sdk)**
- **[Documentation →](https://nexus.bits-innovate.com/docs/sdks/javascript)**

### Python SDK

Ideal for data science, machine learning workflows, and Python backends.

- **Installation**: `pip install nexusai-sdk`
- **Features**: Type hints, async support, dataclasses
- **[PyPI Package →](https://pypi.org/project/nexusai-sdk/)**
- **[Documentation →](https://nexus.bits-innovate.com/docs/sdks/python)**

## Quick Comparison

| Feature | JavaScript | Python |
|---------|------------|--------|
| Installation | `npm install nexusai-sdk` | `pip install nexusai-sdk` |
| Async Support | ✅ Promises/async-await | ✅ asyncio support |
| Type Safety | ✅ TypeScript definitions | ✅ Type hints |
| Bundle Size | < 50KB | N/A |
| Platforms | Browser, Node.js, React Native | Python 3.8+ |

## Common Usage Pattern

Both SDKs follow the same API pattern:

**JavaScript:**
```javascript
const { NexusAIClient } = require('nexusai-sdk');

const client = new NexusAIClient('https://nexus.bits-innovate.com');
const agent = await client.createAgent({
  instructions: "You are a helpful assistant",
  capabilities: ["text", "voice"]
});
```

**Python:**
```python
from nexusai_sdk import NexusAIClient, AgentConfig

client = NexusAIClient('https://nexus.bits-innovate.com')
config = AgentConfig(
    instructions="You are a helpful assistant",
    capabilities=["text", "voice"]
)
agent = client.create_agent(config)
```

## Next Steps

- [JavaScript SDK on npm](https://www.npmjs.com/package/nexusai-sdk)
- [Python SDK on PyPI](https://pypi.org/project/nexusai-sdk/)
- [API Reference](api)
- [Getting Started Guide](getting-started)
