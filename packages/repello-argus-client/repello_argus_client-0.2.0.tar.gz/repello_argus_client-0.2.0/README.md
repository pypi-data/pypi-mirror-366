# Repello Argus Python SDK

[![PyPI Version](https://img.shields.io/pypi/v/repello-argus-client.svg)](https://pypi.org/project/repello-argus-client/)
[![Python Versions](https://img.shields.io/pypi/pyversions/repello-argus-client.svg)](https://pypi.org/project/repello-argus-client/)
[![License](https://img.shields.io/pypi/l/repello-argus-client.svg)](https://github.com/Repello-AI/argus-sdk-client/blob/main/LICENSE)
[![Build Status](https://github.com/Repello-AI/argus-sdk-client/actions/workflows/ci.yml/badge.svg)](https://github.com/Repello-AI/argus-sdk-client/actions)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](https://github.com/Repello-AI/argus-sdk-client/blob/main/CODE_OF_CONDUCT.md)


The official Python SDK for the Repello Argus AI Guardrails API.

The Argus Python SDK provides a robust, high-performance interface for integrating Repello Argus into your Python applications. It allows developers to scan LLM prompts and responses in real-time to detect and mitigate a wide range of security, safety, and content risks.

This SDK is designed for both rapid prototyping with code-defined policies and enterprise-grade orchestration using the Argus Platform, enabling features like centralized policy management, detailed analytics, and conversation tracking.

---

## Key Features

-   **Comprehensive Security Policies:** Scan for PII, prompt injection, toxicity, secrets, banned topics, unsafe content, and more.
-   **Flexible Policy Management:** Define policies directly in your code for rapid development, or leverage the Argus Platform to manage policies centrally in the UI without code changes.
-   **Full Platform Observability:** Use Assets and Sessions to organize and track your data, providing deep insights into application usage and conversation context in the Argus dashboard.
-   **Developer-First Experience:** Built with type-safe enums (`Verdict`, `Action`, etc.) and a clear exception hierarchy for robust and predictable integration.
-   **Resilient & Performant:** Powered by `httpx` for modern, asynchronous-ready HTTP requests and `tenacity` for automatic, resilient retries on network failures.

## Installation

Install the package from PyPI using `pip`:

```bash
pip install repello-argus-client
```

The SDK requires Python 3.8 or higher.

## Quickstart

This example shows how to get started in under a minute. It defines a simple policy in code to block toxic prompts.

First, set your API key as an environment variable:
```bash
export ARGUS_API_KEY="your_api_key_here"
```

Then, run the following Python code:
```python
# quickstart.py
import os
from repello_argus_client import ArgusClient, PolicyName, Action, Verdict

# 1. Load your API Key from the environment
API_KEY = os.environ.get("ARGUS_API_KEY")
if not API_KEY:
    raise ValueError("ARGUS_API_KEY environment variable not set.")

# 2. Define a simple policy in your code
my_policy = {
    PolicyName.TOXICITY: {"action": Action.BLOCK}
}

# 3. Create a client and perform a scan
argus_guard = None
try:
    argus_guard = ArgusClient.create(api_key=API_KEY, policy=my_policy)
    result = argus_guard.check_prompt("You are a piece of garbage.")

    # 4. Handle the result using the Verdict enum
    print(f"Verdict: {result['verdict']}")

    if result['verdict'] == Verdict.BLOCKED:
        print("✅ The prompt was blocked. Application should halt this request.")
    else:
        print("The prompt was allowed to proceed.")

finally:
    if argus_guard:
        argus_guard.close()
```

## Documentation

> For a comprehensive guide covering all features, advanced usage patterns, and a full API reference, please see our official documentation:
>
> **[https://docs.repello.ai/](https://docs.repello.ai/)**

## Usage Example: Platform Workflow

Platform users (with a Runtime Security Key) can leverage policies managed directly in the Argus UI. This simplifies the code significantly.

```python
# platform_usage.py
import os
from repello_argus_client import ArgusClient, Verdict

# This workflow assumes you have:
# 1. A Runtime Security Key (rsk_...).
# 2. An Asset created in the Argus UI with its own policy.
API_KEY = os.environ.get("ARGUS_RUNTIME_API_KEY")
ASSET_ID = "your_asset_id_from_the_dashboard"

argus_guard = None
try:
    # Connect to your asset and enable saving results to the platform.
    # Notice no local `policy` object is needed.
    argus_guard = ArgusClient.create(
        api_key=API_KEY,
        asset_id=ASSET_ID,
        save=True
    )

    # This scan will be evaluated against the policy configured in the Argus UI.
    result = argus_guard.check_prompt("This prompt will be checked against the UI policy.")

    print(f"Verdict from platform policy: {result['verdict']}")

finally:
    if argus_guard:
        argus_guard.close()
```

## 📂 More Examples

See the [`examples/`](https://github.com/Repello-AI/argus-sdk-client/tree/main/examples) directory for more use cases, including:

- Asynchronous usage
- Streaming integrations
- Platform workflows with assets and sessions

## 📄 License

This project is licensed under the [Apache License 2.0](https://github.com/Repello-AI/argus-sdk-client/blob/main/LICENSE).

## 🔗 Useful Links

- 📘 **Documentation**: [docs.repello.ai/argus/sdk/python](https://docs.repello.ai/argus/sdk/python)
- 🧪 **Examples**: [examples/ directory](https://github.com/Repello-AI/argus-sdk-client/tree/main/examples)
- 📥 **Contributing Guide**: [CONTRIBUTING.md](https://github.com/Repello-AI/argus-sdk-client/blob/main/CONTRIBUTING.md)
- 🤝 **Code of Conduct**: [CODE_OF_CONDUCT.md](https://github.com/Repello-AI/argus-sdk-client/blob/main/CODE_OF_CONDUCT.md)
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/Repello-AI/argus-sdk-client/issues)


## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](https://github.com/Repello-AI/argus-sdk-client/blob/main/CONTRIBUTING.md) for guidelines on how to submit pull requests, report issues, and suggest features.

This project follows the [Contributor Covenant Code of Conduct](https://github.com/Repello-AI/argus-sdk-client/blob/main/CODE_OF_CONDUCT.md). By participating, you agree to abide by its terms.


## Support

If you encounter any issues or have questions, please file an issue on our [GitHub Issues page](https://github.com/Repello-AI/argus-sdk-client/issues) or contact our support team at `support@repello.ai`.

© 2025 [RepelloAI](https://repello.ai). All rights reserved.
