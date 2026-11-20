# Requisitos do trabalho

Este registro usa exclusivamente o enunciado oficial *Trabalho Web Semântica e Linked Open Data*, de Tiago Cruz de França, disponível em `descricao_trabalho_web_semantica.pdf` no pacote `trabWebSemantica.zip`. As referências de seção remetem a esse enunciado.

## Requisitos obrigatórios

### Aplicação (§§ 1–3)

- Desenvolver em trio uma aplicação de perfis acadêmicos que funcione para qualquer perfil com a estrutura definida.
- Publicar páginas acessíveis por navegador com, no mínimo, **dois perfis docentes e dois discentes**. O enunciado prevê acrescentar ao menos um perfil de cada tipo aos exemplos fornecidos.
- Usar os modelos HTML e CSS do professor como ponto de partida para a apresentação.
- Gerar as páginas a partir de uma fonte de dados estruturada, mantendo os perfis ligados aos dados do projeto.
- Apresentar nome, vínculo institucional, unidade/departamento ou curso, formação, áreas de atuação ou interesse, disciplinas, projetos, grupos de pesquisa, publicações ou trabalhos e links de redes ou perfis acadêmicos, conforme o tipo de perfil.
- Disponibilizar o site publicamente e fornecer seu endereço.

### Web Semântica e Linked Open Data (§§ 4 e 6)

- Definir um modelo conceitual com entidades, atributos e relacionamentos.
- Produzir um dicionário de dados com o significado, o tipo e as regras relevantes dos campos.
- Identificar metadados e vocabulários controlados pertinentes. Explicar as taxonomias ou classificações utilizadas.
- Pesquisar ontologias e vocabulários existentes, avaliar sua adequação e justificar a reutilização, especialização, alinhamento ou criação. O enunciado orienta consultar também Google e Google Scholar para embasar as escolhas.
- Definir e documentar uma ontologia de aplicação, com classes, propriedades, hierarquias, domínios, alcances e axiomas ou restrições relevantes.
- Representar a ontologia e os dados em **OWL e RDF**, atribuir **URIs públicas** aos recursos publicados e disponibilizar os arquivos de ontologia e dados.
- Relacionar os dados a **pelo menos três recursos externos pertinentes** e justificar semanticamente cada ligação.
- Informar as fontes dos dados, a licença de reutilização e, quando pertinente, a data de atualização.
- Disponibilizar o site, a documentação, a ontologia e os dados RDF em repositório ou hospedagem acessível pela Internet. Demonstrar as URIs públicas, o acesso ao RDF, a correspondência entre o RDF e os perfis do site e as ligações externas.

### Consultas SPARQL (§§ 5–6)

Responder às seis perguntas de competência abaixo, resumidas do enunciado. Para cada uma, apresentar a pergunta em linguagem natural, a consulta SPARQL, o resultado obtido e uma explicação das classes e propriedades utilizadas.

1. Quais docentes estão cadastrados e a quais departamentos ou unidades acadêmicas pertencem?
2. Quais discentes pertencem a um curso específico?
3. Quais docentes atuam em uma área de pesquisa específica?
4. Quais docentes e discentes participam de um mesmo projeto de pesquisa?
5. Quais publicações estão associadas a um docente e quem são seus coautores, quando o dado estiver representado?
6. Quais pessoas, docentes ou discentes, estão vinculadas a uma unidade acadêmica específica?

Pelo menos duas das seis consultas devem explorar relacionamentos entre tipos distintos de entidades. Se o grupo optar por trabalhar sem endpoint público, deverá fornecer os arquivos RDF e evidências reproduzíveis da execução das consultas em um ambiente compatível.

## Requisitos opcionais e escolhas permitidas

