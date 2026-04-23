import random
import re
from pathlib import Path

try:
    import regex
except ImportError:
    print("Installing regex module...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'regex'])
    import regex

def split_top_level_alternatives(pattern):
    parts = []
    cur = []
    depth = 0
    in_char_class = False
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == '[' and not in_char_class:
            in_char_class = True
            cur.append(ch)
        elif ch == ']' and in_char_class:
            in_char_class = False
            cur.append(ch)
        elif ch == '(' and not in_char_class:
            depth += 1
            cur.append(ch)
        elif ch == ')' and not in_char_class:
            if depth > 0:
                depth -= 1
            cur.append(ch)
        elif ch == '|' and depth == 0 and not in_char_class:
            parts.append(''.join(cur))
            cur = []
        else:
            cur.append(ch)
        i += 1
    parts.append(''.join(cur))
    return parts

def sanitize_regex_pattern(pattern):
    """Lightweight fixes:
       - remove leading/trailing pipes
       - collapse consecutive pipes
       - drop empty top-level alternatives and alternatives that look like flag tokens (e.g. 'gm')
    """
    if pattern is None:
        return pattern
    orig = pattern
    p = pattern.strip()
    p = re.sub(r'^\|+', '', p)
    p = re.sub(r'\|+$', '', p)
    p = re.sub(r'\|{2,}', '|', p)
    parts = split_top_level_alternatives(p)
    FLAGS = set('gimuxs')
    clean_parts = []
    for part in parts:
        part_stripped = part.strip()
        if part_stripped == '':
            continue
        if re.fullmatch(r'[A-Za-z]+', part_stripped) and all(ch.lower() in FLAGS for ch in part_stripped):
            # looks like flag junk from buggy converter -> drop
            continue
        clean_parts.append(part)
    if not clean_parts:
        return orig
    sanitized = '|'.join(clean_parts)
    sanitized = re.sub(r'^\|+|\|+$', '', sanitized)
    sanitized = re.sub(r'\|{2,}', '|', sanitized)
    return sanitized

def safe_compile(pattern):
    """Try sanitized first, then original. Write short debug info on failure."""
    dbg_file = Path(__file__).parent / "debug_regex_compile.txt"
    sanitized = sanitize_regex_pattern(pattern)
    try:
        return regex.compile(sanitized)
    except Exception as e_s:
        # try original to capture both errors
        try:
            return regex.compile(pattern)
        except Exception as e_o:
            # best-effort debug write
            try:
                with open(dbg_file, "w", encoding="utf-8") as f:
                    f.write(f"original: {pattern!r}\n")
                    f.write(f"sanitized: {sanitized!r}\n")
                    f.write(f"error_sanitized: {e_s}\n")
                    f.write(f"error_original: {e_o}\n")
            except Exception:
                pass
            # re-raise the original error for caller
            raise

def generate_random_regex(max_length=8, max_depth=3, allow_unicode=False):
    
    def generate_atom():
        base_choices = [
            # Caratteri letterali
            random.choice('abcdefghijklmnopqrstuvwxyz'),
            random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
            random.choice('0123456789'),
            
            # Stringhe letterali (per pattern come 'ab') - AUMENTATE
            ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=2)),
            ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=2)),
            ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=2)),
            ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=2)),
            ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=3)),
            
            # Escape sequences standard
            r'\d',      # cifre
            r'\D',      # non-cifre
            r'\w',      # word characters
            r'\W',      # non-word
            r'\s',      # whitespace
            r'\S',      # non-whitespace
            
            # Character classes
            '[a-z]',
            '[A-Z]',
            '[0-9]',
            '[a-zA-Z]',
            '.',        # any character
        ]
        if allow_unicode:
            base_choices += [
                # Unicode properties (FUNZIONALITÀ REGEX!)
                r'\p{L}',   # lettere Unicode
                r'\p{Ll}',  # lettere minuscole
                r'\p{Lu}',  # lettere maiuscole
                r'\p{N}',   # numeri Unicode
                r'\p{Nd}',  # cifre decimali
                r'\p{Sc}',  # SIMBOLI DI VALUTA ← CHIAVE!
                r'\p{Sm}',  # simboli matematici
                r'\p{P}',   # punteggiatura
                r'\p{S}',   # simboli generici
            ]
        return random.choice(base_choices)
    
    def generate_quantified(depth=0):
        atom = generate_atom()
        
        if random.random() < 0.4:  # 40% di quantificatori
            quantifier = random.choice([
                '*', '+', '?',
                '{2}', '{1,3}', '{2,}',
            ])
            return atom + quantifier
        return atom
    
    def generate_group(depth=0):
        """Genera gruppo con alternazione"""
        if depth >= max_depth:
            return generate_quantified(depth)
        
        # Probabilità di alternazione
        if random.random() < 0.3:
            num_alternatives = random.randint(2, 3)
            alternatives = [generate_quantified(depth + 1) for _ in range(num_alternatives)]
            return '(' + '|'.join(alternatives) + ')'
        else:
            # Gruppo semplice
            inner = generate_quantified(depth + 1)
            return f'({inner})'
    
    def generate_element(depth=0):
        """Genera un elemento completo"""
        if depth >= max_depth:
            return generate_atom()
        
        choice = random.choice([
            'atom',           # 40%
            'atom',
            'quantified',     # 40%
            'quantified',
            'group',          # 20%
        ])
        
        if choice == 'atom':
            return generate_atom()
        elif choice == 'quantified':
            return generate_quantified(depth)
        else:  # group
            return generate_group(depth)
    
    def generate_pattern():
        """Genera il pattern completo"""
        pattern_type = random.choice([
            'simple',      # \p{Sc}
            'quantified',  # \p{Sc}+
            'alternation', # (\p{Sc}|\d)
            'concatenation', # \p{Sc}\d+
        ])
        
        if pattern_type == 'simple':
            return generate_atom()
        
        elif pattern_type == 'quantified':
            return generate_quantified()
        
        elif pattern_type == 'alternation':
            num_alt = random.randint(2, 3)
            alternatives = [generate_quantified() for _ in range(num_alt)]
            return '(' + '|'.join(alternatives) + ')'
        
        else:  # concatenation
            num_elements = random.randint(2, 3)
            elements = [generate_element() for _ in range(num_elements)]
            return ''.join(elements)
    
    # Genera con validazione GARANTITA
    MAX_ATTEMPTS = 50  # Aumentato per garantire successo
    
    for attempt in range(MAX_ATTEMPTS):
        try:
            pattern = generate_pattern()
            
            # VALIDAZIONE IMMEDIATA prima di qualsiasi modifica
            try:
                # use safe compile that tries sanitized pattern first
                safe_compile(pattern)
                return pattern
            except Exception:
                # Pattern invalido, riprova
                continue
            
        except Exception:
            # Errore durante generazione, riprova
            continue
    
    return random.choice([
        r'\p{Sc}',
        r'\p{L}',
        r'\d',
        r'\w',
        '[a-z]',
        '.',
    ])

