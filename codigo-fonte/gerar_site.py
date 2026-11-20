"""Gera o diretório estático do ConectaAcadêmico a partir dos dados editoriais."""

import argparse
import re
from html import escape
from pathlib import Path
from string import Template
from tempfile import NamedTemporaryFile

from validar_dados import carregar_dados


FONTE = Path(__file__).resolve().parent
DADOS_PADRAO = FONTE.parent / "exemplos" / "perfis" / "dados.json"
SAIDA_PADRAO = FONTE.parent / "docs"
LINK_DE_CARTAO = re.compile(r'<h3><a href="perfis/([a-z0-9]+(?:-[a-z0-9]+)*\.html)">')


def lista(itens, classe="clean-list"):
    if not itens:
        return ""
    return f'<ul class="{classe}">' + "".join(f"<li>{item}</li>" for item in itens) + "</ul>"


def secao(titulo, conteudo):
    if not conteudo:
        return ""
    return f'<section class="card"><h2>{titulo}</h2>{conteudo}</section>'


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


def cartao(pessoa, indices):
    tipo, papel = papeis(pessoa)
    nome = escape(pessoa["nome"])
    docencia = pessoa.get("docencia", {})
    discencia = pessoa.get("discencia", {})
    locais = rotulos(indices["unidades"], docencia.get("unidadesDocentes", []))
    locais += rotulos(indices["cursos"], discencia.get("cursos", []))
    contexto = " · ".join(locais)
    return (
        f'<li class="profile-card" data-papel="{tipo}">'
        '<div class="profile-card-top">'
        f'<span class="avatar" aria-hidden="true">{escape(iniciais(pessoa["nome"]))}</span>'
        f'<span class="role-label">{papel}</span></div>'
        f'<h3><a href="perfis/{perfil_url(pessoa)}">{nome}</a></h3>'
        f'<p class="profile-card-detail">{contexto}</p></li>'
    )


def vinculos(pessoa, dados, indices):
    pares = [("Instituição", [escape(dados["instituicaoReferencia"])])]
    docencia = pessoa.get("docencia", {})
    discencia = pessoa.get("discencia", {})
    pares.extend([
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
    ano = f' <span class="publication-year">({obra["anoPublicacao"]})</span>' if "anoPublicacao" in obra else ""
    autores = []
    for chave in obra.get("autores", []):
        pessoa = pessoas[chave]
        nome = escape(pessoa["nome"])
        if chave in ids_com_perfil:
            nome = f'<a href="{perfil_url(pessoa)}">{nome}</a>'
        autores.append(nome)
    autoria = f'<p class="publication-authors">{" · ".join(autores)}</p>' if autores else ""
    return f"<strong>{titulo}</strong>{ano}{autoria}"


def secoes_do_perfil(pessoa, dados, indices, ids_com_perfil):
    secoes = []
    if "apresentacao" in pessoa:
        secoes.append(secao("Apresentação", f'<p>{escape(pessoa["apresentacao"])}</p>'))
    secoes.append(secao("Formação acadêmica", lista([escape(item) for item in pessoa.get("formacao", [])])))

    docencia = pessoa.get("docencia", {})
    discencia = pessoa.get("discencia", {})
    for titulo, papel, campo in (
        ("Áreas de atuação", docencia, "areasAtuacao"),
        ("Áreas de interesse", discencia, "areasInteresse"),
    ):
        areas = rotulos(indices["areas"], papel.get(campo, []), "rotuloPreferido")
        secoes.append(secao(titulo, lista(areas, "tag-list")))
    for titulo, papel, campo in (
        ("Disciplinas ministradas", docencia, "disciplinasMinistradas"),
        ("Disciplinas cursadas", discencia, "disciplinasCursadas"),
    ):
        secoes.append(secao(titulo, lista(rotulos(indices["disciplinas"], papel.get(campo, [])))))

    chave = pessoa["id"]
    projetos = [
        item_descritivo(projeto["titulo"], projeto["descricao"])
        for projeto in dados["projetos"] if chave in projeto["participantes"]
    ]
    grupos = [
        item_descritivo(grupo["nome"], grupo.get("linhaAtuacao"))
        for grupo in dados["grupos"] if chave in grupo["membros"]
    ]
    obras = [
        publicacao(obra, indices["pessoas"], ids_com_perfil)
        for obra in dados["publicacoes"] if chave in obra.get("autores", [])
    ]
    secoes.extend([
        secao("Projetos de pesquisa", lista(projetos, "clean-list detailed-list")),
        secao("Grupos de pesquisa", lista(grupos, "clean-list detailed-list")),
        secao("Publicações e trabalhos", lista(obras, "clean-list detailed-list")),
    ])
    return "\n".join(conteudo for conteudo in secoes if conteudo)


def renderizar_perfil(template, pessoa, dados, indices, ids_com_perfil):
    tipo, papel = papeis(pessoa)
    docencia = pessoa.get("docencia", {})
    discencia = pessoa.get("discencia", {})
    cargo = docencia.get("cargo")
    contexto = [escape(cargo)] if cargo else []
    contexto += rotulos(indices["unidades"], docencia.get("unidadesDocentes", []))
    contexto += rotulos(indices["cursos"], discencia.get("cursos", []))
    subtitulo = f'<p class="profile-subtitle">{" · ".join(contexto)}</p>'
    links = [f'<a href="{escape(url)}">{escape(url)}</a>' for url in pessoa.get("linksAcademicos", [])]
    return template.substitute(
        raiz="../",
        instituicao=escape(dados["instituicaoReferencia"]),
        nome=escape(pessoa["nome"]),
        iniciais=escape(iniciais(pessoa["nome"])),
        papel=papel,
        tipo_papel=tipo,
        subtitulo=subtitulo,
        secoes=secoes_do_perfil(pessoa, dados, indices, ids_com_perfil),
        vinculos=vinculos(pessoa, dados, indices),
        links=secao("Links acadêmicos", lista(links, "clean-list academic-links")),
    )


def gravar(caminho, conteudo):
    temporario = None
    try:
        with NamedTemporaryFile(dir=caminho.parent, delete=False) as arquivo:
            temporario = Path(arquivo.name)
            arquivo.write(conteudo)
        temporario.replace(caminho)
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)


def gerar_site(caminho_dados: Path, destino: Path) -> None:
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
    html_inicio = inicio.substitute(
        raiz="",
        instituicao=escape(dados["instituicaoReferencia"]),
        lista_perfis="\n".join(cartao(pessoa, indices) for pessoa in pessoas),
    )
    paginas = {
        perfil_url(pessoa): renderizar_perfil(perfil, pessoa, dados, indices, ids_com_perfil)
        for pessoa in pessoas
    }
    estilos = (FONTE / "recursos" / "estilos.css").read_bytes()

    indice_anterior = destino / "index.html"
    perfis_anteriores = (
        set(LINK_DE_CARTAO.findall(indice_anterior.read_text(encoding="utf-8")))
        if indice_anterior.is_file() else set()
    )
    pasta_perfis = destino / "perfis"
    pasta_assets = destino / "assets"
    pasta_perfis.mkdir(parents=True, exist_ok=True)
    pasta_assets.mkdir(parents=True, exist_ok=True)
    gravar(pasta_assets / "estilos.css", estilos)
    for arquivo, html in paginas.items():
        gravar(pasta_perfis / arquivo, html.encode("utf-8"))
    gravar(destino / "index.html", html_inicio.encode("utf-8"))
    for arquivo in perfis_anteriores - paginas.keys():
        (pasta_perfis / arquivo).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
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
