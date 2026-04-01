import random

def generate_watdiv_like(filename, num_triplets=100000):
    # Prédicats réels du benchmark WatDiv (wsdbm)
    preds = [
        "http://db.uwaterloo.ca/~galuc/wsdbm/follows",
        "http://db.uwaterloo.ca/~galuc/wsdbm/friendOf",
        "http://db.uwaterloo.ca/~galuc/wsdbm/likes",
        "http://db.uwaterloo.ca/~galuc/wsdbm/makesPurchase",
        "http://db.uwaterloo.ca/~galuc/wsdbm/purchaseFor",
        "http://db.uwaterloo.ca/~galuc/wsdbm/subscribes",
        "http://schema.org/nationality"
    ]
    
    with open(filename, 'w') as f:
        for i in range(num_triplets):
            # Simulation d'utilisateurs et d'objets (Loi de puissance)
            s = f"http://db.uwaterloo.ca/~galuc/wsdbm/User{random.randint(0, num_triplets//10)}"
            p = random.choice(preds)
            o = f"http://db.uwaterloo.ca/~galuc/wsdbm/Product{random.randint(0, num_triplets//5)}"
            
            # Format N-Triples : <S> <P> <O> .
            f.write(f"<{s}> <{p}> <{o}> .\n")
    print(f"Fichier {filename} généré avec {num_triplets} triplets.")

# On génère 100k triplets pour commencer
generate_watdiv_like("watdiv_100k.nt", 100000)
