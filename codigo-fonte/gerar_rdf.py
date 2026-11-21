"""Gera o grafo RDF/Turtle do ConectaAcadêmico a partir do JSON validado."""

import argparse
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
from urllib.parse import urlsplit

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, SKOS, XSD

from validar_dados import carregar_dados


RAIZ = Path(__file__).resolve().parent.parent
DADOS_PADRAO = RAIZ / "exemplos" / "perfis" / "dados.json"
ONTOLOGIA_PADRAO = RAIZ / "ontologia" / "conecta-academico.ttl"
SAIDA_PADRAO = RAIZ / "ontologia" / "instancias.ttl"

BASE = "https://pedromota07.github.io/conecta-academico/"
ONTOLOGIA = BASE + "ontologia/conecta-academico.ttl"
DADOS = BASE + "ontologia/instancias.ttl"
CA = Namespace(ONTOLOGIA + "#")
INST = Namespace(DADOS + "#")
SCHEMA = Namespace("https://schema.org/")
ESQUEMA_AREAS = INST["esquema/areas"]

TIPOS = {
    "pessoas": CA.Pessoa,
    "unidades": CA.UnidadeAcademica,
    "cursos": CA.CursoGraduacao,
    "disciplinas": CA.Disciplina,
    "areas": CA.AreaConhecimento,
    "projetos": CA.ProjetoPesquisa,
    "grupos": CA.GrupoPesquisa,
    "publicacoes": CA.Publicacao,
}
PAPEIS = {"docencia": CA.Docente, "discencia": CA.Discente}

CARACTERES_INVALIDOS_FONTE = re.compile(r'[\s\x00-\x1f\x7f<>"{}|\\^\x60]')
ESCAPES_IRI = str.maketrans({caractere: f"%{ord(caractere):02X}" for caractere in "{}|^\x60"})


def _portugues(texto):
    return Literal(texto, lang="pt-BR")


def _iri_externa(valor):
    return URIRef(valor.translate(ESCAPES_IRI))


ATRIBUTOS = (
    ("id", SCHEMA.identifier, Literal),
    ("nome", SCHEMA.name, _portugues),
    ("apresentacao", DCTERMS.description, _portugues),
    ("formacao", CA.formacao, _portugues),
    ("linksAcademicos", CA.linkAcademico, _iri_externa),
    ("cargo", CA.cargo, _portugues),
    ("tipoUnidade", CA.tipoUnidade, Literal),
    ("rotuloPreferido", SKOS.prefLabel, _portugues),
    ("rotulosAlternativos", SKOS.altLabel, _portugues),
    ("definicao", SKOS.definition, _portugues),
    ("titulo", DCTERMS.title, _portugues),
    ("descricao", DCTERMS.description, _portugues),
    ("linhaAtuacao", CA.linhaAtuacao, _portugues),
    ("tipoProducao", CA.tipoProducao, Literal),
    ("anoPublicacao", CA.anoPublicacao, Literal),
    ("linkBibliografico", CA.linkBibliografico, _iri_externa),
)

RELACOES = (
    ("unidadesDocentes", (CA.temVinculoDocente,)),
    ("unidadesDiscentes", (CA.temVinculoDiscente,)),
    ("cursos", (CA.matriculadoEm,)),
    ("unidadeResponsavel", (CA.temUnidadeResponsavel,)),
    ("unidadeSuperior", (CA.temUnidadeSuperior,)),
    ("disciplinas", (CA.incluiDisciplina,)),
    ("disciplinasMinistradas", (CA.ministraDisciplina,)),
    ("disciplinasCursadas", (CA.cursaDisciplina,)),
    ("areasAtuacao", (CA.atuaEmArea,)),
    ("areasInteresse", (CA.temInteresseEmArea,)),
    ("areasMaisAmplas", (CA.temAreaMaisAmpla, SKOS.broader)),
    ("participantes", (CA.temParticipante,)),
    ("membros", (CA.temMembro,)),
    ("projetos", (CA.associadoAoProjeto,)),
    ("autores", (CA.temAutor, SCHEMA.author)),
)


def _valores(registro, campo):
    valor = registro.get(campo, [])
    return valor if isinstance(valor, list) else (valor,)


def _adicionar_campos(grafo, sujeito, registro):
    for campo, predicado, converter in ATRIBUTOS:
        for valor in _valores(registro, campo):
            grafo.add((sujeito, predicado, converter(valor)))
    for campo, predicados in RELACOES:
        for identificador in _valores(registro, campo):
            for predicado in predicados:
                grafo.add((sujeito, predicado, INST[identificador]))


def _adicionar_papeis(grafo, sujeito, pessoa):
    if not PAPEIS.keys() & pessoa.keys():
        return
    pagina = URIRef(f"{BASE}perfis/{pessoa['id']}.html")
    grafo.add((pagina, RDF.type, SCHEMA.ProfilePage))
    grafo.add((sujeito, SCHEMA.mainEntityOfPage, pagina))
    for bloco, classe in PAPEIS.items():
        if bloco in pessoa:
            grafo.add((sujeito, RDF.type, classe))
            _adicionar_campos(grafo, sujeito, pessoa[bloco])


