from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import threading
import uuid
import os
import json
import time
from pathlib import Path
import sys
import re
import random  # <-- added to fix NameError in /generate_dataset
try:
    from pyformlang.regular_expression import Regex as PyRegex
except Exception:
    PyRegex = None

# Ensure project root is on sys.path before importing main algorithm
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
# Import the main algorithm
from evolutionary_engine.engine import evoluzione
RUNS_DIR = BASE_DIR / 'webapp_runs'
RUNS_DIR.mkdir(exist_ok=True)
DATASETS_DIR = RUNS_DIR / 'datasets'
DATASETS_DIR.mkdir(exist_ok=True)

# Add this import after sys.path modification so the module can be found
from syntactic_representation.ast_generator import RegexParser

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# In-memory runs state: run_id -> dict
runs_state = {}

# Helper to write JSON history

def _write_run_history(run_dir, history):
    # Write atomically to avoid JSON partial reads during concurrent polling
    tmp_path = run_dir / 'history.json.tmp'
    final_path = run_dir / 'history.json'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    try:
        # atomic replace
        os.replace(str(tmp_path), str(final_path))
    except Exception:
        # fallback: attempt non-atomic rename
        try:
            os.remove(str(final_path))
        except Exception:
            pass
        os.rename(str(tmp_path), str(final_path))


