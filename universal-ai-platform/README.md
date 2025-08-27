# Universal AI Agent Platform

A SaaS platform that enables businesses to integrate multimodal AI agents into their applications without building AI infrastructure themselves.

## Architecture Overview

- **Platform Service**: Core agent service built on LiveKit foundation
- **API Gateway**: REST API for client integration
- **Business Logic Adapter**: Framework for customizing agent behavior
- **Usage Tracking**: Monitor and bill API usage
- **Demo Applications**: Language learning and emergency services examples

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment: Copy `.env.example` to `.env` and fill in API keys
3. Start platform service: `python platform/main.py`
4. Run demo applications: `python demos/language_learning/app.py`

## Documentation

- [API Reference](docs/api.md)
- [Business Logic Adapters](docs/adapters.md)
- [Client SDKs](docs/sdks.md)