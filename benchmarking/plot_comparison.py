
import argparse
import csv
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def read_csv(path):
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def plot_comparison(csv_path, out_path=None, show=False):
    import numpy as np
    # Lettura CSV e variabili derivate
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file non trovato: {csv_path}")

    rows = read_csv(csv_path)
    if not rows:
        raise ValueError("CSV vuoto o senza righe")

    runs = [int(r.get('run', i+1)) for i, r in enumerate(rows)]
    # Fitness media per ogni metodo (dopo aver letto i dati)
    ga_fitness = [safe_float(r.get('best_fitness', 0.0)) for r in rows]
    llm_fitness = [safe_float(r.get('llm_fitness', 0.0)) for r in rows]
    hybrid_fitness = [safe_float(r.get('best_fitness_hybrid', 0.0)) for r in rows]
    ga_fitness_avg = np.mean(ga_fitness) if ga_fitness else 0.0
    llm_fitness_avg = np.mean(llm_fitness) if llm_fitness else 0.0
    hybrid_fitness_avg = np.mean(hybrid_fitness) if hybrid_fitness else 0.0
    ga_fitness = [safe_float(r.get('best_fitness', 0.0)) for r in rows]
    llm_fitness = [safe_float(r.get('llm_fitness', 0.0)) for r in rows]
    patterns = [r.get('pattern', '') for r in rows]
    founds = [r.get('found', '') for r in rows]
    ga_times = [safe_float(r.get('time_s', 0.0)) for r in rows]
    llm_regexes = [r.get('llm_regex', '') for r in rows]
    llm_times = [safe_float(r.get('llm_time', 0.0)) for r in rows]
    hybrid_fitness = [safe_float(r.get('best_fitness_hybrid', 0.0)) for r in rows]
    hybrid_times = [safe_float(r.get('time_hybrid', 0.0)) for r in rows]
    founds_hybrid = [r.get('found_hybrid', '') for r in rows]
    # Percentuale di run con fitness > 0.9
    ga_above_09 = 100.0 * sum([x > 0.9 for x in ga_fitness]) / len(ga_fitness) if ga_fitness else 0.0
    llm_above_09 = 100.0 * sum([x > 0.9 for x in llm_fitness]) / len(llm_fitness) if llm_fitness else 0.0
    hybrid_above_09 = 100.0 * sum([x > 0.9 for x in hybrid_fitness]) / len(hybrid_fitness) if hybrid_fitness else 0.0
    # Numero di run con fitness < 0.5
    ga_below_05 = sum([x < 0.5 for x in ga_fitness])
    llm_below_05 = sum([x < 0.5 for x in llm_fitness])
    hybrid_below_05 = sum([x < 0.5 for x in hybrid_fitness])
    # Lunghezze regex
    pattern_lens = [len(p) for p in patterns]
    ga_lens = [len(f) if f else 0 for f in founds]
    llm_lens = [len(f) if f else 0 for f in llm_regexes]
    hybrid_lens = [len(f) if f else 0 for f in founds_hybrid]
    # Media percentuale di quanto la regex trovata è più lunga/corta rispetto all'originale
    def avg_pct_len_over(found_lens, orig_lens):
        diffs = [(f - o) / o * 100 if o > 0 else 0 for f, o in zip(found_lens, orig_lens)]
        return np.mean(diffs) if diffs else 0.0
    ga_pct_len = avg_pct_len_over(ga_lens, pattern_lens)
    llm_pct_len = avg_pct_len_over(llm_lens, pattern_lens)
    hybrid_pct_len = avg_pct_len_over(hybrid_lens, pattern_lens)

    # Numero di run in cui ogni metodo ha ottenuto fitness 1
    ga_ones = sum([abs(x - 1.0) < 1e-6 for x in ga_fitness])
    llm_ones = sum([abs(x - 1.0) < 1e-6 for x in llm_fitness])
    hybrid_ones = sum([abs(x - 1.0) < 1e-6 for x in hybrid_fitness])

    # Calcola la media percentuale di quanto ogni metodo ha superato gli altri due, solo nei run in cui è stato il migliore
    def avg_pct_advantage(f1, f2, f3):
        advantages = [(a - max(b, c)) / max(b, c) * 100 if (a > b and a > c and max(b, c) > 0) else None for a, b, c in zip(f1, f2, f3)]
        filtered = [v for v in advantages if v is not None]
        return np.mean(filtered) if filtered else 0.0
    ga_adv = avg_pct_advantage(ga_fitness, llm_fitness, hybrid_fitness)
    llm_adv = avg_pct_advantage(llm_fitness, ga_fitness, hybrid_fitness)
    hybrid_adv = avg_pct_advantage(hybrid_fitness, ga_fitness, llm_fitness)
    # Calcola statistiche per la tabella overview
    def pct_better(a, b):
        return 100.0 * sum([x > y for x, y in zip(a, b)]) / len(a) if a and b else 0.0
    def avg_diff(a, b):
        vals = [x - y for x, y in zip(a, b)]
        return np.mean(vals) if vals else 0.0
    def pct_exact(a, b):
        return 100.0 * sum([abs(x - y) < 1e-6 for x, y in zip(a, b)]) / len(a) if a and b else 0.0
    # Fitness
    ga_vs_llm = pct_better(ga_fitness, llm_fitness)
    ga_vs_hybrid = pct_better(ga_fitness, hybrid_fitness)
    llm_vs_hybrid = pct_better(llm_fitness, hybrid_fitness)
    ga_vs_llm_avg = avg_diff(ga_fitness, llm_fitness)
    ga_vs_hybrid_avg = avg_diff(ga_fitness, hybrid_fitness)
    llm_vs_hybrid_avg = avg_diff(llm_fitness, hybrid_fitness)
    ga_exact = pct_exact(ga_fitness, [1.0]*len(ga_fitness))
    llm_exact = pct_exact(llm_fitness, [1.0]*len(llm_fitness))
    hybrid_exact = pct_exact(hybrid_fitness, [1.0]*len(hybrid_fitness))

    # Percentuale di run in cui ogni algoritmo ha la fitness massima (inclusi i pareggi)
    def pct_max(f1, f2, f3):
        n = len(f1)
        ga_share = 0.0
        llm_share = 0.0
        hybrid_share = 0.0
        for a, b, c in zip(f1, f2, f3):
            maxval = max(a, b, c)
            winners = []
            if abs(a - maxval) < 1e-6:
                winners.append('ga')
            if abs(b - maxval) < 1e-6:
                winners.append('llm')
            if abs(c - maxval) < 1e-6:
                winners.append('hybrid')
            share = 1.0 / len(winners)
            for w in winners:
                if w == 'ga':
                    ga_share += share
                elif w == 'llm':
                    llm_share += share
                elif w == 'hybrid':
                    hybrid_share += share
        return 100.0 * ga_share / n, 100.0 * llm_share / n, 100.0 * hybrid_share / n
    ga_best, llm_best, hybrid_best = pct_max(ga_fitness, llm_fitness, hybrid_fitness)
    # Tempi
    ga_time_avg = np.mean(ga_times)
    llm_time_avg = np.mean(llm_times)
    hybrid_time_avg = np.mean(hybrid_times)
    # Compattezza
    ga_len_avg = np.mean(ga_lens)
    llm_len_avg = np.mean(llm_lens)
    hybrid_len_avg = np.mean(hybrid_lens)
    pattern_len_avg = np.mean(pattern_lens)
    ga_len_over = ga_len_avg - pattern_len_avg
    llm_len_over = llm_len_avg - pattern_len_avg
    hybrid_len_over = hybrid_len_avg - pattern_len_avg

    # Crea subplot con 3 righe: istogramma sopra, line plot sotto, overview in fondo
    from plotly.subplots import make_subplots
    # Altezza dinamica precisa: 60px per grafico, 40px per riga tabella
    n_table_rows = 1 + len([
        "Percentage of runs where the algorithm has maximum fitness",
        "Average fitness",
        "Average advantage when best",
        "Number of runs with fitness=1",
        "Number of runs with fitness < 0.5",
        "Percentage of runs with fitness > 0.9",
        "Average execution time per run (s)",
        "Average difference between found regex length and original"
    ])
    bar_height = 500
    line_height = 500
    table_height = 40 * n_table_rows
    fig_height = bar_height + line_height + table_height
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.15,
        row_heights=[0.35, 0.35, 0.3],
        subplot_titles=("GA vs LLM vs Hybrid Comparison: Fitness (Bar)", "Time per Run (Line)", "Overview Statistics"),
        specs=[[{}], [{}], [{"type": "table"}]]
    )
    # Tabella overview come trace Table
    import plotly.graph_objects as go
    overview_table = go.Table(
        header=dict(
            values=[
                "Comparison",
                "Genetic Algorithm",
                "LLM",
                "Hybrid"
            ],
            align='center', fill_color='paleturquoise'),
        cells=dict(
            values=[
                [
                    "Percentage of runs where the algorithm has maximum fitness",
                    "Average fitness",
                    "Average advantage when best",
                    "Number of runs with fitness=1",
                    "Number of runs with fitness < 0.5",
                    "Percentage of runs with fitness > 0.9",
                    "Average execution time per run (s)",
                    "Average difference between found regex length and original"
                ],
                [f"{ga_best:.1f}%", f"{ga_fitness_avg:.3f}", f"{ga_adv:.1f}%", f"{ga_ones}", f"{ga_below_05}", f"{ga_above_09:.1f}%", f"{ga_time_avg:.2f}", f"{ga_pct_len:+.1f}%"],
                [f"{llm_best:.1f}%", f"{llm_fitness_avg:.3f}", f"{llm_adv:.1f}%", f"{llm_ones}", f"{llm_below_05}", f"{llm_above_09:.1f}%", f"{llm_time_avg:.2f}", f"{llm_pct_len:+.1f}%"],
                [f"{hybrid_best:.1f}%", f"{hybrid_fitness_avg:.3f}", f"{hybrid_adv:.1f}%", f"{hybrid_ones}", f"{hybrid_below_05}", f"{hybrid_above_09:.1f}%", f"{hybrid_time_avg:.2f}", f"{hybrid_pct_len:+.1f}%"]
            ],
            align='center', fill_color='lavender'
        )
    )
    fig.add_trace(overview_table, row=3, col=1)
    fig.update_layout(height=fig_height)  # altezza dinamica ottimizzata
    # Label asse y per il grafico Time per Run (riga 2)
    fig.update_yaxes(title_text="Time (s)", row=2, col=1)

    # Histogram (row 1)
    fig.add_bar(
        x=runs,
        y=ga_fitness,
        name='GA',
        marker_color='rgba(0, 123, 255, 0.8)',
        customdata=list(zip(patterns, founds, ga_times)),
        hovertemplate='Run %{x}<br>Target: %{customdata[0]}<br>Found: %{customdata[1]}<br>Time: %{customdata[2]:.2f}s<br>Fitness: %{y:.4f}<extra></extra>',
        showlegend=True,
        row=1, col=1
    )
    fig.add_bar(
        x=runs,
        y=llm_fitness,
        name='LLM',
        marker_color='rgba(40, 167, 69, 0.8)',  # green
        customdata=list(zip(patterns, llm_regexes, llm_times)),
        hovertemplate='Run %{x}<br>Target: %{customdata[0]}<br>LLM Regex: %{customdata[1]}<br>Time: %{customdata[2]:.2f}s<br>Fitness: %{y:.4f}<extra></extra>',
        showlegend=True,
        row=1, col=1
    )
    fig.add_bar(
        x=runs,
        y=hybrid_fitness,
        name='Hybrid',
        marker_color='rgba(220, 53, 69, 0.8)',  # red
        customdata=list(zip(patterns, founds_hybrid, hybrid_times)),
        hovertemplate='Run %{x}<br>Target: %{customdata[0]}<br>Found (Hybrid): %{customdata[1]}<br>Time: %{customdata[2]:.2f}s<br>Fitness: %{y:.4f}<extra></extra>',
        showlegend=True,
        row=1, col=1
    )

    # Line plot (row 2) - EXECUTION TIME
    fig.add_trace(
        go.Scatter(
            x=runs,
            y=ga_times,
            mode='lines+markers',
            name='GA Time (s)',
            line=dict(color='blue', width=2),
            marker=dict(color='blue', size=6),
            showlegend=False,
            customdata=list(zip(patterns, founds, ga_times)),
            hovertemplate='Run %{x}<br>Target: %{customdata[0]}<br>Found: %{customdata[1]}<br>Time: %{customdata[2]:.2f}s<extra></extra>'
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=runs,
            y=llm_times,
            mode='lines+markers',
            name='LLM Tempo (s)',
            line=dict(color='rgba(40, 167, 69, 0.8)', width=2),  # verde
            marker=dict(color='rgba(40, 167, 69, 0.8)', size=6),
            showlegend=False,
            customdata=list(zip(patterns, llm_regexes, llm_times)),
            hovertemplate='Run %{x}<br>Target: %{customdata[0]}<br>LLM Regex: %{customdata[1]}<br>Tempo: %{customdata[2]:.2f}s<extra></extra>'
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=runs,
            y=hybrid_times,
            mode='lines+markers',
            name='Hybrid Tempo (s)',
            line=dict(color='rgba(220, 53, 69, 0.8)', width=2),  # rosso
            marker=dict(color='rgba(220, 53, 69, 0.8)', size=6),
            showlegend=False,
            customdata=list(zip(patterns, founds_hybrid, hybrid_times)),
            hovertemplate='Run %{x}<br>Target: %{customdata[0]}<br>Found (Hybrid): %{customdata[1]}<br>Tempo: %{customdata[2]:.2f}s<extra></extra>'
        ),
        row=2, col=1
    )

    fig.update_layout(
        barmode='group',
        title_text=None
    )
    fig.update_xaxes(title_text="Run", row=2, col=1)
    fig.update_yaxes(title_text="Fitness", row=1, col=1)
    fig.update_yaxes(title_text="Tempo (s)", row=2, col=1)

    if out_path:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if out_path.suffix.lower() == '.html':
            fig.write_html(str(out_path))
        else:
            fig.write_image(str(out_path))
        print(f'Saved plot to: {out_path}')

    if show:
        fig.show()


def main():
    parser = argparse.ArgumentParser(description='Plot confronto GA vs LLM da CSV')
    parser.add_argument('--csv', required=True, help='CSV file con risultati esperimenti')
    parser.add_argument('--out', default='comparison_plot.html', help='File di output (HTML per interattivo, PNG/PDF per statico)')
    parser.add_argument('--show', action='store_true', help='Mostra il grafico a schermo')
    args = parser.parse_args()

    plot_comparison(args.csv, out_path=args.out, show=args.show)


if __name__ == '__main__':
    main()
