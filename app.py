from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import uuid
import os

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), 'worldmeet.db')

# ── DB helpers ─────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS boards (
        id   TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS entries (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        board_id    TEXT NOT NULL,
        person_name TEXT NOT NULL,
        country_id  TEXT NOT NULL,
        date_from   TEXT,
        date_to     TEXT,
        FOREIGN KEY (board_id) REFERENCES boards(id)
    )''')
    conn.commit()
    conn.close()

# ── Pages ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create_board():
    name = (request.form.get('name') or 'My Travel Board').strip() or 'My Travel Board'
    board_id = str(uuid.uuid4())[:8]
    conn = get_db()
    conn.execute('INSERT INTO boards (id, name) VALUES (?, ?)', (board_id, name))
    conn.commit()
    conn.close()
    return redirect(url_for('board', board_id=board_id))

@app.route('/board/<board_id>')
def board(board_id):
    conn = get_db()
    b = conn.execute('SELECT * FROM boards WHERE id = ?', (board_id,)).fetchone()
    conn.close()
    if not b:
        return "Board not found", 404
    return render_template('board.html', board=b)

# ── API ────────────────────────────────────────────────────────────────────

@app.route('/api/board/<board_id>/entries')
def get_entries(board_id):
    conn = get_db()
    rows = conn.execute(
        'SELECT person_name, country_id, date_from, date_to FROM entries WHERE board_id = ?',
        (board_id,)
    ).fetchall()
    conn.close()

    result = {}
    for row in rows:
        cid = row['country_id']
        result.setdefault(cid, []).append({
            'person':    row['person_name'],
            'date_from': row['date_from'],
            'date_to':   row['date_to'],
        })
    return jsonify(result)

@app.route('/api/board/<board_id>/add', methods=['POST'])
def add_entry(board_id):
    data        = request.json or {}
    person_name = (data.get('person_name') or '').strip()
    country_id  = (data.get('country_id')  or '').strip()
    date_from   = data.get('date_from') or None
    date_to     = data.get('date_to')   or None

    if not person_name or not country_id:
        return jsonify({'error': 'Missing fields'}), 400

    conn     = get_db()
    existing = conn.execute(
        'SELECT id FROM entries WHERE board_id=? AND person_name=? AND country_id=?',
        (board_id, person_name, country_id)
    ).fetchone()

    if existing:
        conn.execute(
            'UPDATE entries SET date_from=?, date_to=? WHERE id=?',
            (date_from, date_to, existing['id'])
        )
    else:
        conn.execute(
            'INSERT INTO entries (board_id, person_name, country_id, date_from, date_to) VALUES (?,?,?,?,?)',
            (board_id, person_name, country_id, date_from, date_to)
        )
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/board/<board_id>/remove', methods=['POST'])
def remove_entry(board_id):
    data        = request.json or {}
    person_name = (data.get('person_name') or '').strip()
    country_id  = (data.get('country_id')  or '').strip()

    conn = get_db()
    conn.execute(
        'DELETE FROM entries WHERE board_id=? AND person_name=? AND country_id=?',
        (board_id, person_name, country_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── Run ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# Called by gunicorn (production)
init_db()
