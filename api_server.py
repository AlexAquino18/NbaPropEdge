from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from pathlib import Path

app = Flask(__name__)
CORS(app)

DB_PATH = Path(__file__).parent / 'odds_history.db'

@app.route('/api/odds-history', methods=['GET'])
def get_odds_history():
    player_name = request.args.get('player_name')
    stat_type = request.args.get('stat_type')
    
    if not player_name or not stat_type:
        return jsonify({'error': 'player_name and stat_type are required'}), 400
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT player_name, stat_type, draftkings_line, draftkings_over_odds, 
                   draftkings_under_odds, fanduel_line, fanduel_over_odds, 
                   fanduel_under_odds, recorded_at
            FROM odds_history
            WHERE player_name = ? AND stat_type = ?
            ORDER BY recorded_at ASC
        ''', (player_name, stat_type))
        
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'player_name': row[0],
                'stat_type': row[1],
                'draftkings_line': row[2],
                'draftkings_over_odds': row[3],
                'draftkings_under_odds': row[4],
                'fanduel_line': row[5],
                'fanduel_over_odds': row[6],
                'fanduel_under_odds': row[7],
                'recorded_at': row[8]
            })
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'database': str(DB_PATH)})

if __name__ == '__main__':
    print('Starting Odds History API Server')
    print(f'Database: {DB_PATH}')
    print('API running on http://localhost:5000')
    app.run(debug=True, port=5000)
