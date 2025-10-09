from flask import Flask, render_template, request, jsonify
from solver import parallel_n_queens

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
        return jsonify({'error': 'Invalid n'}), 400
    timeout_ms = data.get('timeout_ms', 60000)
    
    result = parallel_n_queens(n, timeout_ms=timeout_ms)
    # Assicura che la risposta abbia la chiave 'solution' per il frontend
    if isinstance(result, dict) and 'solution' in result:
        return jsonify({'solution': result['solution'], 'objective': result.get('objective'), 'time_sec': result.get('time_sec')})
    return jsonify({'error': 'No solution found'})


if __name__ == '__main__':
    # dev server
    app.run(host='127.0.0.1', port=5000, debug=True)