from lark import Tree, Token

def _tokval(node):
    # return token's raw value for Token objects; else string conversion
    if isinstance(node, Token):
        return node.value
    return str(node)

def ast_to_regex(tree):
    if tree is None:
        return ""
    
    if isinstance(tree, Token):
        # return the token's value (avoid str(Token) which can include type)
        return tree.value
    
    if not isinstance(tree, Tree):
        return ""
    
    # Gestione dei vari nodi dell'AST
    
    if tree.data == "start":
        return ast_to_regex(tree.children[0]) if tree.children else ""
    
    elif tree.data == "alternation":
        # Unisce con '|' tutte le alternative
        alternatives = [ast_to_regex(child) for child in tree.children]
        alternatives = [alt for alt in alternatives if alt]  # Rimuove vuoti
        if len(alternatives) > 1:
            return '|'.join(alternatives)
        elif len(alternatives) == 1:
            return alternatives[0]
        return ""
    
    elif tree.data == "concatenation":
        # Concatena tutti gli elementi
        parts = [ast_to_regex(child) for child in tree.children]
        return ''.join(parts)
    
    elif tree.data == "repetition":
        # Elemento base + eventuale quantificatore
        if not tree.children:
            return ""
        base = ast_to_regex(tree.children[0])
        if len(tree.children) > 1:
            quantifier = ast_to_regex(tree.children[1])
            return base + quantifier
        return base
    
    elif tree.data == "quantifier":
        # *, +, ?, o range quantifier
        if tree.children:
            child = tree.children[0]
            # Se è un Tree (range_quantifier), processalo ricorsivamente
            if isinstance(child, Tree):
                return ast_to_regex(child)
            # Altrimenti è un Token (*, +, ?)
            return _tokval(child)
        return ""
    
    elif tree.data == "range_quantifier" or tree.data == "range_exact" or tree.data == "range_min" or tree.data == "range_minmax":
        # {n}, {n,}, {n,m}
        if tree.data == "range_exact":
            # {n}
            return f"{{{_tokval(tree.children[0])}}}"
        elif tree.data == "range_min":
            # {n,}
            return f"{{{_tokval(tree.children[0])},}}"
        elif tree.data == "range_minmax":
            # {n,m}
            return f"{{{_tokval(tree.children[0])},{_tokval(tree.children[1])}}}"
        else:
            # Fallback per il nome generico range_quantifier (legacy)
            numbers = [child for child in tree.children if isinstance(child, Token) and child.type == 'NUMBER']
            if len(numbers) == 1:
                return f"{{{numbers[0].value}}}"
            elif len(numbers) == 2:
                return f"{{{numbers[0].value},{numbers[1].value}}}"
        return ""
    
    elif tree.data == "atom":
        # Atom contiene un singolo figlio (char, group, char_class, etc.)
        return ast_to_regex(tree.children[0]) if tree.children else ""
    
    elif tree.data == "char":
        # Carattere singolo
        return ast_to_regex(tree.children[0]) if tree.children else ""
    
    elif tree.data == "char_class":
        # [abc], [a-z], [^abc]
        if not tree.children:
            return ""
        
        # Verifica se è negata
        content = []
        is_negated = False
        
        for child in tree.children:
            if isinstance(child, Token) and child.type == "NEGATION":
                is_negated = True
            else:
                content.append(ast_to_regex(child))
        
        content_str = ''.join(content)
        
        if is_negated:
            return f"[^{content_str}]"
        return f"[{content_str}]"
    
    elif tree.data == "char_class_content":
        # Contenuto di una char class
        return ''.join(ast_to_regex(child) for child in tree.children)
    
    elif tree.data == "char_range":
        # a-z, 0-9
        if len(tree.children) >= 2:
            start = ast_to_regex(tree.children[0])
            end = ast_to_regex(tree.children[1])
            return f"{start}-{end}"
        return ""
    
    elif tree.data == "escape_sequence":
        # \d, \w, \s, \D, \W, \S, \b, \B, \p{...}, \P{...}, o escape di caratteri speciali
        if tree.children:
            child = tree.children[0]
            # Se è un nodo unicode_property, gestiscilo ricorsivamente
            if isinstance(child, Tree):
                return ast_to_regex(child)
            # Altrimenti è un token normale
            escaped = _tokval(child)
            # Mantieni il backslash
            if not escaped.startswith('\\'):
                return f"\\{escaped}"
            return escaped
        return ""
    
    elif tree.data == "unicode_property":
        # \p{Sc}, \P{Lu}, etc.
        if tree.children and len(tree.children) > 0:
            # Il primo token dovrebbe essere PROPERTY_NAME
            property_name = _tokval(tree.children[0])
            return f"\\p{{{property_name}}}"
        # Se incompleto, ritorna stringa vuota per invalidare
        return ""
    
    elif tree.data == "anchor":
        # ^ o $
        return _tokval(tree.children[0]) if tree.children else ""
    
    elif tree.data == "wildcard":
        # . (any character)
        return "."
    
    elif tree.data == "group":
        # (...)
        if not tree.children:
            return "()"
        content = ast_to_regex(tree.children[0])
        return f"({content})"
    
    # Fallback per nodi sconosciuti
    else:
        # Prova a processare ricorsivamente i figli
        return ''.join(ast_to_regex(child) for child in tree.children)