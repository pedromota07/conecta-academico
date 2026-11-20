"""Validação da fonte editorial do ConectaAcadêmico."""

from datetime import date
from graphlib import CycleError, TopologicalSorter
import json
from pathlib import Path
import re
from urllib.parse import urlsplit


COLECOES = ("pessoas", "unidades", "cursos", "disciplinas", "areas", "projetos", "grupos", "publicacoes")
FORMATO_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
CARACTERES_INVALIDOS_URL = re.compile(r'[\s\x00-\x1f\x7f<>"\\]')
ROTULO_DOMINIO = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")


def _texto(valor, caminho):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{caminho}: informe um texto preenchido.")
    if re.search(r"[\x00\ud800-\udfff]", valor):
        raise ValueError(f"{caminho}: o texto contém caracteres inválidos.")


def _id(valor, caminho):
    if not isinstance(valor, str) or not FORMATO_ID.fullmatch(valor):
        raise ValueError(f"{caminho}: identificador inválido, use letras minúsculas, dígitos e hífens.")


def _lista(valor, caminho):
    if not isinstance(valor, list):
        raise ValueError(f"{caminho}: informe uma lista.")


def _lista_de(validar_item, minimo=0, unica=False):
    def validar(valor, caminho):
        _lista(valor, caminho)
        if len(valor) < minimo:
            raise ValueError(f"{caminho}: informe ao menos {minimo} item.")
        for indice, item in enumerate(valor):
            validar_item(item, f"{caminho}[{indice}]")
        if unica and len(set(valor)) != len(valor):
            raise ValueError(f"{caminho}: a lista contém itens duplicados.")

    return validar


def _objeto(obrigatorios, opcionais=None):
    campos = {**obrigatorios, **(opcionais or {})}

    def validar(valor, caminho):
        if not isinstance(valor, dict):
            raise ValueError(f"{caminho}: informe um objeto.")
        for campo in obrigatorios:
            if campo not in valor:
                raise ValueError(f"{caminho}.{campo}: campo obrigatório ausente.")
        for campo, conteudo in valor.items():
            if campo not in campos:
                raise ValueError(f"{caminho}.{campo}: campo desconhecido.")
            campos[campo](conteudo, f"{caminho}.{campo}")

    return validar


def _opcoes(*opcoes):
    def validar(valor, caminho):
        if valor not in opcoes:
            raise ValueError(f"{caminho}: use um destes valores ({', '.join(opcoes)}).")

    return validar


def _uri(valor, caminho):
    _texto(valor, caminho)
    if CARACTERES_INVALIDOS_URL.search(valor):
        raise ValueError(f"{caminho}: a URI contém caracteres inválidos.")
    try:
        partes = urlsplit(valor)
        _ = partes.port
    except ValueError as erro:
        raise ValueError(f"{caminho}: URI inválida.") from erro
    if not partes.scheme or not (partes.netloc or partes.path):
        raise ValueError(f"{caminho}: informe uma URI absoluta.")
    return partes


def _https(valor, caminho):
    partes = _uri(valor, caminho)
    dominio = partes.hostname
    if partes.scheme != "https" or not dominio or partes.username is not None:
        raise ValueError(f"{caminho}: informe uma URL HTTPS com domínio e sem credenciais.")
    if ":" in dominio:
        if not re.fullmatch(r"\[[^\]]+\](?::[0-9]+)?", partes.netloc):
            raise ValueError(f"{caminho}: endereço HTTPS inválido.")
        return
    try:
        rotulos = dominio.encode("idna").decode("ascii").removesuffix(".").split(".")
    except UnicodeError as erro:
        raise ValueError(f"{caminho}: domínio HTTPS inválido.") from erro
    if partes.netloc.endswith(":") or not all(ROTULO_DOMINIO.fullmatch(rotulo) for rotulo in rotulos):
        raise ValueError(f"{caminho}: domínio ou porta HTTPS inválida.")


