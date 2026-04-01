import pickle
import random

def restructure_kb():
    with open('ukb_data.pkl', 'rb') as f:
        kb = pickle.load(f)

    new_kb = {}
    
    # On définit les règles du modèle WatDiv
    preds = {
        'follows': 'User',
        'friendOf': 'User',
        'likes': 'Product',
        'nationality': 'Country',
        'subscribes': 'Product',
        'makesPurchase': 'Purchase'
    }

    for subject, facts in kb.items():
        new_facts = []
        for f in facts:
            # On choisit un prédicat structuré
            p_name = random.choice(list(preds.keys()))
            obj_type = preds[p_name]
            
            # On génère un objet cohérent avec le type
            rand_id = random.randint(1, 20000)
            new_uri_p = f"http://db.uwaterloo.ca/~galuc/wsdbm/{p_name}"
            new_uri_o = f"http://db.uwaterloo.ca/~galuc/wsdbm/{obj_type}{rand_id}"
            
            if p_name == 'nationality': # Limitation des pays comme dans WatDiv
                new_uri_o = f"http://db.uwaterloo.ca/~galuc/wsdbm/Country{random.randint(1, 25)}"

            new_facts.append({'p': new_uri_p, 'o': new_uri_o, 'v': f['v']})
        
        new_kb[subject] = new_facts

    with open('ukb_structured.pkl', 'wb') as f:
        pickle.dump(new_kb, f)
    print("Base de données structurée selon le modèle WatDiv générée !")

restructure_kb()