# ConectaAcadêmico — Diretório Semântico de Perfis Universitários

Trabalho final da disciplina Web Semântica da Universidade Federal Rural do Rio de Janeiro (UFRRJ), ministrada pelo professor Tiago Cruz de França.

## Objetivo

Desenvolver uma aplicação que gere páginas de perfis acadêmicos de docentes e discentes a partir de uma fonte de dados estruturada. O projeto prevê a publicação desses dados na Web com URIs públicas, sua representação em RDF conforme uma ontologia OWL, consultas SPARQL e ligações com recursos de Linked Open Data (LOD).

## Tecnologias previstas

- HTML e CSS para a apresentação dos perfis, a partir dos modelos fornecidos pelo professor.
- OWL e RDF para a ontologia e os dados, com Turtle previsto para os dados RDF.
- SPARQL para as consultas aos dados.
- Git e GitHub para versionamento e colaboração.

O grupo ainda vai definir o formato da fonte estruturada, a tecnologia de geração das páginas e a hospedagem.

## Estrutura

| Diretório | Finalidade |
| --- | --- |
| `proposta/` | Proposta, requisitos e decisões de modelagem. |
| `documentacao/` | Dicionário de dados, vocabulários, documentação da ontologia e declaração de uso de IA. |
| `exemplos/perfis/` | Exemplos de dados de perfis. |
| `ontologia/` | Arquivos da ontologia e dos dados RDF. |
| `consultas/` e `consultas/resultados/` | Consultas SPARQL e evidências de execução. |
| `codigo-fonte/` | Código da aplicação. |
| `testes/` | Testes da aplicação e dos dados. |
| `docs/` | Arquivos para publicação, conforme a estratégia de hospedagem a definir. |

O Git passará a representar os diretórios vazios quando eles receberem arquivos versionados.

## Modelo conceitual e reprodução do diagrama

A modelagem da Etapa 2 está documentada no [dicionário de dados](documentacao/dicionario-dados.md) e nas [decisões de modelagem](documentacao/decisoes-modelagem.md). O [diagrama SVG](documentacao/diagrama-conceitual.svg) tem como fonte editável o arquivo [Graphviz DOT](documentacao/diagrama-conceitual.dot).

Para regenerar a imagem, instale o [Graphviz](https://graphviz.org/download/), disponibilize o executável `dot` no `PATH` e execute, na raiz do repositório, no PowerShell:

```powershell
dot -V
dot -Tsvg "documentacao/diagrama-conceitual.dot" -o "documentacao/diagrama-conceitual.svg"
```

O comando produz o SVG a partir do DOT. A distribuição visual pode variar com a versão e as fontes disponíveis; após regenerar, confira a legibilidade, as 15 relações (R01–R15) e as multiplicidades. O SVG versionado também possui atributos de acessibilidade e descrição textual (`role`, `aria-labelledby`, `title` e `desc`), que podem precisar ser reaplicados à saída do Graphviz. A ferramenta não estava instalada no terminal utilizado na auditoria da Etapa 2; portanto, a regeneração por esse comando ainda não foi executada nesse ambiente.

## Situação atual

As Etapas 0, 1 e 2 foram concluídas. A pesquisa, o modelo conceitual, o dicionário de dados e o diagrama estão disponíveis no repositório. O desenvolvimento do site, a ontologia executável, os dados RDF, as consultas SPARQL e a publicação do site permanecem para as próximas etapas. Consulte os [requisitos](proposta/requisitos.md) e a [declaração de uso de IA](documentacao/uso-ia.md).

## Integrantes

1. **Integrante 1** · a definir.
2. **Integrante 2** · a definir.
3. **Integrante 3** · a definir.

## Colaboração

1. Cada integrante parte da `main` atualizada e cria uma branch por tarefa.
2. Ao abrir um Pull Request para `main`, descreva a mudança e as verificações realizadas. Peça revisão a pelo menos um dos outros dois integrantes.
3. Incorpore a contribuição após a revisão e atualize a `main` local antes de iniciar outra tarefa.
