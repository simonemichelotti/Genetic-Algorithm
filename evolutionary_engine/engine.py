from data_simulation.regex_generator import generate_random_regex
from syntactic_representation.ast_generator import genera_ast, RegexParser
from syntactic_representation.ast_to_regex import ast_to_regex
import os
import regex
import random
from lark import Tree, Token
import copy
from functools import lru_cache
import subprocess

# ---------------------------------------------------------------------------
# Nodi AST sicuri per crossover conservativo
# ---------------------------------------------------------------------------
NODI_SCAMBIABILI_SICURI = {
    'alternation',
    'repetition',
    'atom',
    'escape_sequence',
    'char',
    'char_class',
    'group',
    'wildcard',
}

# ---------------------------------------------------------------------------
# Parametri globali – fitness e penalità strutturali
# ---------------------------------------------------------------------------
WEIGHT_F1 = 0.65
WEIGHT_SPECIFICITY = 0.35
SIMPLICITY_WEIGHT = 0.25
NEG_SAMPLE_WEIGHT = 0.5
MAX_NEG_SAMPLES = 50
SIMP_BONUS_MAX = 0.02
EMTPY_MATCH_PENALTY = 0.25
NESTED_QUANT_PENALTY = 0.20
WILDCARD_PENALTY_PER = 0.02
CHAR_CLASS_PENALTY_PER = 0.03
UNICODE_PENALTY = 0.06
LITERAL_BONUS = 0.06
RANDOM_NEG_SAMPLES = 30
RANDOM_NEG_LEN_MAX = 6
RANDOM_NEG_SEED = 12345

# Crossover: True = permissive (può produrre regex invalidi) / False = conservativo
PERMISSIVE_CROSSOVER = True


# ---------------------------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------------------------

def query_llm(prompt):
    try:
        result = subprocess.run(
            ['ollama', 'run', 'phi3:mini'],
            input=prompt, text=True, capture_output=True, encoding='utf-8'
        )
        return result.stdout.strip()
    except Exception:
        return ""


def extract_regex_from_llm_response(response):
    """Estrae la regex dalla risposta dell'LLM, ignorando spiegazioni aggiuntive."""
    lines = response.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.lower().startswith(
            ('explanation', 'explangyer', 'note', 'the regex', 'this regex', 'explangy')
        ):
            if any(c in line for c in ['^', '$', '[', ']', '+', '*', '?', '|', '\\', '(', ')']):
                return line
    return response.strip()


# ---------------------------------------------------------------------------
# Inizializzazione della popolazione
# ---------------------------------------------------------------------------

def inizializza(dimensione=50, ibrido=False, tracce_buone=None, tracce_cattive=None):
    """
    Genera la popolazione iniziale di regex.

    In modalità ibrida interroga l'LLM per ottenere candidati semanticamente
    informati; in modalità standard usa regex casuali.
    """
    popolazione = []
    if ibrido and tracce_buone is not None and tracce_cattive is not None:
        print(f"[LLM] Generazione popolazione ibrida con {dimensione} regex...")
        prompt = (
            "You are a regex expert. Given these 10 positive examples that should match the regex (full-match):\n\n"
            + "\n".join(tracce_buone[:10])
            + "\n\nAnd these 10 negative examples that should NOT match (full-match):\n\n"
            + "\n".join(tracce_cattive[:10])
            + f"\n\nGenerate {dimensione} different valid regex patterns (one per line) that FULLY match ALL "
            "the positive examples and NONE of the negative examples. Output only the regexes, one per line, nothing else."
        )
        response = query_llm(prompt)
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        regexes = [
            line for line in lines
            if any(c in line for c in ['^', '$', '[', ']', '+', '*', '?', '|', '\\', '(', ')'])
        ]
        while len(regexes) < dimensione:
            regexes.append(random.choice(regexes) if regexes else 'a')
        popolazione = regexes[:dimensione]
    else:
        for _ in range(dimensione):
            popolazione.append(generate_random_regex())
    return popolazione


# ---------------------------------------------------------------------------
# Caricamento tracce da file
# ---------------------------------------------------------------------------

