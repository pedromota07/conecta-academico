"""Testes das ligações com recursos externos (LOD). Não acessam a Internet."""

from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

from rdflib import Graph, Namespace, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import OWL, RDF, SKOS


RAIZ = Path(__file__).resolve().parents[1]
FONTE = RAIZ / "exemplos" / "perfis" / "dados.json"
INSTANCIAS = RAIZ / "ontologia" / "instancias.ttl"
BASE = "https://pedromota07.github.io/conecta-academico/"
CA = Namespace(BASE + "ontologia/conecta-academico.ttl#")
INST = Namespace(BASE + "ontologia/instancias.ttl#")
MAPEAMENTOS = (SKOS.exactMatch, SKOS.closeMatch, SKOS.broadMatch, SKOS.narrowMatch, SKOS.relatedMatch)
WIKIDATA = {
    "area-web-semantica": URIRef("http://www.wikidata.org/entity/Q54837"),
    "area-dados-abertos": URIRef("http://www.wikidata.org/entity/Q309901"),
    "area-curadoria-digital": URIRef("http://www.wikidata.org/entity/Q5276060"),
}

sys.path.insert(0, str(RAIZ / "codigo-fonte"))
from executar_consultas import executar  # noqa: E402
from gerar_rdf import gerar_rdf  # noqa: E402
from gerar_site import gerar_site  # noqa: E402


def ligacoes(grafo):
    return {
        (s, p, o) for p in MAPEAMENTOS for s, o in grafo.subject_objects(p)
        if isinstance(o, URIRef) and not str(o).startswith(BASE)
    }


