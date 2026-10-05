class VistaBarraHerramientas {
    constructor({ alCambiarTema, alCambiarIdioma }) {
        this.botonTema = document.getElementById("botonTema");
        this.botonIdioma = document.getElementById("botonIdioma");
        this.botonTema.addEventListener("click", alCambiarTema);
        this.botonIdioma.addEventListener("click", alCambiarIdioma);
    }

    aplicar(textos) {
        aplicarTextos(document.querySelector(".herramientas"), textos);
    }
}
