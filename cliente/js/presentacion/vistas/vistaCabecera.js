class VistaCabecera {
    constructor({ alCerrarSesion }) {
        this.usuarioActual = document.getElementById("usuarioActual");
        document.getElementById("botonCerrarSesion").addEventListener("click", alCerrarSesion);
    }

    mostrar(usuario) {
        this.usuarioActual.textContent = `${usuario.nick} (${usuario.email})`;
    }

    ocultar() {
        this.usuarioActual.textContent = "";
    }
}
