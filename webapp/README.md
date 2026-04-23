# Webapp – Genetic Algorithm for Regex Synthesis

A Flask web application that provides an interactive interface to the regex
genetic algorithm. Runs are executed in background threads; the UI polls for
per-generation updates and renders live fitness charts, an AST tree, and a
minimised DFA for the best regex found.

## Running the App

```bash
# From the project root, with the virtual environment activated:
python webapp/app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## REST API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the main HTML interface |
| `POST` | `/start` | Starts a new GA run; returns `{ run_id }` |
| `POST` | `/stop/<run_id>` | Requests a graceful stop of a running job |
| `GET` | `/status/<run_id>` | Returns current status and per-generation history |
| `GET` | `/results/<run_id>` | Returns final results, full history, and best regex AST |
| `POST` | `/upload_dataset` | Uploads positive/negative trace files; returns `{ dataset_id }` |
| `POST` | `/generate_dataset` | Auto-generates a dataset from a random regex; returns dataset info |
| `GET` | `/download/<run_id>` | Downloads `history.json` for the run as an attachment |

### `POST /start` – Body Parameters

```json
{
  "dimensione_popolazione": 50,
  "generazioni": 100,
  "probabilita_mutazione": 0.3,
  "percentuale_elite": 0.1,
  "top_n_display": 10,
  "permissive_crossover": false,
  "dataset_id": "<uuid>",
  "goodDir": "tracce_buone",
  "badDir":  "tracce_cattive"
}
```

If `dataset_id` is provided the run uses the uploaded/generated dataset stored
under `webapp_runs/datasets/<dataset_id>/`. Otherwise `goodDir` / `badDir` paths
are used (relative to the project root).

## File Layout

```
webapp/
├── app.py          # Flask application – routes and background thread logic
├── templates/      # Jinja2 HTML templates
│   └── index.html
└── static/         # CSS and JavaScript assets
```

## Run Artifacts

Per-run data is persisted under `webapp_runs/<run_id>/`:

```
webapp_runs/
└── <run_id>/
    └── history.json   # Array of { generation, top10, best_ast } objects
```

Uploaded and auto-generated datasets are stored under `webapp_runs/datasets/<dataset_id>/`.
