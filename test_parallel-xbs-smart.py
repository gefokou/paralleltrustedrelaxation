import time
# Imports de la logique de base (Oracle et Data)
from alpha_lba import oracle_alpha_lba, KB
# Import des algorithmes SMART (Coopératifs)
from algos_dellal_parallel_xbs_smart import (
    approach_ascending_smart, 
    approach_descending_smart, 
    approach_hybrid_smart
)

# 1. DÉFINITION DE LA REQUÊTE DE TEST (Réelle - 7 Triplets WatDiv)
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

# --- FONCTION DE MESURE ---

def run_and_measure(name, func):
    print(f"Lancement de : {name}...")
    start_time = time.time()
    
    # Exécution de la stratégie intelligente (mémoire partagée)
    res = func(query_test, seuils)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"| {name:25} | Temps : {execution_time:10.4f} s |")
    return res

# --- EXÉCUTION DU BENCHMARK SMART ---

print("\n" + "="*50)
print("COMPARAISON DES STRATÉGIES (VERSION PARALLÈLE SMART)")
print("="*50)

# On mesure les trois approches avec injection GenFilter
res_asc = run_and_measure("Ascendant Smart", approach_ascending_smart)
res_desc = run_and_measure("Descendant Smart", approach_descending_smart)
res_hyb = run_and_measure("Hybride Smart", approach_hybrid_smart)

print("-" * 50)

# --- DÉTAILS QUALITATIFS (ALPHA = 0.5) ---
un_seuil = 0.5
print(f"\n[DÉTAILS POUR ALPHA = {un_seuil}]")
data = res_hyb[un_seuil] 
print(f" -> alpha-XSS : {len(data['xss'])}")
print(f" -> alpha-MFS : {len(data['mfs'])}")

# --- FONCTION DE RESTITUTION ---

def afficher_restitution(alpha, xss, mfs):
    print(f"\n{'='*60}")
    print(f"ANALYSE DE LA REQUÊTE (Seuil de confiance alpha = {alpha})")
    print(f"{'='*60}")

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

# Affichage final
afficher_restitution(un_seuil, data['xss'], data['mfs'])