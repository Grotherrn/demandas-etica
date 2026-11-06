"""Executa SQL do M3 somente em memória, sem ler configurações do aplicativo."""
from contextlib import closing
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def executar(conn):
    conn.executescript((ROOT / 'sql/schema.sql').read_text(encoding='utf-8'))
    outputs = []
    statement = ''
    for line in (ROOT / 'sql/demonstracao.sql').read_text(encoding='utf-8').splitlines(True):
        statement += line
        if sqlite3.complete_statement(statement):
            cursor = conn.execute(statement)
            if cursor.description:
                outputs.append(([col[0] for col in cursor.description], cursor.fetchall()))
            statement = ''
    if statement.strip():
        raise ValueError('SQL incompleto ao final do arquivo')
    return outputs


def main():
    with closing(sqlite3.connect(':memory:')) as conn, conn:
        print('Demonstração M3 | SQLite', sqlite3.sqlite_version)
        print('Base: :memory: | dados de teste | sem acesso ao banco de uso')
        for columns, rows in executar(conn):
            print('\n' + ' | '.join(columns))
            for row in rows:
                print(' | '.join('NULL' if v is None else str(v) for v in row))
            if not rows:
                print('(nenhuma linha)')
        totals = tuple(conn.execute('SELECT (SELECT COUNT(*) FROM demands),(SELECT COUNT(*) FROM history),(SELECT COUNT(*) FROM incidents)').fetchone())
        if totals != (2, 3, 2):
            raise RuntimeError(f'Totais inesperados: {totals}')
        print('\nConclusão: 2 demandas, 3 eventos, 2 incidentes; registro 99 removido.')


if __name__ == '__main__':
    main()
