from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD


RAIZ = Path(__file__).resolve().parents[1]
FONTE = RAIZ / "exemplos" / "perfis" / "dados.json"
ONTOLOGIA = RAIZ / "ontologia" / "conecta-academico.ttl"
INSTANCIAS = RAIZ / "ontologia" / "instancias.ttl"
BASE = "https://pedromota07.github.io/conecta-academico/"
DOCUMENTO_ONTOLOGIA = URIRef(BASE + "ontologia/conecta-academico.ttl")
DOCUMENTO_DADOS = URIRef(BASE + "ontologia/instancias.ttl")
CA = Namespace(str(DOCUMENTO_ONTOLOGIA) + "#")
DADOS = Namespace(str(DOCUMENTO_DADOS) + "#")
SCHEMA = Namespace("https://schema.org/")
AIISO = Namespace("http://purl.org/vocab/aiiso/schema#")
ESQUEMA = DADOS["esquema/areas"]
PORTUGUES = "pt-BR"

sys.path.insert(0, str(RAIZ / "codigo-fonte"))
from gerar_rdf import gerar_rdf
from gerar_site import gerar_site


CLASSES = {
    "pessoas": CA.Pessoa,
    "unidades": CA.UnidadeAcademica,
    "cursos": CA.CursoGraduacao,
    "disciplinas": CA.Disciplina,
    "areas": CA.AreaConhecimento,
    "projetos": CA.ProjetoPesquisa,
    "grupos": CA.GrupoPesquisa,
    "publicacoes": CA.Publicacao,
}
SUBCLASSES = {
    CA.Docente: CA.Pessoa,
    CA.Discente: CA.Pessoa,
    CA.Departamento: CA.UnidadeAcademica,
}

# Cada relação indica coleção, caminho JSON, propriedade local, domínio e alcance.
RELACOES = (
    ("pessoas", ("docencia", "unidadesDocentes"), CA.temVinculoDocente, CA.Docente, CA.UnidadeAcademica),
    ("pessoas", ("discencia", "unidadesDiscentes"), CA.temVinculoDiscente, CA.Discente, CA.UnidadeAcademica),
    ("pessoas", ("discencia", "cursos"), CA.matriculadoEm, CA.Discente, CA.CursoGraduacao),
    ("cursos", ("unidadeResponsavel",), CA.temUnidadeResponsavel, CA.CursoGraduacao, CA.UnidadeAcademica),
    ("unidades", ("unidadeSuperior",), CA.temUnidadeSuperior, CA.UnidadeAcademica, CA.UnidadeAcademica),
    ("cursos", ("disciplinas",), CA.incluiDisciplina, CA.CursoGraduacao, CA.Disciplina),
    ("pessoas", ("docencia", "disciplinasMinistradas"), CA.ministraDisciplina, CA.Docente, CA.Disciplina),
    ("pessoas", ("discencia", "disciplinasCursadas"), CA.cursaDisciplina, CA.Discente, CA.Disciplina),
    ("pessoas", ("docencia", "areasAtuacao"), CA.atuaEmArea, CA.Docente, CA.AreaConhecimento),
    ("pessoas", ("discencia", "areasInteresse"), CA.temInteresseEmArea, CA.Discente, CA.AreaConhecimento),
    ("areas", ("areasMaisAmplas",), CA.temAreaMaisAmpla, CA.AreaConhecimento, CA.AreaConhecimento),
    ("projetos", ("participantes",), CA.temParticipante, CA.ProjetoPesquisa, CA.Pessoa),
    ("grupos", ("membros",), CA.temMembro, CA.GrupoPesquisa, CA.Pessoa),
    ("grupos", ("projetos",), CA.associadoAoProjeto, CA.GrupoPesquisa, CA.ProjetoPesquisa),
    ("publicacoes", ("autores",), CA.temAutor, CA.Publicacao, CA.Pessoa),
)


def buscar(registro, caminho, padrao=None):
    for chave in caminho:
        if chave not in registro:
            return padrao
        registro = registro[chave]
    return registro


def uri_perfil(identificador):
    return URIRef(f"{BASE}perfis/{identificador}.html")


def texto(valor):
    return Literal(valor, lang=PORTUGUES)


