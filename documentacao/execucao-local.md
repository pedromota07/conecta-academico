# Execução local do ConectaAcadêmico

O diretório `docs/` contém a saída estática publicada no GitHub Pages. Faça mudanças nos arquivos-fonte e regenere a saída. Os resultados em `consultas/resultados/` também são gerados.

## Regenerar o RDF e o site

Com Python 3.10 ou superior, execute na raiz do repositório em PowerShell.

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-rdf.txt
& .\.venv\Scripts\python.exe -B codigo-fonte/gerar_rdf.py --publicaveis docs/ontologia
& .\.venv\Scripts\python.exe -B codigo-fonte/executar_consultas.py
& .\.venv\Scripts\python.exe -B codigo-fonte/gerar_site.py
```

Edite os perfis, recursos e vínculos em [dados.json](../exemplos/perfis/dados.json), a apresentação nos [arquivos-fonte do site](../codigo-fonte/) e as consultas em [consultas/](../consultas/). O identificador de uma pessoa é o mesmo quando ela acumula docência e discência.

Para conferir os comandos disponíveis ou variar um parâmetro, use o ID local, a forma `inst:ID` ou a URI completa. [Parâmetros e resultados de referência](consultas-sparql.md).

```powershell
& .\.venv\Scripts\python.exe -B codigo-fonte/executar_consultas.py --listar
& .\.venv\Scripts\python.exe -B codigo-fonte/executar_consultas.py consulta02 --param curso=curso-biblioteconomia
```

## Testes

```powershell
$env:PYTHONUTF8 = '1'
& .\.venv\Scripts\python.exe -B -m unittest discover -s testes -v
```

A suíte verifica o site gerado, a validação dos registros, a ontologia e as instâncias RDF, as consultas e os vínculos externos em ambiente local.

## Modelo conceitual

O [diagrama SVG](diagrama-conceitual.svg) tem como fonte o [arquivo Graphviz DOT](diagrama-conceitual.dot). Com Graphviz no `PATH`, a geração é feita da raiz do repositório.

```powershell
dot -Tsvg documentacao/diagrama-conceitual.dot -o documentacao/diagrama-conceitual.svg
```

Ao substituir a saída, confira a legibilidade, as relações R01–R15 e os atributos de acessibilidade do SVG versionado. [Dicionário de dados](dicionario-dados.md) · [Decisões de modelagem](decisoes-modelagem.md).
