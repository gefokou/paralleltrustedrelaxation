import time
# On importe maintenant la version SMART de ton moteur
from parallel_xbs_smart import ParallelXBSSmart
from alpha_lba import oracle_alpha_lba

# Initialisation du moteur SMART de Valdini (4 processus avec mémoire partagée)
engine_smart = ParallelXBSSmart(num_workers=4)

def filter_xss_mfs(raw_results):
    """
    Identique à la version classique pour garantir que 
    la qualité des résultats (XSS/MFS) reste la même.
    """
    successes = [r['query'] for r in raw_results if r['status'] == 'SUCCESS']
    failures = [r['query'] for r in raw_results if r['status'] == 'FAIL']
    
    xss = []
    successes.sort(key=len, reverse=True)
    for s in successes:
        if not any(set(map(str, s)).issubset(set(map(str, x))) for x in xss):
            xss.append(s)
            
    mfs = []
    failures.sort(key=len)
    for f in failures:
        if not any(set(map(str, m)).issubset(set(map(str, f))) for m in mfs):
            mfs.append(f)
            
    return xss, mfs

# ---------------------------------------------------------
# 1. STRATÉGIE ASCENDANTE (SMART INJECTÉ)
# ---------------------------------------------------------
def approach_ascending_smart(query, thresholds):
    results = {}
    sorted_ts = sorted(thresholds)
    for alpha in sorted_ts:
        # Utilisation du moteur SMART avec élagage par l'échec
        raw = engine_smart.run(query, oracle_alpha_lba, alpha)
        xss, mfs = filter_xss_mfs(raw)
        results[alpha] = {'xss': xss, 'mfs': mfs}
        
        if len(xss) == 0:
            for remaining in sorted_ts[sorted_ts.index(alpha)+1:]:
                results[remaining] = {'xss': [], 'mfs': mfs}
            break
    return results

# ---------------------------------------------------------
# 2. STRATÉGIE DESCENDANTE (SMART INJECTÉ)
# ---------------------------------------------------------
def approach_descending_smart(query, thresholds):
    results = {}
    sorted_ts = sorted(thresholds, reverse=True)
    for alpha in sorted_ts:
        raw = engine_smart.run(query, oracle_alpha_lba, alpha)
        xss, mfs = filter_xss_mfs(raw)
        results[alpha] = {'xss': xss, 'mfs': mfs}
        
        if len(xss) == 1 and len(xss[0]) == len(query):
            for remaining in sorted_ts[sorted_ts.index(alpha)+1:]:
                results[remaining] = {'xss': xss, 'mfs': []}
            break
    return results

# ---------------------------------------------------------
# 3. STRATÉGIE HYBRIDE (SMART INJECTÉ)
# ---------------------------------------------------------
def approach_hybrid_smart(query, thresholds):
    results = {}
    sorted_ts = sorted(thresholds)
    
    def solve(low_idx, high_idx):
        if low_idx > high_idx:
            return
        mid = (low_idx + high_idx) // 2
        alpha = sorted_ts[mid]
        
        # Le moteur SMART va ignorer les combinaisons contenant des MFS déjà trouvés
        raw = engine_smart.run(query, oracle_alpha_lba, alpha)
        xss, mfs = filter_xss_mfs(raw)
        results[alpha] = {'xss': xss, 'mfs': mfs}
        
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