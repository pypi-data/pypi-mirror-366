# Micro-Graph

> If all the fancy langgraph etc. libraries are too heavyweight and complex for you, look no further.

A tiny library allowing you to build graphs for executing workflows.
It is focused purely on minimalism, simplicity and ease of understanding.
It does not need any dependencies.

## 🛠️ Installation

```bash
pip install micro-graph

# to also install `micro_graph.ai` dependencies
pip install micro-graph[ai]
```

## 👨‍💻 Usage

See the [examples](examples) or [tests](tests) for example uses.

## 👥 Contributing

Feel free to make this code better by forking, improving the code and then pull requesting.

However, the goal of this repo is to be the minimal functionallity required and implementing it without any external dependencies.
Please keep this in mind if you modify this repo.

Keep it simple!

### Setup

Install dev dependencies and pre-commit hooks

```bash
pip install -e .[dev,ai]
pre-commit install
```

This will automatically run `ruff check .` and `pytest` before each commit.

## ⚖️ License

Micro-Graph is licensed under the permissive MIT license -- see [LICENSE](LICENSE) for details.
