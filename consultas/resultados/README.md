# Resultados das consultas SPARQL

Arquivo gerado por `codigo-fonte/executar_consultas.py`. Não edite manualmente: altere os dados ou as consultas e execute o script novamente.

Os resultados vêm de uma execução local, com RDFLib, sobre `ontologia/instancias.ttl` (conjunto de demonstração com dados fictícios). Não há endpoint SPARQL público. Cada arquivo `.json` segue o formato SPARQL 1.1 Query Results JSON; variáveis sem valor ficam ausentes do binding e aparecem abaixo como “Não informado”. Valores `inst:` abreviam `https://pedromota07.github.io/conecta-academico/ontologia/instancias.ttl#`.

## PC1 · `consulta01.json`

**Pergunta:** Quais são os docentes cadastrados e seus respectivos departamentos ou unidades acadêmicas?

**Consulta:** [`consultas/consulta01.rq`](../consulta01.rq) · **Parâmetros:** nenhum · **Linhas:** 2

| docente | nomeDocente | unidade | nomeUnidade |
| --- | --- | --- | --- |
| inst:pessoa-ana | Ana Silva | inst:unidade-computacao | Departamento de Computação |
| inst:pessoa-rafael | Rafael Duarte | inst:unidade-gestao-informacao | Departamento de Gestão da Informação |

## PC2 · `consulta02--curso-sistemas-informacao.json`

**Pergunta:** Quais discentes pertencem a determinado curso?

**Consulta:** [`consultas/consulta02.rq`](../consulta02.rq) · **Parâmetros:** `?curso` = `https://pedromota07.github.io/conecta-academico/ontologia/instancias.ttl#curso-sistemas-informacao` · **Linhas:** 1

| curso | nomeCurso | discente | nomeDiscente |
| --- | --- | --- | --- |
| inst:curso-sistemas-informacao | Bacharelado em Sistemas de Informação | inst:pessoa-joao | João Pereira |

## PC2 · `consulta02--curso-biblioteconomia.json`

**Pergunta:** Quais discentes pertencem a determinado curso?

**Consulta:** [`consultas/consulta02.rq`](../consulta02.rq) · **Parâmetros:** `?curso` = `https://pedromota07.github.io/conecta-academico/ontologia/instancias.ttl#curso-biblioteconomia` · **Linhas:** 1

| curso | nomeCurso | discente | nomeDiscente |
| --- | --- | --- | --- |
| inst:curso-biblioteconomia | Bacharelado em Biblioteconomia | inst:pessoa-clara | Clara Nunes |

## PC3 · `consulta03--area-dados-abertos.json`

**Pergunta:** Quais docentes atuam em determinada área de pesquisa?

**Consulta:** [`consultas/consulta03.rq`](../consulta03.rq) · **Parâmetros:** `?area` = `https://pedromota07.github.io/conecta-academico/ontologia/instancias.ttl#area-dados-abertos` · **Linhas:** 1

| area | rotuloArea | docente | nomeDocente |
| --- | --- | --- | --- |
| inst:area-dados-abertos | Dados abertos | inst:pessoa-ana | Ana Silva |

## PC3 · `consulta03--area-curadoria-digital.json`

**Pergunta:** Quais docentes atuam em determinada área de pesquisa?

**Consulta:** [`consultas/consulta03.rq`](../consulta03.rq) · **Parâmetros:** `?area` = `https://pedromota07.github.io/conecta-academico/ontologia/instancias.ttl#area-curadoria-digital` · **Linhas:** 1

| area | rotuloArea | docente | nomeDocente |
| --- | --- | --- | --- |
| inst:area-curadoria-digital | Curadoria digital | inst:pessoa-rafael | Rafael Duarte |

## PC4 · `consulta04.json`

**Pergunta:** Quais docentes e discentes participam de um mesmo projeto de pesquisa?

**Consulta:** [`consultas/consulta04.rq`](../consulta04.rq) · **Parâmetros:** nenhum · **Linhas:** 1

| projeto | tituloProjeto | docente | nomeDocente | discente | nomeDiscente |
| --- | --- | --- | --- | --- | --- |
| inst:projeto-dados-abertos | Catálogo acadêmico de dados abertos | inst:pessoa-ana | Ana Silva | inst:pessoa-joao | João Pereira |

## PC5 · `consulta05--pessoa-ana.json`

**Pergunta:** Quais publicações estão associadas a determinado docente e quem são seus coautores, quando essa informação estiver representada?

