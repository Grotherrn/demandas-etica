# Verificação, validação e testes do módulo 4

Data: 06/11/2026. Base remota: 28e1bfd24425023fa51369100981b8e0d9cb2d4a.

## Execução técnica

Python 3.12.14, SQLite 3.53.1, Flask 3.1.3, Linux. Executar na raiz:

```console
python -m pip install -r requirements.txt
python -m unittest discover -v
```

Foram aprovados 32 métodos de teste: 14 de aplicação, 8 de banco e 10 complementares. São majoritariamente testes de integração HTTP/SQLite. O uso de unittest não os torna testes unitários de funções puras. Não foi medida cobertura de linhas.

Os novos testes verificam janela de datas com relógio fixado, limites de texto, tabela de decisão do encerramento, vínculos inválidos, restauração isolada, cabeçalhos/API, CSRF inválido, transições de etapas, requisição acima de 64 KiB e rollback diante de falha induzida na inclusão do histórico. Dados temporários são removidos ao final.

## Defeitos e limites

- D01, média, corrigido e retestado: demand_id=0 contornava a conferência de existência por ser falso em contexto booleano. A tentativa terminava em IntegrityError; em execução sem modo de teste, poderia resultar em HTTP 500. A condição passou a distinguir ausência de vínculo (None) de qualquer ID informado. O caso Q04 verifica 0, -1, texto e 999; todos rejeitados com HTTP 400.
- D02, baixa, pendente: a captura de lista vazia da versão anterior apresenta duas mensagens equivalentes. O JavaScript pode exibir a linha de filtro vazio junto da mensagem de tabela inicialmente vazia. Não há alteração de dados. Ajuste e confirmação no navegador ficam no backlog.
- O histórico cobre criação, etapa e observações, não versões anteriores de título, cliente, prazo e incidentes.
- A limitação de tentativas depende da sessão do navegador. Banco e backups não são criptografados pela senha. Escopo restrito a loopback, sem autorização para exposição na rede.

## Interface e validação

As capturas da execução local fornecidas em 05/11 documentam painel com demanda, histórico com três etapas e disposição em janela estreita. Elas pertencem à base anterior; a correção D01 não altera HTML/CSS. Não demonstram todos os fluxos, instalação limpa ou aceite do participante.

O roteiro scripts/verificar_interface_m4.py prepara nove cenários para Chromium, incluindo filtros sem JavaScript, teclado, responsividade, incidente e backup. Sua execução no ambiente de elaboração foi impedida antes dos cenários: Chromium não iniciou devido a restrição de socket e o navegador externo não alcançou o serviço local. Nenhum dos nove foi contado como aprovado. O cenário B01 também funciona como reprodução de D02, ainda pendente.

Para executá-lo em ambiente com navegador:

```console
python -m pip install playwright
python -m playwright install chromium
python scripts/verificar_interface_m4.py
```

O script inicia servidor temporário em loopback com banco descartável e encerra o servidor ao final. Não usa dados do usuário. O relatório JSON distingue aprovado e falhou; capturas ficam em evidencias/m4/interface. O resultado nunca equivale a aceite por Felipe, teste de zoom nativo ou certificação WCAG.

A validação de adequação será complementada com três tarefas de Felipe: identificar demanda e prazo, explicar a sequência de etapas e registrar uma situação de comunicação com encaminhamento e aprendizado. Registrar conclusão, ajuda necessária e observação em ficha breve identificada e datada. Não existe resultado de aceite declarado nesta entrega.
