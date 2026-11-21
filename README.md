# ConectaAcadêmico — Diretório Semântico de Perfis Universitários

Trabalho final da disciplina Web Semântica da Universidade Federal Rural do Rio de Janeiro (UFRRJ), ministrada pelo professor Tiago Cruz de França.

## Objetivo

O ConectaAcadêmico é um diretório estático de perfis docentes e discentes. Os quatro perfis desta demonstração, a instituição (Universidade Demonstrativa) e suas unidades são fictícios. A apresentação partiu dos modelos HTML e CSS fornecidos pelo professor.

## Como abrir a aplicação

O site já está gerado. Abra `docs/index.html` no navegador para explorar o catálogo, filtrar os perfis e acessar a página **Dados e consultas**.

Para servir o site via HTTP, abra o PowerShell na pasta `conecta-academico` e execute com o Python instalado no computador.

```powershell
python -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Acesse [a prévia local](http://127.0.0.1:8000/) e mantenha o terminal aberto enquanto navega. Pressione `Ctrl+C` no terminal para encerrar o servidor.

## Tecnologias implementadas

- JSON como fonte editorial única dos perfis, dos recursos acadêmicos e das ligações externas.
- Python 3.10 ou superior e biblioteca padrão para validar os dados e gerar o site.
- HTML5, CSS3 responsivo e um script pequeno e opcional de busca e filtro no catálogo. Os perfis continuam acessíveis sem JavaScript.
- RDFLib 7.6.0, em ambiente virtual, para gerar o RDF/Turtle, executar as consultas SPARQL e rodar os testes.

## Instalação para regenerar os dados e executar as consultas

Na raiz do repositório, no PowerShell. Os comandos chamam o Python do ambiente virtual diretamente e não exigem mudar a política de execução.

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-rdf.txt
```

## Geração e consultas

Execute na ordem abaixo. Cada etapa usa a saída da anterior.

```powershell
# 1. Valida o JSON e gera ontologia/instancias.ttl (e as cópias em docs/ontologia)
& .\.venv\Scripts\python.exe -B codigo-fonte/gerar_rdf.py --publicaveis docs/ontologia

# 2. Executa as seis consultas e a consulta de ligações com os parâmetros de demonstração
& .\.venv\Scripts\python.exe -B codigo-fonte/executar_consultas.py

# 3. Gera catálogo, perfis e a página "Dados e consultas" em docs/
& .\.venv\Scripts\python.exe -B codigo-fonte/gerar_site.py
```

Para executar uma consulta com outro parâmetro (ID local, `inst:ID` ou URI completa):

```powershell
& .\.venv\Scripts\python.exe -B codigo-fonte/executar_consultas.py --listar
& .\.venv\Scripts\python.exe -B codigo-fonte/executar_consultas.py consulta02 --param curso=curso-biblioteconomia
& .\.venv\Scripts\python.exe -B codigo-fonte/executar_consultas.py consulta06 --param unidade=unidade-gestao-informacao --json
```

O arquivo [dados.json](exemplos/perfis/dados.json) contém os metadados do conjunto e as coleções de pessoas, unidades, cursos, disciplinas, áreas, projetos, grupos e publicações. Departamentos são unidades com tipo departamento. Os blocos de docência e discência podem coexistir na mesma pessoa, com um único identificador e uma única página. Edite os dados no JSON, a apresentação nos templates e as consultas em `consultas/`, e repita os três passos. Não edite `docs/` nem `consultas/resultados/` manualmente.

## Ontologia, RDF, SPARQL e LOD

- [Ontologia OWL](ontologia/conecta-academico.ttl) e [grafo de instâncias](ontologia/instancias.ttl), documentados em [ontologia-aplicacao.md](documentacao/ontologia-aplicacao.md).
- [Consultas SPARQL](consultas/) e [resultados](consultas/resultados/README.md), explicados em [consultas-sparql.md](documentacao/consultas-sparql.md).
- Três ligações `skos:closeMatch` entre áreas de conhecimento e itens do Wikidata, justificadas em [ligacoes-externas.md](documentacao/ligacoes-externas.md).

