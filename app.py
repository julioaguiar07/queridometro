from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_super_segura_aqui'
app.config['DATABASE'] = 'database.db'

# Decorator para rotas que requerem login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor faça login primeiro', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Conexão com o banco de dados
def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Inicialização do banco de dados
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                reaction TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (receiver_id) REFERENCES users (id)
            )
        ''')
        db.commit()

# Rotas
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Preencha todos os campos', 'error')
            return redirect(url_for('register'))
        
        try:
            db = get_db()
            db.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            flash('Cadastro realizado com sucesso! Faça login', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Nome de usuário já existe', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', 
            (username,)
        ).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        
        flash('Credenciais inválidas', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta', 'info')
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    db = get_db()
    users = db.execute(
        'SELECT id, username FROM users WHERE id != ?', 
        (session['user_id'],)
    ).fetchall()
    return render_template('index.html', users=users)

@app.route('/send_reaction', methods=['POST'])
@login_required
def send_reaction():
    receiver_id = request.form['receiver_id']
    reaction = request.form['reaction']
    
    db = get_db()
    db.execute(
        'INSERT INTO reactions (sender_id, receiver_id, reaction) VALUES (?, ?, ?)',
        (session['user_id'], receiver_id, reaction)
    )
    db.commit()
    
    flash('Reação enviada com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    reactions = db.execute('''
        SELECT u.username, r.reaction, r.timestamp 
        FROM reactions r
        JOIN users u ON r.sender_id = u.id
        WHERE r.receiver_id = ?
        ORDER BY r.timestamp DESC
    ''', (session['user_id'],)).fetchall()
    
    return render_template('dashboard.html', reactions=reactions)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)