"""Executa jornadas em Chromium com servidor e dados temporários, sem dados reais.
Requer Playwright: python -m pip install playwright; python -m playwright install chromium.
Use --app-python para indicar um Python com as dependências de requirements.txt.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
PASSWORD='TesteInterface!2026'

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--app-python',default=sys.executable)
    cli.add_argument('--output',default=str(ROOT/'evidencias'/'m4'/'interface'))
    args=cli.parse_args()
    out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
    results=[]
    with tempfile.TemporaryDirectory(prefix='demandas-interface-') as temp:
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        runner="from app import create_app; from werkzeug.security import generate_password_hash; from waitress import serve; import sys; a=create_app(sys.argv[1],{'PASSWORD_HASH':generate_password_hash(sys.argv[3])}); serve(a,host='127.0.0.1',port=int(sys.argv[2]))"
        log=open(out/'servidor.txt','w')
        server=subprocess.Popen([args.app_python,'-c',runner,temp,str(port),PASSWORD],cwd=ROOT,stdout=log,stderr=log)
        base=f'http://127.0.0.1:{port}'
        try:
            for _ in range(100):
                try:
                    urllib.request.urlopen(base+'/login',timeout=1);break
                except Exception:
                    if server.poll() is not None:raise RuntimeError('Servidor não iniciou')
                    time.sleep(.1)
            else:raise RuntimeError('Tempo excedido ao iniciar servidor')
            with sync_playwright() as pw:
                opts={'headless':True}
                executable=shutil.which('chromium')
                if executable:opts['executable_path']=executable
                browser=pw.chromium.launch(**opts)
                info={'browser':browser.version,'platform':sys.platform,'date':time.strftime('%Y-%m-%d'),'results':results}
                ctx=browser.new_context(viewport={'width':1440,'height':1000},locale='pt-BR')
                page=ctx.new_page()
                errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                def login(p):
                    p.goto(base+'/login');p.get_by_label('Senha pessoal').fill(PASSWORD);p.get_by_role('button',name='Entrar',exact=True).click()
                    p.wait_for_url(base+'/')
                def check(id,fn):
                    try:fn();results.append({'id':id,'status':'aprovado'})
                    except Exception as e:results.append({'id':id,'status':'falhou','detail':str(e)[:500]})
                login(page)
                def empty():
                    n=page.locator('tbody tr:visible').count()
                    page.screenshot(path=str(out/'painel_vazio.png'),full_page=True)
                    assert n==1,f'Esperada uma mensagem de lista vazia; encontradas {n}'
                check('B01_lista_vazia',empty)
                def demand():
                    page.get_by_role('link',name='+ Nova demanda').click()
                    page.get_by_label('Título',exact=True).fill('Revisar texto informativo')
                    page.get_by_label('Cliente de referência').fill('Referência de teste A')
                    page.get_by_label('Etapa',exact=True).select_option('Em produção')
                    page.get_by_label('Prazo',exact=True).fill('2026-11-15')
                    page.get_by_label('Observações e registro da atuação').fill('Conferir clareza e contexto antes da revisão.')
                    page.get_by_role('button',name='Salvar demanda').click()
                    for stage in ['Em revisão','Aguardando aprovação']:
                        page.get_by_label('Etapa',exact=True).select_option(stage)
                        page.get_by_role('button',name='Salvar demanda').click()
                    assert page.locator('.timeline li').count()==3
                    page.screenshot(path=str(out/'demanda_historico.png'),full_page=True)
                check('B02_demanda_historico',demand)
                def filters():
                    page.goto(base+'/');page.get_by_label('Buscar título ou cliente').fill('inexistente')
                    assert page.locator('tbody tr[data-search]:visible').count()==0
                    assert page.locator('#live-empty').is_visible()
                    page.get_by_role('link',name='Limpar',exact=True).click()
                    assert page.locator('tbody tr[data-search]:visible').count()==1
                    page.goto(base+'/?q=inexistente');page.get_by_role('link',name='Limpar',exact=True).click()
                    assert page.locator('tbody tr[data-search]:visible').count()==1
                    other=browser.new_context(java_script_enabled=False)
                    try:
                        p=other.new_page();login(p)
                        p.get_by_label('Buscar título ou cliente').fill('inexistente');p.get_by_role('button',name='Filtrar',exact=True).click()
                        assert p.locator('tbody tr[data-search]').count()==0
                        p.get_by_role('link',name='Limpar',exact=True).click()
                        assert p.locator('tbody tr[data-search]').count()==1
                    finally:other.close()
                check('B03_filtros_com_e_sem_js',filters)
                def incident():
                    page.goto(base+'/incidentes/novo')
                    page.get_by_label('Título',exact=True).fill('Revisão de mensagem assistida')
                    page.get_by_label('Categoria',exact=True).select_option('Uso de IA')
                    page.get_by_label('Situação',exact=True).select_option('Encerrado')
                    assert page.get_by_label('Encaminhamento',exact=True).get_attribute('required') is not None
                    assert page.get_by_label('Aprendizado',exact=True).get_attribute('required') is not None
                    page.get_by_label('Demanda relacionada (opcional)').select_option('1')
                    page.get_by_label('Descrição factual').fill('Texto de exemplo contém expressão ambígua sugerida por ferramenta automática.')
                    page.get_by_label('Impacto relatado ou potencial').fill('Possibilidade de interpretação incorreta na comunicação.')
                    page.get_by_label('Encaminhamento',exact=True).fill('Revisar a redação antes de encaminhar para aprovação.')
                    page.get_by_label('Aprendizado',exact=True).fill('Confirmar contexto e manter revisão humana do texto.')
                    page.get_by_role('button',name='Salvar incidente').click()
                    assert page.get_by_label('Situação',exact=True).input_value()=='Encerrado'
                    page.goto(base+'/incidentes')
                    assert page.get_by_role('link',name='Revisão de mensagem assistida').count()==1
                    page.screenshot(path=str(out/'incidente_encerrado.png'),full_page=True)
                check('B04_incidente_encerrado',incident)
                def responsive():
                    page.goto(base+'/')
                    for width in [1440,640,390,320]:
                        page.set_viewport_size({'width':width,'height':1000})
                        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),f'Overflow da página em {width}px'
                        assert page.get_by_role('link',name='+ Nova demanda').is_visible()
                        page.screenshot(path=str(out/f'painel_{width}.png'),full_page=True)
                    page.set_viewport_size({'width':1440,'height':1000})
                check('B05_responsividade',responsive)
                def accessibility():
                    page.goto(base+'/');page.keyboard.press('Tab')
                    assert page.locator('.skip-link').evaluate('(e)=>e===document.activeElement')
                    assert page.locator('.skip-link').evaluate('(e)=>parseFloat(getComputedStyle(e).outlineWidth)>0')
                    page.keyboard.press('Enter')
                    assert page.locator('#conteudo').evaluate('(e)=>e===document.activeElement')
                    assert page.locator('html').get_attribute('lang')=='pt-BR'
                    for route in ['/demandas/nova','/incidentes/novo']:
                        page.goto(base+route)
                        assert page.locator('input:not([type=hidden]),select,textarea').evaluate_all('(els)=>els.every(e=>e.labels && e.labels.length>0)')
                    # Metade do viewport equivale ao espaço CSS de uma janela ampliada;
                    # não representa teste de zoom nativo nem certificação WCAG.
                check('B06_teclado_rotulos',accessibility)
                def xss():
                    page.goto(base+'/demandas/nova')
                    page.get_by_label('Título',exact=True).fill('<script>window.provaXss=1</script>')
                    page.get_by_label('Cliente de referência').fill("Teste'); DROP TABLE demands;--")
                    page.get_by_label('Prazo',exact=True).fill('2026-11-16')
                    page.get_by_role('button',name='Salvar demanda').click()
                    page.goto(base+'/')
                    assert page.evaluate('window.provaXss') is None
                    assert page.get_by_role('link',name='<script>window.provaXss=1</script>',exact=True).count()==1
                check('B07_saida_html_no_navegador',xss)
                def backup():
                    page.get_by_role('button',name='Criar cópia de segurança').click()
                    b=list((Path(temp)/'backups').glob('*.sqlite3'));assert len(b)==1
                    with sqlite3.connect(b[0]) as c:
                        assert c.execute('SELECT COUNT(*) FROM demands').fetchone()[0]==2
                        assert c.execute('SELECT COUNT(*) FROM incidents').fetchone()[0]==1
                check('B08_backup_pelo_fluxo',backup)
                def logout():
                    page.get_by_role('button',name='Sair',exact=True).click()
                    assert page.url.endswith('/login')
                    assert ctx.request.get(base+'/api/v1/demandas').status==401
                    assert errors==[],str(errors)
                check('B09_saida_e_api',logout)
                browser.close()
                (out/'resultado.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
                print(json.dumps(info,ensure_ascii=False,indent=2))
        finally:
            server.terminate();server.wait(timeout=10);log.close()
    return int(any(x['status']!='aprovado' for x in results))

if __name__=='__main__':sys.exit(main())