As consultas rodam localmente com RDFLib. Não há endpoint SPARQL público.

## Testes

No PowerShell, habilite o modo UTF-8 do Python para que os testes de linha de comando leiam corretamente os acentos na saída das consultas.

```powershell
$env:PYTHONUTF8 = '1'
& .\.venv\Scripts\python.exe -B -m unittest discover -s testes -v
```

Os testes geram as saídas em diretórios temporários e verificam páginas, links, papéis acadêmicos, rejeição de dados inválidos, a ontologia e o RDF, a execução dos seis arquivos `.rq` com variações de parâmetros e casos adversariais (homônimos, pessoa com dois papéis, projetos de mesmo título, autor sem perfil), as ligações externas e a correspondência entre `docs/` e uma geração limpa. Não acessam a Internet.

## Estrutura

| Diretório | Finalidade |
| --- | --- |
| `proposta/` | Escopo, requisitos, perguntas de competência e rastreabilidade. |
| `documentacao/` | Dicionário de dados, vocabulários, ontologia, consultas SPARQL, ligações externas e declaração de uso de IA. |
| `exemplos/perfis/` | Fonte JSON dos registros da demonstração. |
| `ontologia/` | Ontologia OWL e dados RDF em Turtle. |
| `consultas/` e `consultas/resultados/` | Consultas SPARQL e evidências de execução (SPARQL Results JSON). |
| `codigo-fonte/` | Validador, geradores, executor das consultas, templates, estilos e script do catálogo. |
| `testes/` | Testes do site, do RDF, das consultas e das ligações externas. |
| `docs/` | Saída estática gerada para futura hospedagem. |

## Modelo conceitual e reprodução do diagrama

A modelagem da Etapa 2 está documentada no [dicionário de dados](documentacao/dicionario-dados.md) e nas [decisões de modelagem](documentacao/decisoes-modelagem.md). O [diagrama SVG](documentacao/diagrama-conceitual.svg) tem como fonte editável o arquivo [Graphviz DOT](documentacao/diagrama-conceitual.dot).

Para regenerar a imagem, instale o [Graphviz](https://graphviz.org/download/), disponibilize o executável `dot` no `PATH` e execute, na raiz do repositório, no PowerShell:

```powershell
dot -V
dot -Tsvg "documentacao/diagrama-conceitual.dot" -o "documentacao/diagrama-conceitual.svg"
```

O comando produz o SVG a partir do DOT. A distribuição visual pode variar com a versão e as fontes disponíveis; após regenerar, confira a legibilidade, as 15 relações (R01–R15) e as multiplicidades. O SVG versionado também possui atributos de acessibilidade e descrição textual (`role`, `aria-labelledby`, `title` e `desc`), que podem precisar ser reaplicados à saída do Graphviz. A ferramenta não estava instalada no terminal utilizado na auditoria da Etapa 2; portanto, a regeneração por esse comando ainda não foi executada nesse ambiente.

## Situação atual

As etapas 0 a 5 estão implementadas. Na Etapa 5, o catálogo ganhou busca e filtros, e a página **Dados e consultas** passou a reunir os arquivos RDF, as seis consultas de competência, a consulta de ligações com o Wikidata e os resultados de demonstração. Continuam pendentes a decisão sobre a licença do conjunto, a publicação no GitHub Pages e a verificação pública das URIs. Consulte os [requisitos](proposta/requisitos.md) e a [declaração de uso de IA](documentacao/uso-ia.md).

## Integrantes

1. **Pedro Mota**
2. **Hugo Kauã**
3. **Caio Luiz**

## Colaboração

1. Cada integrante parte da `main` atualizada e cria uma branch por tarefa.
2. Ao abrir um Pull Request para `main`, descreva a mudança e as verificações realizadas. Peça revisão a pelo menos um dos outros dois integrantes.
3. Incorpore a contribuição após a revisão e atualize a `main` local antes de iniciar outra tarefa.
