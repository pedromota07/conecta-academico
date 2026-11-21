import json
import sys
import unittest
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit


RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "exemplos" / "perfis" / "dados.json"
sys.path.insert(0, str(RAIZ / "codigo-fonte"))
from gerar_site import gerar_site


def normalizar(texto):
    return " ".join(texto.split())


class Pagina(HTMLParser):
    def __init__(self, caminho):
        super().__init__()
        self.fragmentos = []
        self.destinos = []
        self.identificadores = set()
        self.elementos = set()
        self.titulos = set()
        self.titulo_atual = []
        self.em_titulo = False
        self.feed(caminho.read_text(encoding="utf-8"))
        self.close()

    @property
    def texto(self):
        return normalizar(" ".join(self.fragmentos))

    def handle_starttag(self, tag, attrs):
        self.elementos.add(tag)
        atributos = dict(attrs)
        self.destinos.extend(
            atributos[nome] for nome in ("href", "src") if atributos.get(nome)
        )
        if atributos.get("id"):
            self.identificadores.add(atributos["id"])
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.em_titulo = True

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.titulos.add(normalizar(" ".join(self.titulo_atual)))
            self.titulo_atual.clear()
            self.em_titulo = False

    def handle_data(self, data):
        self.fragmentos.append(data)
        if self.em_titulo:
            self.titulo_atual.append(data)


def arquivos(diretorio):
    return {
        caminho.relative_to(diretorio).as_posix(): caminho.read_bytes()
        for caminho in diretorio.rglob("*")
        if caminho.is_file()
    }