- Adaptar o layout e acrescentar campos, respeitando os requisitos mínimos (§ 2).
- Escolher a fonte estruturada e a tecnologia de geração. JSON, XML e CSV são exemplos. Banco de dados é facultativo. XSLT é uma opção caso os dados sejam XML (§ 3).
- Criar um tesauro ou usar uma ontologia de fundamentação ou de topo. Também é permitida uma ontologia de aplicação própria, desde que a pesquisa seja documentada (§ 4).
- Usar GitHub Pages ou outra plataforma de hospedagem pública (§ 6).
- Disponibilizar um endpoint SPARQL público, que o enunciado considera desejável (§ 6).
- Usar ferramentas de IA como apoio à pesquisa, à programação, à documentação, à modelagem e às consultas. Declarar o uso, quando houver (§§ 7 e 9).

## Entregáveis (§ 7)

1. Proposta do sistema com objetivo, público-alvo, funcionalidades, tipos de perfil e justificativa das informações selecionadas.
2. Código-fonte e endereço público do site com pelo menos dois perfis docentes e dois discentes.
3. Dicionário de dados e documentação dos metadados e vocabulários.
4. Pesquisa de ontologias e vocabulários existentes com justificativa das escolhas.
5. Documentação da ontologia com diagrama, classes, propriedades, hierarquias, domínios, alcances e axiomas ou restrições.
6. Arquivos OWL e RDF/Turtle. A seção 4 indica Turtle como serialização preferencial e a seção 7 lista o arquivo RDF/Turtle entre os entregáveis.
7. Seis consultas SPARQL com resultados e explicações.
8. Evidências de publicação com URIs, links externos, licença e fontes.
9. README com integrantes, endereços, estrutura e instruções para reproduzir a demonstração.
10. Declaração de uso de ferramentas de IA.

## Critérios de avaliação (§§ 11–12)

| Critério | Pontuação |
| --- | ---: |
| Delimitação, requisitos e pesquisa de soluções existentes | 1,0 |
| Modelo conceitual, dicionário e documentação da ontologia | 2,0 |
| Modelagem OWL e representação RDF | 2,0 |
| Publicação, URIs e integração com LOD | 2,0 |
| Consultas SPARQL e respostas às perguntas de competência | 1,5 |
| Implementação e integração com o site | 1,5 |
| **Total do entregável** | **10,0** |

A nota individual é a nota do entregável multiplicada pelo fator da apresentação, de 0 a 1 para cada integrante. A apresentação considera o domínio individual e a justificativa das decisões. A avaliação também considera a coerência entre problema, modelo, ontologia, dados publicados, consultas e aplicação.

## Restrições e cuidados

- Para os perfis adicionais, usar dados fictícios ou dados públicos cujo uso seja apropriado. Preservar a privacidade de terceiros, excluir dados pessoais sensíveis e informações privadas e respeitar direitos autorais e termos de uso (§§ 3 e 12).
- Empregar `owl:sameAs` somente quando os recursos designarem a mesma entidade (§ 4).
- Usar vocabulários adequados ao domínio e justificar as escolhas (§ 4).
- Preparar evidências de Linked Open Data além do endereço do site (§ 6).
- Na declaração de IA, registrar ferramentas, finalidades, solicitações relevantes ou suas sínteses, partes afetadas e verificações realizadas. Cada integrante deve dominar as decisões e a implementação e estar preparado para explicar ou fazer pequenas alterações no modelo, nos dados e nas consultas (§ 9).
- Cumprir os requisitos do trabalho mesmo quando forem usadas tecnologias adicionais (§ 12).

## Pendências para decisão do grupo

- Delimitar o público-alvo, as funcionalidades da proposta e os campos por tipo de perfil (§§ 2–3 e 7).
- Escolher os dados dos novos perfis, verificar as condições de uso das fontes e definir a licença de reutilização (§§ 3–4 e 12).
- Escolher o formato da fonte estruturada e a tecnologia de geração das páginas (§ 3).
- Após a pesquisa, decidir quais ontologias, vocabulários e classificações adotar e quais recursos externos ligar aos dados (§ 4).
- Definir a estratégia de URIs, onde publicar o site e os arquivos e como executar e demonstrar as consultas, com ou sem endpoint público (§§ 4–6).
