# Decisões de modelagem · ConectaAcadêmico

Esta etapa especifica o modelo conceitual e prepara a implementação semântica. O [dicionário de dados](dicionario-dados.md) define a estrutura editorial e as cardinalidades. O [diagrama](diagrama-conceitual.svg) representa as mesmas relações. A escolha de vocabulários parte da [pesquisa da Etapa 1](pesquisa-vocabularios.md).

## Classes e especializações candidatas

| Classe | Papel no modelo e alinhamento candidato |
| --- | --- |
| `Pessoa` | Identidade comum de perfis e autores. Alinhar a `schema:Person`. |
| `Docente` | Especialização de `Pessoa` para o papel de docência. |
| `Discente` | Especialização de `Pessoa` para o papel de discência. Uma pessoa pode pertencer a ambas as especializações e mantém seu identificador. |
| `UnidadeAcadêmica` | Estrutura organizacional. Alinhar a `schema:Organization` e avaliar termos AIISO para tipos mais específicos. |
| `Departamento` | Especialização de `UnidadeAcadêmica`. Avaliar alinhamento com `aiiso:Department`. |
| `CursoGraduação` | Programa de graduação que reúne componentes curriculares. Avaliar `aiiso:Programme` e `schema:EducationalOccupationalProgram` conforme o recorte de cada termo. |
| `Disciplina` | Componente curricular. `schema:Course` é candidato para o módulo de ensino. Uma disciplina pode constar em mais de um programa. |
| `ÁreaConhecimento` | Conceito temático. Alinhar a `skos:Concept` e avaliar um `skos:ConceptScheme` para o vocabulário local. |
| `ProjetoPesquisa` | Atividade de pesquisa com participantes. Manter classe local para a atividade descrita. `schema:ResearchProject` é uma especialização de organização e exige avaliação antes de qualquer alinhamento. |
| `GrupoPesquisa` | Coletivo de pessoas. Manter classe local e avaliar `schema:Organization` nos casos que representem uma organização. |
| `Publicação` | Produção acadêmica em sentido amplo. Alinhar a `schema:CreativeWork` e usar `schema:ScholarlyArticle` somente para artigos acadêmicos. |

