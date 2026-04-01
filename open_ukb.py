import pickle

# On "décongèle" les données
print("Chargement du fichier binaire...")
with open('ukb_data.pkl', 'rb') as f:
    kb_charge = pickle.load(f)

# On vérifie que tout est là
nb_sujets = len(kb_charge)
print(f"Le fichier contient {nb_sujets} sujets.")

# On affiche un exemple au hasard
un_sujet = list(kb_charge.keys())[0]
print(f"Données pour {un_sujet} : {kb_charge[un_sujet]}")