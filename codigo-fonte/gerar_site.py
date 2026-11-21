"""Gera o diretório estático do ConectaAcadêmico a partir dos dados editoriais.

Além do catálogo e dos perfis, gera a página "Dados e consultas" a partir dos
arquivos reais do projeto: a ontologia e as instâncias em Turtle, as consultas
.rq e os resultados exportados por executar_consultas.py. Esses arquivos são
copiados para o destino para que os links funcionem na hospedagem estática.
Usa apenas a biblioteca padrão.
"""

import argparse
from datetime import date
import json
import re
from html import escape
from pathlib import Path
from string import Template
from tempfile import NamedTemporaryFile

from validar_dados import BASE_LOCAL, carregar_dados


FONTE = Path(__file__).resolve().parent
RAIZ = FONTE.parent
DADOS_PADRAO = RAIZ / "exemplos" / "perfis" / "dados.json"
SAIDA_PADRAO = RAIZ / "docs"
PASTA_CONSULTAS = RAIZ / "consultas"
PASTA_ONTOLOGIA = RAIZ / "ontologia"
ARQUIVOS_RDF = ("conecta-academico.ttl", "instancias.ttl")
LINK_DE_CARTAO = re.compile(r'<h3><a href="perfis/([a-z0-9]+(?:-[a-z0-9]+)*\.html)">')
PREFIXO_INST = BASE_LOCAL + "ontologia/instancias.ttl#"
PREFIXOS_EXIBICAO = (("inst:", PREFIXO_INST), ("skos:", "http://www.w3.org/2004/02/skos/core#"))
XSD_BOOLEAN ="http://www.w3.org/2001/XMLSchema#boolean"
NAO_INFORMADO = "Não informado"
REPOSITORIO = "https://github.com/pedromota07/conecta-academico"
LICENCAS_WIKIDATA = "https://www.wikidata.org/wiki/Wikidata:Licensing"
MAXIMO_AREAS_CARTAO = 3


def lista(itens, classe="clean-list"):
    if not itens:
        return ""
    return f'<ul class="{classe}">' + "".join(f"<li>{item}</li>" for item in itens) + "</ul>"


def secao(titulo, conteudo):
    if not conteudo:
        return ""
    return f'<section class="profile-section"><h2>{titulo}</h2>{conteudo}</section>'


def bloco_lateral(titulo, conteudo):
    if not conteudo:
        return ""
    return f'<section class="sidebar-block"><h2>{titulo}</h2>{conteudo}</section>'


def papeis(pessoa):
    docente = "docencia" in pessoa
    discente = "discencia" in pessoa
    if docente and discente:
        return "ambos", "Docente e discente"
    if docente:
        return "docente", "Docente"
    return "discente", "Discente"


def iniciais(nome):
    partes = nome.split()
    return (partes[0][0] + partes[-1][0] if len(partes) > 1 else partes[0][0]).upper()


def rotulos(indice, referencias, campo="nome"):
    return [escape(indice[chave][campo]) for chave in referencias]


def perfil_url(pessoa):
    return f'{pessoa["id"]}.html'


def areas_da_pessoa(pessoa):
    """Áreas de atuação docente seguidas das de interesse discente, sem repetição."""
    areas = pessoa.get("docencia", {}).get("areasAtuacao", []) + pessoa.get("discencia", {}).get("areasInteresse", [])
    return list(dict.fromkeys(areas))


