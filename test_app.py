from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path
from werkzeug.security import generate_password_hash
from app import create_app

class ApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password = 'SenhaDeTeste!2026'
        cls.hash = generate_password_hash(cls.password)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.app = create_app(self.tmp.name, {'TESTING': True, 'PASSWORD_HASH': self.hash})
        self.client = self.app.test_client()

    def token(self):
        self.client.get('/login')
        with self.client.session_transaction() as s:
            return s['csrf']

    def post(self, path, **data):
        with self.client.session_transaction() as s:
            token = s.get('csrf')
        if not token:
            token = self.token()
        return self.client.post(path, data={'csrf': token, **data}, follow_redirects=True)

    def login(self):
        self.post('/login', password=self.password)

    def demand(self, **overrides):
        vals = dict(title='Conteúdo demonstrativo', client='Clínica fictícia A', stage='Solicitado', due='2026-11-05', notes='Aguardando produção')
        vals.update(overrides)
        return self.post('/demandas/nova', **vals)

    def count(self, table):
        with closing(sqlite3.connect(self.app.config['DATABASE'])) as c, c:
            return c.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0]

    def test_01_protected_access(self):
        self.assertEqual(self.client.get('/').status_code, 302)
        self.assertEqual(self.client.get('/api/v1/demandas').status_code, 401)

    def test_02_login_logout(self):
        self.assertEqual(self.post('/login', password='errada').status_code, 401)
        self.login()
        self.assertIn('Seu fluxo'.encode(), self.client.get('/').data)
        self.post('/logout')
        self.assertEqual(self.client.get('/').status_code, 302)

    def test_03_csrf_rejected(self):
        self.login()
        self.assertEqual(self.client.post('/demandas/nova', data={'title': 'Ataque'}).status_code, 400)
        self.assertEqual(self.count('demands'), 0)

    def test_04_demand_and_persistence(self):
        self.login()
        self.assertEqual(self.demand().status_code, 200)
        self.assertEqual(self.count('demands'), 1)
        second = create_app(self.tmp.name, {'TESTING': True, 'PASSWORD_HASH': self.hash})
        with closing(sqlite3.connect(second.config['DATABASE'])) as c, c:
            self.assertEqual(c.execute('SELECT title FROM demands').fetchone()[0], 'Conteúdo demonstrativo')

    def test_05_invalid_demand(self):
        self.login()
        for vals in [dict(title=''), dict(due='2026-02-30'), dict(stage='Desconhecido'), dict(title='a'*121)]:
            self.assertEqual(self.demand(**vals).status_code, 400)
        self.assertEqual(self.count('demands'), 0)

    def test_06_history(self):
        self.login(); self.demand()
        self.post('/demandas/1', title='Conteúdo demonstrativo', client='Clínica fictícia A', stage='Em produção', due='2026-11-05', notes='Cobrança realizada')
        self.assertEqual(self.count('history'), 2)
        self.assertIn('Cobrança realizada'.encode(), self.client.get('/demandas/1').data)

    def test_07_filters(self):
        self.login(); self.demand()
        self.assertIn('Conteúdo demonstrativo'.encode(), self.client.get('/?q=demonstrativo').data)
        self.assertNotIn('Conteúdo demonstrativo'.encode(), self.client.get('/?stage=Publicado').data)

    def test_08_incident_optional_link(self):
        self.login()
        r = self.post('/incidentes/novo', title='Exemplo', category='Uso de IA', description='Situação fictícia', impact='Risco de mensagem imprecisa', action='', lesson='', status='Aberto', demand_id='')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.count('incidents'), 1)

    def test_09_incident_missing_link_rejected(self):
        self.login()
        r = self.post('/incidentes/novo', title='Exemplo', category='Uso de IA', description='Fato', impact='Impacto', status='Aberto', demand_id='999')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.count('incidents'), 0)

    def test_10_incident_closure(self):
        self.login(); self.demand()
        vals = dict(title='Exemplo', category='Respeito e dignidade', description='Caso fictício', impact='Ruído de comunicação', action='', lesson='', status='Encerrado', demand_id='1')
        self.assertEqual(self.post('/incidentes/novo', **vals).status_code, 400)
        vals.update(action='Revisar tom da mensagem', lesson='Contextualizar a cobrança')
        self.assertEqual(self.post('/incidentes/novo', **vals).status_code, 200)
        self.assertIn('Encerrado'.encode(), self.client.get('/incidentes').data)

    def test_11_xss_and_sql_parameters(self):
        self.login(); self.demand(title='<script>alert(1)</script>', client="Teste'); DROP TABLE demands;--")
        body = self.client.get('/').data
        self.assertNotIn(b'<script>', body)
        self.assertIn(b'&lt;script&gt;', body)
        self.assertEqual(self.count('demands'), 1)

    def test_12_backup(self):
        self.login(); self.demand(); self.post('/backup')
        backups = list((Path(self.tmp.name)/'backups').glob('*.sqlite3'))
        self.assertEqual(len(backups), 1)
        with closing(sqlite3.connect(backups[0])) as c, c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM demands').fetchone()[0], 1)

    def test_13_api_and_not_found(self):
        self.login(); self.demand()
        r = self.client.get('/api/v1/demandas')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json[0]['stage'], 'Solicitado')
        self.assertEqual(self.client.get('/demandas/999').status_code, 404)

    def test_14_overdue_excludes_closed(self):
        self.login(); self.demand(due='2000-01-01'); self.demand(stage='Publicado', due='2000-01-01')
        body = self.client.get('/').data.decode()
        self.assertEqual(body.count('Atrasada ·'), 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)
