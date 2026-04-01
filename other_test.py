import pickle

# Charger la base
with open('ukb_data.pkl', 'rb') as f:
    kb = pickle.load(f)

def extract_real_query(kb, min_triplets=3):
    for subject, facts in kb.items():
        if len(facts) >= min_triplets:
            # On prend les 3 premiers faits de ce sujet réel
            real_query = []
            for i in range(min_triplets):
                real_query.append({'p': facts[i]['p'], 'o': facts[i]['o']})
            
            print(f"Sujet source trouvé : {subject}")
            return real_query
    return None

query_complexe = extract_real_query(kb, min_triplets=7)
print("\nCopie cette requête dans ton fichier de test :")
print(query_complexe)