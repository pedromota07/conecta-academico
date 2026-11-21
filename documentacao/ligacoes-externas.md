# Ligações com recursos externos (LOD)

O enunciado (§ 4) pede ao menos três recursos externos relacionados aos dados, com justificativa e sem uso de `owl:sameAs` como associação genérica. As ligações escolhidas partem das áreas de conhecimento, que são conceitos SKOS locais. Pessoas, publicações e unidades são fictícias e não foram ligadas a identidades, perfis, ORCIDs ou DOIs reais.

## Ligações implementadas

| Recurso local | URI externa (entidade) | Página consultada | Predicado | Justificativa | Conferido em |
| --- | --- | --- | --- | --- | --- |
| `inst:area-web-semantica` (Web Semântica) | `http://www.wikidata.org/entity/Q54837` (Semantic Web) | https://www.wikidata.org/wiki/Q54837 | `skos:closeMatch` | O item é classificado como campo de estudo e disciplina acadêmica e também descreve a extensão da Web para troca de dados. A área local corresponde ao campo de estudo; como o item abrange também a tecnologia, a correspondência é próxima e não exata. | 21/11/2026 |
| `inst:area-dados-abertos` (Dados abertos) | `http://www.wikidata.org/entity/Q309901` (open data) | https://www.wikidata.org/wiki/Q309901 | `skos:closeMatch` | O item descreve dados acessíveis e utilizáveis por outras pessoas e é classificado como conceito e campo de trabalho. A área local trata da publicação desses dados como tema de pesquisa; o recorte local é mais estreito. | 21/11/2026 |
| `inst:area-curadoria-digital` (Curadoria digital) | `http://www.wikidata.org/entity/Q5276060` (digital curation) | https://www.wikidata.org/wiki/Q5276060 | `skos:closeMatch` | O item descreve seleção, preservação, manutenção, coleta e arquivamento de ativos digitais e é subclasse de curadoria (Q63386008). A definição local cobre seleção, documentação e preservação. Os conceitos são muito próximos; a correspondência próxima evita propagar equivalência por transitividade. | 21/11/2026 |

## Escolha do predicado

- `skos:closeMatch` indica conceitos suficientemente semelhantes para serem usados de forma intercambiável em algumas aplicações, sem ser transitivo ([SKOS Reference, § 10](https://www.w3.org/TR/skos-reference/#mapping)). Foi adotado nos três casos porque os itens do Wikidata são entidades gerais (campo de estudo, tipo de dado, prática), e as áreas locais são termos de um vocabulário de pesquisa com definição própria.
- `skos:exactMatch` não foi usado: é transitivo e afirmaria que os conceitos são intercambiáveis em geral. O validador ainda impede que o mesmo recurso seja `exactMatch` de duas áreas locais distintas.
- `owl:sameAs` e `owl:equivalentClass` não são usados: as áreas não são o mesmo indivíduo que o item externo, e a proximidade temática não é equivalência de classes.
- Se uma associação futura for apenas temática, o esquema aceita `skos:relatedMatch`; `skos:broadMatch` e `skos:narrowMatch` cobrem diferenças de generalidade.

## URI da entidade e página

A URI canônica publicada pelo Wikidata nas próprias serializações RDF é `http://www.wikidata.org/entity/Q…` (prefixo `wd:` no Turtle de `Special:EntityData`). Ela é mantida com `http`, como a fonte publica, e não é trocada por `https`. A página `https://www.wikidata.org/wiki/Q…` é um documento sobre a entidade e aparece só no campo `fonte` e nos links do site.

## Condições de reutilização

Segundo as [condições de licenciamento do Wikidata](https://www.wikidata.org/wiki/Wikidata:Licensing), os dados estruturados do espaço principal estão sob CC0 1.0. Textos de outras páginas do projeto estão sob CC BY-SA. O projeto reutiliza apenas URIs e rótulos curtos dos itens, e as justificativas foram redigidas pelo grupo. Isso não define a licença do conjunto ConectaAcadêmico, que continua pendente de decisão do trio.

## Representação na fonte e no RDF

Cada área pode ter o campo opcional `correspondenciasExternas` no [JSON editorial](../exemplos/perfis/dados.json), descrito no [dicionário de dados](dicionario-dados.md). O validador exige `uri` (HTTP/HTTPS absoluta, fora do namespace do projeto), `predicado` (uma das cinco relações de mapeamento SKOS), `rotulo`, `fonte` (HTTPS), `dataVerificacao` (AAAA-MM-DD) e `justificativa`, rejeita campos desconhecidos e URIs repetidas na mesma área. O [gerador RDF](../codigo-fonte/gerar_rdf.py) emite uma tripla por correspondência, com objeto `URIRef`:

```turtle
inst:area-web-semantica skos:closeMatch <http://www.wikidata.org/entity/Q54837> .
```

Os metadados (rótulo, fonte, data e justificativa) ficam no JSON, nesta página e em `dados.html`; o RDF registra apenas a ligação.

## Verificação

- **Local e reproduzível:** `testes/test_lod.py` confere as três triplas, a igualdade entre o JSON e o RDF, a ausência de `owl:sameAs`, a permanência após regeneração, a cópia em `docs/ontologia/` e a rejeição de entradas inválidas sem alterar a saída anterior. A consulta [`ligacoes-externas.rq`](../consultas/ligacoes-externas.rq) lista as três ligações ([resultado](../consultas/resultados/ligacoes-externas.json)). Os testes não acessam a Internet.
- **Externa, em 21/11/2026, feita à parte com `curl -m 20`/`-m 25`:** `https://www.wikidata.org/wiki/Special:EntityData/Q54837.json` (e Q309901, Q5276060) respondeu 200 com rótulos e descrições conferidos; o Turtle de `Special:EntityData/Q….ttl` respondeu 200 e usa `wd:` = `http://www.wikidata.org/entity/`; uma requisição a `https://www.wikidata.org/entity/Q54837` com `Accept: text/turtle` respondeu 303 para `Special:EntityData/Q54837`. A requisição a `http://www.wikidata.org/entity/Q54837` redirecionou (301) para a versão HTTPS. Nenhuma falha foi registrada. Para repetir:

```bash
curl -s -m 20 -o /dev/null -w "%{http_code}\n" https://www.wikidata.org/wiki/Special:EntityData/Q54837.json
curl -s -m 20 -o /dev/null -w "%{http_code} %{redirect_url}\n" -H "Accept: text/turtle" https://www.wikidata.org/entity/Q54837
```

Um 429 ou indisponibilidade momentânea do Wikidata deve ser registrado e repetido mais tarde; não afeta a suíte local.
