# Proposta do ConectaAcadêmico

O ConectaAcadêmico é um diretório acadêmico demonstrativo da UFRRJ. Estudantes, docentes e visitantes podem buscar perfis e descobrir vínculos institucionais, interesses de pesquisa e produções acadêmicas. A publicação de um grafo RDF permite explorar essas mesmas relações com SPARQL.

## Funcionalidades

- Catálogo público com busca e filtro por papel, dois perfis docentes e dois discentes fictícios.
- Páginas individuais geradas de uma fonte JSON comum, com HTML e CSS adaptados dos modelos da disciplina.
- Ontologia OWL, dados em Turtle, seis consultas executáveis localmente e três ligações de áreas do conhecimento ao Wikidata.

O escopo cobre consulta e publicação de perfis. Matrícula, lançamento de notas, edição por visitantes e gestão de contas ficam fora da aplicação.

## Seleção dos dados

Formação, disciplinas e áreas ajudam o visitante a identificar a trajetória e os temas de cada pessoa. Vínculos docentes, unidades responsáveis pelos cursos e matrículas descrevem relações institucionais distintas. Projetos, grupos e publicações registram participação e autoria, permitindo localizar colaborações nas consultas.

O identificador do recurso é estável entre o JSON, o grafo e a página. Uma pessoa pode acumular papéis usando o mesmo identificador. As relações partem dos identificadores, inclusive quando dois nomes coincidem. Links acadêmicos e bibliográficos são opcionais e dependem de um destino verificável. O [dicionário de dados](../documentacao/dicionario-dados.md) define campos e cardinalidades.

## Demonstração e avaliação

O [site público](https://pedromota07.github.io/conecta-academico/) apresenta os quatro perfis e publica os dados sob CC BY 4.0. As [perguntas de competência](perguntas-competencia.md) cobrem vínculos, cursos, áreas, participação em projetos e coautoria. A [ontologia](../documentacao/ontologia-aplicacao.md) descreve URIs, vocabulários e regras. O [guia local](../documentacao/execucao-local.md) permite regenerar os artefatos e executar os testes.
