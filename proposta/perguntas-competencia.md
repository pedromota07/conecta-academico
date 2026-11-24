# Perguntas de competência

As seis perguntas seguem a seção 5 do enunciado. A demonstração consulta o RDF fictício publicado pelo projeto.

| Pergunta | Consulta | Resultado de demonstração |
| --- | --- | --- |
| **PC1.** Quais docentes estão cadastrados e a quais departamentos ou unidades acadêmicas estão vinculados? | [consulta01.rq](../consultas/consulta01.rq) | Ana → Departamento de Computação. Rafael → Departamento de Gestão da Informação. |
| **PC2.** Quais discentes pertencem a determinado curso? | [consulta02.rq](../consultas/consulta02.rq) | João em Sistemas de Informação e Clara em Biblioteconomia. |
| **PC3.** Quais docentes atuam em determinada área de pesquisa? | [consulta03.rq](../consultas/consulta03.rq) | Ana em Dados abertos e Rafael em Curadoria digital. |
| **PC4.** Quais docentes e discentes participam do mesmo projeto de pesquisa? | [consulta04.rq](../consultas/consulta04.rq) | Ana e João no projeto Catálogo acadêmico de dados abertos. |
| **PC5.** Quais publicações estão associadas a determinado docente e quem são seus coautores, quando representados? | [consulta05.rq](../consultas/consulta05.rq) | Ana tem uma publicação com Rafael e outra sem coautor registrado. Rafael tem uma publicação com Ana. |
| **PC6.** Quais pessoas estão vinculadas a uma unidade acadêmica específica, sejam docentes ou discentes? | [consulta06.rq](../consultas/consulta06.rq) | Ana e João em Computação, Rafael e Clara em Gestão da Informação e nenhum vínculo direto em Ciências Exatas. |

PC4 e PC5 atravessam tipos distintos de entidade, como exige o enunciado. A primeira relaciona pessoas e projetos. A segunda relaciona pessoas e publicações.

Os [parâmetros e percursos SPARQL](../documentacao/consultas-sparql.md) permitem reproduzir as respostas. Os [resultados JSON](../consultas/resultados/README.md) preservam os valores e as URIs retornados.
