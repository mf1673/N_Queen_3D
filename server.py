from flask import Flask, render_template, request, jsonify
from solver import solve_n_queens
from multiprocessing import Queue
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/solve', methods=['POST'])
def solve_route():
    data = request.get_json() or {}

    try:
        n = int(data.get('n', 8))
    except Exception:
        print("[ERRORE] Valore di n non valido!")
        return jsonify({'error': 'Invalid n'}), 400

    timeout_ms = data.get('timeout_ms', 60000)

    # Crea la coda per ricevere il risultato dal solver
    q = Queue()
    start_time = time.time()
    solve_n_queens(n, timeout_ms, queue=q)

    # Attendi risultato
    try:
        result = q.get(timeout=timeout_ms / 1000)
    except Exception as e:
        return jsonify({'error': 'Timeout o nessuna soluzione ricevuta'})

    elapsed = time.time() - start_time

    # Controlla che la chiave 'solution' esista
    if isinstance(result, dict) and 'solution' in result:
        return jsonify({
            'status': 'sat',
            'solution': result['solution'],
            'objective': result.get('objective'),
            'time_sec': result.get('time_sec')
        })
    return jsonify({'error': 'No solution found'})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