class TesteLigacoesExternas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.json = json.loads(FONTE.read_text(encoding="utf-8"))
        cls.grafo = Graph().parse(INSTANCIAS, format="turtle")

    def gerar(self, dados, saida_existente=None):
        temporario = TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        pasta = Path(temporario.name)
        fonte = pasta / "dados.json"
        fonte.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        saida = pasta / "instancias.ttl"
        if saida_existente is not None:
            saida.write_bytes(saida_existente)
        return gerar_rdf(fonte, saida), saida

    def test_tres_recursos_externos_distintos_com_mapeamento_skos(self):
        encontradas = ligacoes(self.grafo)
        self.assertGreaterEqual(len({o for _, _, o in encontradas}), 3)
        for area, alvo in WIKIDATA.items():
            with self.subTest(area=area):
                self.assertIn((INST[area], SKOS.closeMatch, alvo), self.grafo)
                self.assertIn((INST[area], RDF.type, CA.AreaConhecimento), self.grafo)
        for sujeito, _, _ in encontradas:
            self.assertIn((sujeito, RDF.type, SKOS.Concept), self.grafo)

    def test_rdf_contem_exatamente_os_mapeamentos_do_json(self):
        esperado = {
            (INST[area["id"]], SKOS[item["predicado"].removeprefix("skos:")], URIRef(item["uri"]))
            for area in self.json["areas"] for item in area.get("correspondenciasExternas", [])
        }
        self.assertEqual(ligacoes(self.grafo), esperado)

    def test_nao_usa_identidade_nem_equivalencia_de_classes(self):
        for predicado in (OWL.sameAs, OWL.equivalentClass, OWL.equivalentProperty):
            self.assertFalse(set(self.grafo.subject_objects(predicado)))
        pessoas = set(self.grafo.subjects(RDF.type, CA.Pessoa))
        self.assertFalse({s for s, _, _ in ligacoes(self.grafo)} & pessoas)

    def test_uri_canonica_da_fonte_e_preservada_sem_trocar_esquema(self):
        for alvo in WIKIDATA.values():
            self.assertTrue(str(alvo).startswith("http://www.wikidata.org/entity/Q"))
        for area in self.json["areas"]:
            for item in area.get("correspondenciasExternas", []):
                self.assertNotEqual(item["uri"], item["fonte"])
                self.assertTrue(item["fonte"].startswith("https://www.wikidata.org/wiki/Q"))

    def test_mapeamentos_sobrevivem_a_regeneracao(self):
        regerado, _ = self.gerar(self.json)
        self.assertEqual(ligacoes(regerado), ligacoes(self.grafo))
        self.assertTrue(isomorphic(regerado, self.grafo))

    def test_rdf_publicado_em_docs_corresponde_ao_canonico_e_ao_json(self):
        publicado = RAIZ / "docs" / "ontologia" / "instancias.ttl"
        self.assertEqual(publicado.read_bytes(), INSTANCIAS.read_bytes())
        regerado, _ = self.gerar(self.json)
        self.assertTrue(isomorphic(Graph().parse(publicado, format="turtle"), regerado))

    def test_consulta_complementar_demonstra_as_ligacoes(self):
        _, linhas, _ = executar(self.grafo, "ligacoes-externas", {})
        self.assertEqual(
            {(str(l["area"]).removeprefix(str(INST)), l["relacao"], l["recursoExterno"]) for l in linhas},
            {(area, SKOS.closeMatch, alvo) for area, alvo in WIKIDATA.items()},
        )

    def test_outro_predicado_de_mapeamento_permitido_e_emitido(self):
        dados = deepcopy(self.json)
        area = next(a for a in dados["areas"] if a["id"] == "area-desenvolvimento-web")
        area["correspondenciasExternas"] = [{
            "uri": "https://example.org/conceito/web",
            "predicado": "skos:relatedMatch",
            "rotulo": "Conceito de teste",
            "fonte": "https://example.org/conceito/web.html",
            "dataVerificacao": "2026-11-21",
            "justificativa": "Associação temática de teste.",
        }]
        grafo, _ = self.gerar(dados)
        self.assertIn(
            (INST["area-desenvolvimento-web"], SKOS.relatedMatch, URIRef("https://example.org/conceito/web")), grafo
        )

    def test_rejeita_mapeamentos_invalidos_sem_destruir_saida_anterior(self):
        anterior = INSTANCIAS.read_bytes()
        casos = {
            "predicado owl:sameAs": ("predicado", "owl:sameAs"),
            "predicado desconhecido": ("predicado", "skos:related"),
            "uri relativa": ("uri", "Q54837"),
            "uri sem http": ("uri", "ftp://www.wikidata.org/entity/Q54837"),
            "uri com espaço": ("uri", "http://www.wikidata.org/entity/Q 1"),
            "uri local": ("uri", BASE + "ontologia/instancias.ttl#area-web-semantica"),
            "fonte sem https": ("fonte", "http://www.wikidata.org/wiki/Q54837"),
            "data inválida": ("dataVerificacao", "21/11/2026"),
            "justificativa vazia": ("justificativa", "  "),
            "campo desconhecido": ("comentario", "texto"),
        }
        for descricao, (campo, valor) in casos.items():
            with self.subTest(caso=descricao):
                dados = deepcopy(self.json)
                item = next(a for a in dados["areas"] if a["id"] == "area-web-semantica")["correspondenciasExternas"][0]
                item[campo] = valor
                with self.assertRaises(ValueError):
                    self.gerar(dados, anterior)
        for descricao, alterar in (
            ("campo obrigatório ausente", lambda item, dados: item.pop("rotulo")),
            ("uri repetida na área", lambda item, dados: next(
                a for a in dados["areas"] if a["id"] == "area-web-semantica"
            )["correspondenciasExternas"].append(deepcopy(item))),
            ("lista em vez de objeto", lambda item, dados: next(
                a for a in dados["areas"] if a["id"] == "area-web-semantica"
            ).__setitem__("correspondenciasExternas", [item["uri"]])),
        ):
            with self.subTest(caso=descricao):
                dados = deepcopy(self.json)
                item = next(a for a in dados["areas"] if a["id"] == "area-web-semantica")["correspondenciasExternas"][0]
                alterar(item, dados)
                with self.assertRaises(ValueError):
                    self.gerar(dados, anterior)

    def test_rejeita_mesma_correspondencia_exata_em_duas_areas(self):
        dados = deepcopy(self.json)
        for area_id in ("area-web-semantica", "area-desenvolvimento-web"):
            area = next(a for a in dados["areas"] if a["id"] == area_id)
            area["correspondenciasExternas"] = [{
                "uri": "http://www.wikidata.org/entity/Q54837",
                "predicado": "skos:exactMatch",
                "rotulo": "Semantic Web",
                "fonte": "https://www.wikidata.org/wiki/Q54837",
                "dataVerificacao": "2026-11-21",
                "justificativa": "Teste.",
            }]
        with self.assertRaisesRegex(ValueError, "correspondência exata"):
            self.gerar(dados)

    def test_saida_preservada_quando_dados_lod_sao_invalidos(self):
        dados = deepcopy(self.json)
        dados["areas"][1]["correspondenciasExternas"][0]["predicado"] = "owl:sameAs"
        anterior = INSTANCIAS.read_bytes()
        temporario = TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        pasta = Path(temporario.name)
        fonte = pasta / "dados.json"
        fonte.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        saida = pasta / "instancias.ttl"
        saida.write_bytes(anterior)
        with self.assertRaises(ValueError):
            gerar_rdf(fonte, saida)
        self.assertEqual(saida.read_bytes(), anterior)

    def test_pagina_de_dados_apresenta_ligacoes_e_paginas_da_fonte(self):
        with TemporaryDirectory() as temporario:
            destino = Path(temporario) / "site"
            gerar_site(FONTE, destino)
            html = (destino / "dados.html").read_text(encoding="utf-8")
        for area, alvo in WIKIDATA.items():
            with self.subTest(area=area):
                self.assertIn(f"<code>{alvo}</code>", html)
                self.assertIn(f'href="https://www.wikidata.org/wiki/{str(alvo).rsplit("/", 1)[1]}"', html)
                self.assertIn(f"inst:{area}", html)


if __name__ == "__main__":
    unittest.main()
