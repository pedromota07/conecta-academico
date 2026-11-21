"""Testes das seis consultas SPARQL (.rq reais executados com RDFLib)."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, XSD
from rdflib.plugins.sparql import prepareQuery


RAIZ = Path(__file__).resolve().parents[1]
FONTE = RAIZ / "exemplos" / "perfis" / "dados.json"
INSTANCIAS = RAIZ / "ontologia" / "instancias.ttl"
CONSULTAS = RAIZ / "consultas"
RESULTADOS = CONSULTAS / "resultados"
SCRIPT = RAIZ / "codigo-fonte" / "executar_consultas.py"
BASE = "https://pedromota07.github.io/conecta-academico/"
CA = Namespace(BASE + "ontologia/conecta-academico.ttl#")
INST = Namespace(BASE + "ontologia/instancias.ttl#")

sys.path.insert(0, str(RAIZ / "codigo-fonte"))
from executar_consultas import CONSULTAS as DEFINICOES  # noqa: E402
from executar_consultas import executar, executar_demonstracao, resultados_json  # noqa: E402
from gerar_rdf import gerar_rdf  # noqa: E402


def local(termo):
    """ID local de uma URI de instância; None continua None (variável não associada)."""
    if termo is None:
        return None
    return str(termo).removeprefix(str(INST))


def colunas(linhas, *variaveis):
    return {tuple(local(linha[v]) for v in variaveis) for linha in linhas}


class BaseConsultas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grafo = Graph().parse(INSTANCIAS, format="turtle")
        cls.json = json.loads(FONTE.read_text(encoding="utf-8"))

    def consultar(self, nome, grafo=None, **parametros):
        _, linhas, _ = executar(grafo if grafo is not None else self.grafo, nome, parametros)
        return linhas

    def grafo_de(self, dados):
        """Gera o RDF de uma cópia dos dados em diretório temporário (a massa principal fica intacta)."""
        temporario = TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        pasta = Path(temporario.name)
        fonte = pasta / "dados.json"
        fonte.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        return gerar_rdf(fonte, pasta / "instancias.ttl")


class TesteArquivosConsulta(BaseConsultas):
    def test_seis_arquivos_rq_sao_consultas_sparql_validas(self):
        for numero in range(1, 7):
            arquivo = CONSULTAS / f"consulta{numero:02}.rq"
            with self.subTest(arquivo=arquivo.name):
                texto = arquivo.read_text(encoding="utf-8")
                self.assertIn("PREFIX ca:", texto)
                self.assertIn("SELECT", texto)
                prepareQuery(texto)

    def test_parametros_usam_somente_bindings_sem_values_fixos(self):
        for nome, definicao in DEFINICOES.items():
            codigo = "\n".join(
                linha for linha in (CONSULTAS / f"{nome}.rq").read_text(encoding="utf-8").splitlines()
                if not linha.lstrip().startswith("#")
            )
            with self.subTest(consulta=nome):
                for parametro in definicao["parametros"]:
                    self.assertIn(f"?{parametro}", codigo)
                    self.assertIn(f"# Parâmetro obrigatório: ?{parametro}",
                                  (CONSULTAS / f"{nome}.rq").read_text(encoding="utf-8"))
                if definicao["parametros"]:
                    self.assertNotIn("VALUES", codigo)


class TestePerguntas(BaseConsultas):
    def test_pc1_lista_somente_docentes_com_suas_unidades(self):
        linhas = self.consultar("consulta01")
        self.assertEqual(colunas(linhas, "docente", "unidade"), {
            ("pessoa-ana", "unidade-computacao"),
            ("pessoa-rafael", "unidade-gestao-informacao"),
        })
        for linha in linhas:
            self.assertIn((linha["docente"], RDF.type, CA.Docente), self.grafo)

    def test_pc2_seleciona_discentes_pela_uri_do_curso(self):
        for curso, esperado in (
            ("curso-sistemas-informacao", {"pessoa-joao"}),
            ("curso-biblioteconomia", {"pessoa-clara"}),
        ):
            with self.subTest(curso=curso):
                linhas = self.consultar("consulta02", curso=curso)
                self.assertEqual({local(linha["discente"]) for linha in linhas}, esperado)
                self.assertEqual({local(linha["curso"]) for linha in linhas}, {curso})

    def test_pc3_interesse_discente_nao_e_atuacao_docente(self):
        for area, esperado in (
            ("area-dados-abertos", {"pessoa-ana"}),
            ("area-curadoria-digital", {"pessoa-rafael"}),
            ("area-web-semantica", {"pessoa-ana"}),
            ("area-desenvolvimento-web", set()),
            ("area-gestao-informacao", set()),
        ):
            with self.subTest(area=area):
                linhas = self.consultar("consulta03", area=area)
                self.assertEqual({local(linha["docente"]) for linha in linhas}, esperado)
        self.assertIn((INST["pessoa-joao"], CA.temInteresseEmArea, INST["area-dados-abertos"]), self.grafo)

    def test_pc3_nao_expande_area_mais_ampla(self):
        # area-dados-abertos tem area-gestao-informacao como conceito mais amplo,
        # mas a consulta básica considera só a área registrada.
        self.assertEqual(self.consultar("consulta03", area="area-gestao-informacao"), [])

    def test_pc4_reune_docente_e_discente_distintos_do_mesmo_projeto(self):
        linhas = self.consultar("consulta04")
        self.assertEqual(colunas(linhas, "projeto", "docente", "discente"), {
            ("projeto-dados-abertos", "pessoa-ana", "pessoa-joao"),
        })

    def test_pc4_atravessa_projeto_e_pessoas_de_tipos_distintos(self):
        for linha in self.consultar("consulta04"):
            self.assertIn((linha["projeto"], RDF.type, CA.ProjetoPesquisa), self.grafo)
            self.assertIn((linha["projeto"], CA.temParticipante, linha["docente"]), self.grafo)
            self.assertIn((linha["projeto"], CA.temParticipante, linha["discente"]), self.grafo)
            self.assertIn((linha["docente"], RDF.type, CA.Docente), self.grafo)
            self.assertIn((linha["discente"], RDF.type, CA.Discente), self.grafo)
            self.assertNotEqual(linha["docente"], linha["discente"])

    def test_pc5_mantem_obra_sem_coautor_e_exclui_o_proprio_docente(self):
        linhas = self.consultar("consulta05", docente="pessoa-ana")
        self.assertEqual(colunas(linhas, "publicacao", "coautor"), {
            ("publicacao-dados-conectados", "pessoa-rafael"),
            ("publicacao-representacao-conhecimento", None),
        })
        self.assertNotIn(INST["pessoa-ana"], {linha["coautor"] for linha in linhas})
        for linha in linhas:
            self.assertIn((linha["publicacao"], RDF.type, CA.Publicacao), self.grafo)
            if linha["coautor"] is not None:
                self.assertIn((linha["publicacao"], CA.temAutor, linha["coautor"]), self.grafo)

    def test_pc5_varia_o_docente(self):
        linhas = self.consultar("consulta05", docente="pessoa-rafael")
        self.assertEqual(colunas(linhas, "publicacao", "coautor"), {
            ("publicacao-dados-conectados", "pessoa-ana"),
        })
        # Um discente não satisfaz o tipo ca:Docente exigido pela consulta.
        self.assertEqual(self.consultar("consulta05", docente="pessoa-joao"), [])

    def test_pc5_resultado_estruturado_omite_variavel_nao_associada(self):
        variaveis, linhas, _ = executar(self.grafo, "consulta05", {"docente": "pessoa-ana"})
        dado = resultados_json(variaveis, linhas)
        sem_coautor = [b for b in dado["results"]["bindings"] if "coautor" not in b]
        self.assertEqual(len(sem_coautor), 1)
        self.assertEqual(sem_coautor[0]["publicacao"]["value"], str(INST["publicacao-representacao-conhecimento"]))
        self.assertNotIn("nomeCoautor", sem_coautor[0])
        self.assertEqual(sem_coautor[0]["ano"], {"type": "literal", "value": "2022", "datatype": str(XSD.integer)})
        self.assertNotIn("None", json.dumps(dado))

    def test_pc6_reune_vinculos_diretos_de_docentes_e_discentes(self):
        for unidade, esperado in (
            ("unidade-computacao", {("pessoa-ana", True, False), ("pessoa-joao", False, True)}),
            ("unidade-gestao-informacao", {("pessoa-rafael", True, False), ("pessoa-clara", False, True)}),
        ):
            with self.subTest(unidade=unidade):
                linhas = self.consultar("consulta06", unidade=unidade)
                self.assertEqual(
                    {(local(l["pessoa"]), l["vinculoDocente"].toPython(), l["vinculoDiscente"].toPython()) for l in linhas},
                    esperado,
                )

    def test_pc6_instituto_nao_herda_pessoas_dos_departamentos(self):
        self.assertIn((INST["unidade-computacao"], CA.temUnidadeSuperior, INST["unidade-ciencias-exatas"]), self.grafo)
        self.assertEqual(self.consultar("consulta06", unidade="unidade-ciencias-exatas"), [])


class TesteParametros(BaseConsultas):
    def test_aceita_id_local_prefixo_inst_e_uri_completa(self):
        for valor in ("curso-biblioteconomia", "inst:curso-biblioteconomia", str(INST["curso-biblioteconomia"])):
            with self.subTest(valor=valor):
                linhas = self.consultar("consulta02", curso=valor)
                self.assertEqual({local(l["discente"]) for l in linhas}, {"pessoa-clara"})

    def test_entrada_bem_formada_sem_correspondencia_retorna_vazio(self):
        self.assertEqual(self.consultar("consulta02", curso="curso-inexistente"), [])
        self.assertEqual(self.consultar("consulta06", unidade="https://example.org/unidade"), [])

    def test_rejeita_parametro_malformado_com_mensagem_util(self):
        for valor in ("<x> } UNION { ?s ?p ?o", "Curso Inválido", "", "ftp://example.org/x", "inst:", '"literal"'):
            with self.subTest(valor=valor):
                with self.assertRaisesRegex(ValueError, "Parâmetro 'curso' inválido"):
                    self.consultar("consulta02", curso=valor)

    def test_rejeita_parametro_desconhecido_ou_ausente(self):
        with self.assertRaisesRegex(ValueError, "parâmetro desconhecido"):
            self.consultar("consulta01", curso="curso-biblioteconomia")
        with self.assertRaisesRegex(ValueError, "informe o parâmetro area"):
            self.consultar("consulta03")
        with self.assertRaisesRegex(ValueError, "Consulta desconhecida"):
            self.consultar("consulta07")

    def test_cli_executa_consulta_individual_e_rejeita_parametro_invalido(self):
        ok = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "consulta03", "--param", "area=area-curadoria-digital"],
            capture_output=True, encoding="utf-8",
        )
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn("inst:pessoa-rafael", ok.stdout)
        falha = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "consulta03", "--param", "area=<x>"],
            capture_output=True, encoding="utf-8",
        )
        self.assertEqual(falha.returncode, 1)
        self.assertIn("Parâmetro 'area' inválido", falha.stderr)


class TesteIdentidadePorURI(BaseConsultas):
    def test_homonimos_e_mudanca_de_nome_nao_alteram_a_selecao(self):
        dados = deepcopy(self.json)
        ana = next(p for p in dados["pessoas"] if p["id"] == "pessoa-ana")
        ana["nome"] = "Ana Souza"
        dados["pessoas"].append({
            "id": "pessoa-ana-homonima",
            "nome": "Ana Souza",
            "discencia": {"unidadesDiscentes": ["unidade-gestao-informacao"], "cursos": ["curso-biblioteconomia"]},
        })
        dados["cursos"].append({
            "id": "curso-homonimo",
            "nome": "Bacharelado em Biblioteconomia",
            "unidadeResponsavel": "unidade-computacao",
        })
        grafo = self.grafo_de(dados)
        self.assertEqual(colunas(self.consultar("consulta01", grafo), "docente"), {("pessoa-ana",), ("pessoa-rafael",)})
        self.assertEqual(
            {local(l["discente"]) for l in self.consultar("consulta02", grafo, curso="curso-biblioteconomia")},
            {"pessoa-clara", "pessoa-ana-homonima"},
        )
        self.assertEqual(self.consultar("consulta02", grafo, curso="curso-homonimo"), [])
        self.assertEqual(
            {local(l["publicacao"]) for l in self.consultar("consulta05", grafo, docente="pessoa-ana")},
            {"publicacao-dados-conectados", "publicacao-representacao-conhecimento"},
        )
        self.assertEqual(self.consultar("consulta05", grafo, docente="pessoa-ana-homonima"), [])

    def test_pc4_projetos_homonimos_papel_duplo_e_grupo_nao_formam_pares(self):
        dados = deepcopy(self.json)
        dados["pessoas"].append({
            "id": "pessoa-dupla",
            "nome": "Pessoa com dois papéis",
            "docencia": {"unidadesDocentes": ["unidade-computacao"]},
            "discencia": {"unidadesDiscentes": ["unidade-computacao"], "cursos": ["curso-sistemas-informacao"]},
        })
        titulo = next(p["titulo"] for p in dados["projetos"] if p["id"] == "projeto-dados-abertos")
        dados["projetos"].extend([
            {"id": "projeto-homonimo-docente", "titulo": titulo, "descricao": "Teste.", "participantes": ["pessoa-rafael"]},
            {"id": "projeto-homonimo-discente", "titulo": titulo, "descricao": "Teste.", "participantes": ["pessoa-clara"]},
            {"id": "projeto-papel-duplo", "titulo": "Projeto individual", "descricao": "Teste.",
             "participantes": ["pessoa-dupla"]},
            {"id": "projeto-duplo-e-discente", "titulo": "Projeto misto", "descricao": "Teste.",
             "participantes": ["pessoa-dupla", "pessoa-clara"]},
        ])
        grupo = next(g for g in dados["grupos"] if g["id"] == "grupo-memoria-digital")
        self.assertIn("projeto-curadoria-digital", grupo["projetos"])
        grafo = self.grafo_de(dados)
        self.assertEqual(colunas(self.consultar("consulta04", grafo), "projeto", "docente", "discente"), {
            ("projeto-dados-abertos", "pessoa-ana", "pessoa-joao"),
            ("projeto-duplo-e-discente", "pessoa-dupla", "pessoa-clara"),
        })

    def test_pc5_preserva_autor_sem_perfil_registrado(self):
        dados = deepcopy(self.json)
        dados["pessoas"].append({"id": "pessoa-autora-externa", "nome": "Autora sem perfil"})
        obra = next(p for p in dados["publicacoes"] if p["id"] == "publicacao-dados-conectados")
        obra["autores"].append("pessoa-autora-externa")
        grafo = self.grafo_de(dados)
        linhas = self.consultar("consulta05", grafo, docente="pessoa-ana")
        self.assertEqual(colunas(linhas, "publicacao", "coautor"), {
            ("publicacao-dados-conectados", "pessoa-rafael"),
            ("publicacao-dados-conectados", "pessoa-autora-externa"),
            ("publicacao-representacao-conhecimento", None),
        })
        externa = next(l for l in linhas if local(l["coautor"]) == "pessoa-autora-externa")
        self.assertEqual(str(externa["nomeCoautor"]), "Autora sem perfil")

    def test_pc6_deduplica_pessoa_com_dois_vinculos_na_unidade(self):
        dados = deepcopy(self.json)
        dados["pessoas"].append({
            "id": "pessoa-dupla",
            "nome": "Pessoa com dois papéis",
            "docencia": {"unidadesDocentes": ["unidade-computacao"]},
            "discencia": {"unidadesDiscentes": ["unidade-computacao"], "cursos": ["curso-sistemas-informacao"]},
        })
        grafo = self.grafo_de(dados)
        linhas = self.consultar("consulta06", grafo, unidade="unidade-computacao")
        duplas = [l for l in linhas if local(l["pessoa"]) == "pessoa-dupla"]
        self.assertEqual(len(duplas), 1)
        self.assertTrue(duplas[0]["vinculoDocente"].toPython())
        self.assertTrue(duplas[0]["vinculoDiscente"].toPython())
        self.assertEqual(len(linhas), len({l["pessoa"] for l in linhas}))


class TesteEvidencias(BaseConsultas):
    def test_resultados_versionados_correspondem_a_uma_nova_execucao(self):
        with TemporaryDirectory() as temporario:
            pasta = Path(temporario)
            executar_demonstracao(INSTANCIAS, pasta)
            gerados = {p.name: p.read_bytes() for p in pasta.iterdir()}
        versionados = {p.name: p.read_bytes().replace(b"\r\n", b"\n") for p in RESULTADOS.iterdir()}
        self.assertEqual(versionados, gerados)

    def test_manifesto_identifica_consultas_parametros_e_seis_perguntas(self):
        manifesto = json.loads((RESULTADOS / "execucoes.json").read_text(encoding="utf-8"))
        consultas = {e["consulta"] for e in manifesto["execucoes"] if not e.get("complementar")}
        self.assertEqual(consultas, {f"consulta{n:02}" for n in range(1, 7)})
        for execucao in manifesto["execucoes"]:
            with self.subTest(resultado=execucao["resultado"]):
                self.assertTrue((RAIZ / execucao["arquivo"]).is_file())
                self.assertEqual(set(execucao["parametros"]), set(DEFINICOES[execucao["consulta"]]["parametros"]))
                for valor in execucao["parametros"].values():
                    self.assertTrue(valor.startswith(str(INST)))
                dado = json.loads((RESULTADOS / execucao["resultado"]).read_text(encoding="utf-8"))
                self.assertEqual(len(dado["results"]["bindings"]), execucao["linhas"])

    def test_resultados_preservam_tipos_de_termos_rdf(self):
        dado = json.loads((RESULTADOS / "consulta06--unidade-computacao.json").read_text(encoding="utf-8"))
        linha = dado["results"]["bindings"][0]
        self.assertEqual(linha["pessoa"]["type"], "uri")
        self.assertEqual(linha["nomePessoa"].get("xml:lang"), "pt-BR")
        self.assertEqual(linha["vinculoDocente"]["datatype"], str(XSD.boolean))
        for arquivo in RESULTADOS.glob("*.json"):
            self.assertNotIn('"None"', arquivo.read_text(encoding="utf-8"))

    def test_copias_publicaveis_das_consultas_coincidem_com_as_fontes(self):
        for arquivo in list(CONSULTAS.glob("*.rq")) + list(RESULTADOS.glob("consulta*.json")):
            copia = RAIZ / "docs" / arquivo.relative_to(RAIZ)
            with self.subTest(arquivo=arquivo.name):
                self.assertEqual(copia.read_bytes(), arquivo.read_bytes())


if __name__ == "__main__":
    unittest.main()
