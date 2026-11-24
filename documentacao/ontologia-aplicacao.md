# Ontologia de aplicação do ConectaAcadêmico

A ontologia OWL 2 representa o diretório acadêmico definido no [dicionário de dados](dicionario-dados.md). O [diagrama conceitual](diagrama-conceitual.svg) fornece os identificadores R01–R15 usados abaixo. O [JSON editorial](../exemplos/perfis/dados.json) é a fonte única dos registros exibidos no HTML e representados no grafo RDF.

## Identificadores e arquivos

A base HTTPS prevista é `https://pedromota07.github.io/conecta-academico/`. Os arquivos estão preparados em `docs/` para hospedagem futura no GitHub Pages.

| Item | Construção a partir da base | Exemplo ou destino local |
| --- | --- | --- |
| Ontologia | `ontologia/conecta-academico.ttl` | [Fonte OWL em Turtle](../ontologia/conecta-academico.ttl) |
| Termo da ontologia | `ontologia/conecta-academico.ttl#` + nome do termo | `ontologia/conecta-academico.ttl#Docente` |
| Documento de instâncias | `ontologia/instancias.ttl` | [Grafo RDF em Turtle](../ontologia/instancias.ttl) |
| Recurso acadêmico | `ontologia/instancias.ttl#` + `id` do JSON | `ontologia/instancias.ttl#pessoa-ana` |
| Página de perfil | `perfis/` + `id` do JSON + `.html` | [Perfil HTML de Ana](../docs/perfis/pessoa-ana.html) |
| Esquema conceitual SKOS | `ontologia/instancias.ttl#esquema/areas` | O caractere `/` no fragmento separa o esquema dos IDs editoriais. |

