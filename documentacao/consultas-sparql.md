# Consultas SPARQL e perguntas de competência

As seis perguntas da seção 5 do enunciado são respondidas por arquivos SPARQL 1.1 em [`consultas/`](../consultas/). As consultas são executadas com RDFLib 7.6.0 sobre o grafo local [`ontologia/instancias.ttl`](../ontologia/instancias.ttl), gerado a partir de [`dados.json`](../exemplos/perfis/dados.json). Não há endpoint SPARQL público. As evidências são os arquivos SPARQL Results JSON em [`consultas/resultados/`](../consultas/resultados/), com uma versão legível gerada em [`consultas/resultados/README.md`](../consultas/resultados/README.md) e na página `dados.html` do site.

## Como executar

```powershell
# Todas as consultas com os parâmetros de demonstração (regrava consultas/resultados/)
& .\.venv\Scripts\python.exe -B codigo-fonte/executar_consultas.py

# Uma consulta, com outro parâmetro (ID local, inst:ID ou URI completa)
& .\.venv\Scripts\python.exe -B codigo-fonte/executar_consultas.py consulta02 --param curso=curso-biblioteconomia
& .\.venv\Scripts\python.exe -B codigo-fonte/executar_consultas.py consulta05 --param docente=inst:pessoa-rafael --json

# Lista de consultas e parâmetros
& .\.venv\Scripts\python.exe -B codigo-fonte/executar_consultas.py --listar
```

**Grafo consultado.** Somente `instancias.ttl`. A ontologia não é carregada porque o gerador emite explicitamente todos os tipos usados (`ca:Pessoa`, `ca:Docente`, `ca:Discente`, `ca:UnidadeAcademica`, `ca:Departamento` etc.). As consultas não dependem de inferência nem de downloads.

**Parâmetros.** Há uma única estratégia: o executor converte o valor informado em `URIRef` e o passa em `initBindings` para a variável da consulta (`?curso`, `?area`, `?docente`, `?unidade`). Nada é interpolado no texto SPARQL. Valores malformados (espaços, `<>`, aspas, esquemas que não sejam http/https) são rejeitados com mensagem; uma URI bem formada que não existe no grafo produz resultado vazio. Os arquivos `.rq` com parâmetro não contêm `VALUES`.

**Fora do executor.** Em outra ferramenta SPARQL 1.1 (por exemplo Apache Jena `arq --data ontologia/instancias.ttl --query consultas/consulta02.rq`), acrescente no início do `WHERE` uma linha como `VALUES ?curso { <https://pedromota07.github.io/conecta-academico/ontologia/instancias.ttl#curso-sistemas-informacao> }`. O comentário de cada `.rq` traz o exemplo correspondente. PC1, PC4 e a consulta de ligações não têm parâmetros.

**Resultados.** Variáveis sem valor ficam ausentes do binding, como define o formato SPARQL Results JSON; na apresentação aparecem como “Não informado”. URIs, literais com idioma (`pt-BR`), inteiros (`xsd:integer`) e booleanos (`xsd:boolean`) conservam seus tipos. A ordenação é estável (`ORDER BY` com desempate pela URI) e os arquivos não têm data de execução, então só mudam quando os dados ou as consultas mudam.

Prefixos usados: `ca:` = `…/ontologia/conecta-academico.ttl#`, `inst:` = `…/ontologia/instancias.ttl#`, `schema:` = `https://schema.org/`, `dcterms:` = `http://purl.org/dc/terms/`, `skos:` = `http://www.w3.org/2004/02/skos/core#`.

## PC1 — Docentes e unidades

**Pergunta.** Quais são os docentes cadastrados e seus respectivos departamentos ou unidades acadêmicas?
**Arquivo.** [`consulta01.rq`](../consultas/consulta01.rq) · sem parâmetros.
**Percurso.** `?docente a ca:Docente` → `ca:temVinculoDocente` → `?unidade`. Nomes por `schema:name`.
**Resultado obtido.** `inst:pessoa-ana` → `inst:unidade-computacao`; `inst:pessoa-rafael` → `inst:unidade-gestao-informacao`.
**Interpretação.** Somente pessoas tipadas como docentes e com vínculo docente aparecem. João e Clara, que têm vínculo discente com as mesmas unidades, ficam fora porque `ca:temVinculoDiscente` não é consultado.

## PC2 — Discentes de um curso

**Pergunta.** Quais discentes pertencem a determinado curso?
**Arquivo.** [`consulta02.rq`](../consultas/consulta02.rq) · parâmetro `?curso`.
**Percurso.** `?discente a ca:Discente` → `ca:matriculadoEm` → `?curso` (`a ca:CursoGraduacao`).
**Resultado obtido.** `curso-sistemas-informacao` → `pessoa-joao`; `curso-biblioteconomia` → `pessoa-clara`.
**Interpretação.** A seleção é pela URI do curso. Um curso homônimo com outra URI não traz os mesmos discentes (verificado em `testes/test_consultas.py`).

## PC3 — Docentes de uma área

