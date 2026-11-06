# Demandas e Ética

Aplicação acadêmica web local de uso individual. Organiza demandas de conteúdo, prazos, etapas, histórico de atuação e registros de incidentes de ética digital. Não publica conteúdo nem envia mensagens a terceiros.

## Instalar no Windows
1. Instale Python 3.12 ou superior pelo site https://www.python.org/downloads/windows/ incluindo o launcher `py`.
2. Extraia toda a pasta do ZIP para uma pasta local do usuário (não execute de dentro do ZIP).
3. Execute `instalar.bat`. A primeira instalação usa internet para baixar as dependências. Defina e confirme uma senha de pelo menos 10 caracteres.
4. Execute `iniciar.bat`. O navegador abrirá http://127.0.0.1:8765. Faça login com a senha definida.
5. Para facilitar o uso, crie um atalho de `iniciar.bat` na área de trabalho. Mantenha a janela do servidor aberta; Ctrl+C encerra o serviço.

O código foi testado em Linux; os scripts de instalação no Windows foram revisados, mas ainda precisam ser executados no computador de Felipe. Não se trata de executável autônomo: é necessário Python. Instalação e inicialização não exigem executar como administrador.

## Dados e backup
Dados padrão no Windows: `%LOCALAPPDATA%\DemandasEtica\dados.sqlite3`. A senha fica em hash e o segredo da sessão em `config.json` nessa pasta. O botão de backup salva cópias em `backups` no mesmo diretório. Copie também os backups para um local protegido fora do computador se precisar de recuperação após perda do equipamento.

Restaurar: pare o aplicativo, preserve uma cópia do `dados.sqlite3` atual e copie o backup escolhido para esse nome. Mantenha o `config.json` existente. Reinicie. Redefinir senha: `.venv\Scripts\python.exe app.py --configure`. Isso troca o segredo de sessão e encerra os acessos anteriores. O backup do banco não inclui `config.json`.

## Operação
- Etapas livres: Solicitado, Em produção, Em revisão, Aguardando aprovação, Agendado, Publicado e Cancelado.
- O histórico acrescenta uma entrada na criação e ao mudar etapa ou observações. Horários são UTC, identificados na tela. Não registra versões anteriores de incidentes.
- Prazos são datas; atrasos excluem demandas publicadas/canceladas. Próximos prazos incluem hoje e os três dias seguintes. Indicadores são do conjunto completo, mesmo com filtro ativo.
- Incidentes podem existir sem demanda; se associados, a demanda precisa existir. Para encerrar, informe encaminhamento e aprendizado.
- Não há exclusão física nesta versão. A API de leitura `GET /api/v1/demandas` exige a sessão do navegador. Não há API de escrita nem acesso externo habilitado.

## Testes e desenvolvimento
```bash
python -m venv .venv
# No Windows: .venv\Scripts\activate
# No Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest -v
python app.py
```
O teste utiliza `unittest` da biblioteca padrão, sem precisar instalar pytest. Cada caso usa diretório temporário e não altera dados do usuário. Evidências em `evidencias/testes.txt`. A base de demonstração usada durante o desenvolvimento é fictícia e não acompanha a instalação.

## Estrutura
`app.py`: rotas, validações, regras e banco. `templates`: HTML/Jinja. `static/style.css`: apresentação responsiva sem CDN. `static/app.js`: filtros imediatos e estado dos campos de incidente. `test_app.py`, `test_banco.py` e `test_qualidade.py`: 33 testes. `docs`: decisões e roteiro de verificação desta versão. `evidencias`: resultados técnicos.

## Limites desta versão
Uso por uma pessoa no computador local. Não expor este serviço na internet nem alterar o host para compartilhar em rede sem revisão de transporte e autenticação. A senha de entrada não criptografa o banco; a proteção do arquivo depende da conta do Windows e das permissões da pasta. O controle de tentativas é por sessão e não substitui proteção de serviço público. Acesso pelo Wi-Fi, sincronização e empacotamento como EXE ficam fora desta entrega. Testes de interface visual, uso em Windows e aceitação por Felipe estão pendentes.

Repositório do projeto: https://github.com/Grotherrn/demandas-etica. A publicação de novos incrementos é realizada pelo titular da conta.

## Interação e acessibilidade na versão M2
A busca e o filtro por etapa atualizam as linhas já carregadas sem recarregar a página. Use Limpar para retornar ao conjunto carregado. Sem JavaScript, use Filtrar para consulta no servidor. A situação Encerrado exige encaminhamento e aprendizado, tanto no navegador quanto no servidor. O layout possui link Pular para o conteúdo, rótulos de campos, mensagens de status e alerta e tabela com legenda e cabeçalhos. A implementação dessas medidas não equivale a auditoria completa de acessibilidade.

## Banco de dados e controle de versão no M3

O esquema antes embutido em `app.py` agora está em `sql/schema.sql`, carregado pelo aplicativo. Mantenha a pasta `sql` ao copiar ou instalar o código. As tabelas e colunas foram preservadas; dois índices foram acrescentados aos vínculos. A reabertura de uma base preexistente foi testada sem apagar a demanda já gravada.

Para executar a demonstração de inserção, atualização, remoção e consultas, sem acessar o banco de uso:

```bash
python scripts/demonstrar_banco.py
```

A demonstração usa somente SQLite em memória, sem bibliotecas adicionais. `sql/demonstracao.sql` contém os comandos; não o execute no banco de uso. O DELETE remove um registro descartável sem dependentes; a aplicação mantém o fluxo sem exclusão física na interface.

Com as dependências instaladas, `python -m unittest -v` executa 22 testes. Resultados em `evidencias/testes_m3.txt` e `evidencias/sql_m3.txt`. O modelo e seu dicionário estão em `docs/modelo_dados_m3.md`; estratégia Git em `docs/versionamento_m3.md`; roteiro de verificação visual em `docs/capturas_m3.md`. O M3 não acrescenta funções de compartilhamento, novos usuários ou integrações externas.

## Qualidade no módulo 4

Regressão complementar e correção de vínculo inválido: `docs/qualidade_m4.md`. Resultados de 06/11/2026 em `evidencias/m4/testes_m4.txt` e ambiente em `evidencias/m4/ambiente.json`. Foram aprovados 32 testes técnicos em Linux. A execução do roteiro de navegador e a validação por Felipe permanecem pendentes; capturas anteriores documentam apenas os estados nelas visíveis.

### Reparo Windows

Fechamento explícito de conexões SQLite e regressão Q11. A suíte passou com 33 testes no Linux; confirmação no Windows pendente. Ver `docs/qualidade_m4.md` e `evidencias/m4/testes_reparo_linux.txt`.