def carica_tracce(cartella_buone="tracce_buone", cartella_cattive="tracce_cattive"):
    """Carica le tracce positive e negative dalle cartelle indicate."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    def leggi_tracce_da_cartella(nome_cartella):
        tracce = []
        path = os.path.join(base_dir, nome_cartella)
        if not os.path.isabs(nome_cartella):
            # Se il percorso non è assoluto, risolvi rispetto alla cwd
            path = os.path.abspath(nome_cartella)
        if os.path.exists(path):
            for filename in os.listdir(path):
                filepath = os.path.join(path, filename)
                if os.path.isfile(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        contenuto = f.read()
                        if contenuto.endswith('\n'):
                            contenuto = contenuto.rstrip('\n')
                        tracce.append('' if contenuto.strip() == '' else contenuto.strip())
        else:
            print(f"ERRORE: Cartella non trovata: {path}")
        return tracce

    return leggi_tracce_da_cartella(cartella_buone), leggi_tracce_da_cartella(cartella_cattive)


# ---------------------------------------------------------------------------
# Pool deterministico di stringhe negative casuali
# ---------------------------------------------------------------------------

def _random_negative_strings(sample_size=RANDOM_NEG_SAMPLES, max_len=RANDOM_NEG_LEN_MAX,
                              alphabet=None, rng=None):
    if alphabet is None:
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    import random as _local_rand
    if rng is None:
        rng = _local_rand
    out = []
    for _ in range(sample_size):
        ln = rng.randint(1, max_len)
        out.append(''.join(rng.choice(alphabet) for _ in range(ln)))
    return out


_RANDOM_NEG_RNG = random.Random(RANDOM_NEG_SEED)
RANDOM_NEG_POOL = _random_negative_strings(RANDOM_NEG_SAMPLES, RANDOM_NEG_LEN_MAX, rng=_RANDOM_NEG_RNG)


# ---------------------------------------------------------------------------
# Compilazione con cache
# ---------------------------------------------------------------------------

@lru_cache(maxsize=512)
def _compile_pattern_cached(regex_str):
    return regex.compile(regex_str)


# ---------------------------------------------------------------------------
# Utilità
# ---------------------------------------------------------------------------

def ottieni_ast(regex_str):
    """Restituisce l'AST di una stringa regex, o None se non parsabile."""
    try:
        return genera_ast(regex_str)
    except Exception:
        return None


def dataset_conflicts(tracce_buone, tracce_cattive):
    """Restituisce le tracce presenti in entrambi i set (conflitti)."""
    return set(tracce_buone) & set(tracce_cattive)


# ---------------------------------------------------------------------------
# Penalità strutturale
# ---------------------------------------------------------------------------

def _regex_structural_penalty(regex_str):
    """Calcola una penalità in [0,1] per regex troppo generiche."""
    num_len = len(regex_str)
    num_alt = regex_str.count('|')
    num_class = regex_str.count('[')
    num_wild = regex_str.count('.')
    num_quant = sum(regex_str.count(c) for c in ('*', '+', '?')) + regex_str.count('{')
    nested_q = bool(regex.search(r'[\)\]\}][*+?{]', regex_str))

    penalty = 0.0
    penalty += min(0.4, num_wild * WILDCARD_PENALTY_PER)
    penalty += min(0.4, num_class * CHAR_CLASS_PENALTY_PER)
    penalty += NESTED_QUANT_PENALTY if nested_q else 0.0
    penalty += min(0.25, 0.01 * num_alt + 0.01 * num_quant)
    penalty += min(0.05, max(0.0, (num_len - 10) / 200.0))
    return max(0.0, min(1.0, penalty))


# ---------------------------------------------------------------------------
# Funzione di fitness
# ---------------------------------------------------------------------------