def _data(valor, caminho):
    if not isinstance(valor, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", valor):
        raise ValueError(f"{caminho}: informe a data no formato AAAA-MM-DD.")
    try:
        date.fromisoformat(valor)
    except ValueError as erro:
        raise ValueError(f"{caminho}: informe uma data válida.") from erro


def _ano(valor, caminho):
    if type(valor) is not int or not 1000 <= valor <= 9999:
        raise ValueError(f"{caminho}: informe um ano inteiro de quatro dígitos.")


def _indexar_identificadores(dados):
    tipos = {}
    for colecao in COLECOES:
        for indice, registro in enumerate(dados[colecao]):
            caminho = f"{colecao}[{indice}]"
            if not isinstance(registro, dict):
                raise ValueError(f"{caminho}: informe um objeto.")
            identificador = registro.get("id")
            _id(identificador, f"{caminho}.id")
            if identificador in tipos:
                raise ValueError(f"{caminho}.id: identificador duplicado {identificador!r}.")
            tipos[identificador] = colecao
    return tipos


def _validar_registros(dados, tipos):
    def referencia(destino):
        def validar(valor, caminho):
            _id(valor, caminho)
            tipo = tipos.get(valor)
            if tipo is None:
                raise ValueError(f"{caminho}: referência inexistente {valor!r}.")
            if tipo != destino:
                raise ValueError(f"{caminho}: {valor!r} pertence a {tipo}, mas o campo exige {destino}.")

        return validar

    pessoa = referencia("pessoas")
    unidade = referencia("unidades")
    curso = referencia("cursos")
    disciplina = referencia("disciplinas")
    area = referencia("areas")
    projeto = referencia("projetos")

    docencia = _objeto(
        {"unidadesDocentes": _lista_de(unidade, minimo=1, unica=True)},
        {
            "cargo": _texto,
            "areasAtuacao": _lista_de(area, unica=True),
            "disciplinasMinistradas": _lista_de(disciplina, unica=True),
        },
    )
    discencia = _objeto(
        {
            "unidadesDiscentes": _lista_de(unidade, minimo=1, unica=True),
            "cursos": _lista_de(curso, minimo=1, unica=True),
        },
        {
            "areasInteresse": _lista_de(area, unica=True),
            "disciplinasCursadas": _lista_de(disciplina, unica=True),
        },
    )
    esquemas = {
        "pessoas": _objeto(
            {"id": _id, "nome": _texto},
            {
                "apresentacao": _texto,
                "formacao": _lista_de(_texto),
                "linksAcademicos": _lista_de(_https, unica=True),
                "docencia": docencia,
                "discencia": discencia,
            },
        ),
        "unidades": _objeto(
            {"id": _id, "nome": _texto, "tipoUnidade": _opcoes("instituto", "departamento", "outra")},
            {"unidadeSuperior": unidade},
        ),
        "cursos": _objeto(
            {"id": _id, "nome": _texto, "unidadeResponsavel": unidade},
            {"disciplinas": _lista_de(disciplina, unica=True)},
        ),
        "disciplinas": _objeto({"id": _id, "nome": _texto}),
        "areas": _objeto(
            {"id": _id, "rotuloPreferido": _texto, "definicao": _texto},
            {"rotulosAlternativos": _lista_de(_texto), "areasMaisAmplas": _lista_de(area, unica=True)},
        ),
        "projetos": _objeto(
            {
                "id": _id,
                "titulo": _texto,
                "descricao": _texto,
                "participantes": _lista_de(pessoa, minimo=1, unica=True),
            },
        ),
        "grupos": _objeto(
            {"id": _id, "nome": _texto, "membros": _lista_de(pessoa, minimo=1, unica=True)},
            {"linhaAtuacao": _texto, "projetos": _lista_de(projeto, unica=True)},
        ),
        "publicacoes": _objeto(
            {"id": _id, "titulo": _texto, "tipoProducao": _opcoes("artigo", "trabalho-academico", "outra")},
            {"anoPublicacao": _ano, "linkBibliografico": _https, "autores": _lista_de(pessoa, unica=True)},
        ),
    }
    for colecao, validar in esquemas.items():
        for registro in dados[colecao]:
            validar(registro, f"{colecao}[{registro['id']}]")


def _sem_ciclo(hierarquia, caminho):
    try:
        TopologicalSorter(hierarquia).prepare()
    except CycleError as erro:
        ciclo = " → ".join(erro.args[1])
        raise ValueError(f"{caminho}: ciclo entre os identificadores {ciclo}.") from erro


def validar_dados(dados):
    """Valida o conjunto editorial e informa o primeiro problema com ValueError."""
    _objeto(
        {"instituicaoReferencia": _texto, **dict.fromkeys(COLECOES, _lista)},
        {"fontes": _lista_de(_texto, minimo=1), "licenca": _uri, "dataAtualizacao": _data},
    )(dados, "dados")
    tipos = _indexar_identificadores(dados)
    _validar_registros(dados, tipos)

    for area in dados["areas"]:
        rotulos = [area["rotuloPreferido"], *area.get("rotulosAlternativos", [])]
        if len({rotulo.strip().casefold() for rotulo in rotulos}) != len(rotulos):
            raise ValueError(f"areas[{area['id']}]: os rótulos preferido e alternativos devem ser distintos.")

    hierarquia_unidades = {
        unidade["id"]: [unidade["unidadeSuperior"]] if "unidadeSuperior" in unidade else []
        for unidade in dados["unidades"]
    }
    _sem_ciclo(hierarquia_unidades, "unidades.unidadeSuperior")
    _sem_ciclo(
        {area["id"]: area.get("areasMaisAmplas", []) for area in dados["areas"]},
        "areas.areasMaisAmplas",
    )

    docentes = {pessoa["id"] for pessoa in dados["pessoas"] if "docencia" in pessoa}
    discentes = {pessoa["id"] for pessoa in dados["pessoas"] if "discencia" in pessoa}
    if len(docentes) < 2 or len(discentes) < 2 or len(docentes | discentes) < 4:
        raise ValueError("pessoas: são necessários dois docentes e dois discentes em quatro pessoas distintas.")


def _pares_unicos(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(f"JSON: chave duplicada {chave!r}.")
        objeto[chave] = valor
    return objeto


def _constante_invalida(valor):
    raise ValueError(f"JSON: valor inválido {valor!r}.")


def carregar_dados(caminho):
    """Lê um arquivo JSON em UTF-8 e devolve o conjunto validado."""
    with Path(caminho).open(encoding="utf-8") as arquivo:
        try:
            dados = json.load(arquivo, object_pairs_hook=_pares_unicos, parse_constant=_constante_invalida)
        except json.JSONDecodeError as erro:
            raise ValueError(f"JSON inválido na linha {erro.lineno}, coluna {erro.colno}.") from erro
    validar_dados(dados)
    return dados
