# Desenvolvimento web da versão M2

## Decisões
- Flask 3.1.3 é o framework da aplicação; Jinja reutiliza o layout base.
- HTML em templates, CSS externo e JavaScript externo mantêm responsabilidades separadas.
- JavaScript nativo melhora a experiência, sem adicionar framework de frontend obrigatório.
- O filtro imediato opera sobre as linhas carregadas no painel. Sem JavaScript, o formulário GET filtra no servidor.
- Alterar a situação de um incidente torna encaminhamento e aprendizado obrigatórios na interface; o servidor mantém a validação autoritativa.
- A lista é renderizada no servidor. Não há sincronização em segundo plano ou atualização entre dispositivos.
- header, nav, main, footer, títulos, labels, caption, scope e mensagens status/alert apoiam semântica e acessibilidade.
- O CSS usa Grid/Flexbox, media queries de 700px e 400px e tabela com rolagem interna.
- Não há fontes externas, CDN, analytics, integração com Instagram nem dados de terceiros no pacote.

## Verificação
Em 02/11/2026, 14 testes HTTP/persistência existentes passaram em Linux com Python 3.12. A análise sintática JavaScript usa node --check.
A tentativa de verificar a interface em Chromium automatizado foi bloqueada pelo ambiente de execução. Não foi concluída verificação visual ou medição de overflow, nem validação em Windows. Os diagramas do relatório representam o código e não capturas de execução visual.

## Verificação visual a realizar
1. Executar instalar.bat e iniciar.bat no Windows.
2. Cadastrar demandas de exemplo e consultar o painel em largura normal e estreita.
3. Digitar na busca e selecionar etapa; confirmar atualização sem recarregar e usar Limpar.
4. Percorrer os campos por teclado e usar Pular para o conteúdo.
5. Em incidente, alternar Aberto/Encerrado e verificar os campos obrigatórios.
6. Registrar navegador, data e possíveis dificuldades. Não usar dados reais nas capturas.
