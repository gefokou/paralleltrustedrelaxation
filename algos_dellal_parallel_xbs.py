import time
from parallel_xbs import ParallelXBS
from alpha_lba import oracle_alpha_lba

# Initialisation du moteur Valdini avec 4 processus ouvriers
engine = ParallelXBS(num_workers=4)

def filter_xss_mfs(raw_results):
    """
    Analyse les résultats bruts renvoyés par les processus parallèles 
    pour extraire les ensembles XSS et MFS selon la logique de Dellal.
    """
    successes = [r['query'] for r in raw_results if r['status'] == 'SUCCESS']
    failures = [r['query'] for r in raw_results if r['status'] == 'FAIL']
    
    # Extraction des XSS (Succès maximaux : aucun succès n'est inclus dans un autre)
    xss = []
    successes.sort(key=len, reverse=True)
    for s in successes:
        if not any(set(map(str, s)).issubset(set(map(str, x))) for x in xss):
            xss.append(s)
            
    # Extraction des MFS (Échecs minimaux : aucun échec n'inclut un autre échec plus petit)
    mfs = []
    failures.sort(key=len)
    for f in failures:
        if not any(set(map(str, m)).issubset(set(map(str, f))) for m in mfs):
            mfs.append(f)
            
    return xss, mfs

# ---------------------------------------------------------
# 1. STRATÉGIE ASCENDANTE (PARALLEL XBS INJECTÉ)
# ---------------------------------------------------------
def approach_ascending_parallel(query, thresholds):
    results = {}
    sorted_ts = sorted(thresholds)
    for alpha in sorted_ts:
        # Appel au moteur parallèle pour explorer l'espace des sous-requêtes
        raw = engine.run(query, oracle_alpha_lba, alpha)
        xss, mfs = filter_xss_mfs(raw)
        results[alpha] = {'xss': xss, 'mfs': mfs}
        
        # Élagage Dellal : si plus aucun succès à ce alpha, inutile de tester plus haut
        if len(xss) == 0:
            for remaining in sorted_ts[sorted_ts.index(alpha)+1:]:
                results[remaining] = {'xss': [], 'mfs': mfs}
            break
    return results

# ---------------------------------------------------------
# 2. STRATÉGIE DESCENDANTE (PARALLEL XBS INJECTÉ)
# ---------------------------------------------------------
def approach_descending_parallel(query, thresholds):
    results = {}
    sorted_ts = sorted(thresholds, reverse=True)
    for alpha in sorted_ts:
        # Appel au moteur parallèle
        raw = engine.run(query, oracle_alpha_lba, alpha)
        xss, mfs = filter_xss_mfs(raw)
        results[alpha] = {'xss': xss, 'mfs': mfs}
        
        # Élagage Dellal : si succès total à ce alpha, inutile de tester plus bas
        if len(xss) == 1 and len(xss[0]) == len(query):
            for remaining in sorted_ts[sorted_ts.index(alpha)+1:]:
                results[remaining] = {'xss': xss, 'mfs': []}
            break
    return results

# ---------------------------------------------------------
# 3. STRATÉGIE HYBRIDE (PARALLEL XBS INJECTÉ)
# ---------------------------------------------------------
def approach_hybrid_parallel(query, thresholds):
    results = {}
    sorted_ts = sorted(thresholds)
    
    def solve(low_idx, high_idx):
        if low_idx > high_idx:
            return
        mid = (low_idx + high_idx) // 2
        alpha = sorted_ts[mid]
        
        # Appel au moteur parallèle
        raw = engine.run(query, oracle_alpha_lba, alpha)
        xss, mfs = filter_xss_mfs(raw)
        results[alpha] = {'xss': xss, 'mfs': mfs}
        
        # Logique d'élagage hybride (Propriété de monotonie de Dellal)
        if len(xss) == 0:
            for i in range(mid + 1, high_idx + 1):
                results[sorted_ts[i]] = {'xss': [], 'mfs': mfs}
            solve(low_idx, mid - 1)
        elif len(xss) == 1 and len(xss[0]) == len(query):
            for i in range(low_idx, mid):
                results[sorted_ts[i]] = {'xss': xss, 'mfs': []}
            solve(mid + 1, high_idx)
        else:
            solve(low_idx, mid - 1)
            solve(mid + 1, high_idx)

    solve(0, len(sorted_ts) - 1)
    return results