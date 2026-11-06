"""Regressão complementar do módulo 4; usa somente bases descartáveis."""
import re
import shutil
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
import test_app as support
from app import create_app, STAGES

class QualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        support.ApplicationTests.setUpClass()

    def setUp(self):
        self.h = support.ApplicationTests(methodName='runTest')
        self.h.setUp()
        self.addCleanup(self.h.doCleanups)
        self.h.login()

    def test_q01_due_window_fixed_clock(self):
        class FixedDate(date):
            @classmethod
            def today(cls): return cls(2026, 11, 6)
        for due in ['2026-11-05','2026-11-06','2026-11-09','2026-11-10']:
            self.h.demand(due=due)
        for stage in ['Publicado','Cancelado']:
            self.h.demand(due='2026-11-05',stage=stage)
        with patch('app.date', FixedDate):
            html=self.h.client.get('/').get_data(as_text=True)
        self.assertEqual(re.findall(r'<strong>(\d+)</strong>',html),['4','1','2','0'])

    def test_q02_text_boundaries(self):
        for n,expected in [(1,200),(120,200),(121,400),(0,400)]:
            for field in ['title','client']:
                self.assertEqual(self.h.demand(**{field:'x'*n}).status_code,expected)
        self.assertEqual(self.h.demand(notes='x'*2000).status_code,200)
        self.assertEqual(self.h.demand(notes='x'*2001).status_code,400)
        self.assertEqual(self.h.demand(title='  ').status_code,400)
        self.assertEqual(self.h.count('demands'),5)

    def test_q03_incident_closure_decision_table(self):
        for action,lesson,expected in [('', '',400),('Revisar','',400),('','Confirmar contexto',400),('Revisar','Confirmar contexto',200)]:
            r=self.h.post('/incidentes/novo',title='Revisão',category='Uso de IA',description='Texto de teste',impact='Ambiguidade',status='Encerrado',demand_id='',action=action,lesson=lesson)
            self.assertEqual(r.status_code,expected)
        self.assertEqual(self.h.count('incidents'),1)

    def test_q04_invalid_incident_links(self):
        for link in ['0','-1','texto','999']:
            with self.subTest(link=link):
                r=self.h.post('/incidentes/novo',title='Revisão',category='Uso de IA',description='Texto de teste',impact='Ambiguidade',status='Aberto',demand_id=link)
                self.assertEqual(r.status_code,400)
        self.assertEqual(self.h.count('incidents'),0)

    def test_q05_backup_restore_in_isolated_folder(self):
        self.h.demand(); self.h.post('/backup')
        backup=next((Path(self.h.tmp.name)/'backups').glob('*.sqlite3'))
        with tempfile.TemporaryDirectory() as folder:
            shutil.copy2(backup,Path(folder)/'dados.sqlite3')
            app=create_app(folder,{'TESTING':True,'PASSWORD_HASH':self.h.hash})
            with sqlite3.connect(app.config['DATABASE']) as c:
                self.assertEqual(c.execute('SELECT COUNT(*) FROM demands').fetchone()[0],1)
                self.assertEqual(c.execute('SELECT COUNT(*) FROM history').fetchone()[0],1)
                self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
                self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])

    def test_q06_api_methods_and_headers(self):
        r=self.h.client.get('/api/v1/demandas')
        for k,v in [('X-Content-Type-Options','nosniff'),('X-Frame-Options','DENY'),('Cache-Control','no-store')]:
            self.assertEqual(r.headers[k],v)
        self.assertIn("default-src 'self'",r.headers['Content-Security-Policy'])
        self.assertEqual(self.h.post('/api/v1/demandas').status_code,405)
        self.h.post('/logout')
        self.assertEqual(self.h.client.get('/api/v1/demandas').status_code,401)

    def test_q07_invalid_csrf_no_write(self):
        r=self.h.client.post('/demandas/nova',data={'csrf':'invalido','title':'Teste'})
        self.assertEqual(r.status_code,400)
        self.assertEqual(self.h.count('demands'),0)

    def test_q08_history_stage_transitions(self):
        self.h.demand()
        for stage in STAGES[1:]:
            self.h.post('/demandas/1',title='Conteúdo demonstrativo',client='Clínica fictícia A',stage=stage,due='2026-11-05',notes='Aguardando produção')
        self.assertEqual(self.h.count('history'),7)
        self.h.post('/demandas/1',title='Título revisado',client='Referência',stage='Cancelado',due='2026-11-10',notes='Aguardando produção')
        self.assertEqual(self.h.count('history'),7) # título e prazo não são eventos nesta versão

    def test_q09_oversized_request(self):
        r=self.h.client.post('/demandas/nova',data={'notes':'x'*70000})
        self.assertEqual(r.status_code,413)
        self.assertEqual(self.h.count('demands'),0)

    def test_q10_atomic_write_when_history_fails(self):
        with sqlite3.connect(self.h.app.config['DATABASE']) as c:
            c.execute("CREATE TRIGGER reject_history BEFORE INSERT ON history BEGIN SELECT RAISE(ABORT,'falha de teste'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.h.demand()
        self.assertEqual(self.h.count('demands'),0)
        self.assertEqual(self.h.count('history'),0)

if __name__=='__main__': unittest.main(verbosity=2)
