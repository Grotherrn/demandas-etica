"""Verifica SQL, restrições e compatibilidade em bases isoladas."""
from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path
from app import create_app, SCHEMA
from scripts.demonstrar_banco import executar


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        executar(self.db)

    def test_demo_crud_and_queries(self):
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM demands').fetchone()[0], 2)
        self.assertIsNone(self.db.execute('SELECT id FROM demands WHERE id=99').fetchone())
        self.assertEqual(self.db.execute('SELECT stage FROM demands WHERE id=1').fetchone()[0], 'Em produção')
        self.assertEqual(self.db.execute('SELECT status FROM incidents WHERE id=1').fetchone()[0], 'Encerrado')
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM history WHERE demand_id=1').fetchone()[0], 2)
        self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(), [])
        self.assertEqual(self.db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')

    def test_primary_key_unique(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute('INSERT INTO demands SELECT * FROM demands WHERE id=1')

    def test_not_null(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute('UPDATE demands SET title=NULL WHERE id=1')

    def test_foreign_key_rejects_orphan(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute('UPDATE incidents SET demand_id=999 WHERE id=1')

    def test_incident_link_optional(self):
        self.assertIsNone(self.db.execute('SELECT demand_id FROM incidents WHERE id=2').fetchone()[0])

    def test_delete_parent_blocked(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute('DELETE FROM demands WHERE id=1')
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM history WHERE demand_id=1').fetchone()[0], 2)

    def test_rollback_keeps_stage(self):
        self.db.execute('BEGIN')
        self.db.execute("UPDATE demands SET stage='Cancelado' WHERE id=1")
        self.db.rollback()
        self.assertEqual(self.db.execute('SELECT stage FROM demands WHERE id=1').fetchone()[0], 'Em produção')

    def test_reopen_existing_schema_preserves_data(self):
        with tempfile.TemporaryDirectory() as folder:
            dbfile = Path(folder) / 'dados.sqlite3'
            with closing(sqlite3.connect(dbfile)) as conn, conn:
                conn.executescript(SCHEMA.split('-- Índices')[0])
                conn.execute("INSERT INTO demands VALUES(1,'Persistir','Ref','Solicitado','2026-11-06','','2026-11-04','2026-11-04')")
            create_app(folder, {'TESTING': True})
            with closing(sqlite3.connect(dbfile)) as conn, conn:
                self.assertEqual(conn.execute('SELECT title FROM demands WHERE id=1').fetchone()[0], 'Persistir')
                indexes = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")}
                self.assertTrue({'idx_history_demand', 'idx_incidents_demand'} <= indexes)