def cartao(pessoa, indices):
    tipo, papel = papeis(pessoa)
    nome = escape(pessoa["nome"])
    docencia = pessoa.get("docencia", {})
    discencia = pessoa.get("discencia", {})
    cargo = docencia.get("cargo")
    papel_texto = f"{papel} · {escape(cargo)}" if cargo else papel
    locais = rotulos(indices["unidades"], docencia.get("unidadesDocentes", []))
    locais += rotulos(indices["cursos"], discencia.get("cursos", []))
    areas = areas_da_pessoa(pessoa)
    rotulos_areas = rotulos(indices["areas"], areas, "rotuloPreferido")
    busca = [pessoa["nome"], papel]
    busca += [indices["unidades"][u]["nome"] for u in docencia.get("unidadesDocentes", []) + discencia.get("unidadesDiscentes", [])]
    busca += [indices["cursos"][c]["nome"] for c in discencia.get("cursos", [])]
    busca += [indices["areas"][a]["rotuloPreferido"] for a in areas]
    return (
        f'<li class="profile-card" data-papel="{tipo}" data-busca="{escape(" ".join(busca).lower())}">'
        f'<span class="avatar" aria-hidden="true">{escape(iniciais(pessoa["nome"]))}</span>'
        '<div class="profile-card-body">'
        f'<p class="role-label">{papel_texto}</p>'
        f'<h3><a href="perfis/{perfil_url(pessoa)}">{nome}</a></h3>'
        f'<p class="profile-card-detail">{" · ".join(locais)}</p>'
        + lista(rotulos_areas[:MAXIMO_AREAS_CARTAO], "area-list")
        + "</div></li>"
    )


def vinculos(pessoa, dados, indices):
    pares = [("Instituição", [escape(dados["instituicaoReferencia"])])]
    docencia = pessoa.get("docencia", {})
    discencia = pessoa.get("discencia", {})
    pares.extend([
        ("Cargo", [escape(docencia["cargo"])] if "cargo" in docencia else []),
        ("Vínculo docente", rotulos(indices["unidades"], docencia.get("unidadesDocentes", []))),
        ("Vínculo discente", rotulos(indices["unidades"], discencia.get("unidadesDiscentes", []))),
        ("Curso de graduação", rotulos(indices["cursos"], discencia.get("cursos", []))),
    ])
    detalhes = "".join(
        f"<div><dt>{rotulo}</dt><dd>{'<br>'.join(valores)}</dd></div>"
        for rotulo, valores in pares if valores
    )
    return f'<dl class="contact-list">{detalhes}</dl>'


def item_descritivo(titulo, descricao=None):
    texto = f"<p>{escape(descricao)}</p>" if descricao else ""
    return f"<strong>{escape(titulo)}</strong>{texto}"


def publicacao(obra, pessoas, ids_com_perfil):
    titulo = escape(obra["titulo"])
    if "linkBibliografico" in obra:
        titulo = f'<a href="{escape(obra["linkBibliografico"])}">{titulo}</a>'
    tipo = {"artigo": "Artigo", "trabalho-academico": "Trabalho acadêmico"}.get(obra["tipoProducao"], "Produção")
    detalhes = [tipo] + ([str(obra["anoPublicacao"])] if "anoPublicacao" in obra else [])
    autores = []
    for chave in obra.get("autores", []):
        pessoa = pessoas[chave]
        nome = escape(pessoa["nome"])
        if chave in ids_com_perfil:
            nome = f'<a href="{perfil_url(pessoa)}">{nome}</a>'
        autores.append(nome)
    autoria = f'<p class="publication-authors">Autoria: {" · ".join(autores)}</p>' if autores else ""
    return (
        f"<strong>{titulo}</strong>"
        f'<p class="publication-meta">{" · ".join(detalhes)}</p>{autoria}'
    )


def secoes_do_perfil(pessoa, dados, indices, ids_com_perfil):
    secoes = []
    if "apresentacao" in pessoa:
        secoes.append(secao("Apresentação", f'<p>{escape(pessoa["apresentacao"])}</p>'))

    docencia = pessoa.get("docencia", {})
    discencia = pessoa.get("discencia", {})
    for titulo, papel, campo in (
        ("Áreas de atuação", docencia, "areasAtuacao"),
        ("Áreas de interesse", discencia, "areasInteresse"),
    ):
        areas = rotulos(indices["areas"], papel.get(campo, []), "rotuloPreferido")
        secoes.append(secao(titulo, lista(areas, "tag-list")))

    chave = pessoa["id"]
    projetos = [
        item_descritivo(projeto["titulo"], projeto["descricao"])
        for projeto in dados["projetos"] if chave in projeto["participantes"]
    ]
    obras = [
        publicacao(obra, indices["pessoas"], ids_com_perfil)
        for obra in dados["publicacoes"] if chave in obra.get("autores", [])
    ]
    grupos = [
        item_descritivo(grupo["nome"], grupo.get("linhaAtuacao"))
        for grupo in dados["grupos"] if chave in grupo["membros"]
    ]
    secoes.extend([
        secao("Projetos de pesquisa", lista(projetos, "detailed-list")),
        secao("Publicações e trabalhos", lista(obras, "detailed-list")),
        secao("Grupos de pesquisa", lista(grupos, "detailed-list")),
    ])
    for titulo, papel, campo in (
        ("Disciplinas ministradas", docencia, "disciplinasMinistradas"),
        ("Disciplinas cursadas", discencia, "disciplinasCursadas"),
    ):
        secoes.append(secao(titulo, lista(rotulos(indices["disciplinas"], papel.get(campo, [])), "inline-list")))
    return "\n".join(conteudo for conteudo in secoes if conteudo)


