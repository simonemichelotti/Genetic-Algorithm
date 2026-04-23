# Genetic Algorithm for Regular Expression Synthesis

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey?logo=flask)
![Lark](https://img.shields.io/badge/Parser-LALR(1)-orange)

A research project developed as part of a Bachelor's thesis in Computer Science.
It implements a **genetic algorithm (GA) that automatically synthesises regular
expressions** from sets of positive and negative example strings.

The system evolves a population of candidate regex patterns over successive
generations, using **AST-level crossover and mutation** operators, a composite
fitness function, and optional **LLM-assisted warm-start initialisation** via a
local Ollama model.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **AST-based operators** | Crossover and mutation work directly on the parse tree, preserving syntactic validity |
| **Composite fitness** | Accuracy on traces + structural penalties (wildcards, nested quantifiers) + literal bonuses |
| **Hybrid initialisation** | Optionally seeds part of the population with LLM-generated candidates (`phi3:mini` via Ollama) |
| **Interactive webapp** | Flask UI to configure runs, upload datasets, monitor per-generation progress, and inspect the best regex AST and DFA |
| **Benchmarking suite** | Automated multi-run experiments comparing Classic GA, Hybrid GA, and a standalone LLM baseline |
| **LALR(1) parser** | Custom Lark grammar for regex → AST and AST → regex round-tripping |

---

## 🏗️ Architecture

```
AG_Tesi/
├── evolutionary_engine/        # Core GA loop
│   └── engine.py               # Initialisation, fitness, selection, crossover, mutation
├── syntactic_representation/   # Regex ↔ AST translation layer
│   ├── ast_generator.py        # LALR(1) parser (Lark): regex string → AST
│   └── ast_to_regex.py         # Inverse compiler: AST → regex string
├── data_simulation/            # Dataset generation
│   ├── trace_generator.py      # Generates positive/negative traces from a ground-truth regex
│   ├── regex_generator.py      # Generates random syntactically valid regex
│   └── llm_prompt.py           # Builds LLM prompts for hybrid initialisation
├── benchmarking/               # Experiment scripts
│   ├── experiments.py          # Multi-run GA vs LLM comparison
│   └── plot_comparison.py      # Result visualisation (Plotly)
├── webapp/                     # Flask web application
│   ├── app.py                  # REST API + background run management
│   ├── templates/              # Jinja2 HTML templates
│   └── static/                 # CSS / JS assets
└── docs/                       # Extended documentation
    ├── architecture.md
    └── pipeline.md
```

For a detailed walkthrough of each module see [`docs/architecture.md`](docs/architecture.md)
and [`docs/pipeline.md`](docs/pipeline.md).

---

## ⚙️ Installation

**Requirements:** Python 3.10+

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/AG_Tesi.git
cd AG_Tesi

# 2. Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

> **Optional – LLM hybrid mode:** install [Ollama](https://ollama.com/) and pull
> the model used during experiments:
> ```bash
> ollama pull phi3:mini
> ```

---

## 🚀 Usage

### 1. Web Application (recommended)

```bash
python webapp/app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

The UI allows you to:
- **Generate a dataset automatically** (random ground-truth regex + trace synthesis)
- **Upload your own dataset** (positive traces in one folder, negative in another)
- Configure GA parameters (population size, generations, mutation probability, elite %)
- **Monitor real-time progress** per generation with a live fitness chart
- Inspect the best regex's **AST tree** and its **minimised DFA**

### 2. Command-Line Interface

```bash
# Classic GA (random initialisation)
python -m evolutionary_engine.engine

# Hybrid GA (LLM warm-start, requires Ollama)
python -m evolutionary_engine.engine --ibrido
```

Positive and negative traces are read from `tracce_buone/` and `tracce_cattive/`
folders in the working directory (one trace per `.txt` file).

### 3. Benchmarking Suite

```bash
# Run 10 experiments, 500-individual population, 200 generations
python -m benchmarking.experiments \
    --n 10 \
    --pop 500 \
    --gens 200 \
    --per_category 200 \
    --out results.csv
```

Results are saved to CSV and can be visualised with `benchmarking/plot_comparison.py`.

---

## 🧬 How the Genetic Algorithm Works

```
Initialise population (random regex or LLM-seeded)
│
└─► For each generation:
       │
       ├─ Evaluate fitness:
       │     accuracy on good/bad traces
       │   + structural penalty (wildcards, nested quantifiers, …)
       │   + literal bonus
       │
       ├─ Select elite (top k%)
       │
       ├─ Crossover: swap homologous AST sub-trees between two parents
       │
       ├─ Mutate offspring:
       │     char substitution │ escape-class change │ quantifier toggle
       │     domain-bias injection (literal 'ab' alternation)
       │
       └─ Replace population; repeat until convergence or max generations
```

Mutation probability decays **linearly** over generations to balance exploration
and exploitation.

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `lark-parser` | LALR(1) regex grammar / AST construction |
| `regex` | Extended regex engine (Unicode properties support) |
| `flask` | Web application backend |
| `flask-cors` | Cross-Origin Resource Sharing for the REST API |
| `pyformlang` | DFA construction and minimisation for the webapp visualiser |
| `plotly` | Interactive charts for benchmarking results |

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.