**Consulta:** [`consultas/consulta05.rq`](../consulta05.rq) · **Parâmetros:** `?docente` = `https://pedromota07.github.io/conecta-academico/ontologia/instancias.ttl#pessoa-ana` · **Linhas:** 2

| docente | nomeDocente | publicacao | tituloPublicacao | ano | coautor | nomeCoautor |
| --- | --- | --- | --- | --- | --- | --- |
| inst:pessoa-ana | Ana Silva | inst:publicacao-dados-conectados | Dados conectados para descrever coleções universitárias | 2024 | inst:pessoa-rafael | Rafael Duarte |
| inst:pessoa-ana | Ana Silva | inst:publicacao-representacao-conhecimento | Representação do conhecimento em diretórios acadêmicos | 2022 | Não informado | Não informado |

## PC5 · `consulta05--pessoa-rafael.json`

**Pergunta:** Quais publicações estão associadas a determinado docente e quem são seus coautores, quando essa informação estiver representada?

**Consulta:** [`consultas/consulta05.rq`](../consulta05.rq) · **Parâmetros:** `?docente` = `https://pedromota07.github.io/conecta-academico/ontologia/instancias.ttl#pessoa-rafael` · **Linhas:** 1

| docente | nomeDocente | publicacao | tituloPublicacao | ano | coautor | nomeCoautor |
| --- | --- | --- | --- | --- | --- | --- |
| inst:pessoa-rafael | Rafael Duarte | inst:publicacao-dados-conectados | Dados conectados para descrever coleções universitárias | 2024 | inst:pessoa-ana | Ana Silva |

## PC6 · `consulta06--unidade-computacao.json`

**Pergunta:** Quais pessoas estão vinculadas a uma unidade acadêmica específica, independentemente de serem docentes ou discentes?

**Consulta:** [`consultas/consulta06.rq`](../consulta06.rq) · **Parâmetros:** `?unidade` = `https://pedromota07.github.io/conecta-academico/ontologia/instancias.ttl#unidade-computacao` · **Linhas:** 2

| unidade | nomeUnidade | pessoa | nomePessoa | vinculoDocente | vinculoDiscente |
| --- | --- | --- | --- | --- | --- |
| inst:unidade-computacao | Departamento de Computação | inst:pessoa-ana | Ana Silva | sim | não |
| inst:unidade-computacao | Departamento de Computação | inst:pessoa-joao | João Pereira | não | sim |

## PC6 · `consulta06--unidade-gestao-informacao.json`

**Pergunta:** Quais pessoas estão vinculadas a uma unidade acadêmica específica, independentemente de serem docentes ou discentes?

**Consulta:** [`consultas/consulta06.rq`](../consulta06.rq) · **Parâmetros:** `?unidade` = `https://pedromota07.github.io/conecta-academico/ontologia/instancias.ttl#unidade-gestao-informacao` · **Linhas:** 2

| unidade | nomeUnidade | pessoa | nomePessoa | vinculoDocente | vinculoDiscente |
| --- | --- | --- | --- | --- | --- |
| inst:unidade-gestao-informacao | Departamento de Gestão da Informação | inst:pessoa-clara | Clara Nunes | não | sim |
| inst:unidade-gestao-informacao | Departamento de Gestão da Informação | inst:pessoa-rafael | Rafael Duarte | sim | não |

## PC6 · `consulta06--unidade-ciencias-exatas.json`

**Pergunta:** Quais pessoas estão vinculadas a uma unidade acadêmica específica, independentemente de serem docentes ou discentes?

**Consulta:** [`consultas/consulta06.rq`](../consulta06.rq) · **Parâmetros:** `?unidade` = `https://pedromota07.github.io/conecta-academico/ontologia/instancias.ttl#unidade-ciencias-exatas` · **Linhas:** 0

Nenhum resultado para estes parâmetros.

## Consulta complementar · `ligacoes-externas.json`

**Pergunta:** Quais áreas locais estão ligadas a recursos externos e por qual relação de mapeamento SKOS?

**Consulta:** [`consultas/ligacoes-externas.rq`](../ligacoes-externas.rq) · **Parâmetros:** nenhum · **Linhas:** 3

| area | rotuloArea | relacao | recursoExterno |
| --- | --- | --- | --- |
| inst:area-curadoria-digital | Curadoria digital | skos:closeMatch | http://www.wikidata.org/entity/Q5276060 |
| inst:area-dados-abertos | Dados abertos | skos:closeMatch | http://www.wikidata.org/entity/Q309901 |
| inst:area-web-semantica | Web Semântica | skos:closeMatch | http://www.wikidata.org/entity/Q54837 |