def lateral_do_perfil(pessoa, dados, indices):
    links = [f'<a href="{escape(url)}">{escape(url)}</a>' for url in pessoa.get("linksAcademicos", [])]
    rdf = (
        f'<p>URI: <code>inst:{escape(pessoa["id"])}</code></p>'
        f'<p><a href="../ontologia/instancias.ttl#{escape(pessoa["id"])}">Descrição em RDF (Turtle)</a></p>'
    )
    return "\n".join(bloco for bloco in (
        '<section class="sidebar-block" aria-labelledby="vinculo-institucional">'
        '<h2 id="vinculo-institucional">Vínculo institucional</h2>'
        f"{vinculos(pessoa, dados, indices)}</section>",
        bloco_lateral("Formação acadêmica", lista([escape(item) for item in pessoa.get("formacao", [])])),
        bloco_lateral("Links acadêmicos", lista(links, "clean-list academic-links")),
        bloco_lateral("Dados do perfil", rdf),
    ) if bloco)


def renderizar_perfil(template, pessoa, dados, indices, ids_com_perfil):
    tipo, papel = papeis(pessoa)
    docencia = pessoa.get("docencia", {})
    discencia = pessoa.get("discencia", {})
    contexto = rotulos(indices["unidades"], docencia.get("unidadesDocentes", []))
    contexto += rotulos(indices["cursos"], discencia.get("cursos", []))
    subtitulo = f'<p class="profile-subtitle">{" · ".join(contexto)}</p>'
    cargo = docencia.get("cargo")
    return template.substitute(
        raiz="../",
        instituicao=escape(dados["instituicaoReferencia"]),
        nome=escape(pessoa["nome"]),
        iniciais=escape(iniciais(pessoa["nome"])),
        papel=f"{papel} · {escape(cargo)}" if cargo else papel,
        tipo_papel=tipo,
        subtitulo=subtitulo,
        secoes=secoes_do_perfil(pessoa, dados, indices, ids_com_perfil),
        lateral=lateral_do_perfil(pessoa, dados, indices),
    )


# Página "Dados e consultas" -------------------------------------------------


def apresentar_termo(termo):
    """Texto legível de um termo do SPARQL Results JSON; ausência vira 'Não informado'."""
    if termo is None:
        return NAO_INFORMADO
    tipo, valor = termo["type"], termo["value"]
    if tipo == "uri":
        for prefixo, namespace in PREFIXOS_EXIBICAO:
            if valor.startswith(namespace):
                return prefixo + valor.removeprefix(namespace)
    if termo.get("datatype") == XSD_BOOLEAN:
        return "sim" if valor == "true" else "não"
    return valor


def celula_resultado(termo):
    if termo is None:
        return f'<td class="unbound">{NAO_INFORMADO}</td>'
    texto = escape(apresentar_termo(termo))
    return f"<td><code>{texto}</code></td>" if termo["type"] == "uri" else f"<td>{texto}</td>"


def tabela_resultado(dado, legenda):
    variaveis = dado["head"]["vars"]
    linhas = dado["results"]["bindings"]
    if not linhas:
        return f'<p class="query-empty">{legenda}: nenhum resultado.</p>'
    cabecalho = "".join(f'<th scope="col">?{escape(v)}</th>' for v in variaveis)
    corpo = "".join(
        "<tr>" + "".join(celula_resultado(linha.get(v)) for v in variaveis) + "</tr>" for linha in linhas
    )
    return (
        f'<div class="table-wrap" role="region" aria-label="{escape(legenda)}" tabindex="0">'
        f"<table><caption>{escape(legenda)}</caption><thead><tr>{cabecalho}</tr></thead>"
        f"<tbody>{corpo}</tbody></table></div>"
    )


