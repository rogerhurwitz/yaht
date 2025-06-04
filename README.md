# Yaht

A Python-based framework for playing [Yahtzee](https://en.wikipedia.org/wiki/Yahtzee). This is a work-in-progress project focused on building a modular, extensible engine for the full Yahtzee gameplay experience.

Currently, the emphasis is on implementing and validating the **scorecard** mechanics.

---

## 🚧 Project Status

🔧 **In Development**  
✅ Scorecard logic is implemented and partially tested  
⏳ Game flow, player interactions, and UI are pending

---

## 🧩 Features

- 🧠 Core scorecard logic with category evaluation
- 📦 Modular architecture (`src/yaht/`)
- 🧪 Unit tests in place for scorecard module

---

## 📁 Project Structure

```
yaht/
├── src/
│   └── yaht/
│       ├── __init__.py
│       ├── exceptions.py      # Custom game exceptions
│       ├── main.py            # Entry point (stub for now)
│       └── scorecard.py       # Scoring logic
├── tests/
│   └── test_scorecard.py      # Scorecard unit tests
├── rules.md                   # Game rule notes and references
├── pyproject.toml             # Project metadata and dependencies
└── README.md                  # This file
```

---

## 🔧 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/rogerhurwitz/yaht.git
   cd yaht
   ```

2. Create and initialize a virtual environment with [uv](https://github.com/astral-sh/uv):

   ```bash
   uv venv
   uv pip install
   ```

---

## 🚀 Running Tests

Use `pytest` (preferred test runner):

```bash
uv run pytest
```

If using `unittest` directly, you must specify the source path:

```bash
PYTHONPATH=src uv run python -m unittest discover tests
```

---

## 📜 Planned Features

- Full game loop with turn logic
- Multiple player support
- Yahtzee bonus and Joker rules
- CLI and/or GUI front-end
- Persistent high scores

---

## 🤝 Contributing

This project is currently in solo development by [Roger Hurwitz](https://github.com/rogerhurwitz). Contributions and suggestions are welcome as the project grows.

---

## 📄 License

[MIT License](LICENSE) (to be added)
