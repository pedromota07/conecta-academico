"""Executa as consultas SPARQL do ConectaAcadêmico sobre o RDF local gerado.

Sem argumentos, executa as seis consultas e a consulta complementar de ligações
externas com os parâmetros de demonstração e grava as evidências em
consultas/resultados/. Com o nome de uma consulta, executa somente ela e
imprime o resultado no terminal.

Os parâmetros entram na consulta como termos RDF (URIRef) por initBindings do
RDFLib; nenhum valor informado é interpolado no texto SPARQL.
"""

import argparse
import json
from pathlib import Path
import re
import sys
from tempfile import NamedTemporaryFile

from rdflib import BNode, Graph, Literal, URIRef

from gerar_rdf import INST
from gerar_site import NAO_INFORMADO, apresentar_termo
from validar_dados import FORMATO_ID


RAIZ = Path(__file__).resolve().parent.parent
PASTA_CONSULTAS = RAIZ / "consultas"
PASTA_RESULTADOS = PASTA_CONSULTAS / "resultados"
GRAFO_PADRAO = RAIZ / "ontologia" / "instancias.ttl"
MANIFESTO = "execucoes.json"
URI_ABSOLUTA = re.compile(r"https?://[^\s<>\"{}|\\^`]+")

# Cada parâmetro é uma variável da consulta preenchida por initBindings.
CONSULTAS = {
    "consulta01": {
        "pergunta": "Quais são os docentes cadastrados e seus respectivos departamentos ou unidades acadêmicas?",
        "parametros": {},
        "demonstracao": [{}],
    },
    "consulta02": {
        "pergunta": "Quais discentes pertencem a determinado curso?",
        "parametros": {"curso": "URI de um curso de graduação (ca:CursoGraduacao)"},
        "demonstracao": [{"curso": "curso-sistemas-informacao"}, {"curso": "curso-biblioteconomia"}],
    },
    "consulta03": {
        "pergunta": "Quais docentes atuam em determinada área de pesquisa?",
        "parametros": {"area": "URI de uma área de conhecimento (ca:AreaConhecimento)"},
        "demonstracao": [{"area": "area-dados-abertos"}, {"area": "area-curadoria-digital"}],
    },
    "consulta04": {
        "pergunta": "Quais docentes e discentes participam de um mesmo projeto de pesquisa?",
        "parametros": {},
        "demonstracao": [{}],
    },
    "consulta05": {
        "pergunta": (
            "Quais publicações estão associadas a determinado docente e quem são seus coautores, "
            "quando essa informação estiver representada?"
        ),
        "parametros": {"docente": "URI de uma pessoa docente (ca:Docente)"},
        "demonstracao": [{"docente": "pessoa-ana"}, {"docente": "pessoa-rafael"}],
    },
    "consulta06": {
        "pergunta": (
            "Quais pessoas estão vinculadas a uma unidade acadêmica específica, "
            "independentemente de serem docentes ou discentes?"
        ),
        "parametros": {"unidade": "URI de uma unidade acadêmica (ca:UnidadeAcademica)"},
        "demonstracao": [
            {"unidade": "unidade-computacao"},
            {"unidade": "unidade-gestao-informacao"},
            {"unidade": "unidade-ciencias-exatas"},
        ],
    },
    "ligacoes-externas": {
        "pergunta": "Quais áreas locais estão ligadas a recursos externos e por qual relação de mapeamento SKOS?",
        "parametros": {},
        "demonstracao": [{}],
        "complementar": True,
    },
}


def resolver_parametro(nome, valor):
    """Converte um ID local, inst:ID ou URI absoluta HTTP(S) em URIRef."""
    texto = valor.strip() if isinstance(valor, str) else ""
    if texto.startswith("inst:"):
        texto = texto.removeprefix("inst:")
    if FORMATO_ID.fullmatch(texto):
        return INST[texto]
    if URI_ABSOLUTA.fullmatch(texto):
        return URIRef(texto)
    raise ValueError(
        f"Parâmetro {nome!r} inválido ({valor!r}). Use um identificador local como "
        "'curso-sistemas-informacao', a forma 'inst:<id>' ou uma URI absoluta http(s) sem espaços ou '<>'."
    )


def ler_consulta(nome, pasta=PASTA_CONSULTAS):
    if nome not in CONSULTAS:
        raise ValueError(f"Consulta desconhecida {nome!r}. Opções: {', '.join(CONSULTAS)}.")
    return (Path(pasta) / f"{nome}.rq").read_text(encoding="utf-8")


def carregar_grafo(caminho=GRAFO_PADRAO):
    """Carrega somente o Turtle local; não há inferência nem download de vocabulários."""
    return Graph().parse(Path(caminho), format="turtle")