As URIs com fragmento resolvem para o arquivo Turtle correspondente no GitHub Pages. Assim, a resolução estática dispensa reescritas HTTP. A identidade do recurso deriva do identificador estável do JSON. A página HTML é um recurso distinto, relacionado à pessoa por `schema:mainEntityOfPage` e tipado como `schema:ProfilePage`. Pessoas sem papel acadêmico registrado podem aparecer como autoras ou participantes, sem gerar página. [Schema.org mainEntityOfPage](https://schema.org/mainEntityOfPage), [Schema.org ProfilePage](https://schema.org/ProfilePage)

## Classes

O prefixo `ca:` identifica o namespace terminado em `ontologia/conecta-academico.ttl#`. Os nomes técnicos abaixo são as partes locais das URIs. Os rótulos e comentários da ontologia estão em português.

| Classe | Origem no JSON | Especialização ou alinhamento |
| --- | --- | --- |
| `ca:Pessoa` | Registro em `pessoas` | `schema:Person` |
| `ca:Docente` | Bloco `docencia` na pessoa | `ca:Pessoa` |
| `ca:Discente` | Bloco `discencia` na pessoa | `ca:Pessoa` |
| `ca:UnidadeAcademica` | Registro em `unidades` | `schema:Organization` |
| `ca:Departamento` | Unidade com `tipoUnidade` igual a `departamento` | `ca:UnidadeAcademica`, `aiiso:Department` |
| `ca:CursoGraduacao` | Registro em `cursos` | `aiiso:Programme`, `schema:EducationalOccupationalProgram` |
| `ca:Disciplina` | Registro em `disciplinas` | `schema:Course` |
| `ca:AreaConhecimento` | Registro em `areas` | `skos:Concept` |
| `ca:ProjetoPesquisa` | Registro em `projetos` | Classe local para a atividade de pesquisa |
| `ca:GrupoPesquisa` | Registro em `grupos` | Classe local para o coletivo acadêmico |
| `ca:Publicacao` | Registro em `publicacoes` | `schema:CreativeWork` |

Uma pessoa com os dois papéis recebe os tipos `ca:Pessoa`, `ca:Docente` e `ca:Discente` na mesma URI. O alinhamento preserva a distinção entre o programa de graduação e o componente curricular. O projeto modelado como atividade permanece uma classe local, pois `schema:ResearchProject` especializa uma organização. As correspondências expressam especializações, mantidas sem importar vocabulários completos. [Schema.org EducationalOccupationalProgram](https://schema.org/EducationalOccupationalProgram), [Schema.org Course](https://schema.org/Course), [Schema.org ResearchProject](https://schema.org/ResearchProject), [AIISO](https://vocab.org/aiiso/)

## Propriedades de objeto

Cada referência editorial vira uma ligação para a URI do registro identificado. Uma lista com vários IDs produz uma tripla por relação. A orientação dos predicados segue o dicionário.

| ID | Propriedade | Domínio → alcance em `ca:` | Campo no JSON | Superpropriedade |
| --- | --- | --- | --- | --- |
| R01 | `ca:temVinculoDocente` | Docente → UnidadeAcademica | `docencia.unidadesDocentes` | `schema:affiliation` |
| R02 | `ca:temVinculoDiscente` | Discente → UnidadeAcademica | `discencia.unidadesDiscentes` | `schema:affiliation` |
| R03 | `ca:matriculadoEm` | Discente → CursoGraduacao | `discencia.cursos` | — |
| R04 | `ca:temUnidadeResponsavel` | CursoGraduacao → UnidadeAcademica | `unidadeResponsavel` | — |
| R05 | `ca:temUnidadeSuperior` | UnidadeAcademica → UnidadeAcademica | `unidadeSuperior` | `aiiso:part_of` |
| R06 | `ca:incluiDisciplina` | CursoGraduacao → Disciplina | `disciplinas` | `schema:hasCourse` |
| R07 | `ca:ministraDisciplina` | Docente → Disciplina | `docencia.disciplinasMinistradas` | — |
| R08 | `ca:cursaDisciplina` | Discente → Disciplina | `discencia.disciplinasCursadas` | — |
| R09 | `ca:atuaEmArea` | Docente → AreaConhecimento | `docencia.areasAtuacao` | — |
| R10 | `ca:temInteresseEmArea` | Discente → AreaConhecimento | `discencia.areasInteresse` | — |
| R11 | `ca:temAreaMaisAmpla` | AreaConhecimento → AreaConhecimento | `areasMaisAmplas` | `skos:broader` |
| R12 | `ca:temParticipante` | ProjetoPesquisa → Pessoa | `participantes` | — |
| R13 | `ca:temMembro` | GrupoPesquisa → Pessoa | `membros` | — |
| R14 | `ca:associadoAoProjeto` | GrupoPesquisa → ProjetoPesquisa | `projetos` | — |
| R15 | `ca:temAutor` | Publicacao → Pessoa | `autores` | `schema:author` |

`skos:broader` e `schema:author` são emitidos explicitamente junto de R11 e R15, para consumo direto sem configuração de inferência. Os demais alinhamentos da tabela estão nos axiomas da ontologia. O grafo também usa `skos:inScheme` para associar as áreas ao esquema local. A hierarquia SKOS relaciona conceitos, e as especializações OWL relacionam classes. Matrícula atual tem predicado próprio. `schema:alumniOf` cobre vínculo de ex-aluno e `aiiso:teaches` parte de uma organização, por isso a ontologia usa relações locais para matrícula e docência. [Schema.org affiliation](https://schema.org/affiliation), [Schema.org hasCourse](https://schema.org/hasCourse), [Schema.org author](https://schema.org/author), [SKOS Reference](https://www.w3.org/TR/skos-reference/)

As áreas podem ter ligações com conceitos externos por `skos:exactMatch`, `skos:closeMatch`, `skos:broadMatch`, `skos:narrowMatch` ou `skos:relatedMatch`, geradas a partir de `correspondenciasExternas` no JSON. A ontologia declara essas cinco propriedades SKOS como `owl:ObjectProperty`, sem redefinir domínio ou alcance. Os dados atuais usam três `skos:closeMatch` para itens do Wikidata ([ligações externas](ligacoes-externas.md)). `owl:sameAs` continua fora do modelo.

Os links opcionais `ca:linkAcademico` e `ca:linkBibliografico` partem de `ca:Pessoa` e `ca:Publicacao`, respectivamente, e têm alcance `owl:Thing`. Seus valores são recursos identificados por IRI e só aparecem quando registrados na fonte.

## Valores e metadados

| Campo editorial | Representação RDF | Domínio de uso e tipo do valor |
| --- | --- | --- |
| `id` | `schema:identifier` | Todos os registros · texto sem etiqueta de idioma |
| `nome` | `schema:name` | Pessoa, unidade, curso, disciplina e grupo · texto em `pt-BR` |
| `titulo` | `dcterms:title` | Projeto e publicação · texto em `pt-BR` |
| `apresentacao`, `descricao` | `dcterms:description` | Pessoa e projeto, respectivamente · texto em `pt-BR` |
| `formacao`, `docencia.cargo`, `linhaAtuacao` | `ca:formacao`, `ca:cargo`, `ca:linhaAtuacao` | Pessoa, docente e grupo, respectivamente · texto em `pt-BR` |
| `tipoUnidade`, `tipoProducao` | `ca:tipoUnidade`, `ca:tipoProducao` | Unidade e publicação, respectivamente · `xsd:string` |
| `anoPublicacao` | `ca:anoPublicacao` | Publicação · `xsd:integer` |
| `rotuloPreferido`, `rotulosAlternativos`, `definicao` | `skos:prefLabel`, `skos:altLabel`, `skos:definition` | Área de conhecimento · texto em `pt-BR` |
| `instituicaoReferencia` | `ca:instituicaoReferencia` | Documento de instâncias tipado como `schema:Dataset` · texto em `pt-BR` |
| `fontes` | `ca:fonteEditorial` ou `dcterms:source` | Dataset · texto em `pt-BR` para descrição, IRI para fonte identificável |
| `licenca`, `dataAtualizacao` | `dcterms:license`, `dcterms:modified` | Dataset · IRI de licença e literal `xsd:date`, respectivamente |

As propriedades de dados locais que aceitam texto com idioma têm alcance `rdf:PlainLiteral`. A definição formal de domínio e alcance fica nas propriedades locais. O grafo registra a proveniência dos exemplos fictícios, a [licença CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) e a data declarada na [fonte JSON](../exemplos/perfis/dados.json). A instituição de referência contextualiza os registros. [DCMI Metadata Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/), [Schema.org identifier](https://schema.org/identifier), [SKOS Reference](https://www.w3.org/TR/skos-reference/)

## Axiomas e validação editorial

A ontologia declara classes, hierarquias, subpropriedades, domínios, alcances e anotações. `ca:temUnidadeSuperior` é irreflexiva porque uma unidade não pode ser sua própria superior imediata. Docência e discência são compatíveis. O validador JSON continua verificando formato e unicidade dos IDs, preenchimento, cardinalidades, referências e ausência de ciclos. Em OWL, domínio e alcance permitem inferir tipos. Sob a hipótese de mundo aberto, uma tripla ausente pode representar um fato desconhecido. Cardinalidades editoriais e unicidade dos IDs são verificadas na fonte JSON. [OWL 2 Primer](https://www.w3.org/TR/owl2-primer/)

## Percursos usados nas consultas

As seis consultas estão em [`consultas/`](../consultas/) e são explicadas em [consultas-sparql.md](consultas-sparql.md). Elas usam o [Turtle das instâncias](../ontologia/instancias.ttl) e os percursos abaixo.

| Pergunta | Percurso no RDF e cuidados |
| --- | --- |
| PC1 | Partir de `ca:Docente` via `ca:temVinculoDocente` até a unidade direta, que pode ter tipo `ca:Departamento`. |
| PC2 | Selecionar a URI do curso e localizar instâncias de `ca:Discente` que chegam a ela por `ca:matriculadoEm`. |
| PC3 | Selecionar o conceito da área e percorrer `ca:atuaEmArea` a partir de `ca:Docente`. O interesse discente é `ca:temInteresseEmArea`. |
| PC4 | Partir do mesmo `ca:ProjetoPesquisa` e percorrer `ca:temParticipante` até duas URIs de pessoa distintas, com os tipos docente e discente. |
| PC5 | Encontrar `ca:Publicacao` por `ca:temAutor` ou `schema:author` do lado da obra. Procurar outras URIs de autor na mesma publicação, mantendo a obra quando só houver o docente registrado. |
| PC6 | Consultar `ca:temVinculoDocente` e `ca:temVinculoDiscente` para a mesma unidade. Deduplicar pela URI da pessoa. A responsabilidade pelo curso e a unidade superior são relações diferentes. |

Use `schema:name` para pessoas e unidades, `dcterms:title` para projetos e publicações e `skos:prefLabel` para áreas.

## Modelo conceitual e reprodução

O [diagrama conceitual](diagrama-conceitual.svg) representa as entidades e relações R01–R15. O [dicionário](dicionario-dados.md) detalha a estrutura editorial e as cardinalidades. A [pesquisa de vocabulários](pesquisa-vocabularios.md) explica os alinhamentos escolhidos.

Edite a ontologia canônica em `ontologia/` e os registros em JSON. O [guia local](execucao-local.md) apresenta a ordem de geração e os testes. O RDF e as páginas geradas são publicados pelo GitHub Pages.
