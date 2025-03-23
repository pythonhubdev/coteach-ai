# Co-Teach AI

A multi-agent AI system that transforms simple course ideas into fully structured educational experiences through
automated research and intelligent content organization.

## Running in Local

1. Sync dependencies with UV
```shell
uv sync --group dev openai
```
2. Run the API
```shell
uv run python -m src
```

## Folder Structure
```
src
└── coteach_ai
    ├── agent
    │   └── config
    ├── api
    │   └── course
    ├── core
    │   ├── config
    │   ├── constants
    │   ├── schema
    │   │   ├── dto
    │   │   └── response
    │   └── utils
    ├── errors
    ├── middlewares
    ├── services
    └── static
        └── docs
```
