from z3 import *
from multiprocessing import Process, Queue, cpu_count
import json 
import time
import os

def solve_n_queens(n, timeout_ms, fixed_pos=None, queue=None):
    # --- Creazione optimizer
    opt = Optimize()

    # --- Variabili booleane: Q[x][y][z] = True se c’è una regina in (x,y,z)
    Q = [[[Bool(f"Q_{x}_{y}_{z}") for z in range(n)] for y in range(n)] for x in range(n)]

    # ============================
    #           Vincoli
    # ============================  
    # Al Max una per Asse XYZ
    [opt.add(AtMost(*[Q[x][y][z] for x in range(n)], 1)) for y in range(n) for z in range(n)]
    [opt.add(AtMost(*[Q[x][y][z] for y in range(n)], 1)) for x in range(n) for z in range(n)]
    [opt.add(AtMost(*[Q[x][y][z] for z in range(n)], 1)) for x in range(n) for y in range(n)]

    # YX -YX
    opt.add(
        [AtMost(*[Q[x][y][z] for x in range(n) for y in range(n) if x - y == d], 1)
        for z in range(n) for d in range(-(n-1), n)] +
        [AtMost(*[Q[x][y][z] for x in range(n) for y in range(n) if x + y == s], 1)
        for z in range(n) for s in range(2*n - 1)])
    # ZX -ZX
    opt.add(
        [AtMost(*[Q[x][y][z] for x in range(n) for z in range(n) if x - z == d], 1)
        for y in range(n) for d in range(-(n-1), n)] +
        [AtMost(*[Q[x][y][z] for x in range(n) for z in range(n) if x + z == s], 1)
        for y in range(n) for s in range(2*n - 1)])
    # ZY -ZY
    opt.add(
        [AtMost(*[Q[x][y][z] for y in range(n) for z in range(n) if y - z == d], 1)
        for x in range(n) for d in range(-(n-1), n)] +
        [AtMost(*[Q[x][y][z] for y in range(n) for z in range(n) if y + z == s], 1)
        for x in range(n) for s in range(2*n - 1)])
    

    # XYZ   -X-Y-Z
    opt.add([AtMost(*[Q[x][y][z]for x in range(n)for y in range(n)for z in range(n)if x+y+z==d], 1)for d in range(0, 3*n - 3)])
    
    # X-YZ  -XYZ
    opt.add([AtMost(*[Q[x][y][z]for x in range(n)for y in range(n)for z in range(n)if x-y+z==d], 1)for d in range(-(n-1), 2*n - 2)])
    
    # XY-Z  -X-YZ
    opt.add([AtMost(*[Q[x][y][z]for x in range(n)for y in range(n)for z in range(n)if x+y-z==d], 1)for d in range(-(n - 1), 2 * n - 1)])

    # -XYZ  X-Y-Z
    opt.add([AtMost(*[Q[x][y][z]for x in range(n)for y in range(n)for z in range(n)if y-x+z==d], 1)for d in range(-(n - 1), 2 * n - 1)])



    # =====================================
    #     Vincolo specifico del processo
    # =====================================
    # serve a differenziare la ricerca
    if fixed_pos:
        x0, y0, z0 = fixed_pos
        opt.add(Q[x0][y0][z0])

    # ====================================
    #              Obiettivo
    # ====================================
    start = time.time()

    try:
        opt.set('timeout', int(timeout_ms))
    except Exception:
        pass

    objective = Sum([If(Q[x][y][z], 1, 0) for x in range(n) for y in range(n) for z in range(n)])
    opt.maximize(objective)

    # ---| Check & Model Evaluate
    result = opt.check()

    if result == sat:
        m = opt.model()
        solution = [[[1 if m.evaluate(Q[x][y][z]) else 0 for z in range(n)]
                     for y in range(n)] for x in range(n)]
        try:
            obj_val = m.evaluate(objective).as_long()
        except Exception:
            obj_val = sum(solution[x][y][z] for x in range(n)
                          for y in range(n) for z in range(n))
        elapsed = time.time() - start

        if queue:
            queue.put({
                'status': 'sat',
                'solution': solution,
                'objective': int(obj_val),
                'time_sec': elapsed,
                'fixed_pos': fixed_pos
            })
    elif queue:
        queue.put({'status': str(result), 'fixed_pos': fixed_pos})


def parallel_n_queens(n, timeout_ms):
    num_procs = min(cpu_count(), 12)
    #print(f"🔹 Avvio {num_procs} processi paralleli\n")

    from multiprocessing import Manager
    with Manager() as manager:
        queue = manager.Queue()
        procs = []

        positions = [(0, i % n, (i * 3) % n) for i in range(num_procs)]

        for pos in positions:
            p = Process(target=solve_n_queens, args=(n, timeout_ms, pos, queue))
            p.start()
            procs.append(p)

        # Aspetta il primo risultato
        result = queue.get()
        #print(f"\n🧩 Primo risultato da processo con pos {result.get('fixed_pos')}: {result['status']}")

        # Termina gli altri
        for p in procs:
            p.terminate()

        if result['status'] == 'sat':
            sol = result['solution']
            print(f"\n=== Soluzione trovata per N={n} ===")
            for x in range(n):
                print(f"\nLayer X={x}:")
                for y in range(n):
                    print(' '.join(str(sol[x][y][z]) for z in range(n)))
            print(f"\nValore obiettivo: {result['objective']}")
            print(f"Tempo impiegato: {result['time_sec']:.2f} sec\n")

            
            # alla fine di parallel_n_queens:
            with open("solution.json", "w") as f:
                json.dump(result, f)