def ast_to_json(node):
    """Convert Lark Tree/Token into serializable dict at module scope"""
    from lark import Tree, Token
    if node is None:
        return None
    if isinstance(node, Token):
        return {'type': 'token', 'token_type': node.type, 'value': str(node)}
    if isinstance(node, Tree):
        return {'type': 'tree', 'data': node.data, 'children': [ast_to_json(c) for c in node.children]}
    return {'type': 'other', 'value': str(node)}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def start_run():
    body = request.get_json()
    # Parse/pop validation for population size: clamp to [1, 1000]
    # Ensure a sane integer and clamp to max 1000 to avoid system overload
    try:
        dim_pop_raw = int(body.get('dimensione_popolazione', 50))
    except Exception:
        dim_pop_raw = 50
    dim_pop = max(1, min(1000, dim_pop_raw))
    params = {
        'dimensione_popolazione': dim_pop,
        'generazioni': int(body.get('generazioni', 50)),
        'probabilita_mutazione': float(body.get('probabilita_mutazione', 0.3)),
        'percentuale_elite': float(body.get('percentuale_elite', 0.1)),
        'top_n_display': int(body.get('top_n_display', 10)),
        'permissive_crossover': bool(body.get('permissive_crossover', False)),
        'cartella_buone': body.get('goodDir', 'tracce_buone'),
        'cartella_cattive': body.get('badDir', 'tracce_cattive'),
        'dataset_id': body.get('dataset_id')
    }

    run_id = str(uuid.uuid4())
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(exist_ok=True)

    runs_state[run_id] = {
        'status': 'queued',
        'params': params,
        'start_time': None,
        'end_time': None,
        'history_file': str(run_dir / 'history.json'),
        'history': []  # keep the in-memory history to avoid partial file reads
    }

    # Background thread
    def _task():
        runs_state[run_id]['status'] = 'running'
        runs_state[run_id]['start_time'] = time.time()
        history = []

        def ast_to_json(node):
            """Convert Lark Tree/Token into serializable dict"""
            from lark import Tree, Token
            if node is None:
                return None
            if isinstance(node, Token):
                return {'type': 'token', 'token_type': node.type, 'value': str(node)}
            if isinstance(node, Tree):
                return {'type': 'tree', 'data': node.data, 'children': [ast_to_json(c) for c in node.children]}
            return {'type': 'other', 'value': str(node)}








        def on_generation(gen, popolazione):
            # write minimal info: generation index and top10
            top10 = [{'regex': ind['regex'], 'voto': float(ind['voto'])} for ind in (popolazione[:10] if popolazione else [])]
            best_ast = None
            if popolazione and len(popolazione) > 0 and isinstance(popolazione[0].get('ast'), object):
                try:
                    best_ast = ast_to_json(popolazione[0]['ast'])
                except Exception:
                    best_ast = None
            history.append({'generation': gen, 'top10': top10, 'best_ast': best_ast})
            _write_run_history(run_dir, history)
            # save a copy in-memory to avoid partial-disk read races on /status
            try:
                runs_state[run_id]['history'] = list(history)
            except Exception:
                pass
            # Check for stop request: if requested, raise to abort the evoluzione call
            if runs_state.get(run_id, {}).get('stop_requested'):
                raise KeyboardInterrupt('Stop requested')

        # Call the algorithm (evoluzione) with a callback
        try:
            # We expect evoluzione to accept on_generation param; else run simple
            try:
                best = evoluzione(
                    dimensione_popolazione=params['dimensione_popolazione'],
                    generazioni=params['generazioni'],
                    probabilita_mutazione=params['probabilita_mutazione'],
                    percentuale_elite=params['percentuale_elite'],
                    top_n_display=params['top_n_display'],
                    permissive_crossover=params['permissive_crossover'],
                    on_generation=on_generation,
                    cartella_buone=(str(DATASETS_DIR / params['dataset_id'] / 'tracce_buone') if params.get('dataset_id') else params.get('cartella_buone')),
                    cartella_cattive=(str(DATASETS_DIR / params['dataset_id'] / 'tracce_cattive') if params.get('dataset_id') else params.get('cartella_cattive'))
                )
            except TypeError:
                # Fallback: no callback support in evoluzione
                best = evoluzione(
                    dimensione_popolazione=params['dimensione_popolazione'],
                    generazioni=params['generazioni'],
                    probabilita_mutazione=params['probabilita_mutazione'],
                    percentuale_elite=params['percentuale_elite'],
                    top_n_display=params['top_n_display'],
                    permissive_crossover=params['permissive_crossover'],
                    cartella_buone=(str(DATASETS_DIR / params['dataset_id'] / 'tracce_buone') if params.get('dataset_id') else params.get('cartella_buone')),
                    cartella_cattive=(str(DATASETS_DIR / params['dataset_id'] / 'tracce_cattive') if params.get('dataset_id') else params.get('cartella_cattive'))
                )
                # We have no per-generation data, so only final is appended
                history.append({'generation': 'final', 'top10': [{'regex': best['regex'], 'voto': float(best['voto'])}]})
                _write_run_history(run_dir, history)

            runs_state[run_id]['status'] = 'finished'
            runs_state[run_id]['end_time'] = time.time()
            # Finalize history
            _write_run_history(run_dir, history)
            runs_state[run_id]['history'] = history
            runs_state[run_id]['best'] = best

        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                runs_state[run_id]['status'] = 'stopped'
            else:
                runs_state[run_id]['status'] = 'error'
                runs_state[run_id]['error'] = str(e)

    t = threading.Thread(target=_task, daemon=True)
    t.start()

    return jsonify({'run_id': run_id})


@app.route('/stop/<run_id>', methods=['POST'])
def stop_run(run_id):
    if run_id not in runs_state:
        return jsonify({'error': 'not found'}), 404
    runs_state[run_id]['stop_requested'] = True
    return jsonify({'status': 'stopping'})


@app.route('/status/<run_id>', methods=['GET'])
def status_run(run_id):
    state = runs_state.get(run_id)
    if not state:
        return jsonify({'error': 'run_id not found'}), 404
    # Prefer in-memory history (updated every generation) to avoid partial file reads
    history = state.get('history', []) or []
    if not history:
        # Fall back to reading the file only if in-memory history is empty
        history_file = Path(state['history_file'])
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    if isinstance(loaded, list):
                        history = loaded
            except Exception:
                # Keep in-memory history as fallback (could be empty).
                history = state.get('history', []) or []

    return jsonify({
        'status': state.get('status'),
        'start_time': state.get('start_time'),
        'end_time': state.get('end_time'),
        'history': history
    })