class TesteRDF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.json = json.loads(FONTE.read_text(encoding="utf-8"))
        cls.ontologia = Graph().parse(ONTOLOGIA, format="turtle")
        cls.grafo = Graph().parse(INSTANCIAS, format="turtle")

    def gerar_em_temporario(self, dados=None):
        temporario = TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        pasta = Path(temporario.name)
        fonte = FONTE
        if dados is not None:
            fonte = pasta / "dados-teste.json"
            fonte.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        saida = pasta / "instancias.ttl"
        resultado = gerar_rdf(fonte, saida)
        return resultado, Graph().parse(saida, format="turtle")

    def test_ontologia_carrega_com_as_onze_classes_rotuladas(self):
        self.assertIn((DOCUMENTO_ONTOLOGIA, RDF.type, OWL.Ontology), self.ontologia)
        classes = {
            classe for classe in self.ontologia.subjects(RDF.type, OWL.Class)
            if str(classe).startswith(CA)
        }
        self.assertEqual(classes, set(CLASSES.values()) | SUBCLASSES.keys())
        for classe in classes:
            with self.subTest(classe=classe):
                for predicado in (RDFS.label, RDFS.comment):
                    self.assertTrue(any(
                        isinstance(valor, Literal) and valor.language == PORTUGUES
                        for valor in self.ontologia.objects(classe, predicado)
                    ))

    def test_especializacoes_sem_disjuncao_entre_papeis(self):
        for subclasse, classe in SUBCLASSES.items():
            self.assertIn((subclasse, RDFS.subClassOf, classe), self.ontologia)
        self.assertNotIn((CA.Docente, OWL.disjointWith, CA.Discente), self.ontologia)
        self.assertNotIn((CA.Discente, OWL.disjointWith, CA.Docente), self.ontologia)
        for ax in self.ontologia.subjects(RDF.type, OWL.AllDisjointClasses):
            for lista in self.ontologia.objects(ax, OWL.members):
                self.assertFalse({CA.Docente, CA.Discente} <= set(self.ontologia.items(lista)))

    def test_dominios_e_alcances_das_quinze_relacoes_conforme_dicionario(self):
        for numero, (_, _, propriedade, dominio, alcance) in enumerate(RELACOES, start=1):
            with self.subTest(relacao=f"R{numero:02}"):
                self.assertIn((propriedade, RDF.type, OWL.ObjectProperty), self.ontologia)
                self.assertEqual(set(self.ontologia.objects(propriedade, RDFS.domain)), {dominio})
                self.assertEqual(set(self.ontologia.objects(propriedade, RDFS.range)), {alcance})

    def test_alinhamentos_externos_sem_redefinir_vocabularios(self):
        self.assertIn((CA.Pessoa, RDFS.subClassOf, SCHEMA.Person), self.ontologia)
        self.assertIn((CA.Departamento, RDFS.subClassOf, AIISO.Department), self.ontologia)
        self.assertIn((CA.AreaConhecimento, RDFS.subClassOf, SKOS.Concept), self.ontologia)
        for propriedade, externa in (
            (CA.temVinculoDocente, SCHEMA.affiliation),
            (CA.temVinculoDiscente, SCHEMA.affiliation),
            (CA.temUnidadeSuperior, AIISO.part_of),
            (CA.incluiDisciplina, SCHEMA.hasCourse),
            (CA.temAreaMaisAmpla, SKOS.broader),
            (CA.temAutor, SCHEMA.author),
        ):
            with self.subTest(propriedade=propriedade):
                self.assertIn((propriedade, RDFS.subPropertyOf, externa), self.ontologia)
                self.assertFalse(set(self.ontologia.objects(externa, RDFS.domain)))
                self.assertFalse(set(self.ontologia.objects(externa, RDFS.range)))
        for predicado in (OWL.imports, OWL.equivalentClass, OWL.equivalentProperty, OWL.sameAs):
            self.assertFalse(set(self.ontologia.subject_objects(predicado)))

    def test_alcances_das_propriedades_locais_de_dados(self):
        texto_com_idioma = URIRef(str(RDF) + "PlainLiteral")
        for propriedade, dominio, alcance in (
            (CA.formacao, CA.Pessoa, texto_com_idioma),
            (CA.cargo, CA.Docente, texto_com_idioma),
            (CA.linhaAtuacao, CA.GrupoPesquisa, texto_com_idioma),
            (CA.tipoUnidade, CA.UnidadeAcademica, XSD.string),
            (CA.tipoProducao, CA.Publicacao, XSD.string),
            (CA.anoPublicacao, CA.Publicacao, XSD.integer),
            (CA.instituicaoReferencia, SCHEMA.Dataset, texto_com_idioma),
            (CA.fonteEditorial, SCHEMA.Dataset, texto_com_idioma),
        ):
            with self.subTest(propriedade=propriedade):
                self.assertIn((propriedade, RDF.type, OWL.DatatypeProperty), self.ontologia)
                self.assertEqual(set(self.ontologia.objects(propriedade, RDFS.domain)), {dominio})
                self.assertEqual(set(self.ontologia.objects(propriedade, RDFS.range)), {alcance})

    def test_vinte_e_oito_registros_tipos_e_correspondencia_de_identificadores(self):
        esperados = {
            (DADOS[registro["id"]], Literal(registro["id"]))
            for colecao in CLASSES for registro in self.json[colecao]
        }
        self.assertEqual(len(esperados), 28)
        self.assertEqual(set(self.grafo.subject_objects(SCHEMA.identifier)), esperados)
        for colecao, classe in CLASSES.items():
            for registro in self.json[colecao]:
                with self.subTest(registro=registro["id"]):
                    recurso = DADOS[registro["id"]]
                    self.assertIn((recurso, RDF.type, classe), self.grafo)
                    if registro.get("tipoUnidade") == "departamento":
                        self.assertIn((recurso, RDF.type, CA.Departamento), self.grafo)

    def test_quatro_perfis_tipados_com_recursos_e_paginas_distintos(self):
        for campo, classe in (("docencia", CA.Docente), ("discencia", CA.Discente)):
            membros = {DADOS[pessoa["id"]] for pessoa in self.json["pessoas"] if campo in pessoa}
            self.assertEqual(len(membros), 2)
            self.assertEqual(set(self.grafo.subjects(RDF.type, classe)), membros)
        self.assertEqual(len(set(self.grafo.subjects(SCHEMA.mainEntityOfPage, None))), 4)
        for pessoa in self.json["pessoas"]:
            with self.subTest(pessoa=pessoa["id"]):
                recurso = DADOS[pessoa["id"]]
                pagina = uri_perfil(pessoa["id"])
                self.assertNotEqual(recurso, pagina)
                self.assertIn((recurso, SCHEMA.name, texto(pessoa["nome"])), self.grafo)
                self.assertEqual(set(self.grafo.objects(recurso, SCHEMA.mainEntityOfPage)), {pagina})
                self.assertIn((pagina, RDF.type, SCHEMA.ProfilePage), self.grafo)
                self.assertTrue((RAIZ / "docs" / "perfis" / f"{pessoa['id']}.html").is_file())

    def test_relacoes_rdf_contem_exatamente_as_referencias_json(self):
        externos = {CA.temAreaMaisAmpla: SKOS.broader, CA.temAutor: SCHEMA.author}
        for numero, (colecao, caminho, propriedade, _, _) in enumerate(RELACOES, start=1):
            esperado = set()
            for registro in self.json[colecao]:
                valores = buscar(registro, caminho, [])
                if isinstance(valores, str):
                    valores = [valores]
                esperado.update((DADOS[registro["id"]], DADOS[valor]) for valor in valores)
            with self.subTest(relacao=f"R{numero:02}"):
                self.assertEqual(set(self.grafo.subject_objects(propriedade)), esperado)
                if propriedade in externos:
                    predicado = externos[propriedade]
                    self.assertEqual(set(self.grafo.subject_objects(predicado)), esperado)
                    self.assertIn((propriedade, RDFS.subPropertyOf, predicado), self.ontologia)

    def test_conceitos_skos_tem_esquema_e_rotulos_portugueses(self):
        self.assertIn((ESQUEMA, RDF.type, SKOS.ConceptScheme), self.grafo)
        for area in self.json["areas"]:
            with self.subTest(area=area["id"]):
                conceito = DADOS[area["id"]]
                self.assertIn((conceito, RDF.type, SKOS.Concept), self.grafo)
                self.assertIn((conceito, SKOS.inScheme, ESQUEMA), self.grafo)
                self.assertEqual(set(self.grafo.objects(conceito, SKOS.prefLabel)), {texto(area["rotuloPreferido"])})
                self.assertEqual(set(self.grafo.objects(conceito, SKOS.definition)), {texto(area["definicao"])})
                self.assertEqual(
                    set(self.grafo.objects(conceito, SKOS.altLabel)),
                    {texto(rotulo) for rotulo in area.get("rotulosAlternativos", [])},
                )
                self.assertFalse(set(self.grafo.objects(conceito, RDFS.subClassOf)))

    def test_literais_combinam_campos_json_e_datatypes(self):
        campos = (
            ("pessoas", ("formacao",), CA.formacao, texto),
            ("pessoas", ("apresentacao",), DCTERMS.description, texto),
            ("pessoas", ("docencia", "cargo"), CA.cargo, texto),
            ("unidades", ("tipoUnidade",), CA.tipoUnidade, Literal),
            ("grupos", ("linhaAtuacao",), CA.linhaAtuacao, texto),
            ("projetos", ("titulo",), DCTERMS.title, texto),
            ("projetos", ("descricao",), DCTERMS.description, texto),
            ("publicacoes", ("titulo",), DCTERMS.title, texto),
            ("publicacoes", ("tipoProducao",), CA.tipoProducao, Literal),
            ("publicacoes", ("anoPublicacao",), CA.anoPublicacao, lambda ano: Literal(ano, datatype=XSD.integer)),
        )
        for colecao, caminho, predicado, converter in campos:
            for registro in self.json[colecao]:
                valor = buscar(registro, caminho)
                valores = valor if isinstance(valor, list) else [] if valor is None else [valor]
                with self.subTest(id=registro["id"], predicado=predicado):
                    self.assertEqual(
                        set(self.grafo.objects(DADOS[registro["id"]], predicado)),
                        {converter(item) for item in valores},
                    )

    def test_metadados_descritivos_sem_recursos_inventados(self):
        self.assertIn((DOCUMENTO_DADOS, RDF.type, SCHEMA.Dataset), self.grafo)
        self.assertIn(
            (DOCUMENTO_DADOS, CA.instituicaoReferencia, texto(self.json["instituicaoReferencia"])),
            self.grafo,
        )
        self.assertEqual(
            set(self.grafo.objects(DOCUMENTO_DADOS, CA.fonteEditorial)),
            {texto(fonte) for fonte in self.json["fontes"]},
        )
        # Licença e data só existem no grafo quando declaradas no JSON; nada além disso é inventado.
        licenca = {URIRef(self.json["licenca"])} if "licenca" in self.json else set()
        self.assertEqual(set(self.grafo.objects(DOCUMENTO_DADOS, DCTERMS.license)), licenca)
        modificado = (
            {Literal(self.json["dataAtualizacao"], datatype=XSD.date)}
            if "dataAtualizacao" in self.json
            else set()
        )
        self.assertEqual(set(self.grafo.objects(DOCUMENTO_DADOS, DCTERMS.modified)), modificado)
        # dcterms:source só pode vir de fontes do JSON que sejam URIs.
        fontes_uri = {URIRef(fonte) for fonte in self.json["fontes"]}
        self.assertLessEqual(set(self.grafo.objects(DOCUMENTO_DADOS, DCTERMS.source)), fontes_uri)

    def test_dataset_sem_identidades_externas_ou_matriculas_com_alumni_of(self):
        for predicado in (OWL.sameAs, SCHEMA.sameAs, SCHEMA.alumniOf):
            self.assertFalse(set(self.grafo.subject_objects(predicado)))
        for predicado in (SCHEMA.url, CA.linkAcademico, CA.linkBibliografico):
            self.assertFalse(set(self.grafo.subject_objects(predicado)))

    def test_regenera_sem_alterar_triplas_e_copias_publicaveis(self):
        resultado, regerado = self.gerar_em_temporario()
        self.assertTrue(isomorphic(resultado, regerado))
        self.assertTrue(isomorphic(self.grafo, regerado))
        for original in (ONTOLOGIA, INSTANCIAS):
            publicavel = RAIZ / "docs" / "ontologia" / original.name
            with self.subTest(arquivo=original.name):
                self.assertEqual(original.read_bytes(), publicavel.read_bytes())
                self.assertTrue(Graph().parse(publicavel, format="turtle"))

    def test_cli_prepara_copias_publicaveis_em_diretorio_isolado(self):
        with TemporaryDirectory() as temporario:
            pasta = Path(temporario)
            saida = pasta / "instancias.ttl"
            publicaveis = pasta / "publicaveis"
            processo = subprocess.run(
                [
                    sys.executable, "-B", str(RAIZ / "codigo-fonte" / "gerar_rdf.py"),
                    "--dados", str(FONTE), "--saida", str(saida), "--publicaveis", str(publicaveis),
                ],
                capture_output=True,
            )
            self.assertEqual(processo.returncode, 0, processo.stderr)
            self.assertEqual((publicaveis / ONTOLOGIA.name).read_bytes(), ONTOLOGIA.read_bytes())
            self.assertEqual((publicaveis / INSTANCIAS.name).read_bytes(), saida.read_bytes())
            self.assertTrue(isomorphic(Graph().parse(saida, format="turtle"), self.grafo))

    def test_gerador_reutiliza_validacao_json_e_preserva_saida_anterior(self):
        dados = deepcopy(self.json)
        dados["projetos"][0]["participantes"].append("pessoa-inexistente-teste")
        with TemporaryDirectory() as temporario:
            pasta = Path(temporario)
            fonte = pasta / "dados-teste.json"
            fonte.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
            saida = pasta / "instancias.ttl"
            saida.write_bytes(INSTANCIAS.read_bytes())
            with self.assertRaisesRegex(ValueError, "referência inexistente"):
                gerar_rdf(fonte, saida)
            self.assertEqual(saida.read_bytes(), INSTANCIAS.read_bytes())

    def test_exporta_uma_pessoa_com_dois_papeis_e_campos_opcionais(self):
        dados = deepcopy(self.json)
        pessoa = next(p for p in dados["pessoas"] if "docencia" in p)
        estudante = next(p for p in dados["pessoas"] if "discencia" in p)
        pessoa["discencia"] = deepcopy(estudante["discencia"])
        pessoa["linksAcademicos"] = [BASE + "referencias/pessoa-teste"]
        dados["publicacoes"][0]["linkBibliografico"] = BASE + "referencias/obra-teste"
        dados["fontes"].append(BASE + "referencias/fonte-teste")
        dados["licenca"] = "https://creativecommons.org/licenses/by/4.0/"
        dados["dataAtualizacao"] = "2026-01-05"
        _, grafo = self.gerar_em_temporario(dados)
        recurso = DADOS[pessoa["id"]]
        self.assertIn((recurso, RDF.type, CA.Docente), grafo)
        self.assertIn((recurso, RDF.type, CA.Discente), grafo)
        self.assertEqual(set(grafo.subjects(SCHEMA.identifier, Literal(pessoa["id"]))), {recurso})
        self.assertEqual(set(grafo.objects(recurso, SCHEMA.mainEntityOfPage)), {uri_perfil(pessoa["id"])})
        self.assertIn((recurso, CA.linkAcademico, URIRef(pessoa["linksAcademicos"][0])), grafo)
        obra = dados["publicacoes"][0]
        self.assertIn((DADOS[obra["id"]], CA.linkBibliografico, URIRef(obra["linkBibliografico"])), grafo)
        self.assertIn((DOCUMENTO_DADOS, DCTERMS.source, URIRef(dados["fontes"][-1])), grafo)
        self.assertIn((DOCUMENTO_DADOS, DCTERMS.license, URIRef(dados["licenca"])), grafo)
        self.assertIn((DOCUMENTO_DADOS, DCTERMS.modified, Literal(dados["dataAtualizacao"], datatype=XSD.date)), grafo)

    def test_autor_sem_papel_tem_identidade_sem_pagina(self):
        dados = deepcopy(self.json)
        autor = {"id": "pessoa-autora-teste", "nome": "Autoria de teste"}
        dados["pessoas"].append(autor)
        dados["publicacoes"][0]["autores"].append(autor["id"])
        _, grafo = self.gerar_em_temporario(dados)
        recurso = DADOS[autor["id"]]
        self.assertIn((recurso, RDF.type, CA.Pessoa), grafo)
        self.assertFalse(set(grafo.objects(recurso, SCHEMA.mainEntityOfPage)))
        self.assertIn((DADOS[dados["publicacoes"][0]["id"]], SCHEMA.author, recurso), grafo)

    def test_geracao_rdf_preserva_html_e_regeneracao_do_site(self):
        # Todo o conteúdo de docs/ (páginas, assets, RDF, consultas e resultados)
        # deve coincidir com uma geração limpa a partir das fontes versionadas.
        pasta_site = RAIZ / "docs"
        existentes = {
            caminho.relative_to(pasta_site): caminho.read_bytes()
            for caminho in pasta_site.rglob("*")
            if caminho.is_file()
        }
        self.gerar_em_temporario()
        with TemporaryDirectory() as temporario:
            pasta_temporaria = Path(temporario)
            gerar_site(FONTE, pasta_temporaria)
            gerados = {
                caminho.relative_to(pasta_temporaria): caminho.read_bytes()
                for caminho in pasta_temporaria.rglob("*") if caminho.is_file()
            }
        self.assertEqual(
            {caminho: corpo.replace(b"\r\n", b"\n") for caminho, corpo in existentes.items()},
            {caminho: corpo.replace(b"\r\n", b"\n") for caminho, corpo in gerados.items()},
        )
        for caminho, corpo in existentes.items():
            self.assertEqual((pasta_site / caminho).read_bytes(), corpo)

    def test_pc1_docentes_e_suas_unidades(self):
        resultado = set(self.grafo.subject_objects(CA.temVinculoDocente))
        self.assertEqual(resultado, {
            (DADOS["pessoa-ana"], DADOS["unidade-computacao"]),
            (DADOS["pessoa-rafael"], DADOS["unidade-gestao-informacao"]),
        })
        self.assertTrue(all((pessoa, RDF.type, CA.Docente) in self.grafo for pessoa, _ in resultado))

    def test_pc2_distingue_discentes_por_curso(self):
        resultado = set(self.grafo.subjects(CA.matriculadoEm, DADOS["curso-sistemas-informacao"]))
        self.assertEqual(resultado, {DADOS["pessoa-joao"]})
        self.assertIn((DADOS["pessoa-joao"], RDF.type, CA.Discente), self.grafo)

    def test_pc3_interesse_discente_nao_conta_como_atuacao_docente(self):
        area = DADOS["area-dados-abertos"]
        self.assertEqual(set(self.grafo.subjects(CA.atuaEmArea, area)), {DADOS["pessoa-ana"]})
        self.assertIn((DADOS["pessoa-joao"], CA.temInteresseEmArea, area), self.grafo)

    def test_pc4_reune_pessoas_distintas_no_mesmo_projeto(self):
        pares = set()
        for projeto in self.grafo.subjects(RDF.type, CA.ProjetoPesquisa):
            participantes = set(self.grafo.objects(projeto, CA.temParticipante))
            docentes = {p for p in participantes if (p, RDF.type, CA.Docente) in self.grafo}
            discentes = {p for p in participantes if (p, RDF.type, CA.Discente) in self.grafo}
            pares.update((projeto, d, s) for d in docentes for s in discentes if d != s)
        self.assertEqual(pares, {(DADOS["projeto-dados-abertos"], DADOS["pessoa-ana"], DADOS["pessoa-joao"])})

    def test_pc5_preserva_obras_com_e_sem_coautor_registrado(self):
        docente = DADOS["pessoa-ana"]
        obras = {
            obra: set(self.grafo.objects(obra, SCHEMA.author)) - {docente}
            for obra in self.grafo.subjects(SCHEMA.author, docente)
        }
        self.assertEqual(obras, {
            DADOS["publicacao-dados-conectados"]: {DADOS["pessoa-rafael"]},
            DADOS["publicacao-representacao-conhecimento"]: set(),
        })

    def test_pc6_reune_ambos_os_tipos_de_vinculo_direto(self):
        unidade = DADOS["unidade-computacao"]
        pessoas = set(self.grafo.subjects(CA.temVinculoDocente, unidade))
        pessoas.update(self.grafo.subjects(CA.temVinculoDiscente, unidade))
        self.assertEqual(pessoas, {DADOS["pessoa-ana"], DADOS["pessoa-joao"]})