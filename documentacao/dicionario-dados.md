# Dicionário de dados · ConectaAcadêmico

O modelo descreve pessoas, vínculos, formação e produção acadêmica do diretório. As cardinalidades são regras da fonte estruturada. As classes e propriedades correspondentes estão na [ontologia de aplicação](ontologia-aplicacao.md).

[Diagrama conceitual em SVG](diagrama-conceitual.svg) · [Fonte editável em Graphviz DOT](diagrama-conceitual.dot)

## Identidade e preenchimento

- Cada registro de entidade tem um `id` textual, obrigatório e singular. O identificador é estável e único em todo o conjunto, com letras minúsculas sem acentos, dígitos e hífens entre segmentos. Exemplos fictícios são `pessoa-01`, `unidade-01` e `curso-01`.
- `Docente` e `Discente` especializam `Pessoa` e herdam seu identificador. Uma pessoa pode exercer ambos os papéis ou aparecer apenas como autora, participante ou membro. A fonte registra o papel pela presença dos dados correspondentes de docência e/ou discência. Cada papel ocorre no máximo uma vez por pessoa. A pessoa é identificada separadamente da página que a descreve.
- `Departamento` especializa `UnidadeAcadêmica`. O valor `departamento` em `tipoUnidade` identifica a especialização e o registro conserva o mesmo `id`.
- Nas tabelas, `1` indica preenchimento obrigatório singular e `0..1` indica preenchimento opcional singular. `1..*` exige ao menos um valor e `0..*` admite ausência. Um texto preenchido deve conter conteúdo após a remoção dos espaços nas extremidades. Listas podem ficar vazias quando opcionais. Referências de uma mesma lista não se repetem.
- Os exemplos são fragmentos ilustrativos. Os registros publicados deverão respeitar a identidade, a privacidade e as condições de uso de cada fonte.

## Entidades e atributos

O atributo comum `id` aplica-se a todas as entidades concretas e é herdado nas especializações. As referências entre entidades estão na tabela de relações.

### Pessoa

Identidade comum a perfis docentes e discentes e a pessoas referenciadas pela pesquisa ou autoria.

| Atributo | Tipo | Preenchimento | Restrição ou exemplo |
| --- | --- | --- | --- |
| `nome` | Texto | Obrigatório · 1 | Nome de exibição. Pode coincidir com o de outra pessoa. Ex. `Pessoa demonstrativa 01`. |
| `apresentacao` | Texto | Opcional · 0..1 | Descrição pública breve da trajetória. |
| `formacao` | Lista de textos | Opcional · 0..* | Resumos de formação ou etapa de estudos para exibição. Ex. `Graduação em andamento`. |
| `linksAcademicos` | Lista de URLs HTTPS | Opcional · 0..* | Destinos distintos, pertinentes e verificados para a própria pessoa. |

### Docente

Pessoa com papel de docência. Usa os atributos comuns e tem vínculo institucional R01, disciplinas ministradas R07 e áreas de atuação R09.

| Atributo próprio | Tipo | Preenchimento | Restrição ou exemplo |
| --- | --- | --- | --- |
| `cargo` | Texto | Opcional · 0..1 | Denominação pública da função quando conhecida. Ex. `Professora associada`. |

### Discente

Pessoa com papel de discência. Usa os atributos de `Pessoa`. Os campos próprios são as referências institucionais R02, de matrícula R03, de disciplinas R08 e de interesse R10. A formação ou etapa de estudos pode ser exibida a partir de `formacao`.

### UnidadeAcadêmica

Unidade organizacional da instituição de referência. Recebe vínculos de pessoas e de cursos. Pode integrar uma estrutura com unidade superior.

| Atributo | Tipo | Preenchimento | Restrição ou exemplo |
| --- | --- | --- | --- |
| `nome` | Texto | Obrigatório · 1 | Nome de exibição. Ex. `Instituto demonstrativo`. |
| `tipoUnidade` | Texto controlado | Obrigatório · 1 | Valores iniciais `instituto`, `departamento` ou `outra`. |

### Departamento

Unidade acadêmica de tipo `departamento`. Herda `id`, `nome`, `tipoUnidade` e as relações de `UnidadeAcadêmica`. Pode ser o alvo direto dos vínculos institucionais.

### CursoGraduação

Programa de formação com matrícula discente, unidade responsável e currículo. Uma disciplina pode integrar o currículo de vários cursos.

| Atributo | Tipo | Preenchimento | Restrição ou exemplo |
| --- | --- | --- | --- |
| `nome` | Texto | Obrigatório · 1 | Nome do programa. Ex. `Bacharelado em Sistemas de Informação`. |

### Disciplina

Componente curricular. Pode ser ministrado por docentes, cursado por discentes e incluído em currículos.