def bloco_consulta(nome, execucoes, textos, resultados):
    primeira = execucoes[0]
    complementar = primeira.get("complementar", False)
    numero = re.fullmatch(r"consulta0*([1-9][0-9]*)", nome)
    titulo = f"PC{numero.group(1)}. {escape(primeira['pergunta'])}" if numero else escape(primeira["pergunta"])
    partes = [f'<section class="query" id="{escape(nome)}"><h3>{titulo}</h3>']
    if complementar:
        partes.append('<p class="query-note">Consulta complementar, fora das seis perguntas de competência.</p>')
    tabelas, arquivos = [], [f'<a href="consultas/{escape(nome)}.rq">{escape(nome)}.rq</a>']
    for execucao in execucoes:
        parametros = ", ".join(
            f"?{chave} = {apresentar_termo({'type': 'uri', 'value': valor})}"
            for chave, valor in execucao["parametros"].items()
        )
        quantidade = execucao["linhas"]
        legenda = f"{parametros or 'Sem parâmetros'} · {quantidade} {'linha' if quantidade == 1 else 'linhas'}"
        tabelas.append(tabela_resultado(resultados[execucao["resultado"]], legenda))
        arquivos.append(
            f'<a href="consultas/resultados/{escape(execucao["resultado"])}">{escape(execucao["resultado"])}</a>'
        )
    partes.append(
        "<details><summary>Ver consulta SPARQL</summary>"
        f'<pre><code>{escape(textos[nome])}</code></pre></details>'
    )
    partes.extend(tabelas)
    partes.append(f'<p class="query-files">Arquivos: {" · ".join(arquivos)}</p></section>')
    return "".join(partes)


def secao_consultas(manifesto, textos, resultados):
    if manifesto is None:
        return (
            '<p class="query-empty">Os resultados ainda não foram exportados. Execute '
            "<code>codigo-fonte/executar_consultas.py</code> e gere o site novamente.</p>"
        )
    por_consulta = {}
    for execucao in manifesto["execucoes"]:
        por_consulta.setdefault(execucao["consulta"], []).append(execucao)
    return "\n".join(
        bloco_consulta(nome, execucoes, textos, resultados) for nome, execucoes in por_consulta.items()
    )


def data_br(texto):
    return date.fromisoformat(texto).strftime("%d/%m/%Y")


def secao_ligacoes(dados):
    itens = []
    for area in dados["areas"]:
        for item in area.get("correspondenciasExternas", []):
            itens.append(
                f'<li><strong>{escape(area["rotuloPreferido"])}</strong> '
                f'<code>inst:{escape(area["id"])}</code> → <code>{escape(item["predicado"])}</code> → '
                f'<code>{escape(item["uri"])}</code> ({escape(item["rotulo"])}, '
                f'<a href="{escape(item["fonte"])}">página da fonte</a>)'
                f'<p>{escape(item["justificativa"])}</p>'
                f'<p class="query-files">Conferido em {data_br(item["dataVerificacao"])}.</p></li>'
            )
    if not itens:
        return '<p class="query-empty">Nenhuma ligação externa registrada nos dados.</p>'
    return f'<ul class="detailed-list link-list">{"".join(itens)}</ul>'


def carregar_consultas(pasta_consultas):
    """Lê o manifesto, os resultados JSON e os textos .rq exportados pelo executor."""
    pasta = Path(pasta_consultas)
    manifesto_arquivo = pasta / "resultados" / "execucoes.json"
    if not manifesto_arquivo.is_file():
        return None, {}, {}
    manifesto = json.loads(manifesto_arquivo.read_text(encoding="utf-8"))
    resultados, textos = {}, {}
    for execucao in manifesto["execucoes"]:
        arquivo = pasta / "resultados" / execucao["resultado"]
        resultados[execucao["resultado"]] = json.loads(arquivo.read_text(encoding="utf-8"))
        textos[execucao["consulta"]] = (pasta / f"{execucao['consulta']}.rq").read_text(encoding="utf-8")
    return manifesto, resultados, textos


