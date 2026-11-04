# Versionamento e entrega do Módulo 3

Repositório: https://github.com/Grotherrn/demandas-etica

## Histórico e estratégia

O trabalho partiu de um clone do repositório público no commit `69b773f48cc708a7ffe34f059dbff2630dd6ae38`, de 02/11/2026. A base contém o commit inicial e o envio do M2. Não foi criado outro histórico independente.

A branch `m3-banco-dados` concentra o incremento: primeiro a extração do esquema e a documentação do modelo; depois o SQL de demonstração e os testes de integridade; por fim as orientações, o diagrama e os registros técnicos. Os commits representam alterações reais deste ciclo. As mensagens seguem tipo e escopo para facilitar a leitura, sem impor uma ferramenta adicional.

Cada unidade foi adicionada ao índice e registrada separadamente. Foram utilizados `git status`, `git diff`, `git add`, `git commit` e `git log`. A suíte passou antes da preparação da entrega. Os hashes completos ficam no histórico Git e no manifesto que acompanha o pacote.

A integração em main será feita por fast-forward, preservando os commits e sem reescrever o histórico. Não houve trabalho simultâneo nem conflito; não se relata merge com resolução de conflitos ou revisão por terceiros. CI/CD não foi implantado neste módulo.

## Publicação pelo titular

O pacote externo inclui `demandas-etica-m3.bundle`, que conserva os commits, e `PUBLICAR_M3.bat`, que clona o repositório, importa a branch e tenta integrá-la por fast-forward antes do push. O titular deve usar sua própria autenticação GitHub. O script para diante de falhas e não usa force push. Se main tiver evoluído em paralelo, é necessária revisão antes de integrar.

Subir apenas os arquivos pela interface web preserva o conteúdo, mas perde os três commits preparados. Para esta entrega, prefira o bundle. O envio efetivo ao GitHub precisa ser conferido após a execução pelo titular; o pacote não declara que esse envio já ocorreu.

## Práticas adotadas

Versionar código, SQL, documentação e resultados de testes. Manter bancos de uso, configuração de senha e ambientes virtuais fora do Git. Usar commits delimitados, ler o diff antes de registrar e executar os testes antes de integrar. Para mudanças futuras no esquema, criar scripts de migração específicos em vez de editar silenciosamente bancos existentes.
