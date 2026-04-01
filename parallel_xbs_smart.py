import multiprocessing
from itertools import combinations

class ParallelXBSSmart:
    def __init__(self, num_workers=4):
        self.num_workers = num_workers

    def _is_redundant(self, sub_query, shared_mfs):
        """Vérifie si la requête contient déjà un échec connu (MFS)"""
        sub_set = set(map(str, sub_query))
        for mfs in shared_mfs:
            if set(map(str, mfs)).issubset(sub_set):
                return True
        return False

    def _consumer(self, queue, results_list, shared_mfs, oracle_func, alpha):
        while True:
            sub_query = queue.get()
            if sub_query is None: break
            
            # ÉTAPE SMART : On évite le calcul si c'est un échec certain
            if self._is_redundant(sub_query, shared_mfs):
                results_list.append({'status': 'FAIL', 'query': sub_query, 'smart_skipped': True})
                continue

            if oracle_func(sub_query, alpha):
                results_list.append({'status': 'SUCCESS', 'query': sub_query})
            else:
                results_list.append({'status': 'FAIL', 'query': sub_query, 'smart_skipped': False})
                # On informe les autres de cet échec
                shared_mfs.append(sub_query)

    def run(self, query, oracle_func, alpha):
        manager = multiprocessing.Manager()
        results_list = manager.list()
        shared_mfs = manager.list() # La mémoire partagée des échecs
        queue = multiprocessing.Queue()

        processes = []
        for _ in range(self.num_workers):
            p = multiprocessing.Process(target=self._consumer, 
                                        args=(queue, results_list, shared_mfs, oracle_func, alpha))
            p.start()
            processes.append(p)

        # Génération des sous-requêtes
        n = len(query)
        for r in range(n, 0, -1):
            for combo in combinations(query, r):
                queue.put(list(combo))

        for _ in range(self.num_workers): queue.put(None)
        for p in processes: p.join()

        return list(results_list)