@app.route('/results/<run_id>', methods=['GET'])
def result_run(run_id):
    state = runs_state.get(run_id)
    if not state:
        return jsonify({'error': 'run_id not found'}), 404
    history_file = Path(state['history_file'])
    if not history_file.exists():
        return jsonify({'error': 'no history file yet', 'status': state.get('status')}), 404
    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
    # Ensure best is JSON-serializable: remove Tree instances
    best = state.get('best')
    if isinstance(best, dict):
        best_serializable = {k: best[k] for k in ('regex', 'voto') if k in best}
        if best.get('ast') is not None:
            best_serializable['ast'] = ast_to_json(best.get('ast'))
        else:
            best_serializable['ast'] = None
    else:
        best_serializable = None

    return jsonify({'status': state.get('status'), 'history': history, 'best': best_serializable})


@app.route('/upload_dataset', methods=['POST'])
def upload_dataset():
    # Accept multiple files for good and bad traces
    files_good = request.files.getlist('good_files')
    files_bad = request.files.getlist('bad_files')
    if not files_good and not files_bad:
        return jsonify({'error': 'no files uploaded'}), 400
    dataset_id = str(uuid.uuid4())
    dataset_dir = DATASETS_DIR / dataset_id
    (dataset_dir / 'tracce_buone').mkdir(parents=True, exist_ok=True)
    (dataset_dir / 'tracce_cattive').mkdir(parents=True, exist_ok=True)
    # write good files
    for i, f in enumerate(files_good):
        fname = f.filename or f'good_{i:03d}.txt'
        with open(dataset_dir / 'tracce_buone' / fname, 'wb') as out:
            out.write(f.read())
    for i, f in enumerate(files_bad):
        fname = f.filename or f'bad_{i:03d}.txt'
        with open(dataset_dir / 'tracce_cattive' / fname, 'wb') as out:
            out.write(f.read())
    return jsonify({'dataset_id': dataset_id})


@app.route('/download/<run_id>', methods=['GET'])
def download_history(run_id):
    state = runs_state.get(run_id)
    if not state:
        return jsonify({'error': 'run_id not found'}), 404
    history_file = Path(state['history_file'])
    if not history_file.exists():
        return jsonify({'error': 'no history file yet', 'status': state.get('status')}), 404
    return send_file(history_file, as_attachment=True, download_name=f'history_{run_id}.json')


@app.route('/generate_dataset', methods=['POST'])
def generate_dataset():
    """Generate a random regex and populate tracce_buone/tracce_cattive"""
    try:
        # Import necessary functions from trace_generator before using them
        from data_simulation.trace_generator import (
            generate_simple_pattern,
            classify_and_save_traces,
        )
        import regex

        # Generate a simple pattern (after import to avoid NameError)
        pattern = generate_simple_pattern()
        
        # Create a new dataset directory
        dataset_id = str(uuid.uuid4())
        dataset_dir = DATASETS_DIR / dataset_id
        (dataset_dir / 'tracce_buone').mkdir(parents=True, exist_ok=True)
        (dataset_dir / 'tracce_cattive').mkdir(parents=True, exist_ok=True)
        (dataset_dir / 'debug').mkdir(parents=True, exist_ok=True)
        
        # Validate pattern first
        try:
            regex.compile(pattern)
        except Exception as e:
            return jsonify({'error': f'Invalid pattern: {str(e)}'}), 400
        
        # Delegate to trace_generator to create dataset and debug info
        result = classify_and_save_traces(pattern, selected_per_category=1000, dataset_dir=str(dataset_dir), max_attempts=50000)
        
        # If generation didn't reach required counts, keep the info and return partial dataset with debug
        return jsonify({
            'dataset_id': dataset_id,
            'pattern': result.get('pattern'),
            'good_count': result.get('good_count'),
            'bad_count': result.get('bad_count'),
            'traces_generated': result.get('traces_generated'),
            'goods_that_not_match': result.get('goods_that_not_match'),
            'bads_that_match': result.get('bads_that_match'),
            'dataset_dir': result.get('dataset_dir')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
