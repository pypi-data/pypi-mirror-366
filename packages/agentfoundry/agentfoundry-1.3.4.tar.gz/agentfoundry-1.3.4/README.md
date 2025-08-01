# AIgent

**AIgent** is a modular, extensible AI framework designed to support the construction and orchestration of autonomous agents across a variety of complex tasks. The system is built in Python and leverages modern AI tooling to integrate large language models (LLMs), vector stores, rule-based decision logic, and dynamic tool discovery in secure and performance-conscious environments.

## Features

- Modular agent architecture with support for specialization (e.g., memory agents, reactive agents, compliance agents)
- Cython-compiled backend for performance and IP protection
- Integration with popular frameworks such as LangChain, ChromaDB, and OpenAI
- Support for licensed or embedded deployments via license file verification or compiled-only distribution
- Configurable with runtime enforcement of execution licenses (RSA-signed, machine-bound)

## Use Cases

AIgent is designed to serve as a core intelligence engine for:

- Secure enterprise AI platforms (e.g., QuantumDrive)
- Compliance monitoring and rule-based alerting systems
- Conversational interfaces with dynamic tool execution
- Embedded agents in SaaS and on-premise environments

## Requirements

- Python 3.11+
- Cython
- Compatible dependencies (see `requirements.txt`)

## Author

**Christopher Steel**  
AI Practice Lead, AlphaSix Corporation  
Founder, Syntheticore, Inc.  
Email: `csteel@syntheticore.com`

## Licensing and Legal Notice

© Syntheticore, Inc. All rights reserved.

> **This software is proprietary and confidential.**  
> Any use, reproduction, modification, distribution, or commercial deployment of AIgent or any part thereof requires **explicit written authorization** from Syntheticore, Inc.

Unauthorized use is strictly prohibited and may result in legal action.

---

For licensing inquiries or permission to use this software, please contact:  
📧 **csteel@syntheticore.com**

## Gradio Chat Interface

A simple Gradio-based chat interface for interacting with the HybridOrchestrator agent.

### Prerequisites

- Ensure you have set your OpenAI API key:

```bash
export OPENAI_API_KEY=<your_api_key>
```

### Running the App

```bash
python gradio_app.py
```

The interface will be available at http://localhost:7860 by default.

## API Server

Genie can be accessed programmatically via a FastAPI‑based HTTP API. Two main endpoints are provided:

- **POST /v1/chat**: Send or continue a multi‑turn conversation with Genie. Accepts JSON payload with conversation history and returns the assistant reply and updated history.
- **POST /v1/orchestrate**: Discover APIs and execute a main task across all agents. Returns aggregated results.
- **GET /health**: Health check endpoint.

### Prerequisites

- Ensure you have set your OpenAI API key:

```bash
export OPENAI_API_KEY=<your_api_key>
```
- Install FastAPI and Uvicorn (if not already):

```bash
pip install fastapi uvicorn[standard]
```

### Running the API

```bash
python api_server.py
# Or with auto‑reload during development:
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

Interactive API docs will be available at http://localhost:8000/docs

## Logging & Debugging

AgentFoundry automatically logs events to a file and rotates it on each startup.

By default, logs are written to `agentfoundry.log` at INFO level. You can customize
logging behavior via environment variables:

```bash
export AGENTFOUNDRY_LOG_FILE=agentfoundry.log
export AGENTFOUNDRY_LOG_LEVEL=DEBUG  # or INFO, WARNING, ERROR
```

Upon each restart of the application or API server, if `agentfoundry.log` already exists,
it is renamed to `agentfoundry.log.YYYYMMDDHHMMSS` for archival, and a fresh log file
is started. View live logs in `agentfoundry.log` and inspect past runs in the timestamped
backup files.

