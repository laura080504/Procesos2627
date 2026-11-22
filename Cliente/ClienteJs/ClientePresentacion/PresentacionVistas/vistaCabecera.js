class VistaCabecera {
    constructor({ alCerrarSesion }) {
        this.usuarioActual = document.getElementById("usuarioActual");
        document.getElementById("botonCerrarSesion").addEventListener("click", alCerrarSesion);
        document.getElementById("botonCerrarSesionCuenta").addEventListener("click", alCerrarSesion);
    }

    mostrar(usuario, textos) {
        pintarIdentidadUsuario(this.usuarioActual, usuario);
    }

    ocultar() {
        this.usuarioActual.textContent = "";
    }
}