def renumber_automaton_states(text, start_index=0):
    """
    Rinumerazione semplice per stati nominati qN (es. q1, q2, ...).
    - Scansiona il testo e, nell'ordine di prima occorrenza, mappa ogni "q<number>"
      in q{start_index}, q{start_index+1}, ...
    - Utile quando il convertitore di automi comincia da q1 invece di q0 o produce indici non contigui.
    Restituisce il testo ridenominato (non modifica altro).
    """
    if not isinstance(text, str):
        return text
    mapping = {}
    def repl(m):
        full = m.group(0)       # e.g. 'q12'
        if full not in mapping:
            mapping[full] = f"q{len(mapping) + start_index}"
        return mapping[full]
    return re.sub(r'\bq(\d+)\b', repl, text)

if __name__ == "__main__":
    print("Testing regex generator...\n")
    
    # Test without Unicode
    print("Patterns WITHOUT Unicode:")
    for i in range(5):
        pattern = generate_random_regex(max_length=8, max_depth=3, allow_unicode=False)
        print(f"  {i+1}. {pattern}")
    
    print("\nPatterns WITH Unicode:")
    for i in range(5):
        pattern = generate_random_regex(max_length=8, max_depth=3, allow_unicode=True)
        print(f"  {i+1}. {pattern}")
    
    print("\n✓ Script executed successfully!")
    
    # Example: normalizza nomi di stati se un automa parte da q1 invece di q0
    sample = "digraph { q1 -> q2; q2 -> q3; q1 [label=\"start\"]; }"
    print("\nEsempio ridenominazione automa (q1->q0):")
    print("  originale:", sample)
    print("  normalizzato:", renumber_automaton_states(sample, start_index=0))

