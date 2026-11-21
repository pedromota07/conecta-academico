# ConectaAcadêmico — Diretório Semântico de Perfis Universitários

Trabalho final da disciplina Web Semântica da Universidade Federal Rural do Rio de Janeiro (UFRRJ), ministrada pelo professor Tiago Cruz de França.

## Objetivo

O ConectaAcadêmico é um diretório estático de perfis docentes e discentes. Os quatro perfis desta demonstração usam dados fictícios e foram preparados a partir dos modelos HTML e CSS fornecidos pelo professor.

## Tecnologias implementadas

- JSON como fonte editorial dos perfis e dos recursos acadêmicos relacionados.
- Python 3.10 ou superior e biblioteca padrão para validar os dados, gerar o site e executar os testes.
- HTML5 e CSS3 responsivo para a navegação estática no navegador.
- RDFLib em ambiente virtual para gerar e testar o RDF/Turtle.

## Dados e execução local

O arquivo [dados.json](exemplos/perfis/dados.json) contém os metadados do conjunto e as coleções de pessoas, unidades, cursos, disciplinas, áreas, projetos, grupos e publicações. Departamentos são unidades com tipo departamento. Os blocos de docência e discência podem coexistir na mesma pessoa, com um único identificador e uma única página. Referências por identificador representam as relações R01–R15.

Execute o gerador a partir da raiz do repositório.

```powershell
python -B codigo-fonte/gerar_site.py
```

O comando valida o JSON e gera o catálogo, os perfis e a folha de estilos em [docs/](docs/index.html). Edite os dados no JSON e a apresentação nos templates. Execute a geração novamente para atualizar a saída a partir dessas fontes.

Para visualizar o site, abra [docs/index.html](docs/index.html) no navegador. O comando a seguir simula a hospedagem estática.

```powershell
python -B -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Com o servidor rodando, abra [a prévia local](http://127.0.0.1:8000/). Os caminhos relativos também funcionam sob um subdiretório.

## Ontologia e RDF

A [ontologia OWL](ontologia/conecta-academico.ttl) e o [grafo de instâncias](ontologia/instancias.ttl) seguem o modelo aprovado. A [documentação da ontologia](documentacao/ontologia-aplicacao.md) explica as URIs previstas, os caminhos para PC1–PC6 e os comandos de instalação, geração, preparação das cópias estáticas e teste da Etapa 4.

## Testes do site

```powershell
python -B -m unittest discover -s testes -p "test_gerar_site.py" -v
```

Os testes geram a saída em diretórios temporários e verificam páginas, links, papéis acadêmicos, rejeição de dados inválidos e cobertura dos cenários PC1–PC6. O teste de um quinto perfil usa uma cópia dos dados.

## Estrutura

| Diretório | Finalidade |
| --- | --- |
| `proposta/` | Proposta, requisitos e decisões de modelagem. |
| `documentacao/` | Dicionário de dados, vocabulários, documentação da ontologia e declaração de uso de IA. |
| `exemplos/perfis/` | Fonte JSON dos registros da demonstração. |
| `ontologia/` | Arquivos da ontologia e dos dados RDF. |
| `consultas/` e `consultas/resultados/` | Consultas SPARQL e evidências de execução. |
| `codigo-fonte/` | Validador, gerador, templates e estilos. |
| `testes/` | Testes da aplicação e dos dados. |
| `docs/` | Saída estática gerada para futura hospedagem. |

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

As Etapas 0 a 4 estão concluídas e integradas à branch principal, incluindo o diretório estático, a ontologia OWL e a geração de dados RDF/Turtle. As consultas SPARQL, as ligações externas LOD, a aprovação da licença e a hospedagem pública do site ficam para as próximas etapas. Consulte os [requisitos](proposta/requisitos.md) e a [declaração de uso de IA](documentacao/uso-ia.md).

## Integrantes

1. **Pedro Mota**
2. **Hugo Kauã**
3. **Caio Luiz**

## Colaboração

1. Cada integrante parte da `main` atualizada e cria uma branch por tarefa.
2. Ao abrir um Pull Request para `main`, descreva a mudança e as verificações realizadas. Peça revisão a pelo menos um dos outros dois integrantes.
3. Incorpore a contribuição após a revisão e atualize a `main` local antes de iniciar outra tarefa.