| Atributo | Tipo | Preenchimento | Restrição ou exemplo |
| --- | --- | --- | --- |
| `nome` | Texto | Obrigatório · 1 | Nome do componente. Ex. `Web Semântica`. |

### ÁreaConhecimento

Conceito de vocabulário controlado que pode qualificar uma atuação docente ou um interesse discente.

| Atributo | Tipo | Preenchimento | Restrição ou exemplo |
| --- | --- | --- | --- |
| `rotuloPreferido` | Texto em português | Obrigatório · 1 | Termo principal. Ex. `Dados Abertos`. |
| `definicao` | Texto | Obrigatório · 1 | Definição que distingue o conceito no vocabulário. |
| `rotulosAlternativos` | Lista de textos em português | Opcional · 0..* | Variantes distintas entre si e do rótulo preferido do mesmo conceito. |
| `correspondenciasExternas` | Lista de objetos | Opcional · 0..* | Ligações do conceito local com conceitos de outros vocabulários (LOD). Cada recurso externo aparece uma única vez por área. Campos na tabela abaixo. |

Campos de cada item de `correspondenciasExternas` (todos obrigatórios; outros campos são rejeitados):

| Campo | Tipo | Regra |
| --- | --- | --- |
| `uri` | URI HTTP ou HTTPS | Identificador da entidade externa na forma canônica publicada pela fonte (ex. `http://www.wikidata.org/entity/Q54837`). Não pode estar no namespace do projeto. |
| `predicado` | Texto controlado | `skos:exactMatch`, `skos:closeMatch`, `skos:broadMatch`, `skos:narrowMatch` ou `skos:relatedMatch`. A mesma URI não pode ser `skos:exactMatch` de duas áreas distintas. |
| `rotulo` | Texto | Rótulo do recurso externo, para leitura. |
| `fonte` | URL HTTPS | Página consultada para conferir o recurso, distinta da URI da entidade. |
| `dataVerificacao` | Data ISO 8601 | Dia em que a correspondência foi conferida. |
| `justificativa` | Texto | Razão semântica do predicado escolhido. |

No RDF, cada item gera uma tripla `área → predicado SKOS → URI externa`. Ver [ligações externas](ligacoes-externas.md).

### ProjetoPesquisa

Projeto com pelo menos uma pessoa participante registrada. Pode estar associado a grupos de pesquisa.

| Atributo | Tipo | Preenchimento | Restrição ou exemplo |
| --- | --- | --- | --- |
| `titulo` | Texto | Obrigatório · 1 | Título de exibição. Projetos com o mesmo título continuam distintos pelo `id`. |
| `descricao` | Texto | Obrigatório · 1 | Resumo do objetivo do projeto. |

### GrupoPesquisa

Grupo com integrantes registrados e associação opcional a projetos.

| Atributo | Tipo | Preenchimento | Restrição ou exemplo |
| --- | --- | --- | --- |
| `nome` | Texto | Obrigatório · 1 | Nome de exibição. Ex. `Grupo demonstrativo de dados abertos`. |
| `linhaAtuacao` | Texto | Opcional · 0..1 | Descrição pública breve da linha de pesquisa. |

### Publicação

Produção acadêmica identificável, inclusive trabalho discente. A autoria é uma relação com pessoas e pode estar parcialmente documentada.

| Atributo | Tipo | Preenchimento | Restrição ou exemplo |
| --- | --- | --- | --- |
| `titulo` | Texto | Obrigatório · 1 | Título da produção. Ex. `Experimento didático de dados abertos`. |
| `tipoProducao` | Texto controlado | Obrigatório · 1 | Valores iniciais `artigo`, `trabalho-academico` ou `outra`. |
| `anoPublicacao` | Inteiro | Opcional · 0..1 | Ano com quatro dígitos, quando conhecido. Ex. `2025`. |
| `linkBibliografico` | URL HTTPS | Opcional · 0..1 | Destino legítimo e verificado para a obra. |

## Relações e multiplicidades

A coluna **Origem** indica quantas instâncias da origem podem se ligar a uma instância do destino. A coluna **Destino** indica quantas instâncias do destino podem se ligar a uma instância da origem. A exigência de preenchimento incide sobre o registro que guarda a relação, na origem. Os identificadores R01–R15 são os mesmos do diagrama.

