import pickle

# Ouvrir le fichier
with open("ukb_structured.pkl", "rb") as f:
    data = pickle.load(f)

# Vérifier ce que contient
print(type(data))  # pour voir le type de l'objet
print(data)        # afficher (attention si c'est très gros)
