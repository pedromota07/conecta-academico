# Perguntas de competência

As perguntas abaixo seguem a seção 5 do enunciado. As entidades e relações são descritas em linguagem de domínio para orientar a modelagem. Os cenários são especificações para uma futura massa de demonstração.

| Pergunta | Dados e entidades | Relação necessária | Condição de aceitação proposta |
| --- | --- | --- | --- |
| **PC1.** Quais docentes estão cadastrados e a quais departamentos ou unidades acadêmicas estão vinculados? | Identificador, nome e tipo de cada pessoa. Identificador e nome da unidade. | Docente tem vínculo com departamento ou unidade. | Listar os dois docentes e seus vínculos. Usar unidades distintas na demonstração e verificar que um discente da mesma unidade fica fora da lista de docentes. Uma seleção por unidade deve distinguir os dois casos. |
| **PC2.** Quais discentes pertencem a determinado curso? | Identificador e nome de discente e de curso. | Discente está vinculado a um curso de graduação. | Usar pelo menos um discente no curso consultado e outro em curso diferente. Usar a identidade do curso na seleção. |
| **PC3.** Quais docentes atuam em determinada área de pesquisa? | Identificador e nome do docente. Identificador e rótulo preferido da área. | Docente atua em uma área de pesquisa controlada. | Incluir um docente na área consultada e outro em área diferente. Se um discente tiver interesse no mesmo tema, esse interesse não conta como atuação docente. |
| **PC4.** Quais docentes e discentes participam do mesmo projeto de pesquisa? | Identificador e tipo da pessoa, identificador e título do projeto. | Pessoas com papéis distintos referenciam o mesmo projeto. | Incluir um projeto com ao menos um docente e um discente e outro projeto com um único tipo de perfil. Conferir que as participações se cruzam pelo identificador do projeto, inclusive se houver títulos semelhantes. |
| **PC5.** Quais publicações estão associadas a determinado docente e quem são seus coautores, quando representados? | Identificadores e nomes do docente e dos autores. Identificador e título de cada publicação. | Para a demonstração, a associação docente–publicação é por autoria. Coautores são outros autores da mesma publicação. | Usar uma publicação com um docente e pelo menos outro autor identificado e uma segunda publicação desse docente sem coautor registrado. Retornar ambas e mostrar coautores apenas onde houver registro, excluindo o próprio docente da lista de coautores. |
| **PC6.** Quais pessoas estão vinculadas a uma unidade acadêmica específica, sejam docentes ou discentes? | Identificadores, nomes e tipos das pessoas. Identificador e nome da unidade. | Os dois tipos de perfil têm um vínculo explícito com a unidade que será consultada. O curso também identifica sua unidade responsável. | Incluir um docente e um discente vinculados à unidade selecionada e pelo menos uma pessoa em outra unidade. Verificar que a seleção reúne os dois tipos e distingue as unidades pelas suas identidades. |

## Cobertura da demonstração

Com quatro perfis, é possível atender aos seis cenários. A proposta usa dois cursos, duas unidades e duas áreas para distinguir os filtros. Um dos docentes e um dos discentes compartilham unidade e projeto. O segundo projeto pode ter somente o outro docente. Para a coautoria, dois dos perfis já cadastrados podem compartilhar uma publicação fictícia.

PC4 e PC5 evidenciam o requisito de pelo menos duas consultas que explorem relações entre tipos de entidade. A primeira atravessa as participações de pessoas no projeto e a segunda percorre a autoria compartilhada de uma publicação.

## Implementação e evidências (Etapa 5)

| Pergunta | Consulta | Parâmetros de demonstração | Resultado obtido |
| --- | --- | --- | --- |
| PC1 | [consulta01.rq](../consultas/consulta01.rq) | — | Ana → Departamento de Computação; Rafael → Departamento de Gestão da Informação |
| PC2 | [consulta02.rq](../consultas/consulta02.rq) | `curso-sistemas-informacao`, `curso-biblioteconomia` | João; Clara |
| PC3 | [consulta03.rq](../consultas/consulta03.rq) | `area-dados-abertos`, `area-curadoria-digital` | Ana (o interesse de João não conta); Rafael |
| PC4 | [consulta04.rq](../consultas/consulta04.rq) | — | Projeto Catálogo acadêmico de dados abertos: Ana e João |
| PC5 | [consulta05.rq](../consultas/consulta05.rq) | `pessoa-ana`, `pessoa-rafael` | Ana: obra com Rafael e obra sem coautor registrado; Rafael: obra com Ana |
| PC6 | [consulta06.rq](../consultas/consulta06.rq) | `unidade-computacao`, `unidade-gestao-informacao`, `unidade-ciencias-exatas` | Ana e João; Rafael e Clara; nenhum (vínculo direto) |

Os resultados completos estão em [consultas/resultados/](../consultas/resultados/README.md) e as explicações em [consultas-sparql.md](../documentacao/consultas-sparql.md).
