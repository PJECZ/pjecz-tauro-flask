/*
 * Tema claro/oscuro
 * - Sin elección guardada, sigue la preferencia del sistema (prefers-color-scheme)
 * - Al usar el switch se guarda la elección en localStorage
 * Se carga en el <head> para aplicar el tema antes de pintar la página y evitar parpadeos.
 */
(function () {
  const KEY = "tauro-theme";
  const root = document.documentElement;
  const mq = window.matchMedia("(prefers-color-scheme: dark)");

  function leer() {
    try {
      return localStorage.getItem(KEY);
    } catch (e) {
      return null;
    }
  }

  function guardar(valor) {
    try {
      localStorage.setItem(KEY, valor);
    } catch (e) {
      // Sin almacenamiento, el tema solo dura mientras la página esté abierta
    }
  }

  function aplicar() {
    const tema = leer() || (mq.matches ? "dark" : "light");
    root.setAttribute("data-theme", tema);
    const interruptor = document.getElementById("themeSwitch");
    if (interruptor) {
      interruptor.checked = tema === "dark";
    }
  }

  aplicar();
  mq.addEventListener("change", aplicar);
  document.addEventListener("DOMContentLoaded", function () {
    aplicar();
    const interruptor = document.getElementById("themeSwitch");
    if (interruptor) {
      interruptor.addEventListener("change", function () {
        guardar(interruptor.checked ? "dark" : "light");
        aplicar();
      });
    }
  });
})();
