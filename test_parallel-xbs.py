import time
# Imports de la logique de base (Oracle et Data)
from alpha_lba import oracle_alpha_lba, KB
# Import de tes nouveaux algorithmes INJECTÉS avec le parallélisme
from algos_dellal_parallel_xbs import approach_ascending_parallel, approach_descending_parallel, approach_hybrid_parallel

# 1. DÉFINITION DE LA REQUÊTE DE TEST (Réelle - WatDiv)
# Requet 2 : 5 triplets
query_test = [
    {'var': 'v0', 'p': 'http://db.uwaterloo.ca/~galuc/wsdbm/nationality', 'o': 'http://db.uwaterloo.ca/~galuc/wsdbm/Country20'},
    {'var': 'v0', 'p': 'http://db.uwaterloo.ca/~galuc/wsdbm/friendOf', 'o': 'http://db.uwaterloo.ca/~galuc/wsdbm/User500'},
    {'var': 'v0', 'p': 'http://db.uwaterloo.ca/~galuc/wsdbm/likes', 'o': 'http://db.uwaterloo.ca/~galuc/wsdbm/Product16770'},
    {'var': 'v0', 'p': 'http://db.uwaterloo.ca/~galuc/wsdbm/subscribes', 'o': 'http://db.uwaterloo.ca/~galuc/wsdbm/SubGenre7'},
    {'var': 'v0', 'p': 'http://purl.org/ontology/mo/artist', 'o': 'http://db.uwaterloo.ca/~galuc/wsdbm/Artist10'}
]

# Liste des seuils de confiance (alpha) à tester
seuils = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

# --- FONCTION DE MESURE (Identique à ton ancienne structure) ---

def run_and_measure(name, func):
    print(f"Lancement de : {name}...")
    start_time = time.time()
    
    # Exécution de la stratégie parallèle
    res = func(query_test, seuils)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"| {name:25} | Temps : {execution_time:10.4f} s |")
    return res

# --- EXÉCUTION DU BENCHMARK ---

print("\n" + "="*50)
print("COMPARAISON DES STRATÉGIES (VERSION PARALLÈLE)")
print("="*50)

# On mesure les trois approches injectées
res_asc = run_and_measure("Ascendant", approach_ascending_parallel)
res_desc = run_and_measure("Descendant", approach_descending_parallel)
res_hyb = run_and_measure("Hybride", approach_hybrid_parallel)

print("-" * 50)

# --- DÉTAILS QUALITATIFS (ALPHA = 0.5) ---
un_seuil = 0.5
print(f"\n[DÉTAILS POUR ALPHA = {un_seuil}]")
data = res_hyb[un_seuil] # On récupère les données calculées par l'hybride
print(f" -> alpha-XSS : {len(data['xss'])}")
print(f" -> alpha-MFS : {len(data['mfs'])}")

# --- FONCTION DE RESTITUTION IDENTIQUE À DELLAL ---

def afficher_restitution(alpha, xss, mfs):
    print(f"\n{'='*60}")
    print(f"ANALYSE DE LA REQUÊTE (Seuil de confiance alpha = {alpha})")
    print(f"{'='*60}")

    # 1. EXPLICATION DE L'ÉCHEC (via les MFS)
    print("\n POURQUOI VOTRE REQUÊTE A ÉCHOUÉ :")
    if not mfs:
        print(" -> La requête n'a pas d'échec minimal identifié.")
    else:
        for i, cause in enumerate(mfs, 1):
            print(f" Cause {i} (combinaison impossible) :")
            for item in cause:
                valeur = item['o'].split('/')[-1]
                predicat = item['p'].split('/')[-1]
                print(f"   - La contrainte '{predicat}' avec la valeur '{valeur}'")

    # 2. SOLUTIONS DE SECOURS (via les XSS)
    print("\n SOLUTIONS DE RECHANGE (Résultats relaxés) :")
    if not xss:
        print(" -> Désolé, aucune sous-partie de votre requête ne donne de résultats.")
    else:
        for i, sol in enumerate(xss, 1):
            print(f" Option {i} (Ce qui fonctionne ensemble) :")
            for item in sol:
                predicat = item['p'].split('/')[-1]
                valeur = item['o'].split('/')[-1]
                print(f"   - {predicat} : {valeur}")
    print(f"{'='*60}\n")

# Appel final pour l'affichage détaillé
afficher_restitution(un_seuil, data['xss'], data['mfs'])