def calcola_fitness(regex_str, tracce_buone, tracce_cattive, ast=None):
    """
    Calcola la fitness composita F(r) ∈ [0,1]:
        F = A(r) · G(r) · P(r) + bonus_literal

    dove:
        A(r) = accuracy sulle tracce buone/cattive
        G(r) = penalità per over-generalizzazione (random negative pool)
        P(r) = penalità strutturale (wildcard, char class, quantificatori annidati)

    Ritorna (score, info_dict).
    """
    MAX_REGEX_LENGTH = 200
    if len(regex_str) > MAX_REGEX_LENGTH:
        return 0.0, {'invalid': True, 'reason': 'too_long'}

    try:
        pattern = _compile_pattern_cached(regex_str)
    except Exception:
        return 0.0, {'invalid': True, 'reason': 'compile_error'}

    totali = len(tracce_buone) + len(tracce_cattive)
    if totali == 0:
        return 0.0, {'invalid': True, 'reason': 'no_traces'}

    corretti = 0
    matched_good_examples = []
    matched_bad_examples = []

    for t in tracce_buone:
        try:
            is_full = bool(pattern.fullmatch(t))
        except Exception:
            is_full = False
        if is_full:
            corretti += 1
            if len(matched_good_examples) < 5:
                matched_good_examples.append(t)

    for t in tracce_cattive:
        try:
            is_full = bool(pattern.fullmatch(t))
        except Exception:
            is_full = True
        if not is_full:
            corretti += 1
        else:
            if len(matched_bad_examples) < 5:
                matched_bad_examples.append(t)

    base_score = corretti / totali
    struct_pen = _regex_structural_penalty(regex_str)

    neg_samples = RANDOM_NEG_POOL
    if neg_samples:
        neg_matched = 0
        for ns in neg_samples:
            try:
                if bool(pattern.fullmatch(ns)):
                    neg_matched += 1
            except Exception:
                neg_matched += 1
        neg_ratio = neg_matched / len(neg_samples)
    else:
        neg_ratio = 0.0

    neg_penalty = neg_ratio * NEG_SAMPLE_WEIGHT
    total_struct_penalty = SIMPLICITY_WEIGHT * (struct_pen * (1 - NEG_SAMPLE_WEIGHT) + neg_penalty)

    literal_bonus = 0.0
    if 'ab' in regex_str:
        literal_bonus += 0.012
    if 'c+' in regex_str or 'cc*' in regex_str or 'c*' in regex_str:
        literal_bonus += 0.01
    literal_bonus = min(SIMP_BONUS_MAX, literal_bonus)

    final_score = max(0.0, min(1.0, base_score * (1.0 - total_struct_penalty) + literal_bonus))

    info = {
        'base_score': base_score,
        'final_score': final_score,
        'correctly_classified': corretti,
        'total_traces': totali,
        'matched_good_examples': matched_good_examples,
        'matched_bad_examples': matched_bad_examples,
        'struct_penalty': struct_pen,
        'neg_ratio': neg_ratio,
        'total_struct_penalty': total_struct_penalty,
    }
    return final_score, info


def fitness(popolazione, tracce_buone, tracce_cattive):
    """Valuta tutta la popolazione e aggiorna il campo 'voto' di ogni individuo."""
    risultati = []
    for individuo in popolazione:
        regex_val = individuo['regex']
        if not isinstance(regex_val, str):
            continue
        ast = individuo.get('ast')
        if ast is None:
            ast = ottieni_ast(regex_val)
        voto, info = calcola_fitness(regex_val, tracce_buone, tracce_cattive, ast=ast)
        risultati.append({'regex': regex_val, 'ast': ast, 'voto': voto, 'info': info})
    return risultati


def selezione(popolazione, top_n=None):
    """Ordina la popolazione per voto decrescente e ritorna i primi top_n."""
    sorted_pop = sorted(popolazione, key=lambda x: x.get('voto', 0), reverse=True)
    if top_n is None:
        top_n = len(sorted_pop)
    return sorted_pop[:max(0, int(top_n))]


# ---------------------------------------------------------------------------
# Operatori genetici – Crossover
# ---------------------------------------------------------------------------

def get_all_subtrees(tree, subtrees=None):
    """Restituisce tutti i sottoalberi dell'AST come lista di (parent, index, subtree)."""
    if subtrees is None:
        subtrees = []
    if isinstance(tree, Tree):
        subtrees.append((None, None, tree))
        for i, child in enumerate(tree.children):
            if isinstance(child, Tree):
                subtrees.append((tree, i, child))
                get_all_subtrees(child, subtrees)
    return subtrees


