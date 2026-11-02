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
`app.py`: rotas, validações, regras e banco. `templates`: HTML/Jinja. `static/style.css`: apresentação responsiva sem CDN. `static/app.js`: filtros imediatos e estado dos campos de incidente. `test_app.py`: 14 testes. `docs`: decisões e roteiro de verificação desta versão. `evidencias`: resultados técnicos.

## Limites desta versão
Uso por uma pessoa no computador local. Não expor este serviço na internet nem alterar o host para compartilhar em rede sem revisão de transporte e autenticação. A senha de entrada não criptografa o banco; a proteção do arquivo depende da conta do Windows e das permissões da pasta. O controle de tentativas é por sessão e não substitui proteção de serviço público. Acesso pelo Wi-Fi, sincronização e empacotamento como EXE ficam fora desta entrega. Testes de interface visual, uso em Windows e aceitação por Felipe estão pendentes.

Pacote preparado para publicação em repositório GitHub do estudante. O endereço do repositório deverá constar no relatório acadêmico após a publicação.

## Interação e acessibilidade na versão M2
A busca e o filtro por etapa atualizam as linhas já carregadas sem recarregar a página. Use Limpar para retornar ao conjunto carregado. Sem JavaScript, use Filtrar para consulta no servidor. A situação Encerrado exige encaminhamento e aprendizado, tanto no navegador quanto no servidor. O layout possui link Pular para o conteúdo, rótulos de campos, mensagens de status e alerta e tabela com legenda e cabeçalhos. A implementação dessas medidas não equivale a auditoria completa de acessibilidade.
