// Busca e filtro do catálogo. Sem JavaScript, o formulário fica oculto
// e todos os perfis continuam listados e acessíveis.
(function () {
  "use strict";

  var formulario = document.querySelector("[data-filtro]");
  var lista = document.querySelector("[data-perfis]");
  var contagem = document.getElementById("contagem");
  var vazio = document.getElementById("sem-resultados");
  if (!formulario || !lista || !contagem || !vazio) {
    return;
  }

  var cartoes = Array.prototype.slice.call(lista.querySelectorAll("[data-busca]"));
  var busca = formulario.querySelector("#busca");
  var papel = formulario.querySelector("#papel");
  var limpar = vazio.querySelector("[data-limpar]");

  function normalizar(texto) {
    return texto.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }

  function rotulo(quantidade) {
    return quantidade === 1 ? "1 perfil" : quantidade + " perfis";
  }

  function atualizar() {
    var termos = normalizar(busca.value).split(/\s+/).filter(Boolean);
    var papelEscolhido = papel.value;
    var visiveis = 0;

    cartoes.forEach(function (cartao) {
      var texto = normalizar(cartao.getAttribute("data-busca"));
      var papelCartao = cartao.getAttribute("data-papel");
      var papelConfere = !papelEscolhido || papelCartao === papelEscolhido || papelCartao === "ambos";
      var textoConfere = termos.every(function (termo) {
        return texto.indexOf(termo) !== -1;
      });
      cartao.hidden = !(papelConfere && textoConfere);
      if (!cartao.hidden) {
        visiveis += 1;
      }
    });

    var filtrado = termos.length > 0 || papelEscolhido !== "";
    contagem.textContent = filtrado
      ? visiveis + " de " + rotulo(cartoes.length)
      : rotulo(cartoes.length);
    vazio.hidden = visiveis !== 0;
  }

  formulario.hidden = false;
  formulario.addEventListener("input", atualizar);
  formulario.addEventListener("change", atualizar);
  formulario.addEventListener("submit", function (evento) {
    evento.preventDefault();
  });
  formulario.addEventListener("reset", function () {
    window.setTimeout(atualizar, 0);
  });
  limpar.addEventListener("click", function () {
    formulario.reset();
    busca.focus();
  });
})();