def preparar_bindings(nome, parametros):
    if nome not in CONSULTAS:
        raise ValueError(f"Consulta desconhecida {nome!r}. Opções: {', '.join(CONSULTAS)}.")
    esperados = CONSULTAS[nome]["parametros"]
    desconhecidos = sorted(set(parametros) - set(esperados))
    if desconhecidos:
        aceitos = ", ".join(esperados) or "nenhum"
        raise ValueError(f"{nome}: parâmetro desconhecido {', '.join(desconhecidos)}. Aceitos: {aceitos}.")
    ausentes = [chave for chave in esperados if chave not in parametros]
    if ausentes:
        raise ValueError(f"{nome}: informe o parâmetro {', '.join(ausentes)} ({esperados[ausentes[0]]}).")
    return {chave: resolver_parametro(chave, valor) for chave, valor in parametros.items()}


def executar(grafo, nome, parametros=None, pasta=PASTA_CONSULTAS):
    """Executa o arquivo .rq com Graph.query() e devolve (variáveis, linhas, bindings)."""
    bindings = preparar_bindings(nome, parametros or {})
    resultado = grafo.query(ler_consulta(nome, pasta), initBindings=bindings)
    variaveis = [str(variavel) for variavel in resultado.vars]
    linhas = [dict(zip(variaveis, linha)) for linha in resultado]
    return variaveis, linhas, bindings


def termo_json(termo):
    """Serializa um termo RDF segundo o formato SPARQL 1.1 Query Results JSON."""
    if isinstance(termo, URIRef):
        return {"type": "uri", "value": str(termo)}
    if isinstance(termo, BNode):
        return {"type": "bnode", "value": str(termo)}
    if isinstance(termo, Literal):
        dado = {"type": "literal", "value": str(termo)}
        if termo.language:
            dado["xml:lang"] = termo.language
        elif termo.datatype:
            dado["datatype"] = str(termo.datatype)
        return dado
    raise TypeError(f"Termo RDF não suportado: {termo!r}")


def resultados_json(variaveis, linhas):
    """Variáveis não associadas ficam ausentes do binding, como define a especificação."""
    return {
        "head": {"vars": variaveis},
        "results": {
            "bindings": [
                {variavel: termo_json(valor) for variavel, valor in linha.items() if valor is not None}
                for linha in linhas
            ]
        },
    }


def rotulo_pergunta(nome):
    """consulta03 → PC3; consultas complementares mantêm o nome do arquivo."""
    numero = re.fullmatch(r"consulta0*([1-9][0-9]*)", nome)
    return f"PC{numero.group(1)}" if numero else nome


def nome_resultado(nome, bindings):
    sufixo = "--".join(
        str(uri).removeprefix(str(INST)) if str(uri).startswith(str(INST)) else re.sub(r"[^a-z0-9]+", "-", str(uri).lower())
        for _, uri in sorted(bindings.items())
    )
    return f"{nome}--{sufixo}.json" if sufixo else f"{nome}.json"


def _gravar(caminho, texto):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with NamedTemporaryFile(dir=caminho.parent, delete=False) as arquivo:
            temporario = Path(arquivo.name)
            arquivo.write(texto.encode("utf-8"))
        temporario.replace(caminho)
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)


def _json(dado):
    return json.dumps(dado, ensure_ascii=False, indent=2) + "\n"


def _tabela_markdown(variaveis, bindings):
    def celula(texto):
        return texto.replace("|", "\\|")

    if not bindings:
        return "Nenhum resultado para estes parâmetros.\n"
    linhas = ["| " + " | ".join(variaveis) + " |", "|" + " --- |" * len(variaveis)]
    for binding in bindings:
        linhas.append("| " + " | ".join(celula(apresentar_termo(binding.get(v))) for v in variaveis) + " |")
    return "\n".join(linhas) + "\n"


def _leia_me(execucoes, resultados):
    partes = [
        "# Resultados das consultas SPARQL\n",
        "Arquivo gerado por `codigo-fonte/executar_consultas.py`. Não edite manualmente: altere os dados ou as "
        "consultas e execute o script novamente.\n",
        "Os resultados vêm de uma execução local, com RDFLib, sobre `ontologia/instancias.ttl` (conjunto de "
        "demonstração com dados fictícios). Não há endpoint SPARQL público. Cada arquivo `.json` segue o formato "
        "SPARQL 1.1 Query Results JSON; variáveis sem valor ficam ausentes do binding e aparecem abaixo como "
        f"“{NAO_INFORMADO}”. Valores `inst:` abreviam `{INST}`.\n",
    ]
    for execucao in execucoes:
        parametros = ", ".join(f"`?{k}` = `{v}`" for k, v in execucao["parametros"].items()) or "nenhum"
        rotulo = "Consulta complementar" if execucao.get("complementar") else rotulo_pergunta(execucao["consulta"])
        dado = resultados[execucao["resultado"]]
        partes.append(
            f"## {rotulo} · `{execucao['resultado']}`\n\n"
            f"**Pergunta:** {execucao['pergunta']}\n\n"
            f"**Consulta:** [`{execucao['arquivo']}`](../{execucao['consulta']}.rq) · **Parâmetros:** {parametros} · "
            f"**Linhas:** {execucao['linhas']}\n\n"
            + _tabela_markdown(dado["head"]["vars"], dado["results"]["bindings"])
        )
    return "\n".join(partes)


