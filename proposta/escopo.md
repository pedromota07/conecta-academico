# Escopo proposto

## Objetivo e público

Oferecer um diretório público de perfis acadêmicos que ajude estudantes, docentes e visitantes a identificar vínculos institucionais, interesses de pesquisa e trabalhos acadêmicos. A publicação de dados estruturados e interligados permite consultar essas relações e reutilizar os dados com a licença indicada. O diretório é uma aplicação demonstrativa da disciplina Web Semântica da UFRRJ.

## Funcionalidades e limites

- Disponibilizar uma lista de perfis com acesso às páginas individuais de pelo menos dois docentes e dois discentes. Usar os exemplos do professor como ponto de partida visual e para os dados demonstrativos e acrescentar ao menos um perfil fictício de cada tipo.
- Gerar as páginas com base em registros estruturados. Exibir os campos pertinentes ao tipo de perfil e as relações com unidades, cursos, áreas, projetos, grupos, disciplinas e produções.
- Publicar o site, a documentação, a ontologia e os dados RDF, com URIs públicas e pelo menos três ligações externas pertinentes e justificadas. Disponibilizar o endereço do site e instruções para reproduzir as seis respostas SPARQL.
- Considerar como opcionais filtros por tipo de perfil, unidade ou área e um endpoint SPARQL público. A seleção de filtros na interface é independente da cobertura das seis perguntas no conjunto RDF.

A proposta abrange consulta e publicação de informações acadêmicas. Operações de matrícula, lançamento de notas, acesso a prontuários, edição de perfis por visitantes e gestão de contas ficam fora do escopo. HTML, CSS e JavaScript com JSON como fonte editorial única são a primeira opção para revisão do trio. A ontologia deverá descrever a estrutura dos registros e os dados RDF deverão corresponder ao conteúdo exibido no site. A estratégia de exportação fica para depois da modelagem. Para uma demonstração de quatro perfis, a hospedagem estática é uma opção em avaliação.

## Dados mínimos propostos

Cada recurso terá um identificador estável. As referências entre registros usarão esses identificadores, inclusive quando duas pessoas ou dois recursos tiverem o mesmo nome. As listas de atividades e produções podem ficar vazias para um perfil individual quando a informação for ausente ou inaplicável. O conjunto de demonstração deve cobrir os casos previstos nas [perguntas de competência](perguntas-competencia.md).

| Recurso | Dados e relações previstos |
| --- | --- |
| Docente | Identificador, nome, vínculo e unidade/departamento. Formação, áreas de atuação, disciplinas ministradas, projetos, grupos, publicações e links acadêmicos pertinentes. |
| Discente | Identificador, nome, vínculo, curso e unidade acadêmica vinculada. Formação ou etapa acadêmica, áreas de interesse, projetos, grupos, disciplinas cursadas quando pertinentes, trabalhos e links acadêmicos pertinentes. |
| Curso de graduação | Identificador, nome e unidade responsável. Referências a disciplinas se a relação fizer parte da demonstração. |
| Departamento ou unidade acadêmica | Identificador, nome, tipo de unidade e instituição de referência. Unidade superior quando aplicável. |
| Área de pesquisa ou interesse | Identificador, rótulo preferido em português e definição breve. Termos alternativos ou área mais ampla quando úteis. |
| Projeto de pesquisa | Identificador, título, descrição breve e participantes referenciados por identificador. |
| Disciplina | Identificador, nome e vínculo com curso ou unidade quando pertinente. As relações de docência e de participação discente têm significados distintos. |
| Publicação ou trabalho | Identificador, título, tipo de produção, ano quando conhecido e autores identificados quando representados. Link bibliográfico somente se legítimo e verificável. |
| Grupo de pesquisa | Identificador, nome e membros por referência. Linha de atuação ou projetos associados quando pertinentes. |

Links de perfis e publicações fictícias devem ser omitidos quando não houver um destino legítimo. Os exemplos podem reutilizar os tipos e campos apresentados pelo professor, com tratamento adequado para contatos, imagens e fontes antes da publicação.

## Identidade, metadados e publicação

- Separar a identidade da pessoa da página que a descreve. Usar um identificador por recurso, manter o mesmo identificador em todas as representações e definir a base HTTPS e a resolução das URIs na etapa de publicação.
- Aproveitar os metadados **descritivos** para nomes, apresentações e temas, os **estruturais** para tipos e relações entre registros e os **administrativos** para fonte, licença e atualização, quando pertinente.
- Usar uma taxonomia simples de tipos de perfil e um vocabulário controlado para áreas. Termos preferidos e variantes de um tesauro são referências para padronização terminológica. A necessidade de um tesauro próprio fica para revisão.
- Aplicar o que foi trabalhado com XML à separação entre estrutura e apresentação. A etapa de modelagem vai converter os relacionamentos aqui definidos em decisões sobre classes, propriedades e triplas. OWL, Protégé, SPARQL e LOD servirão à modelagem, à revisão da ontologia, à consulta e à publicação, respectivamente.

## Critérios de aceitação propostos

1. A lista abre quatro páginas distintas no navegador, com dois docentes e dois discentes e os campos pertinentes a cada perfil. A inclusão de outro registro válido no conjunto de demonstração usa o mesmo mecanismo de geração.
2. Os registros têm identificadores únicos, referências válidas e papéis distinguíveis. As seções pertinentes dos modelos originais aparecem no site e dados ausentes recebem tratamento coerente.
3. As seis perguntas têm casos esperados documentados. O conjunto inclui vínculo em unidade compartilhada, participação de docente e discente no mesmo projeto e coautoria verificável no conjunto.
4. Na publicação, conferir o acesso às URIs e aos arquivos RDF/OWL, a correspondência dos dados com os perfis e a justificativa de cada ligação externa, com pelo menos três recursos distintos. Fonte e licença estão identificadas e a demonstração pode ser repetida.

O trio precisa validar a abordagem de geração, as fontes e a licença dos dados, a base das URIs, a hospedagem, os recursos e predicados externos e a forma de executar SPARQL. A [pesquisa de vocabulários](../documentacao/pesquisa-vocabularios.md) registra as opções para essa revisão.
