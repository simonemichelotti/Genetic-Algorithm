import argparse
import time
import csv
from pathlib import Path
import os
import uuid
import json
from datetime import datetime
import subprocess
import regex

from data_simulation.trace_generator import classify_and_save_traces, generate_simple_pattern
from evolutionary_engine import engine as ga_main


def load_traces(dir_path):
    traces = []
    for f in Path(dir_path).glob('*.txt'):
        with open(f, 'r', encoding='utf-8') as file:
            traces.append(file.read().strip())
    return traces


def compute_fitness(compiled_regex, good_dir, bad_dir):
    good_files = list(Path(good_dir).glob('*.txt'))
    bad_files = list(Path(bad_dir).glob('*.txt'))
    matches_good = 0
    for f in good_files:
        with open(f, 'r', encoding='utf-8') as file:
            if compiled_regex.fullmatch(file.read().strip()):
                matches_good += 1
    matches_bad = 0
    for f in bad_files:
        with open(f, 'r', encoding='utf-8') as file:
            if not compiled_regex.fullmatch(file.read().strip()):
                matches_bad += 1
    total = len(good_files) + len(bad_files)
    fitness = (matches_good + matches_bad) / total if total > 0 else 0
    return fitness


def query_llm(prompt):
    try:
        result = subprocess.run(['ollama', 'run', 'phi3:mini'], input=prompt, text=True, capture_output=True, encoding='utf-8')
        return result.stdout.strip()
    except Exception:
        return ""


def extract_regex_from_llm_response(response):
    """Estrae la regex dalla risposta dell'LLM, ignorando spiegazioni aggiuntive."""
    lines = response.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.lower().startswith(('explanation', 'explangyer', 'note', 'the regex', 'this regex', 'explangy')):
            # Controlla se contiene caratteri tipici delle regex
            if any(c in line for c in ['^', '$', '[', ']', '+', '*', '?', '|', '\\', '(', ')']):
                return line
    return response.strip()


def run_one(run_index, selected_per_category=200, ga_params=None):
    # 1. genera regex semplice (compatibile con trace_generator, come fa la webapp)
    pattern = generate_simple_pattern()

    # 2. crea cartelle dataset per questo lancio
    datasets_base = Path.cwd() / 'webapp_runs' / 'datasets'
    datasets_base.mkdir(parents=True, exist_ok=True)
    dataset_id = f"exp_{run_index:04d}_{uuid.uuid4().hex[:8]}"
    dataset_dir = datasets_base / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)
    try:
        info = classify_and_save_traces(pattern, selected_per_category=selected_per_category, dataset_dir=str(dataset_dir), max_attempts=50000)
    except Exception as e:
        print(f"[Run {run_index}] Errore nella generazione del dataset: {e}")
        return {'run': run_index, 'pattern': pattern, 'found': '', 'best_fitness': 0.0, 'time_s': 0.0, 'dataset_dir': str(dataset_dir), 'error': str(e)}


    good_dir = dataset_dir / 'tracce_buone'
    bad_dir = dataset_dir / 'tracce_cattive'

    # 4. esegui GA classico
    ga_params = ga_params or {}
    # --- GA classico ---
    start = time.perf_counter()
    try:
        migliore = ga_main.evoluzione(
            dimensione_popolazione=ga_params.get('dimensione_popolazione', 50),
            generazioni=ga_params.get('generazioni', 100),
            probabilita_mutazione=ga_params.get('probabilita_mutazione', 0.3),
            percentuale_elite=ga_params.get('percentuale_elite', 0.1),
            top_n_display=ga_params.get('top_n_display', 10),
            permissive_crossover=ga_params.get('permissive_crossover', False),
            cartella_buone=str(good_dir),
            cartella_cattive=str(bad_dir)
        )
    except Exception as e:
        end = time.perf_counter()
        print(f"[Run {run_index}] Errore durante GA: {e}")
        migliore = None
        time_s = end - start
        found = ''
        best_fitness = 0.0
    else:
        end = time.perf_counter()
        time_s = end - start
        if not migliore:
            found = ''
            best_fitness = 0.0
        else:
            found = migliore.get('regex', '')
            best_fitness = float(migliore.get('voto', 0.0) or 0.0)
    print(f"[Run {run_index}] GA: best_fitness={best_fitness:.4f} time={time_s:.2f}s")

    # --- LLM ---
    print(f"[Run {run_index}] Querying LLM...")
    good_traces = load_traces(good_dir)
    bad_traces = load_traces(bad_dir)
    prompt = f"""You are a regex expert. Given these 10 positive examples that should match the regex (full-match):\n\n{chr(10).join(good_traces[:10])}\n\nAnd these 10 negative examples that should NOT match (full-match):\n\n{chr(10).join(bad_traces[:10])}\n\nGenerate a single valid regex pattern that FULLY matches ALL the positive examples and NONE of the negative examples. The regex must be valid, plausible, not overly long, and should not use constructs that are unlikely to generalize. Output only the regex, nothing else."""
    llm_start = time.perf_counter()
    llm_response = query_llm(prompt)
    llm_time = time.perf_counter() - llm_start
    llm_regex = extract_regex_from_llm_response(llm_response)
    print(f"[Run {run_index}] LLM regex: {llm_regex} (time={llm_time:.2f}s)")
    llm_fitness = 0.0
    try:
        llm_compiled = regex.compile(llm_regex)
        llm_fitness = compute_fitness(llm_compiled, good_dir, bad_dir)
    except Exception:
        llm_fitness = 0.0
    print(f"[Run {run_index}] LLM fitness: {llm_fitness:.4f}")

    # --- GA ibrido ---
    print(f"[Run {run_index}] GA ibrido...")
    start_h = time.perf_counter()
    try:
        tracce_buone = good_traces[:10]
        tracce_cattive = bad_traces[:10]
        n_llm = 5
        n_rand = ga_params.get('dimensione_popolazione', 200) - n_llm
        popolazione_random = ga_main.inizializza(n_rand, ibrido=False)
        popolazione_llm = ga_main.inizializza(n_llm, ibrido=True, tracce_buone=tracce_buone, tracce_cattive=tracce_cattive)
        popolazione_ibrida = popolazione_random + popolazione_llm
        migliore_h = ga_main.evoluzione(
            dimensione_popolazione=ga_params.get('dimensione_popolazione', 200),
            generazioni=ga_params.get('generazioni', 20),
            probabilita_mutazione=ga_params.get('probabilita_mutazione', 0.3),
            percentuale_elite=ga_params.get('percentuale_elite', 0.1),
            top_n_display=ga_params.get('top_n_display', 10),
            permissive_crossover=ga_params.get('permissive_crossover', False),
            cartella_buone=str(good_dir),
            cartella_cattive=str(bad_dir),
            popolazione_iniziale=popolazione_ibrida
        )
    except Exception as e:
        end_h = time.perf_counter()
        print(f"[Run {run_index}] Errore durante GA ibrido: {e}")
        migliore_h = None
        time_h = end_h - start_h
        found_h = ''
        best_fitness_h = 0.0
    else:
        end_h = time.perf_counter()
        time_h = end_h - start_h
        if not migliore_h:
            found_h = ''
            best_fitness_h = 0.0
        else:
            found_h = migliore_h.get('regex', '')
            best_fitness_h = float(migliore_h.get('voto', 0.0) or 0.0)
    print(f"[Run {run_index}] GA ibrido: best_fitness={best_fitness_h:.4f} time={time_h:.2f}s")

    return {
        'run': run_index,
        'pattern': pattern,
        'found': found,
        'best_fitness': best_fitness,
        'time_s': time_s,
        'llm_regex': llm_regex,
        'llm_fitness': llm_fitness,
        'llm_time': llm_time,
        'found_hybrid': found_h,
        'best_fitness_hybrid': best_fitness_h,
        'time_hybrid': time_h,
        'dataset_dir': str(dataset_dir),
        'error': ''
    }