A sobreposição de papéis decorre do domínio. Uma docente também pode estar matriculada em um curso e ter relações específicas para cada papel. Por isso, não se propõe disjunção entre `Docente` e `Discente`. As correspondências externas são candidatas a reúso, subclasse ou subpropriedade conforme a semântica de cada termo. Equivalências formais dependem de revisão. [Schema.org Person](https://schema.org/Person), [Schema.org ResearchProject](https://schema.org/ResearchProject), [AIISO](https://vocab.org/aiiso/), [SKOS](https://www.w3.org/TR/skos-reference/)

## Propriedades de objeto

Os nomes são candidatos e compartilham os identificadores R01–R15 do dicionário. Domínio e alcance são os tipos que participam de cada relação neste modelo. Para vocabulários reutilizados, a especialização local preserva a definição externa.

| Relação | Domínio proposto | Alcance proposto | Reúso ou extensão |
| --- | --- | --- | --- |
| R01 · `temVinculoDocente` | Docente | UnidadeAcadêmica | Propriedade própria. Candidata a subpropriedade de `schema:affiliation` para projetar a afiliação genérica. |
| R02 · `temVinculoDiscente` | Discente | UnidadeAcadêmica | Propriedade própria. Candidata a subpropriedade de `schema:affiliation`, preservando a natureza discente. |
| R03 · `matriculadoEm` | Discente | CursoGraduação | Propriedade própria para matrícula em um programa. `schema:alumniOf` descreve ex-alunos e tem outro significado. |
| R04 · `temUnidadeResponsavel` | CursoGraduação | UnidadeAcadêmica | Propriedade própria para responsabilidade institucional no recorte do diretório. |
| R05 · `temUnidadeSuperior` | UnidadeAcadêmica | UnidadeAcadêmica | Propriedade própria para a unidade imediatamente superior. Avaliar seu alinhamento como subpropriedade de `aiiso:part_of`. |
| R06 · `incluiDisciplina` | CursoGraduação | Disciplina | Reutilizar `schema:hasCourse` se programa e disciplina forem alinhados aos tipos correspondentes. Nome local candidato para a relação conceitual. |
| R07 · `ministraDisciplina` | Docente | Disciplina | Propriedade própria. `aiiso:teaches` tem uma organização como origem. |
| R08 · `cursaDisciplina` | Discente | Disciplina | Propriedade própria para o registro de participação do discente em uma disciplina. |
| R09 · `atuaEmArea` | Docente | ÁreaConhecimento | Propriedade própria para a atuação em pesquisa. O destino pode ser um `skos:Concept`. |
| R10 · `temInteresseEmArea` | Discente | ÁreaConhecimento | Propriedade própria para interesse. A seleção de um mesmo tema conserva as duas relações distintas. |
| R11 · `temAreaMaisAmpla` | ÁreaConhecimento | ÁreaConhecimento | Reutilizar `skos:broader` para conceitos imediatamente mais amplos no esquema local. |
| R12 · `temParticipante` | ProjetoPesquisa | Pessoa | Propriedade própria para participação, que pode existir independentemente de autoria ou integração a um grupo. |
| R13 · `temMembro` | GrupoPesquisa | Pessoa | Propriedade própria para composição do grupo no diretório. |
| R14 · `associadoAoProjeto` | GrupoPesquisa | ProjetoPesquisa | Propriedade própria para associar grupo e projeto. Mantém-se independente da participação individual. |
| R15 · `temAutor` | Publicação | Pessoa | Reutilizar `schema:author` para a autoria de obras. No diretório, o alvo é `Pessoa`. Se forem necessários domínio e alcance formais restritos, avaliar uma subpropriedade local. |

Em R12, uma participação pertence à pessoa. Os tipos docente e discente são recuperados dos papéis daquela pessoa no diretório. O modelo atual representa a participação conjunta sem registrar a função exercida por cada pessoa no projeto. Em R15, a autoria fica vinculada à publicação e coautores são recuperados pela identidade da obra e de seus autores. [Afiliação em Schema.org](https://schema.org/affiliation), [currículo em Schema.org](https://schema.org/hasCourse), [autoria em Schema.org](https://schema.org/author), [hierarquia SKOS](https://www.w3.org/TR/skos-reference/#semantic-relations)

## Campos literais, anotações e metadados

Os tipos abaixo são candidatos a valores literais ou referências na futura representação. O tipo de cada termo reutilizado, inclusive quando for anotação ou tiver alcance em recursos, será preservado.

| Campos | Domínio no modelo | Valor ou alcance proposto | Reúso ou extensão |
| --- | --- | --- | --- |
| `id` | Entidades da aplicação | Texto com chave local estável | Origem para o identificador público. Avaliar `schema:identifier` se a chave também precisar ser exposta como dado. |
| `nome` | Pessoa, UnidadeAcadêmica, CursoGraduação, Disciplina e GrupoPesquisa | Texto | `schema:name`. |
| `titulo` | ProjetoPesquisa e Publicação | Texto | `dcterms:title`. |
| `apresentacao`, `descricao` | Pessoa e ProjetoPesquisa, respectivamente | Texto | `dcterms:description`. |
| `cargo` | Docente | Texto | `schema:jobTitle` quando indicar o cargo público. |
| `formacao` | Pessoa | Textos | Propriedade local para os resumos editoriais. `schema:alumniOf` exigiria uma relação própria com uma organização e evidência de vínculo como ex-aluno. |
| `linksAcademicos`, `linkBibliografico` | Pessoa e Publicação, respectivamente | URLs HTTPS verificadas | Usar `schema:url` para URL do próprio recurso quando seu significado couber. Usar uma propriedade local de referência nos demais casos. |
| `tipoUnidade` | UnidadeAcadêmica | Valor controlado | Usar o tipo editorial para selecionar a classe local. Para departamentos, a tipagem em `Departamento` evita repetir a classificação sem necessidade. |
| `rotuloPreferido`, `rotulosAlternativos`, `definicao` | ÁreaConhecimento | Literais textuais com idioma, quando conhecido | Reutilizar `skos:prefLabel`, `skos:altLabel` e `skos:definition`. |
| `linhaAtuacao` | GrupoPesquisa | Texto | Propriedade local para uma descrição da linha, se publicada separadamente. |
| `tipoProducao`, `anoPublicacao` | Publicação | Texto controlado e inteiro, respectivamente | Termos locais ou tipagem mais específica para a categoria. Preservar o ano sem inventar mês ou dia. |
| `instituicaoReferencia`, `fontes`, `licenca`, `dataAtualizacao` | Metadados do conjunto e fonte específica do registro quando aplicável | Nome textual de referência institucional, recurso de origem quando identificável, URI da licença e data | Usar `dcterms:source`, `dcterms:license` e `dcterms:modified` nos casos correspondentes. A instituição de contexto não implica autoria ou publicação institucional. |

Os dados de origem podem incluir uma descrição editorial quando o material não tiver uma URL pública. A futura representação com `dcterms:source` usará um recurso de origem identificável. O repertório de domínios e alcances não altera os termos originais. [Schema.org](https://schema.org/), [DCMI Metadata Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/), [rótulos e notas em SKOS](https://www.w3.org/TR/skos-reference/#labels)

## Validação da fonte e semântica OWL

- **Validação da fonte candidata em JSON.** Verificar chaves e campos obrigatórios, tipos, preenchimento e limites de listas. A integridade de referências, a unicidade global de identificadores, os ciclos e a cobertura das quatro pessoas e dos cenários de demonstração exigem verificações entre registros do conjunto.
- **Axiomas candidatos.** As três especializações e os domínios e alcances das propriedades locais expressam conhecimento. Em OWL, domínio e alcance permitem inferir tipos. O uso de um predicado de docência pode levar à inferência de que seu sujeito é docente. Uma regra editorial sobre preenchimento poderá permanecer exclusivamente na validação e só deve se tornar axioma se descrever o domínio.
- **Mundo aberto.** Um fato ausente pode ser desconhecido. Uma restrição existencial pode ser satisfeita por um valor que não aparece explicitamente no documento. Sob OWL, dois nomes diferentes também não garantem indivíduos distintos. Uma restrição máxima pode levar à inferência de identidade em vez de acusar um erro de cadastro. Cada registro e suas referências devem ser validados na fonte, ainda que haja axiomas relacionados.
- **Hierarquias.** As especializações ligam classes. R11 liga conceitos temáticos por `skos:broader`. A ligação direta temática não indica que um conceito seja subclasse de outro. A consulta PC3 usa a área explicitamente registrada, sem expansão automática por áreas mais amplas neste recorte.

[OWL 2 Primer](https://www.w3.org/TR/owl2-primer/), [SKOS Reference](https://www.w3.org/TR/skos-reference/)

## Conferência das seis perguntas de competência

Usam-se quatro pessoas fictícias e distintas como exemplos conceituais. D1 e D2 têm papel docente. S1 e S2 têm papel discente. U1 e U2 são unidades diferentes, C1 e C2 são cursos diferentes e A1 e A2 são áreas diferentes. P1 e P2 são projetos. B1 e B2 são publicações. Os caminhos a seguir descrevem como obter a resposta a partir dos fatos registrados.

| Pergunta | Caminho conceitual | Caso ilustrativo e resposta esperada |
| --- | --- | --- |
| PC1 · Docentes e unidades | `Docente` → R01 → `UnidadeAcadêmica`. A unidade também pode ter tipo `Departamento`. | D1 tem R01 para U1 e D2 para U2. A resposta inclui essas duas ligações. S1, com vínculo discente em U1, fica fora da listagem docente. |
| PC2 · Discentes de um curso | `CursoGraduação` ← R03 ← `Discente`. Selecionar o curso pelo identificador. | S1 está matriculado em C1 e S2 em C2. Para C1, a resposta é S1. |
| PC3 · Docentes em uma área | `ÁreaConhecimento` ← R09 ← `Docente`. R10 documenta interesse discente com significado distinto. | D1 atua em A1 e D2 em A2. Para A1, a resposta é D1, mesmo se S1 tiver interesse nessa área. |
| PC4 · Projeto com docentes e discentes | `ProjetoPesquisa` → R12 → duas instâncias distintas de `Pessoa`, uma com papel docente e outra com papel discente. | P1 registra D1 e S1. P2 registra somente D2. A resposta inclui P1 com D1 e S1. Um só participante com os dois papéis é insuficiente. |
| PC5 · Publicação e coautores | `Docente` ← R15 ← `Publicação` → R15 → demais instâncias de `Pessoa`, quando a autoria estiver registrada. | B1 registra D1 e D2 entre os autores. B2 registra apenas D1. Para D1, retornam B1 com coautor D2 e B2 sem coautor informado. |
| PC6 · Pessoas vinculadas à mesma unidade | `UnidadeAcadêmica` ← R01 ← `Docente` ou `UnidadeAcadêmica` ← R02 ← `Discente`. Unificar as respostas por identificador de pessoa. | Em U1, D1 tem vínculo docente e S1 tem vínculo discente. U2 tem D2 e S2. Para U1, retornam D1 e S1. Se a mesma pessoa tiver ambos os vínculos em U1, aparece uma vez, com os papéis pertinentes. |

R04 indica a unidade responsável pelo curso. R05 indica subordinação organizacional. Na PC6, ambas podem contextualizar o vínculo, mas a unidade da resposta é a registrada diretamente em R01 ou R02. PC4 e PC5 atravessam tipos distintos de entidade, conforme a exigência do professor.

## Pendências para a Etapa 3

- Definir o namespace local, padrões de URIs e tratamento das páginas que descrevem os recursos. Confirmar se haverá publicação explícita da chave editorial.
- Revisar os alinhamentos, a reutilização ou importação de vocabulários, os termos locais e os axiomas que expressam conhecimento do domínio. Conferir a consistência da ontologia e as inferências em ambiente compatível.
- Selecionar os mecanismos de validação editorial e do grafo, ajustar a tipagem dos literais e definir como registrar fontes, licença e data. Verificar os exemplos reais da demonstração antes de publicá-los.
- Identificar e verificar pelo menos três recursos externos. Justificar os predicados conforme os referentes, considerando mapeamentos SKOS entre conceitos quando couber. Reservar `owl:sameAs` para identidade comprovada. Confirmar hospedagem e ambiente de execução SPARQL na fase correspondente.