# Gravação ---------------------------------------------------------------------


def gravar(caminho, conteudo):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with NamedTemporaryFile(dir=caminho.parent, delete=False) as arquivo:
            temporario = Path(arquivo.name)
            arquivo.write(conteudo)
        temporario.replace(caminho)
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)


def gerar_site(caminho_dados: Path, destino: Path, pasta_consultas: Path = PASTA_CONSULTAS,
               pasta_ontologia: Path = PASTA_ONTOLOGIA) -> None:
    dados = carregar_dados(caminho_dados)
    indices = {
        colecao: {registro["id"]: registro for registro in dados[colecao]}
        for colecao in ("pessoas", "unidades", "cursos", "disciplinas", "areas")
    }
    pessoas = [pessoa for pessoa in dados["pessoas"] if "docencia" in pessoa or "discencia" in pessoa]
    ids_com_perfil = {pessoa["id"] for pessoa in pessoas}
    templates = FONTE / "templates"
    inicio = Template((templates / "inicio.html").read_text(encoding="utf-8"))
    perfil = Template((templates / "perfil.html").read_text(encoding="utf-8"))
    pagina_dados = Template((templates / "dados.html").read_text(encoding="utf-8"))
    quantidade = len(pessoas)
    html_inicio = inicio.substitute(
        raiz="",
        instituicao=escape(dados["instituicaoReferencia"]),
        quantidade=f"{quantidade} {'perfil' if quantidade == 1 else 'perfis'}",
        lista_perfis="\n".join(cartao(pessoa, indices) for pessoa in pessoas),
    )
    paginas = {
        perfil_url(pessoa): renderizar_perfil(perfil, pessoa, dados, indices, ids_com_perfil)
        for pessoa in pessoas
    }
    manifesto, resultados, textos = carregar_consultas(pasta_consultas)
    html_dados = pagina_dados.substitute(
        raiz="",
        instituicao=escape(dados["instituicaoReferencia"]),
        consultas=secao_consultas(manifesto, textos, resultados),
        ligacoes=secao_ligacoes(dados),
        repositorio=REPOSITORIO,
        licencas_wikidata=LICENCAS_WIKIDATA,
    )
    copias = {
        Path("assets") / "estilos.css": (FONTE / "recursos" / "estilos.css").read_bytes(),
        Path("assets") / "diretorio.js": (FONTE / "recursos" / "diretorio.js").read_bytes(),
    }
    for nome in ARQUIVOS_RDF:
        copias[Path("ontologia") / nome] = (Path(pasta_ontologia) / nome).read_bytes()
    for nome in textos:
        copias[Path("consultas") / f"{nome}.rq"] = (Path(pasta_consultas) / f"{nome}.rq").read_bytes()
    for arquivo in resultados:
        copias[Path("consultas") / "resultados" / arquivo] = (
            Path(pasta_consultas) / "resultados" / arquivo
        ).read_bytes()

    indice_anterior = destino / "index.html"
    perfis_anteriores = (
        set(LINK_DE_CARTAO.findall(indice_anterior.read_text(encoding="utf-8")))
        if indice_anterior.is_file() else set()
    )
    pasta_perfis = destino / "perfis"
    pasta_perfis.mkdir(parents=True, exist_ok=True)
    for caminho, conteudo in copias.items():
        gravar(destino / caminho, conteudo)
    for arquivo, html in paginas.items():
        gravar(pasta_perfis / arquivo, html.encode("utf-8"))
    gravar(destino / "dados.html", html_dados.encode("utf-8"))
    gravar(destino / "index.html", html_inicio.encode("utf-8"))
    for arquivo in perfis_anteriores - paginas.keys():
        (pasta_perfis / arquivo).unlink(missing_ok=True)
    for antigo in (destino / "consultas").glob("resultados/*.json"):
        if antigo.name not in resultados:
            antigo.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dados", type=Path, default=DADOS_PADRAO, help="Arquivo JSON de origem.")
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO, help="Diretório de saída estática.")
    args = parser.parse_args()
    try:
        gerar_site(args.dados, args.saida)
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Falha na geração: {erro}\n")
    print(f"Diretório gerado em {args.saida}")


if __name__ == "__main__":
    main()
