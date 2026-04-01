import pickle
from itertools import combinations

# On charge la KB une seule fois au début
def get_kb():
    # Utilise 'ukb_structured.pkl' si tu as déjà lancé le script de restructuration
    try:
        with open('ukb_structured.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        with open('ukb_data.pkl', 'rb') as f:
            return pickle.load(f)

KB = get_kb()

# --- NOUVEL ORACLE UNIVERSEL ---

def check_star_constraints(facts, constraints, alpha):
    """Vérifie si un sujet possède ces triplets avec le seuil alpha"""
    for c in constraints:
        match = False
        for f in facts:
            if f['p'] == c['p'] and f['o'] == c['o'] and f['v'] >= alpha:
                match = True
                break
        if not match: return False
    return True

def oracle_alpha_lba(sub_items, alpha):
    """
    Détermine si un sous-ensemble de la requête (items) possède au moins 1 résultat.
    Gère automatiquement les variables (v0, v1) et les jointures.
    """
    # 1. Identifier les variables présentes dans ce sous-ensemble
    vars_in_sub = set()
    for item in sub_items:
        vars_in_sub.add(item.get('var', 'v0')) # Par défaut v0 pour les Star Queries
    
    # 2. Séparer contraintes locales et jointures
    local_constraints = {v: [] for v in vars_in_sub}
    joins = []
    
    for item in sub_items:
        if 'from' in item: # C'est une jointure
            joins.append(item)
            vars_in_sub.add(item['from'])
            vars_in_sub.add(item['to'])
        else: # C'est un triplet local
            v = item.get('var', 'v0')
            local_constraints[v].append(item)

    # CAS A : Star Query (Une seule variable v0)
    if len(vars_in_sub) <= 1:
        v = list(vars_in_sub)[0] if vars_in_sub else 'v0'
        for subject, facts in KB.items():
            if check_star_constraints(facts, local_constraints[v], alpha):
                return True
        return False

    # CAS B : Join Query (v0 et v1)
    else:
        # On suppose v0 comme point d'entrée pour la recherche
        for s0, facts_s0 in KB.items():
            if check_star_constraints(facts_s0, local_constraints.get('v0', []), alpha):
                # Vérifier les liens vers un s1
                for j in joins:
                    if j['from'] == 'v0':
                        for f in facts_s0:
                            if f['p'] == j['p'] and f['v'] >= alpha:
                                s1 = f['o']
                                if s1 in KB and check_star_constraints(KB[s1], local_constraints.get('v1', []), alpha):
                                    # Vérifier si tous les autres liens (ex: v1 -> v0) sont respectés
                                    all_ok = True
                                    for other_j in joins:
                                        src = s0 if other_j['from'] == 'v0' else s1
                                        tgt = s1 if other_j['to'] == 'v1' else s0
                                        if not any(f2['p'] == other_j['p'] and f2['o'] == tgt and f2['v'] >= alpha for f2 in KB[src]):
                                            all_ok = False
                                            break
                                    if all_ok: return True
        return False

# --- MOTEUR DE RELAXATION ADAPTÉ ---

def compute_xss_mfs(query_items, alpha):
    """Calcul des alpha-XSS et alpha-MFS universel"""
    n = len(query_items)
    indices = list(range(n))
    all_subsets = []
    for r in range(n, 0, -1):
        for combo in combinations(indices, r):
            all_subsets.append(list(combo))

    successes = []
    failures = []

    for subset_indices in all_subsets:
        if any(set(subset_indices).issubset(set(s)) for s in successes):
            continue
        if any(set(f).issubset(set(subset_indices)) for f in failures):
            continue

        sub_query = [query_items[i] for i in subset_indices]
        
        # On appelle l'Oracle Universel
        if oracle_alpha_lba(sub_query, alpha):
            successes.append(subset_indices)
        else:
            failures.append(subset_indices)

    # Filtrage MFS
    alpha_mfs_indices = []
    for f in failures:
        if not any(set(smaller).issubset(set(f)) for smaller in failures if smaller != f):
            alpha_mfs_indices.append(f)

    alpha_xss = [[query_items[i] for i in s] for s in successes]
    alpha_mfs = [[query_items[i] for i in f] for f in alpha_mfs_indices]

    return alpha_xss, alpha_mfs