**Pergunta.** Quais docentes atuam em determinada área de pesquisa?
**Arquivo.** [`consulta03.rq`](../consultas/consulta03.rq) · parâmetro `?area`.
**Percurso.** `?docente a ca:Docente` → `ca:atuaEmArea` → `?area` (`skos:prefLabel`).
**Resultado obtido.** `area-dados-abertos` → `pessoa-ana`; `area-curadoria-digital` → `pessoa-rafael`.
**Interpretação.** João tem `ca:temInteresseEmArea` em Dados abertos, mas interesse discente não é atuação docente e ele não aparece. Só a área registrada conta: consultar `area-gestao-informacao`, que é mais ampla que Dados abertos, retorna vazio porque não há expansão por `skos:broader`.

## PC4 — Docentes e discentes no mesmo projeto

**Pergunta.** Quais docentes e discentes participam de um mesmo projeto de pesquisa?
**Arquivo.** [`consulta04.rq`](../consultas/consulta04.rq) · sem parâmetros.
**Percurso (relação entre tipos de entidade).** `?projeto a ca:ProjetoPesquisa` → `ca:temParticipante` → `?docente a ca:Docente`, e o mesmo `?projeto` → `ca:temParticipante` → `?discente a ca:Discente`, com `FILTER (?docente != ?discente)`.
**Resultado obtido.** `projeto-dados-abertos`: `pessoa-ana` (docente) com `pessoa-joao` (discente).
**Interpretação.** O join é feito pela variável `?projeto`, ou seja, pela URI. Os projetos de Rafael e de Clara têm títulos parecidos, mas são recursos distintos com um único tipo de participante e não formam par. O `FILTER` impede que uma pessoa com os dois papéis forme par consigo mesma. A associação de um grupo ao projeto (`ca:associadoAoProjeto`) não é usada, porque não comprova participação individual.

## PC5 — Publicações e coautores de um docente

**Pergunta.** Quais publicações estão associadas a determinado docente e quem são seus coautores, quando essa informação estiver representada?
**Arquivo.** [`consulta05.rq`](../consultas/consulta05.rq) · parâmetro `?docente`.
**Percurso (relação entre tipos de entidade).** `?publicacao a ca:Publicacao` → `ca:temAutor` → `?docente`; dentro de `OPTIONAL`, a mesma `?publicacao` → `ca:temAutor` → `?coautor`, com `FILTER (?coautor != ?docente)`. Título por `dcterms:title`, ano opcional por `ca:anoPublicacao`.
**Resultado obtido para `pessoa-ana`.** `publicacao-dados-conectados` (2024) com coautor `pessoa-rafael`; `publicacao-representacao-conhecimento` (2022) com coautor não informado.
**Interpretação.** O `FILTER` fica dentro do `OPTIONAL`. Se ficasse fora, a obra sem outro autor seria descartada (o filtro sobre variável não associada é erro, que elimina a linha). Assim, a segunda obra continua no resultado com `?coautor` sem valor. Isso indica ausência de registro, não autoria exclusiva comprovada. Usa-se só `ca:temAutor`: o grafo também tem `schema:author` com os mesmos pares, e combinar os dois duplicaria linhas. O coautor não precisa ter perfil; uma pessoa só autora aparece com seu nome (teste com fixture).

## PC6 — Pessoas vinculadas a uma unidade

**Pergunta.** Quais pessoas estão vinculadas a uma unidade acadêmica específica, independentemente de serem docentes ou discentes?
**Arquivo.** [`consulta06.rq`](../consultas/consulta06.rq) · parâmetro `?unidade`.
**Percurso.** `?pessoa` → (`ca:temVinculoDocente` | `ca:temVinculoDiscente`) → `?unidade`. `SELECT DISTINCT` deixa uma linha por pessoa; `BIND(EXISTS {…})` produz `?vinculoDocente` e `?vinculoDiscente` (`xsd:boolean`).
**Resultado obtido.** `unidade-computacao` → `pessoa-ana` (docente) e `pessoa-joao` (discente); `unidade-gestao-informacao` → `pessoa-rafael` (docente) e `pessoa-clara` (discente); `unidade-ciencias-exatas` → nenhum resultado.
**Interpretação.** Uma pessoa com os dois vínculos na mesma unidade aparece uma vez, com os dois indicadores verdadeiros (teste com fixture). O vínculo é direto: `ca:temUnidadeSuperior` e `ca:temUnidadeResponsavel` não são seguidos, por isso o Instituto de Ciências Exatas não herda as pessoas do Departamento de Computação. Uma consulta hierárquica seria uma extensão separada.

## Consulta complementar — ligações externas

[`ligacoes-externas.rq`](../consultas/ligacoes-externas.rq) lista as áreas com relações de mapeamento SKOS para URIs fora do namespace do projeto. Resultado: três `skos:closeMatch` para itens do Wikidata. Não substitui nenhuma das seis consultas. Ver [ligações externas](ligacoes-externas.md).

## Testes

`testes/test_consultas.py` executa os arquivos `.rq` reais e confere os resultados por URI, varia cursos, áreas, docentes e unidades, valida parâmetros malformados, usa fixtures temporárias com homônimos, mudança de nome, projetos de mesmo título, pessoa com dois papéis e autor sem perfil, e confirma que os resultados versionados coincidem com uma nova execução.