def crossover_singolo(ast1, ast2, permissive=False):
    """
    Crossover strutturale su AST: scambia sottoalberi omologhi tra due genitori.

    In modalità conservativa (permissive=False) applica filtri di sicurezza per
    evitare quantificatori annidati e nodi non sicuri.
    """
    if ast1 is None or ast2 is None:
        return ast1, ast2

    figlio1 = copy.deepcopy(ast1)
    figlio2 = copy.deepcopy(ast2)

    subtrees1 = get_all_subtrees(figlio1)
    subtrees2 = get_all_subtrees(figlio2)
    if len(subtrees1) < 1 or len(subtrees2) < 1:
        return figlio1, figlio2

    def group_by_type(subtrees, permissive_mode):
        groups = {}
        for parent, index, subtree in subtrees:
            if not isinstance(subtree, Tree):
                continue
            node_type = subtree.data
            if not permissive_mode:
                if parent is None:
                    continue
                if node_type not in NODI_SCAMBIABILI_SICURI:
                    continue
                if node_type == 'repetition' and parent is not None and parent.data == 'repetition':
                    continue

                def contains_repetition(n):
                    if not isinstance(n, Tree):
                        return False
                    if n.data == 'repetition':
                        return True
                    return any(contains_repetition(c) for c in n.children)

                if parent is not None and parent.data == 'repetition' and contains_repetition(subtree):
                    continue
            if node_type not in groups:
                groups[node_type] = []
            groups[node_type].append((parent, index, subtree))
        return groups

    groups1 = group_by_type(subtrees1, permissive)
    groups2 = group_by_type(subtrees2, permissive)

    common_types = set(groups1.keys()) & set(groups2.keys())
    if not common_types:
        return figlio1, figlio2

    node_type = random.choice(list(common_types))
    punto1 = random.choice(groups1[node_type])
    punto2 = random.choice(groups2[node_type])
    parent1, index1, subtree1 = punto1
    parent2, index2, subtree2 = punto2

    if parent1 is None:
        figlio1 = copy.deepcopy(subtree2)
    else:
        parent1.children[index1] = copy.deepcopy(subtree2)

    if parent2 is None:
        figlio2 = copy.deepcopy(subtree1)
    else:
        parent2.children[index2] = copy.deepcopy(subtree1)

    return figlio1, figlio2


# ---------------------------------------------------------------------------
# Operatori genetici – Mutazione
# ---------------------------------------------------------------------------

def mutazione_singola(ast, probabilita=0.1):
    """
    Mutazione strutturale su AST: modifica un nodo in modo type-safe.

    Tipi di mutazione supportati:
        - char         : sostituisce il carattere con uno alfanumerico casuale
        - escape_seq   : cambia l'escape class (\\d → \\w) o la Unicode property
        - repetition   : aggiunge o rimuove il quantificatore
        - domain bias  : con bassa probabilità inietta la concatenazione 'ab' come alternativa
    """
    if ast is None or random.random() > probabilita:
        return copy.deepcopy(ast)

    mutante = copy.deepcopy(ast)
    subtrees = get_all_subtrees(mutante)
    if len(subtrees) < 2:
        return mutante

    parent, index, subtree = random.choice(subtrees[1:])
    if parent is None or not isinstance(subtree, Tree):
        return mutante

    if subtree.data == "char" and len(subtree.children) > 0:
        if isinstance(subtree.children[0], Token) and subtree.children[0].type == 'CHAR':
            nuovo_char = random.choice(
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            )
            subtree.children[0] = Token('CHAR', nuovo_char)

    elif subtree.data == "escape_sequence" and len(subtree.children) > 0:
        child = subtree.children[0]
        if isinstance(child, Tree) and child.data == "unicode_property":
            nuova_property = random.choice(['Sc', 'L', 'Ll', 'Lu', 'N', 'Nd', 'Sm', 'P', 'S'])
            child.children[0] = Token('PROPERTY_NAME', nuova_property)
        elif isinstance(child, Token):
            nuovo_escape = random.choice(['d', 'D', 'w', 'W', 's', 'S'])
            subtree.children[0] = Token(child.type, nuovo_escape)

    elif subtree.data == "repetition":
        if len(subtree.children) == 1:
            quantificatore = random.choice(['*', '+', '?'])
            token_type = {'*': 'STAR', '+': 'PLUS', '?': 'QMARK'}[quantificatore]
            quantifier_tree = Tree('quantifier', [Token(token_type, quantificatore)])
            subtree.children.append(quantifier_tree)
        elif len(subtree.children) > 1 and random.random() < 0.3:
            subtree.children = [subtree.children[0]]

    # Domain-specific bias: inietta alternanza con literal 'ab'
    if isinstance(parent, Tree) and isinstance(subtree, Tree) and random.random() < 0.12:
        try:
            ab_char_a = Tree('char', [Token('CHAR', 'a')])
            ab_rep_a = Tree('repetition', [ab_char_a])
            ab_char_b = Tree('char', [Token('CHAR', 'b')])
            ab_rep_b = Tree('repetition', [ab_char_b])
            ab_concat = Tree('concatenation', [ab_rep_a, ab_rep_b])
            new_alt = Tree('alternation', [copy.deepcopy(subtree), ab_concat])
            parent.children[index] = new_alt
            return mutante
        except Exception:
            pass

    # Iniezione di concatenazione 'ab' prima o dopo il nodo selezionato
    if isinstance(parent, Tree) and isinstance(subtree, Tree) and random.random() < 0.10:
        try:
            ab_char_a = Tree('char', [Token('CHAR', 'a')])
            ab_rep_a = Tree('repetition', [ab_char_a])
            ab_char_b = Tree('char', [Token('CHAR', 'b')])
            ab_rep_b = Tree('repetition', [ab_char_b])
            ab_concat = Tree('concatenation', [ab_rep_a, ab_rep_b])
            if random.random() < 0.5:
                parent.children.insert(index, ab_concat)
            else:
                parent.children.insert(index + 1, ab_concat)
            return mutante
        except Exception:
            pass

    return mutante