| Relação | Direção | Nome conceitual · campo candidato | Origem | Destino | Participação na origem | Significado |
| --- | --- | --- | --- | --- | --- | --- |
| R01 | Docente → UnidadeAcadêmica | `temVinculoDocente` · `unidadesDocentes` | 0..* | 1..* | Obrigatória | Unidades do vínculo docente. Um departamento vale como unidade. |
| R02 | Discente → UnidadeAcadêmica | `temVinculoDiscente` · `unidadesDiscentes` | 0..* | 1..* | Obrigatória | Unidades do vínculo discente informado no registro. |
| R03 | Discente → CursoGraduação | `matriculadoEm` · `cursos` | 0..* | 1..* | Obrigatória | Cursos de graduação com matrícula vigente registrada. |
| R04 | CursoGraduação → UnidadeAcadêmica | `temUnidadeResponsavel` · `unidadeResponsavel` | 0..* | 1 | Obrigatória | Unidade responsável pelo programa de graduação no diretório. |
| R05 | UnidadeAcadêmica → UnidadeAcadêmica | `temUnidadeSuperior` · `unidadeSuperior` | 0..* | 0..1 | Opcional | Unidade imediatamente superior, quando registrada. |
| R06 | CursoGraduação → Disciplina | `incluiDisciplina` · `disciplinas` | 0..* | 0..* | Opcional | Disciplinas que integram o currículo do curso. |
| R07 | Docente → Disciplina | `ministraDisciplina` · `disciplinasMinistradas` | 0..* | 0..* | Opcional | Disciplinas ministradas pelo docente no contexto informado. |
| R08 | Discente → Disciplina | `cursaDisciplina` · `disciplinasCursadas` | 0..* | 0..* | Opcional | Disciplinas que o discente cursa ou cursou, sem inferir aprovação. |
| R09 | Docente → ÁreaConhecimento | `atuaEmArea` · `areasAtuacao` | 0..* | 0..* | Opcional | Áreas em que o docente atua em pesquisa. |
| R10 | Discente → ÁreaConhecimento | `temInteresseEmArea` · `areasInteresse` | 0..* | 0..* | Opcional | Áreas de interesse do discente. |
| R11 | ÁreaConhecimento → ÁreaConhecimento | `temAreaMaisAmpla` · `areasMaisAmplas` | 0..* | 0..* | Opcional | Conceitos imediatamente mais amplos na classificação local. |
| R12 | ProjetoPesquisa → Pessoa | `temParticipante` · `participantes` | 0..* | 1..* | Obrigatória | Pessoas com participação registrada no projeto. |
| R13 | GrupoPesquisa → Pessoa | `temMembro` · `membros` | 0..* | 1..* | Obrigatória | Pessoas com participação registrada no grupo. |
| R14 | GrupoPesquisa → ProjetoPesquisa | `associadoAoProjeto` · `projetos` | 0..* | 0..* | Opcional | Projetos associados ao grupo, independentemente dos membros individuais. |
| R15 | Publicação → Pessoa | `temAutor` · `autores` | 0..* | 0..* | Opcional | Pessoas com autoria registrada. Coautores são apurados a partir da mesma publicação. |

Nas relações, um destino máximo de `1` corresponde a uma referência singular por `id`. Destino máximo `*` corresponde a uma lista de referências por `id`. Os dados de papel de docência e discência guardam somente os campos próprios de seus papéis.

## Metadados e integridade

| Metadado editorial | Tipo | Preenchimento | Uso |
| --- | --- | --- | --- |
| `instituicaoReferencia` | Texto | Obrigatório · 1 por conjunto | Instituição de referência do diretório. As unidades compartilham esse contexto. |
| `fontes` | Lista de referências (textos ou URIs) | Antes de publicar · 1..* por conjunto | Identificar fontes e distinguir o que é fictício. Registros com origens distintas devem indicar a fonte aplicável. |
| `licenca` | URI da licença | Antes de publicar · 1 por conjunto | Indicar os termos de reutilização do conjunto, depois de verificar a compatibilidade das fontes. |
| `dataAtualizacao` | Data ISO 8601 (`AAAA-MM-DD`) | Opcional · 0..1 por conjunto | Registrar quando a informação for pertinente. |

1. Toda referência interna resolve para um identificador existente do tipo esperado. A conferência de tipo considera as especializações. Títulos e nomes são rótulos de exibição.
2. R01 e R02 registram vínculos de natureza diferente. A unidade responsável pelo curso em R04 pode coincidir com a de R02, mas os campos respondem a fatos distintos. R05 representa uma unidade imediatamente superior. Os encadeamentos R05 e R11 devem ser acíclicos e excluir autorreferências no conjunto editorial.
3. Registrar cada fato uma vez na origem indicada. Navegações inversas, como os projetos e as publicações de uma pessoa, são recuperadas a partir das referências declaradas. Integrar um grupo, atuar numa área e assinar uma publicação são fatos independentes.
4. A ausência de uma lista de autores significa informação indisponível no conjunto. Um autor conhecido que também tenha perfil reutiliza o `id` de sua pessoa. Endereços, fontes e licenças passam por revisão antes da publicação.
5. A demonstração deverá usar quatro pessoas distintas para os quatro perfis mínimos e incluir os casos positivos e negativos de [PC1–PC6](../proposta/perguntas-competencia.md). Essa cobertura é uma exigência do conjunto de demonstração, enquanto as cardinalidades da tabela são regras de cada registro.
