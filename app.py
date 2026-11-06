"""Demandas e Ética: aplicação local de usuário único."""
import argparse
import getpass
import json
import os
import secrets
import sqlite3
import webbrowser
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from threading import Timer

from flask import Flask, abort, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

STAGES = ('Solicitado', 'Em produção', 'Em revisão', 'Aguardando aprovação', 'Agendado', 'Publicado', 'Cancelado')
CATEGORIES = ('Respeito e dignidade', 'Privacidade', 'Uso de IA', 'Desinformação', 'Outro')
SCHEMA = (Path(__file__).resolve().parent / 'sql' / 'schema.sql').read_text(encoding='utf-8')

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def create_app(data_dir=None, test_config=None):
    folder = Path(data_dir or os.environ.get('FELIPE_DATA_DIR') or Path(os.getenv('LOCALAPPDATA', str(Path.home()))) / 'DemandasEtica')
    folder.mkdir(parents=True, exist_ok=True)
    config_file = folder / 'config.json'
    if not config_file.exists():
        config_file.write_text(json.dumps({'secret': secrets.token_hex(32), 'password_hash': None}), encoding='utf-8')
    config = json.loads(config_file.read_text(encoding='utf-8'))
    app = Flask(__name__)
    app.config.update(SECRET_KEY=config['secret'], PASSWORD_HASH=config['password_hash'], DATABASE=str(folder / 'dados.sqlite3'),
                      MAX_CONTENT_LENGTH=64 * 1024, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
                      PERMANENT_SESSION_LIFETIME=timedelta(hours=8), DATA_DIR=str(folder))
    if test_config:
        app.config.update(test_config)
    with sqlite3.connect(app.config['DATABASE']) as conn:
        conn.executescript(SCHEMA)

    def db():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
            g.db.execute('PRAGMA foreign_keys=ON')
        return g.db

    @app.teardown_appcontext
    def close_db(error):
        conn = g.pop('db', None)
        if conn:
            conn.close()

    @app.context_processor
    def helpers():
        if 'csrf' not in session:
            session['csrf'] = secrets.token_hex(24)
        return dict(csrf=session['csrf'], stages=STAGES, categories=CATEGORIES)

    @app.before_request
    def guard():
        if request.endpoint == 'static':
            return
        if request.method == 'POST' and not secrets.compare_digest(str(request.form.get('csrf', '')), str(session.get('csrf', '!'))):
            abort(400, 'Formulário expirado. Recarregue a página.')
        if request.endpoint != 'login' and not session.get('authenticated'):
            if request.path.startswith('/api/'):
                abort(401)
            return redirect(url_for('login'))

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
        response.headers['Cache-Control'] = 'no-store'
        return response

    def value(key, limit, required=True):
        text = request.form.get(key, '').strip()
        if (required and not text) or len(text) > limit:
            raise ValueError(f'Campo {key}: informe entre {1 if required else 0} e {limit} caracteres.')
        return text

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if not app.config['PASSWORD_HASH']:
            return render_template('login.html', setup=True), 503
        if request.method == 'POST':
            blocked_until = session.get('blocked_until', 0)
            current = datetime.now(timezone.utc).timestamp()
            if current < blocked_until:
                return render_template('login.html', error='Aguarde um minuto para tentar novamente.'), 429
            if check_password_hash(app.config['PASSWORD_HASH'], request.form.get('password', '')):
                session.clear()
                session['authenticated'] = True
                session.permanent = True
                return redirect(url_for('dashboard'))
            session['attempts'] = session.get('attempts', 0) + 1
            if session['attempts'] >= 5:
                session['blocked_until'] = current + 60
                session['attempts'] = 0
            return render_template('login.html', error='Senha incorreta.'), 401
        return render_template('login.html')

    @app.post('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.get('/')
    def dashboard():
        stage = request.args.get('stage', '')
        q = request.args.get('q', '').strip()[:120]
        rows = db().execute('SELECT * FROM demands ORDER BY due, id').fetchall()
        today = date.today()
        def pending(r):
            return r['stage'] not in ('Publicado', 'Cancelado')
        overdue = sum(pending(r) and r['due'] < today.isoformat() for r in rows)
        upcoming = sum(pending(r) and today.isoformat() <= r['due'] <= (today + timedelta(days=3)).isoformat() for r in rows)
        active = sum(pending(r) for r in rows)
        visible = [r for r in rows if (not stage or r['stage'] == stage) and (not q or q.casefold() in (r['title'] + ' ' + r['client']).casefold())]
        incidents = db().execute('SELECT COUNT(*) FROM incidents WHERE status=?', ('Aberto',)).fetchone()[0]
        return render_template('dashboard.html', rows=visible, overdue=overdue, upcoming=upcoming, active=active, incident_count=incidents, today=today.isoformat(), q=q, selected=stage)

    @app.route('/demandas/nova', methods=['GET', 'POST'])
    @app.route('/demandas/<int:item_id>', methods=['GET', 'POST'])
    def demand(item_id=None):
        item = db().execute('SELECT * FROM demands WHERE id=?', (item_id,)).fetchone() if item_id else None
        if item_id and not item:
            abort(404)
        error = None
        if request.method == 'POST':
            try:
                title, client = value('title', 120), value('client', 120)
                stage, due, notes = value('stage', 40), value('due', 10), value('notes', 2000, False)
                if stage not in STAGES:
                    raise ValueError('Etapa inválida.')
                if date.fromisoformat(due).isoformat() != due:
                    raise ValueError('Data inválida.')
                stamp = now()
                with db():
                    if item:
                        db().execute('UPDATE demands SET title=?,client=?,stage=?,due=?,notes=?,updated_at=? WHERE id=?', (title, client, stage, due, notes, stamp, item_id))
                    else:
                        item_id = db().execute('INSERT INTO demands(title,client,stage,due,notes,created_at,updated_at) VALUES(?,?,?,?,?,?,?)', (title, client, stage, due, notes, stamp, stamp)).lastrowid
                    if not item or item['stage'] != stage or item['notes'] != notes:
                        db().execute('INSERT INTO history(demand_id,previous_stage,new_stage,note,happened_at) VALUES(?,?,?,?,?)', (item_id, item['stage'] if item else None, stage, notes, stamp))
                flash('Demanda salva.')
                return redirect(url_for('demand', item_id=item_id))
            except (ValueError, TypeError):
                error = 'Confira título, cliente, etapa e data válida. Respeite os limites de texto.'
        history = db().execute('SELECT * FROM history WHERE demand_id=? ORDER BY id DESC', (item_id,)).fetchall() if item_id else []
        return render_template('demand.html', item=item, history=history, error=error, form=request.form if request.method == 'POST' else dict(item) if item else {}), 400 if error else 200

    @app.get('/incidentes')
    def incidents():
        rows = db().execute('SELECT incidents.*,demands.title AS demand_title FROM incidents LEFT JOIN demands ON demands.id=incidents.demand_id ORDER BY incidents.id DESC').fetchall()
        return render_template('incidents.html', rows=rows)

    @app.route('/incidentes/novo', methods=['GET', 'POST'])
    @app.route('/incidentes/<int:item_id>', methods=['GET', 'POST'])
    def incident(item_id=None):
        item = db().execute('SELECT * FROM incidents WHERE id=?', (item_id,)).fetchone() if item_id else None
        if item_id and not item:
            abort(404)
        error = None
        if request.method == 'POST':
            try:
                title, category = value('title', 120), value('category', 40)
                description, impact = value('description', 2000), value('impact', 2000)
                action, lesson, status = value('action', 2000, False), value('lesson', 2000, False), value('status', 20)
                if category not in CATEGORIES or status not in ('Aberto', 'Encerrado'):
                    raise ValueError('Categoria ou situação inválida.')
                demand_id = int(request.form['demand_id']) if request.form.get('demand_id') else None
                if demand_id is not None and not db().execute('SELECT id FROM demands WHERE id=?', (demand_id,)).fetchone():
                    raise ValueError('Demanda inexistente.')
                if status == 'Encerrado' and (not action or not lesson):
                    raise ValueError('Para encerrar, informe encaminhamento e aprendizado.')
                stamp = now()
                vals = (demand_id, title, category, description, impact, action, lesson, status)
                with db():
                    if item:
                        db().execute('UPDATE incidents SET demand_id=?,title=?,category=?,description=?,impact=?,action=?,lesson=?,status=?,updated_at=? WHERE id=?', vals + (stamp, item_id))
                    else:
                        item_id = db().execute('INSERT INTO incidents(demand_id,title,category,description,impact,action,lesson,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)', vals + (stamp, stamp)).lastrowid
                flash('Registro de ética salvo.')
                return redirect(url_for('incident', item_id=item_id))
            except (ValueError, TypeError):
                error = 'Confira os campos obrigatórios e o vínculo. Para encerrar, preencha encaminhamento e aprendizado.'
        demands = db().execute('SELECT id,title FROM demands ORDER BY title').fetchall()
        return render_template('incident.html', item=item, demands=demands, error=error, form=request.form if request.method == 'POST' else dict(item) if item else {}), 400 if error else 200

    @app.get('/api/v1/demandas')
    def api_demands():
        return jsonify([dict(r) for r in db().execute('SELECT * FROM demands ORDER BY id')])

    @app.post('/backup')
    def backup():
        backup_dir = folder / 'backups'
        backup_dir.mkdir(exist_ok=True)
        name = 'dados-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.sqlite3'
        with sqlite3.connect(backup_dir / name) as dest:
            db().backup(dest)
        flash('Cópia de segurança criada na pasta backups dos dados locais.')
        return redirect(url_for('dashboard'))

    return app

def configure(data_dir):
    app = create_app(data_dir)
    file = Path(app.config['DATA_DIR']) / 'config.json'
    cfg = json.loads(file.read_text(encoding='utf-8'))
    password = getpass.getpass('Crie a senha de acesso (mínimo 10 caracteres): ')
    if len(password) < 10 or password != getpass.getpass('Repita a senha: '):
        raise SystemExit('Senha curta ou confirmação diferente. Tente novamente.')
    cfg['password_hash'] = generate_password_hash(password)
    cfg['secret'] = secrets.token_hex(32)
    file.write_text(json.dumps(cfg), encoding='utf-8')
    print('Senha configurada. Dados em:', app.config['DATA_DIR'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--configure', action='store_true')
    parser.add_argument('--data-dir')
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    if args.configure:
        configure(args.data_dir)
    else:
        from waitress import serve
        app = create_app(args.data_dir)
        if not app.config['PASSWORD_HASH']:
            configure(args.data_dir)
            app = create_app(args.data_dir)
        if not args.no_browser:
            Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:8765')).start()
        print('Demandas e Ética: http://127.0.0.1:8765 | Ctrl+C para parar')
        serve(app, host='127.0.0.1', port=8765)