def _adicionar_registros(grafo, dados):
    for colecao, classe in TIPOS.items():
        for registro in dados[colecao]:
            sujeito = INST[registro["id"]]
            grafo.add((sujeito, RDF.type, classe))
            _adicionar_campos(grafo, sujeito, registro)
            if colecao == "pessoas":
                _adicionar_papeis(grafo, sujeito, registro)
            if colecao == "unidades" and registro["tipoUnidade"] == "departamento":
                grafo.add((sujeito, RDF.type, CA.Departamento))
            if colecao == "areas":
                grafo.add((sujeito, RDF.type, SKOS.Concept))
                grafo.add((sujeito, SKOS.inScheme, ESQUEMA_AREAS))


def _uri_da_fonte(fonte):
    if CARACTERES_INVALIDOS_FONTE.search(fonte):
        return None
    try:
        partes = urlsplit(fonte)
        if partes.scheme in {"http", "https"} and not partes.hostname:
            return None
    except ValueError:
        return None
    if partes.scheme and (partes.netloc or partes.path):
        return URIRef(fonte)
    return None


def _adicionar_metadados(grafo, dados):
    conjunto = URIRef(DADOS)
    grafo.add((conjunto, RDF.type, SCHEMA.Dataset))
    grafo.add((conjunto, CA.instituicaoReferencia, _portugues(dados["instituicaoReferencia"])))
    grafo.add((ESQUEMA_AREAS, RDF.type, SKOS.ConceptScheme))
    for fonte in dados.get("fontes", []):
        uri = _uri_da_fonte(fonte)
        if uri is None:
            grafo.add((conjunto, CA.fonteEditorial, _portugues(fonte)))
        else:
            grafo.add((conjunto, DCTERMS.source, uri))
    if "licenca" in dados:
        grafo.add((conjunto, DCTERMS.license, _iri_externa(dados["licenca"])))
    if "dataAtualizacao" in dados:
        grafo.add((conjunto, DCTERMS.modified, Literal(dados["dataAtualizacao"], datatype=XSD.date)))


def _gravar(caminho, conteudo):
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


def gerar_rdf(caminho_dados: Path, destino: Path) -> Graph:
    """Valida o JSON, grava o Turtle e devolve o grafo gerado."""
    caminho_dados = Path(caminho_dados)
    destino = Path(destino)
    if destino.suffix.lower() != ".ttl":
        raise ValueError("A saída Turtle deve ter extensão .ttl.")
    if destino.resolve() in {caminho_dados.resolve(), ONTOLOGIA_PADRAO.resolve()}:
        raise ValueError("Escolha uma saída que preserve o JSON e a ontologia.")

    dados = carregar_dados(caminho_dados)
    grafo = Graph(bind_namespaces="none")
    for prefixo, namespace in (
        ("ca", CA), ("inst", INST), ("schema", SCHEMA), ("dcterms", DCTERMS),
        ("rdf", RDF), ("skos", SKOS), ("xsd", XSD),
    ):
        grafo.bind(prefixo, namespace)
    _adicionar_registros(grafo, dados)
    _adicionar_metadados(grafo, dados)
    turtle = grafo.serialize(format="turtle", encoding="utf-8")
    _gravar(destino, turtle.rstrip(b"\n") + b"\n")
    return grafo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", type=Path, default=DADOS_PADRAO, help="Arquivo JSON de origem.")
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO, help="Arquivo Turtle de destino.")
    parser.add_argument("--publicaveis", type=Path, metavar="PASTA",
                        help="Pasta para copiar a ontologia e o grafo pronto para hospedagem estática.")
    args = parser.parse_args()

    try:
        if args.publicaveis is not None:
            copia_ontologia = args.publicaveis / ONTOLOGIA_PADRAO.name
            copia_instancias = args.publicaveis / SAIDA_PADRAO.name
            protegidos = {args.dados.resolve(), ONTOLOGIA_PADRAO.resolve()}
            if (
                copia_ontologia.resolve() in protegidos | {args.saida.resolve(), copia_instancias.resolve()}
                or copia_instancias.resolve() in protegidos
            ):
                raise ValueError("Escolha uma pasta de cópias que preserve os arquivos de origem.")
            ontologia = ONTOLOGIA_PADRAO.read_bytes()
        grafo = gerar_rdf(args.dados, args.saida)
        if args.publicaveis is not None:
            _gravar(copia_ontologia, ontologia)
            if copia_instancias.resolve() != args.saida.resolve():
                _gravar(copia_instancias, args.saida.read_bytes())
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Falha na geração RDF: {erro}\n")
    print(f"Grafo com {len(grafo)} triplas gravado em {args.saida}")


if __name__ == "__main__":
    main()
