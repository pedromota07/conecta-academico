# Declaração de uso de ferramentas de IA

## Etapa 0

**Ferramenta e finalidade** — OpenAI Codex, para auxiliar na inspeção dos materiais do professor, na síntese do enunciado e na preparação do repositório local.

**Síntese da solicitação** — Ler o enunciado e os modelos originais antes de criar o projeto. Registrar os requisitos e critérios de avaliação com base no PDF, preparar o README e o `.gitignore` e inicializar o Git local na branch `main`.

**Partes preparadas com auxílio da ferramenta** — Estrutura inicial de diretórios, README, `.gitignore`, documento de requisitos, esta declaração e inicialização do repositório local.

**Verificações realizadas** — Foram lidas e revisadas visualmente as quatro páginas do PDF, incluindo a tabela de avaliação e a regra de nota individual. Os dois modelos HTML e a folha de estilos foram inspecionados diretamente no ZIP. Os requisitos e o README foram conferidos com o enunciado. A integridade do ZIP foi verificada e seu SHA-256 foi comparado antes e depois da preparação. Também foram conferidos a estrutura local, os links do README, as regras do `.gitignore` com caminhos representativos e o estado do Git, com a branch `main` sem commits, índice vazio e nenhum remoto.

O grupo deve revisar este registro e acrescentar o uso de IA das próximas etapas, indicando as ferramentas, as finalidades, os pedidos relevantes, as partes afetadas e as verificações efetivamente realizadas.

## Etapa 1

**Ferramentas e finalidades** — OpenAI Codex para organizar a pesquisa e redigir a proposta, as perguntas de competência e a matriz de rastreabilidade. Firecrawl e busca na Web para consultar especificações oficiais e localizar literatura, incluindo resultados do Google e do Google Acadêmico.

**Síntese da solicitação** — Delimitar o diretório de perfis docentes e discentes, comparar vocabulários, identificar os dados e vínculos necessários para as seis perguntas do professor e associar cada exigência a um artefato e a um critério de validação.

**Partes preparadas com auxílio da ferramenta** — `proposta/escopo.md`, `proposta/perguntas-competencia.md`, `proposta/rastreabilidade.md` e `documentacao/pesquisa-vocabularios.md`. A ferramenta também auxiliou na criação da branch de trabalho e nesta declaração.

**Verificações realizadas** — O enunciado de quatro páginas, os modelos HTML/CSS e a atividade sobre ontologias do slide 50 foram consultados. Os termos comparados foram conferidos nas especificações ou nos arquivos publicados pelos projetos. A rastreabilidade foi revisada com os requisitos da Etapa 0 e os campos e relações propostos foram cruzados com as seis perguntas. Foram conferidos os links internos e a formatação dos quatro documentos. Os cenários de aceitação descrevem verificações previstas para a implementação.

## Etapa 2

**Ferramenta e finalidade** — OpenAI Codex para propor e documentar o modelo conceitual, o dicionário, as decisões para OWL, o diagrama e os exemplos conceituais. A busca na Web apoiou a conferência de especificações oficiais de OWL, Schema.org, AIISO, DCMI e SKOS.

**Síntese da solicitação** — Especificar entidades, identificadores, relações e cardinalidades, admitir múltiplos papéis acadêmicos para a mesma pessoa e demonstrar a cobertura de PC1–PC6 em termos conceituais.

**Partes afetadas** — Dicionário de dados, decisões de modelagem, fonte editável e imagem do diagrama, referências da matriz de rastreabilidade e esta entrada da declaração.

**Verificações realizadas** — Foram consultados o enunciado e os documentos aprovados. Foram cruzadas as entidades, as relações e as multiplicidades do diagrama, do dicionário e das decisões. O SVG foi renderizado a partir da fonte editável e inspecionado visualmente. Os caminhos de PC1–PC6 foram conferidos com exemplos fictícios abstratos, incluindo o tratamento de uma pessoa com dois papéis. A verificação foi conceitual.

## Etapa 3

**Ferramenta e finalidade** — OpenAI Codex, com assistência delegada para preparar a fonte JSON e o validador, adaptar a apresentação dos perfis aos modelos do professor e criar os testes. A ferramenta também auxiliou na implementação do gerador e na revisão da documentação.

**Síntese da solicitação** — Implementar um diretório acadêmico fictício em HTML e CSS, gerado a partir de uma única fonte JSON, seguindo a modelagem aprovada e usando quatro perfis com dados suficientes para PC1–PC6.

**Partes afetadas** — Dados em `exemplos/perfis/`, gerador, validador, templates e estilos em `codigo-fonte/`, testes automatizados, saída estática em `docs/`, README e esta entrada.

**Verificações realizadas** — Os arquivos HTML e CSS do professor foram consultados no ZIP original. A geração local e os testes automatizados verificaram as páginas, os vínculos, as referências internas, o escape de conteúdo, os cenários PC1–PC6 e a inclusão isolada de um quinto perfil. O quinto registro de teste exerceu os dois papéis com o mesmo identificador. No Chrome, foram conferidos os links, a navegação por teclado e a responsividade em desktop e em telas estreitas.

**Auditoria final** — Na raiz do repositório, `python -B codigo-fonte/gerar_site.py` gerou seis arquivos, que coincidiram byte a byte com a segunda geração em um diretório temporário. `python -B -m unittest discover -s testes -v` executou 23 testes com sucesso. A navegação no Chrome foi verificada em 1440, 390 e 320 px, diretamente pelos arquivos e por HTTP local em um subdiretório. `git diff --check` e a checagem complementar dos arquivos novos passaram.

## Etapa 4

**Ferramenta e finalidade** — OpenAI Codex, com assistência delegada para preparar a ontologia OWL, o gerador RDF/Turtle e os testes. A busca na Web apoiou a conferência das especificações oficiais de OWL, Schema.org, AIISO, DCMI e SKOS.

**Síntese da solicitação** — Implementar as 11 classes e as relações R01–R15 conforme o modelo aprovado, converter os registros JSON em Turtle com URIs estáveis e conferir por travessia do grafo a cobertura de PC1–PC6.

**Partes afetadas** — Ontologia, grafo de instâncias, gerador e sua dependência, cópias estáticas, testes RDF, documentação da ontologia, rastreabilidade, README e esta entrada.

**Verificações realizadas** — O RDFLib 7.6.0 carregou a ontologia e as instâncias. Foram conferidos os 28 registros, os vínculos com os quatro perfis e os percursos de PC1–PC6. A auditoria dos grafos incluiu verificação do perfil OWL 2 DL com OWLAPI 3.4.3 e análise de consistência da ontologia com as instâncias locais pelo Pellet 2.3.1, via Owlready2 0.51 e OpenJDK 25. A análise local não encontrou inconsistências ou classes insatisfatíveis. Os testes do site e os testes RDF foram executados em ambiente virtual.