class TesteGerador(unittest.TestCase):
    def setUp(self):
        temporario = TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        self.pasta = Path(temporario.name)
        self.destino = self.pasta / "site"
        self.dados = json.loads(DADOS.read_text(encoding="utf-8"))
        self.docentes = [pessoa for pessoa in self.dados["pessoas"] if "docencia" in pessoa]
        self.discentes = [pessoa for pessoa in self.dados["pessoas"] if "discencia" in pessoa]
        self.perfis = {
            pessoa["id"]: pessoa for pessoa in self.docentes + self.discentes
        }

    def gerar(self, dados=None, destino=None):
        entrada = DADOS
        if dados is not None:
            entrada = self.pasta / "dados-teste.json"
            entrada.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        gerar_site(entrada, destino or self.destino)

    def quinto_perfil(self):
        return {
            "id": "pessoa-quinto-teste",
            "nome": "Quinto perfil demonstrativo",
            "docencia": deepcopy(self.docentes[0]["docencia"]),
            "discencia": deepcopy(self.discentes[0]["discencia"]),
        }

    def test_gera_quatro_paginas_individuais_e_cartoes_no_diretorio(self):
        self.gerar()
        inicio = Pagina(self.destino / "index.html")
        self.assertEqual(len(self.docentes), 2)
        self.assertEqual(len(self.discentes), 2)
        self.assertEqual(len(self.perfis), 4)
        esperados = {f"perfis/{identificador}.html" for identificador in self.perfis}
        navegaveis = {caminho for caminho in inicio.destinos if caminho.startswith("perfis/")}
        geradas = {
            caminho.relative_to(self.destino).as_posix()
            for caminho in self.destino.glob("perfis/*.html")
        }
        self.assertEqual(navegaveis, esperados)
        self.assertEqual(geradas, esperados)
        self.assertTrue((self.destino / "assets" / "estilos.css").is_file())
        for identificador, pessoa in self.perfis.items():
            with self.subTest(pessoa=identificador):
                self.assertIn(normalizar(pessoa["nome"]), inicio.texto)
                perfil = Pagina(self.destino / "perfis" / f"{identificador}.html")
                self.assertIn(normalizar(pessoa["nome"]), perfil.titulos)

    def test_links_e_ancoras_internos_funcionam_em_subdiretorio(self):
        self.gerar()
        for caminho in self.destino.rglob("*.html"):
            for destino in Pagina(caminho).destinos:
                with self.subTest(pagina=caminho.name, destino=destino):
                    uri = urlsplit(destino)
                    if uri.scheme:
                        self.assertEqual(uri.scheme, "https")
                        self.assertNotIn(uri.hostname, ("localhost", "127.0.0.1"))
                        continue
                    relativo = unquote(uri.path)
                    self.assertFalse(uri.netloc or relativo.startswith(("/", "\\")))
                    alvo = (caminho.parent / relativo).resolve() if relativo else caminho
                    self.assertTrue(alvo.is_relative_to(self.destino.resolve()))
                    self.assertTrue(alvo.is_file(), f"Destino não gerado: {alvo}")
                    if uri.fragment and alvo.suffix == ".html":
                        self.assertIn(unquote(uri.fragment), Pagina(alvo).identificadores)

    def test_perfis_renderizam_atributos_e_relacoes_da_fonte(self):
        self.gerar()
        unidades = {item["id"]: item["nome"] for item in self.dados["unidades"]}
        cursos = {item["id"]: item["nome"] for item in self.dados["cursos"]}
        areas = {item["id"]: item["rotuloPreferido"] for item in self.dados["areas"]}
        disciplinas = {item["id"]: item["nome"] for item in self.dados["disciplinas"]}
        for identificador, pessoa in self.perfis.items():
            with self.subTest(pessoa=identificador):
                perfil = Pagina(self.destino / "perfis" / f"{identificador}.html")
                valores = list(pessoa.get("formacao", []))
                if pessoa.get("apresentacao"):
                    valores.append(pessoa["apresentacao"])
                if "docencia" in pessoa:
                    papel = pessoa["docencia"]
                    valores.extend(unidades[valor] for valor in papel["unidadesDocentes"])
                    valores.extend(areas[valor] for valor in papel.get("areasAtuacao", []))
                    valores.extend(disciplinas[valor] for valor in papel.get("disciplinasMinistradas", []))
                    if papel.get("cargo"):
                        valores.append(papel["cargo"])
                    self.assertNotIn("Áreas de interesse", perfil.titulos)
                if "discencia" in pessoa:
                    papel = pessoa["discencia"]
                    valores.extend(unidades[valor] for valor in papel["unidadesDiscentes"])
                    valores.extend(cursos[valor] for valor in papel["cursos"])
                    valores.extend(areas[valor] for valor in papel.get("areasInteresse", []))
                    valores.extend(disciplinas[valor] for valor in papel.get("disciplinasCursadas", []))
                    self.assertNotIn("Áreas de atuação", perfil.titulos)
                for colecao, referencia, rotulo in (
                    ("projetos", "participantes", "titulo"),
                    ("grupos", "membros", "nome"),
                    ("publicacoes", "autores", "titulo"),
                ):
                    valores.extend(
                        item[rotulo] for item in self.dados[colecao]
                        if identificador in item.get(referencia, [])
                    )
                for valor in valores:
                    self.assertIn(normalizar(valor), perfil.texto)

    def test_quinto_perfil_limita_mudanca_a_fonte_e_suporta_dois_papeis(self):
        self.gerar()
        pessoa = self.quinto_perfil()
        self.dados["pessoas"].append(pessoa)
        self.gerar(self.dados)
        inicio = Pagina(self.destino / "index.html")
        url = f"perfis/{pessoa['id']}.html"
        self.assertIn(url, inicio.destinos)
        self.assertIn(pessoa["nome"], inicio.texto)
        self.assertEqual(len(list(self.destino.glob("perfis/*.html"))), 5)
        perfil = Pagina(self.destino / url)
        self.assertIn(pessoa["nome"], perfil.titulos)
        self.assertIn("Áreas de atuação", perfil.titulos)
        self.assertIn("Áreas de interesse", perfil.titulos)
        self.assertNotIn("Apresentação", perfil.titulos)
        self.assertNotIn("Links acadêmicos", perfil.titulos)
        self.assertNotIn(pessoa["id"], DADOS.read_text(encoding="utf-8"))

    def test_remove_perfil_obsoleto_e_preserva_html_alheio_no_destino(self):
        pessoa = self.quinto_perfil()
        self.dados["pessoas"].append(pessoa)
        self.gerar(self.dados)
        url = f"perfis/{pessoa['id']}.html"
        perfil_removido = self.destino / url
        self.assertTrue(perfil_removido.is_file())
        manual = self.destino / "perfis" / "informacoes-manuais.html"
        conteudo = b"<!doctype html><title>Arquivo mantido separadamente</title>"
        manual.write_bytes(conteudo)
        self.gerar()
        self.assertFalse(perfil_removido.exists())
        self.assertNotIn(url, Pagina(self.destino / "index.html").destinos)
        self.assertEqual(manual.read_bytes(), conteudo)

    def test_gera_resultados_deterministicos(self):
        self.gerar()
        segunda_saida = self.pasta / "segundo-site"
        self.gerar(destino=segunda_saida)
        self.assertEqual(arquivos(self.destino), arquivos(segunda_saida))

    def test_escapa_conteudo_textual_em_vez_de_criar_elementos(self):
        pessoa = self.docentes[0]
        descricao = 'Exemplo <marcador-de-teste>"citação"</marcador-de-teste> & Unicode'
        pessoa["apresentacao"] = descricao
        self.gerar(self.dados)
        perfil = Pagina(self.destino / "perfis" / f"{pessoa['id']}.html")
        self.assertIn(descricao, perfil.texto)
        self.assertNotIn("marcador-de-teste", perfil.elementos)

    def test_rejeita_json_sintaticamente_invalido(self):
        entrada = self.pasta / "invalido.json"
        entrada.write_text("{", encoding="utf-8")
        with self.assertRaises(ValueError):
            gerar_site(entrada, self.destino)

    def test_rejeita_referencia_inexistente_antes_de_alterar_site(self):
        self.gerar()
        antes = arquivos(self.destino)
        self.docentes[0]["docencia"]["unidadesDocentes"] = ["unidade-inexistente-teste"]
        with self.assertRaises(ValueError):
            self.gerar(self.dados)
        self.assertEqual(arquivos(self.destino), antes)

    def test_rejeita_identificador_repetido_entre_tipos(self):
        self.dados["unidades"][0]["id"] = self.dados["pessoas"][0]["id"]
        with self.assertRaises(ValueError):
            self.gerar(self.dados)

    def test_rejeita_identificador_fora_do_formato(self):
        self.dados["disciplinas"].append({"id": "Identificador inválido", "nome": "Disciplina de teste"})
        with self.assertRaises(ValueError):
            self.gerar(self.dados)

    def test_rejeita_campo_obrigatorio_sem_texto(self):
        self.dados["unidades"][0]["nome"] = "   "
        with self.assertRaises(ValueError):
            self.gerar(self.dados)

    def test_rejeita_referencia_a_recurso_de_tipo_diferente(self):
        self.discentes[0]["discencia"]["cursos"] = [self.dados["disciplinas"][0]["id"]]
        with self.assertRaises(ValueError):
            self.gerar(self.dados)

    def test_rejeita_cardinalidade_obrigatoria_violada(self):
        self.docentes[0]["docencia"]["unidadesDocentes"] = []
        with self.assertRaises(ValueError):
            self.gerar(self.dados)

    def test_rejeita_lista_de_referencias_repetidas(self):
        referencias = self.discentes[0]["discencia"]["cursos"]
        referencias.append(referencias[0])
        with self.assertRaises(ValueError):
            self.gerar(self.dados)

    def test_rejeita_ciclos_nas_duas_hierarquias(self):
        for colecao, campo, lista in (
            ("unidades", "unidadeSuperior", False),
            ("areas", "areasMaisAmplas", True),
        ):
            with self.subTest(colecao=colecao):
                dados = deepcopy(self.dados)
                primeiro, segundo = dados[colecao][:2]
                primeiro[campo] = [segundo["id"]] if lista else segundo["id"]
                segundo[campo] = [primeiro["id"]] if lista else primeiro["id"]
                with self.assertRaises(ValueError):
                    self.gerar(dados)

    def test_rejeita_link_de_perfil_sem_https(self):
        self.docentes[0]["linksAcademicos"] = ["http://example.org/perfil"]
        with self.assertRaises(ValueError):
            self.gerar(self.dados)

    def test_preserva_url_https_com_caracteres_especiais_em_href(self):
        pessoa = self.docentes[0]
        url = "https://example.org/perfil?grupo=dados&copy;"
        pessoa["linksAcademicos"] = [url]
        self.gerar(self.dados)
        perfil = Pagina(self.destino / "perfis" / f"{pessoa['id']}.html")
        self.assertIn(url, perfil.destinos)

    def test_rejeita_conjunto_com_menos_de_dois_discentes(self):
        del self.discentes[0]["discencia"]
        with self.assertRaises(ValueError):
            self.gerar(self.dados)

    def test_pagina_de_dados_apresenta_artefatos_reais_das_consultas(self):
        self.gerar()
        dados = Pagina(self.destino / "dados.html")
        manifesto = json.loads((RAIZ / "consultas" / "resultados" / "execucoes.json").read_text(encoding="utf-8"))
        for alvo in ("ontologia/conecta-academico.ttl", "ontologia/instancias.ttl"):
            self.assertIn(alvo, dados.destinos)
            self.assertEqual((self.destino / alvo).read_bytes(), (RAIZ / alvo).read_bytes())
        for execucao in manifesto["execucoes"]:
            with self.subTest(resultado=execucao["resultado"]):
                self.assertIn(f"consultas/resultados/{execucao['resultado']}", dados.destinos)
                self.assertIn(f"consultas/{execucao['consulta']}.rq", dados.destinos)
                self.assertIn(normalizar(execucao["pergunta"]), dados.texto)
        self.assertIn("Não informado", dados.texto)
        self.assertIn("Não há endpoint SPARQL público", dados.texto)
        for pagina in ("index.html", "perfis/pessoa-ana.html"):
            self.assertTrue(any(d.endswith("dados.html") for d in Pagina(self.destino / pagina).destinos))

    def test_busca_e_filtro_sao_progressivos_e_perfis_ficam_no_html(self):
        self.gerar()
        html = (self.destino / "index.html").read_text(encoding="utf-8")
        self.assertRegex(html, r"<form[^>]*data-filtro[^>]*hidden")
        self.assertRegex(html, r'id="sem-resultados" hidden')
        self.assertIn('src="assets/diretorio.js"', html)
        self.assertTrue((self.destino / "assets" / "diretorio.js").is_file())
        cursos = {curso["id"]: curso["nome"] for curso in self.dados["cursos"]}
        for pessoa in self.discentes:
            with self.subTest(pessoa=pessoa["id"]):
                self.assertIn(f'href="perfis/{pessoa["id"]}.html"', html)
                for curso in pessoa["discencia"]["cursos"]:
                    self.assertIn(cursos[curso].lower(), html)

    def test_perfil_aponta_para_o_recurso_rdf_correspondente(self):
        self.gerar()
        instancias = (self.destino / "ontologia" / "instancias.ttl").read_text(encoding="utf-8")
        for identificador in self.perfis:
            with self.subTest(pessoa=identificador):
                perfil = Pagina(self.destino / "perfis" / f"{identificador}.html")
                self.assertIn(f"../ontologia/instancias.ttl#{identificador}", perfil.destinos)
                self.assertIn(f"inst:{identificador}", instancias)

    def test_saida_funciona_em_subdiretorio_aninhado(self):
        destino = self.pasta / "publicacao" / "conecta-academico"
        self.gerar(destino=destino)
        for caminho in destino.rglob("*.html"):
            for alvo in Pagina(caminho).destinos:
                with self.subTest(pagina=caminho.name, destino=alvo):
                    self.assertFalse(alvo.startswith("/"))

    def test_pc1_e_pc6_discriminam_papel_e_unidade(self):
        vinculos_docentes = [set(p["docencia"]["unidadesDocentes"]) for p in self.docentes]
        vinculos_discentes = [set(p["discencia"]["unidadesDiscentes"]) for p in self.discentes]
        self.assertTrue(all(vinculos_docentes))
        self.assertGreater(len(set.union(*vinculos_docentes)), 1)
        compartilhadas = set.union(*vinculos_docentes) & set.union(*vinculos_discentes)
        self.assertTrue(any(
            unidade not in vinculos
            for unidade in compartilhadas
            for vinculos in vinculos_docentes + vinculos_discentes
        ))

    def test_pc2_e_pc3_separam_cursos_areas_e_interesses(self):
        cursos = [set(p["discencia"]["cursos"]) for p in self.discentes]
        areas = [set(p["docencia"].get("areasAtuacao", [])) for p in self.docentes]
        self.assertTrue(set.union(*cursos) - set.intersection(*cursos))
        self.assertTrue(all(areas))
        self.assertTrue(set.union(*areas) - set.intersection(*areas))
        interesses = {area for p in self.discentes for area in p["discencia"].get("areasInteresse", [])}
        self.assertTrue(interesses & set.union(*areas))

    def test_pc4_projetos_distinguem_participacao_mista(self):
        docentes = {pessoa["id"] for pessoa in self.docentes}
        discentes = {pessoa["id"] for pessoa in self.discentes}
        projetos = [set(projeto["participantes"]) for projeto in self.dados["projetos"]]
        self.assertTrue(any(
            docente != discente
            for projeto in projetos
            for docente in projeto & docentes
            for discente in projeto & discentes
        ))
        self.assertTrue(any(bool(projeto & docentes) != bool(projeto & discentes) for projeto in projetos))

    def test_pc5_um_mesmo_docente_tem_publicacao_com_e_sem_coautor_identificado(self):
        autorias = [set(publicacao.get("autores", [])) for publicacao in self.dados["publicacoes"]]
        pessoas = {pessoa["id"] for pessoa in self.dados["pessoas"]}
        self.assertTrue(any(
            {docente["id"]} in autorias
            and any(
                docente["id"] in autores and autores & (pessoas - {docente["id"]})
                for autores in autorias
            )
            for docente in self.docentes
        ))
