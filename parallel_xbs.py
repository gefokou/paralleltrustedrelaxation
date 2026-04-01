import multiprocessing
from itertools import combinations

class ParallelXBS:
    def __init__(self, num_workers=4):
        self.num_workers = num_workers

    def _consumer(self, queue, results_list, oracle_func, alpha):
        """Chaque ouvrier teste les sous-requêtes reçues via la queue"""
        while True:
            sub_query = queue.get()
            if sub_query is None: break
            
            # On utilise l'oracle de Dellal (alpha-LBA)
            if oracle_func(sub_query, alpha):
                results_list.append({'status': 'SUCCESS', 'query': sub_query})
            else:
                results_list.append({'status': 'FAIL', 'query': sub_query})

    def run(self, query, oracle_func, alpha):
        manager = multiprocessing.Manager()
        results_list = manager.list()
        queue = multiprocessing.Queue()

        # Démarrage des ouvriers
        processes = []
        for _ in range(self.num_workers):
            p = multiprocessing.Process(target=self._consumer, 
                                        args=(queue, results_list, oracle_func, alpha))
            p.start()
            processes.append(p)

        # Le Producteur génère toutes les sous-requêtes (Relaxation)
        n = len(query)
        for r in range(n, 0, -1):
            for combo in combinations(query, r):
                queue.put(list(combo))

        # Arrêt des ouvriers
        for _ in range(self.num_workers): queue.put(None)
        for p in processes: p.join()

        return list(results_list)