# ---------------------------------------------------------------------------
# Generazione figli (crossover + immigrazione)
# ---------------------------------------------------------------------------

def genera_figli(popolazione, dimensione_target, permissive_crossover=False):
    """
    Genera la prole tramite crossover su AST e aggiunge immigrati casuali.

    Ritorna una lista di individui (dizionari con chiavi 'regex', 'ast', 'voto').
    """
    n_immigrati = max(2, int(dimensione_target * 0.1))
    n_figli_crossover = max(0, dimensione_target - n_immigrati)

    figli = []
    MAX_TENTATIVI = max(10, n_figli_crossover * 3)
    tentativi = 0

    genitori_validi = [ind for ind in popolazione if isinstance(ind, dict) and ind.get('ast') is not None]
    if len(genitori_validi) < 2:
        immigrati = []
        for _ in range(n_immigrati):
            r = generate_random_regex()
            immigrati.append({'regex': r, 'ast': ottieni_ast(r), 'voto': 0})
        return immigrati

    while len(figli) < n_figli_crossover and tentativi < MAX_TENTATIVI:
        tentativi += 1
        pesi = [max(0.1, ind.get('voto', 0.1)) for ind in genitori_validi]
        genitore1 = random.choices(genitori_validi, weights=pesi, k=1)[0]
        genitore2 = random.choices(genitori_validi, weights=pesi, k=1)[0]
        try:
            figlio1_ast, figlio2_ast = crossover_singolo(
                genitore1['ast'], genitore2['ast'], permissive=permissive_crossover
            )
            for ast_fig in (figlio1_ast, figlio2_ast):
                if len(figli) >= n_figli_crossover:
                    break
                regex_fig = ast_to_regex(ast_fig)
                if not regex_fig:
                    continue
                if permissive_crossover:
                    figli.append({'regex': regex_fig, 'ast': ast_fig, 'voto': 0})
                else:
                    try:
                        regex.compile(regex_fig)
                        figli.append({'regex': regex_fig, 'ast': ast_fig, 'voto': 0})
                    except Exception:
                        pass
        except Exception:
            continue

    # Riempi eventuali mancanze con copie dei migliori
    while len(figli) < n_figli_crossover and popolazione:
        figli.append(copy.deepcopy(random.choice(popolazione[:max(1, len(popolazione) // 2)])))

    # Immigrati casuali
    immigrati = []
    for _ in range(n_immigrati):
        r = generate_random_regex()
        immigrati.append({'regex': r, 'ast': ottieni_ast(r), 'voto': 0})

    return figli + immigrati


# ---------------------------------------------------------------------------
# Ciclo evolutivo principale
# ---------------------------------------------------------------------------

def evoluzione(
    dimensione_popolazione=50,
    generazioni=100,
    probabilita_mutazione=0.3,
    percentuale_elite=0.1,
    top_n_display=5,
    permissive_crossover=False,
    on_generation=None,
    cartella_buone='tracce_buone',
    cartella_cattive='tracce_cattive',
    popolazione_iniziale=None,
):
    """
    Esegue il ciclo evolutivo completo (Algorithm 1 nella tesi).

    Args:
        dimensione_popolazione : numero di individui per generazione
        generazioni            : numero massimo di generazioni
        probabilita_mutazione  : probabilità iniziale di mutazione (decade linearmente)
        percentuale_elite      : frazione della popolazione preservata per elitismo
        top_n_display          : quanti individui stampare a ogni generazione
        permissive_crossover   : se True usa crossover permissivo (senza validazione)
        on_generation          : callback opzionale chiamato dopo ogni generazione
        cartella_buone         : percorso cartella tracce positive
        cartella_cattive       : percorso cartella tracce negative
        popolazione_iniziale   : lista di regex (stringhe) per warm-start ibrido

    Returns:
        dict con chiavi 'regex', 'ast', 'voto' del miglior individuo trovato
    """
    tracce_buone, tracce_cattive = carica_tracce(cartella_buone, cartella_cattive)

    # Costruisce la popolazione iniziale
    if popolazione_iniziale is not None:
        popolazione = [
            {'regex': r, 'ast': ottieni_ast(r), 'voto': 0}
            for r in popolazione_iniziale
        ]
    else:
        popolazione = [
            {'regex': r, 'ast': ottieni_ast(r), 'voto': 0}
            for r in inizializza(dimensione_popolazione)
        ]

    migliore = None

    def stampa_migliori(pop, n=top_n_display, limit_len=120):
        for rank, ind in enumerate(pop[:n], start=1):
            regex_short = ind['regex'][:limit_len - 3] + '...' if len(ind['regex']) > limit_len else ind['regex']
            print(f"{rank:>2d}. {ind['voto']:.4f} | {regex_short}")

    for i in range(generazioni):
        popolazione = fitness(popolazione, tracce_buone, tracce_cattive)
        popolazione = selezione(popolazione, dimensione_popolazione)

        if len(popolazione) > 0 and (migliore is None or popolazione[0]['voto'] > migliore['voto']):
            migliore = copy.deepcopy(popolazione[0])

        print(f"Gen {i}")
        stampa_migliori(popolazione)

        if callable(on_generation):
            try:
                on_generation(i, popolazione)
            except Exception:
                pass

        if migliore and migliore['voto'] >= 1.0:
            break

        figli = genera_figli(popolazione, dimensione_popolazione, permissive_crossover=permissive_crossover)

        # Probabilità di mutazione con decay lineare
        if generazioni <= 1:
            current_mut_prob = probabilita_mutazione
        else:
            current_mut_prob = probabilita_mutazione * max(0.0, 1.0 - (i / float(generazioni - 1)))

        # Muta solo i figli (i genitori restano intatti)
        figli_mutati = []
        for fig in figli:
            if not isinstance(fig, dict) or not isinstance(fig.get('regex'), str):
                continue
            ast_fig = fig.get('ast') or ottieni_ast(fig['regex'])
            if random.random() < current_mut_prob and ast_fig is not None:
                ast_mutato = mutazione_singola(ast_fig, probabilita=1.0)
                regex_mutata = ast_to_regex(ast_mutato)
                if regex_mutata and isinstance(regex_mutata, str) and len(regex_mutata) > 0:
                    try:
                        regex.compile(regex_mutata)
                        figli_mutati.append({'regex': regex_mutata, 'ast': ast_mutato, 'voto': 0})
                        continue
                    except Exception:
                        pass
            figli_mutati.append(fig)

        candidati = fitness(popolazione + figli_mutati, tracce_buone, tracce_cattive)
        candidati = selezione(candidati, dimensione_popolazione)
        popolazione = candidati[:dimensione_popolazione]

    # Valutazione finale
    popolazione = fitness(popolazione, tracce_buone, tracce_cattive)
    popolazione = selezione(popolazione, dimensione_popolazione)
    if len(popolazione) > 0 and (migliore is None or popolazione[0]['voto'] > migliore['voto']):
        migliore = copy.deepcopy(popolazione[0])

    return migliore


# ---------------------------------------------------------------------------
# Entry-point CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    DIMENSIONE_POPOLAZIONE = 1000
    NUMERO_GENERAZIONI = 200
    PROBABILITA_MUTAZIONE = 0.2
    PERCENTUALE_ELITE = 0.15
    IBRIDO = '--ibrido' in sys.argv

    tracce_buone, tracce_cattive = (None, None)
    if IBRIDO:
        tracce_buone, tracce_cattive = carica_tracce()

    popolazione = inizializza(
        DIMENSIONE_POPOLAZIONE,
        ibrido=IBRIDO,
        tracce_buone=tracce_buone,
        tracce_cattive=tracce_cattive,
    )

    migliore = evoluzione(
        dimensione_popolazione=DIMENSIONE_POPOLAZIONE,
        generazioni=NUMERO_GENERAZIONI,
        probabilita_mutazione=PROBABILITA_MUTAZIONE,
        percentuale_elite=PERCENTUALE_ELITE,
        permissive_crossover=PERMISSIVE_CROSSOVER,
        popolazione_iniziale=popolazione if IBRIDO else None,
    )
    if migliore:
        print(f"\nMiglior regex trovata: {migliore['regex']}  (fitness={migliore['voto']:.4f})")
