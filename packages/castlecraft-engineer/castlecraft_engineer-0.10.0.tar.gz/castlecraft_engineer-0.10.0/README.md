# Castlecraft Engineer

[![GitLab CI Pipeline](https://gitlab.com/castlecraft/framework/engineer/badges/main/pipeline.svg)](https://gitlab.com/castlecraft/framework/engineer/-/commits/main)
[![Coverage Report](https://gitlab.com/castlecraft/framework/engineer/badges/main/coverage.svg)](https://gitlab.com/castlecraft/framework/engineer/-/pipelines)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://img.shields.io/badge/docs-latest-blue.svg)](https://engineer.castlecraft.in/)
[![PyPI version](https://img.shields.io/pypi/v/castlecraft-engineer.svg)](https://pypi.org/project/castlecraft-engineer/)
[![Python versions](https://img.shields.io/pypi/pyversions/castlecraft-engineer.svg)](https://pypi.org/project/castlecraft-engineer/)

**Castlecraft Engineer** is a Python framework designed to help developers build robust, scalable, and maintainable applications by leveraging established software design patterns like Domain-Driven Design (DDD), Command Query Responsibility Segregation (CQRS), and Event Sourcing.

It provides a collection of abstractions, base classes, and utilities to streamline the development of complex business logic while promoting clean architecture principles.

## Guiding Principles & Target Audience

Castlecraft Engineer is built upon established software design principles, primarily:

*   **Domain-Driven Design (DDD)**: Tools to model complex business domains effectively.
*   **Command Query Responsibility Segregation (CQRS)**: Encouraging separation of write and read operations.
*   **Event-Driven Architecture (EDA)**: Support for Domain Events for decoupled communication.

This library is ideal for Python developers building applications with these principles, aiming for highly testable, maintainable, and scalable systems.
It may be less suitable for very simple CRUD applications or for teams seeking a fully opinionated, all-in-one web framework.

For a more detailed breakdown, see ["Who Is This Library For?"](https://engineer.castlecraft.in/#who-is-this-library-for) in our main documentation.

## Accelerate Development with Castlecraft Architect

While Castlecraft Engineer provides the foundational building blocks for DDD, we recognize that starting a new project can still involve significant boilerplate. To address this, we developed **[Castlecraft Architect](https://architect.castlecraft.in)**—an intelligent scaffolding and development acceleration tool.

Architect leverages the principles of Engineer to:
*   **Generate DDD-aligned boilerplate**: Quickly scaffold your application with a well-structured foundation.
*   **Facilitate Domain Exploration**: Generate context for LLMs to assist in discussions with domain experts.
*   **Provide AI-Powered Guidance**: Suggest contextually relevant code additions while respecting architectural integrity.

Engineer is the open-source framework that provides the building blocks, and Architect is our open-source tool to help you get started faster and streamline development on top of it.

## Key Features

*   **Domain-Driven Design (DDD) Primitives**: Base classes for `Aggregate` and `AggregateRepository` to model your domain and manage persistence with optimistic concurrency.
*   **Command Query Responsibility Segregation (CQRS)**: Clear separation of write operations (Commands) and read operations (Queries) with dedicated buses (`CommandBus`, `QueryBus`) and handlers.
*   **Event System**: Support for domain events (`Event`), in-process `EventBus`, and abstractions for `ExternalEventPublisher` and `EventStreamConsumer` for integrating with message brokers.
*   **Event Store**: An `EventStore` abstraction for persisting event streams, crucial for implementing Event Sourcing. Includes an `InMemoryEventStore` for testing.
*   **Sagas**: Support for managing distributed transactions and long-running processes through sagas (newly documented).
*   **Dependency Injection**: Built-in DI container (`ContainerBuilder` based on `punq`) for managing dependencies and promoting loosely coupled components.
*   **SQLModel-based Persistence**: Easy integration with SQL databases using `SQLModel`, with generic repositories (`ModelRepository`, `AsyncModelRepository`) for data access.
*   **Authorization Framework**: A flexible authorization service (`AuthorizationService`, `Permission` objects, `@ctx` decorator) to secure your application's features.
*   **Caching Utilities**: Helpers for integrating with Redis (`RedisCacheClient`, `AsyncRedisCacheClient`) for both synchronous and asynchronous caching needs.
*   **OIDC Authentication**: Utilities for OpenID Connect (OIDC) token verification and JWKS caching (`AuthenticationService`).
*   **Cryptography**: Simple encryption/decryption utilities (`encrypt_data`, `decrypt_data`) using AES-GCM (via the `cryptography` library).
*   **Testing Utilities**: A suite of test helpers and base classes to facilitate unit and integration testing of components built with the framework.
*   **CLI Support**: Basic CLI structure for bootstrapping tasks (e.g., database schema creation).

## Installation

You can install `castlecraft-engineer` using `uv` (recommended) or `pip`:

```bash
uv pip install castlecraft-engineer
```
Or:
```bash
pip install castlecraft-engineer
```

## Quickstart

To give you a taste of how Engineer structures operations, here's a brief example of defining a business command and its handler (a core concept in CQRS):

```python
from dataclasses import dataclass
from castlecraft_engineer.abstractions.command import Command
from castlecraft_engineer.abstractions.command_handler import CommandHandler
from castlecraft_engineer.common.di import ContainerBuilder
from castlecraft_engineer.abstractions.command_bus import CommandBus
import asyncio

# 1. Define a Command
@dataclass(frozen=True)
class CreateItemCommand(Command[str]): # Returns a string (e.g., item ID)
    name: str

# 2. Define a Command Handler
class CreateItemHandler(CommandHandler[CreateItemCommand, str]):
    async def execute(self, command: CreateItemCommand) -> str:
        print(f"Creating item: {command.name}")
        # ... actual logic to create and persist item ...
        item_id = f"item_{command.name.lower().replace(' ', '_')}"
        print(f"Item created with ID: {item_id}")
        return item_id

async def main():
    # 3. Setup DI Container and Buses
    builder = ContainerBuilder()
    builder.with_command_bus()
    # Register with DI
    builder.register(CreateItemHandler)
    # Register with Command Bus
    builder.command_bus.register(CreateItemHandler)
    container = builder.build()

    # 4. Get the Command Bus and execute the command
    command_bus = container.resolve(CommandBus)
    item_id = await command_bus.execute(CreateItemCommand(name="My New Item"))
    print(f"Command executed, returned ID: {item_id}")

if __name__ == "__main__":
    asyncio.run(main())
```

For more detailed examples and usage, please refer to the Full Documentation.

## Documentation

Comprehensive documentation, including conceptual guides, tutorials, and API references, is available at:
https://engineer.castlecraft.in

The documentation is built using MkDocs with the Material theme and includes:
*   Installation Guide
*   Quickstart Guide
*   In-depth Conceptual Explanations
*   Step-by-step Tutorials
*   API Reference
*   Guides on Error Handling, Testing, and CLI usage.

To build the documentation locally:
```bash
uv pip install mkdocs mkdocs-material pymdown-extensions mike mkdocs-awesome-pages-plugin
mkdocs serve
```

## Contributing

Contributions are welcome! If you'd like to contribute, please:
1.  Fork the repository on GitLab.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and ensure tests pass.
4.  Add or update documentation as necessary.
5.  Submit a Merge Request with a clear description of your changes.

Please refer to the `CONTRIBUTING.md` file for more detailed guidelines.
We use `python-semantic-release` for versioning and releases, and `pre-commit` for code quality checks.

## Development Setup

To set up the project for development:
```bash
# 1. Clone the repository
git clone https://gitlab.com/castlecraft/framework/engineer.git
cd castlecraft-engineer

# 2. Create a virtual environment and install dependencies (using uv)
python -m venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 3. Install pre-commit hooks
pre-commit install
```

## Running Tests

To run the test suite:
```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with passion by the Castlecraft Engineering team.