def executar_demonstracao(caminho_grafo=GRAFO_PADRAO, destino=PASTA_RESULTADOS, pasta=PASTA_CONSULTAS):
    """Executa todas as consultas com os parâmetros de demonstração e grava as evidências."""
    destino = Path(destino)
    grafo = carregar_grafo(caminho_grafo)
    execucoes, resultados = [], {}
    for nome, definicao in CONSULTAS.items():
        for parametros in definicao["demonstracao"]:
            variaveis, linhas, bindings = executar(grafo, nome, parametros, pasta)
            arquivo = nome_resultado(nome, bindings)
            resultados[arquivo] = resultados_json(variaveis, linhas)
            execucao = {
                "consulta": nome,
                "arquivo": f"consultas/{nome}.rq",
                "pergunta": definicao["pergunta"],
                "parametros": {chave: str(uri) for chave, uri in bindings.items()},
                "resultado": arquivo,
                "linhas": len(linhas),
            }
            if definicao.get("complementar"):
                execucao["complementar"] = True
            execucoes.append(execucao)

    manifesto = {
        "grafo": "ontologia/instancias.ttl",
        "motor": "RDFLib Graph.query() com initBindings",
        "observacao": "Execução local sobre o conjunto de demonstração; não é um endpoint público.",
        "execucoes": execucoes,
    }
    for arquivo, dado in resultados.items():
        _gravar(destino / arquivo, _json(dado))
    _gravar(destino / MANIFESTO, _json(manifesto))
    _gravar(destino / "README.md", _leia_me(execucoes, resultados))
    for antigo in destino.glob("*.json"):
        if antigo.name not in resultados and antigo.name != MANIFESTO:
            antigo.unlink()
    return manifesto


def _imprimir(nome, variaveis, linhas, bindings):
    print(f"{nome}: {CONSULTAS[nome]['pergunta']}")
    for chave, uri in bindings.items():
        print(f"  ?{chave} = <{uri}>")
    if not linhas:
        print("Nenhum resultado para estes parâmetros.")
        return
    for linha in linhas:
        print("  - " + " | ".join(
            f"{v}: {apresentar_termo(None if linha[v] is None else termo_json(linha[v]))}" for v in variaveis
        ))
    print(f"{len(linhas)} linha(s).")


def _par(texto):
    chave, separador, valor = texto.partition("=")
    if not separador or not chave:
        raise argparse.ArgumentTypeError("use o formato nome=valor, por exemplo curso=curso-biblioteconomia")
    return chave.strip(), valor


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("consulta", nargs="?", help="Nome da consulta, por exemplo consulta02. Omita para executar todas.")
    parser.add_argument("--param", action="append", type=_par, default=[], metavar="NOME=VALOR",
                        help="Parâmetro da consulta: ID local, inst:ID ou URI absoluta.")
    parser.add_argument("--json", action="store_true", help="Imprime o resultado em SPARQL Results JSON.")
    parser.add_argument("--listar", action="store_true", help="Lista as consultas e seus parâmetros.")
    parser.add_argument("--grafo", type=Path, default=GRAFO_PADRAO, help="Arquivo Turtle consultado.")
    parser.add_argument("--resultados", type=Path, default=PASTA_RESULTADOS,
                        help="Pasta das evidências gravadas ao executar todas as consultas.")
    args = parser.parse_args(argv)

    try:
        if args.listar:
            for nome, definicao in CONSULTAS.items():
                parametros = ", ".join(f"{k} ({v})" for k, v in definicao["parametros"].items()) or "sem parâmetros"
                print(f"{nome}: {definicao['pergunta']}\n    parâmetros: {parametros}")
            return
        if args.consulta is None:
            if args.param:
                raise ValueError("Informe o nome da consulta para usar --param.")
            manifesto = executar_demonstracao(args.grafo, args.resultados)
            for execucao in manifesto["execucoes"]:
                print(f"{execucao['resultado']}: {execucao['linhas']} linha(s)")
            print(f"Resultados gravados em {args.resultados}")
            return
        parametros = dict(args.param)
        if len(parametros) != len(args.param):
            raise ValueError("Cada parâmetro deve ser informado uma única vez.")
        variaveis, linhas, bindings = executar(carregar_grafo(args.grafo), args.consulta, parametros)
        if args.json:
            sys.stdout.write(_json(resultados_json(variaveis, linhas)))
        else:
            _imprimir(args.consulta, variaveis, linhas, bindings)
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Falha na consulta: {erro}\n")


if __name__ == "__main__":
    main()