def main():
    parser = argparse.ArgumentParser(description='Esegui esperimenti ripetuti del GA su dataset generati da regex casuali')
    parser.add_argument('--n', type=int, default=5, help='Numero di lanci (default: 5)')
    parser.add_argument('--out', type=str, default=None, help='CSV di output (default: risultati esperimenti/experiments_results_<timestamp>.csv)')
    parser.add_argument('--per_category', type=int, default=100, help='Numero di tracce per categoria nel dataset (default: 500)')
    parser.add_argument('--pop', type=int, default=500, help='Dimensione popolazione GA')
    parser.add_argument('--gens', type=int, default=200, help='Numero generazioni GA')
    parser.add_argument('--mut', type=float, default=0.3, help='Probabilità di mutazione iniziale')
    parser.add_argument('--permissive', action='store_true', help='Usa crossover permissivo')
    parser.add_argument('--elite', type=float, default=0.1, help='Percentuale elitismo (es. 0.1 => 10%)')
    parser.add_argument('--topn', type=int, default=10, help='Top N da salvare per generazione (default:10)')
    args = parser.parse_args()

    n_runs = args.n

    # Crea cartella "risultati esperimenti" se non esiste
    results_dir = Path.cwd() / 'risultati esperimenti'
    results_dir.mkdir(parents=True, exist_ok=True)

    # Se --out non specificato, crea un filename con timestamp (data e ora)
    if args.out is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        out_path = results_dir / f'experiments_results_{timestamp}.csv'
    else:
        out_path = Path(args.out)

    ga_params = {
        'dimensione_popolazione': args.pop,
        'generazioni': args.gens,
        'probabilita_mutazione': args.mut,
        'permissive_crossover': args.permissive,
        'percentuale_elite': args.elite,
        'top_n_display': args.topn
    }

    # Apri il file CSV e scrivi l'header
    fieldnames = ['run', 'pattern', 'found', 'best_fitness', 'time_s', 'llm_regex', 'llm_fitness', 'llm_time', 'found_hybrid', 'best_fitness_hybrid', 'time_hybrid', 'dataset_dir', 'error']
    with open(out_path, 'w', newline='', encoding='utf-8') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, n_runs + 1):
            res = run_one(i, selected_per_category=args.per_category, ga_params=ga_params)
            # Scrivi immediatamente il risultato nel CSV
            writer.writerow({k: res.get(k, '') for k in fieldnames})

    print(f"Esperimenti completati. Risultati salvati in: {out_path}")


if __name__ == '__main__':
    main()
