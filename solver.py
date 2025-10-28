from z3 import *
from multiprocessing import Queue
import json 
import time
import os

def solve_n_queens(n, timeout_ms,queue=None):
    # --- Create optimizer
    opt = Optimize()

    # --- Boolean Matrix: Q[x][y][z] = True there is a queen in (x,y,z)
    Q = [[[Bool(f"Q_{x}_{y}_{z}") for z in range(n)] for y in range(n)] for x in range(n)]

    # ------| Costraints |------
        
    # XYZ 
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
    
    
    # Indipendent directons (4): (1,1,1), (1,1,-1), (1,-1,1), (1,-1,-1)
    dirs = [(1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1)]
    for x in range(n):
        for y in range(n):
            for z in range(n):
                for dx,dy,dz in dirs:
                    # make the list of subsequent cells along the positive radius
                    targets_pos = [(x + t*dx, y + t*dy, z + t*dz) for t in range(1, n) 
                                if 0 <= x + t*dx < n and 0 <= y + t*dy < n and 0 <= z + t*dz < n]
                    if targets_pos:
                        opt.add(Implies(Q[x][y][z], And([Not(Q[xx][yy][zz]) for (xx,yy,zz) in targets_pos])))
                    # make the list of cells along the opposite radius (for explicit safety)
                    targets_neg = [(x - t*dx, y - t*dy, z - t*dz) for t in range(1, n) 
                                if 0 <= x - t*dx < n and 0 <= y - t*dy < n and 0 <= z - t*dz < n]
                    if targets_neg:
                        opt.add(Implies(Q[x][y][z], And([Not(Q[xx][yy][zz]) for (xx,yy,zz) in targets_neg])))

    # ------ Objective ------
    
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
            })
    elif queue:
        queue.put({'status': str(result), 'fixed_pos': fixed_pos})


if __name__ == "__main__":
    solve_n_queens(2,10000)