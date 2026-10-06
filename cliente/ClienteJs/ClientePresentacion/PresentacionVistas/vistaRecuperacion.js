class VistaRecuperacion {
    constructor({ alSolicitar, alGuardar, alVolver, alNoCoinciden }) {
        this.seccion = document.getElementById("vistaRecuperacion");
        this.formularioEmail = document.getElementById("formularioRecuperacion");
        this.formularioContrasena = document.getElementById("formularioNuevaContrasena");
        this.token = null;

        this.formularioEmail.addEventListener("submit", (evento) => {
            evento.preventDefault();
            alSolicitar(new FormData(this.formularioEmail).get("email").trim());
        });
        this.formularioContrasena.addEventListener("submit", (evento) => {
            evento.preventDefault();
            const datos = new FormData(this.formularioContrasena);
            const contrasena = datos.get("contrasena");
            if (contrasena !== datos.get("confirmar")) {
                alNoCoinciden();
                return;
            }
            alGuardar(this.token, contrasena);
        });
        document.getElementById("enlaceVolverInicio").addEventListener("click", (evento) => {
            evento.preventDefault();
            alVolver();
        });
        document.getElementById("enlaceCancelarRecuperacion").addEventListener("click", (evento) => {
            evento.preventDefault();
            alVolver();
        });
        this.formularioContrasena.querySelectorAll(".ver-contrasena").forEach((boton) => {
            boton.addEventListener("click", () => this.alternarContrasena(boton));
        });
    }

    aplicarTextos(textos) {
        this.textos = textos;
        aplicarTextos(this.seccion, textos);
        this.actualizarEtiquetas();
    }

    alternarContrasena(boton) {
        const campo = boton.closest(".linea").querySelector("input");
        campo.type = campo.type === "password" ? "text" : "password";
        this.actualizarEtiquetas();
    }

    actualizarEtiquetas() {
        if (!this.textos) {
            return;
        }
        this.formularioContrasena.querySelectorAll(".ver-contrasena").forEach((boton) => {
            const visible = boton.closest(".linea").querySelector("input").type === "text";
            boton.setAttribute("aria-label", visible ? this.textos.ocultarContrasena : this.textos.verContrasena);
        });
    }

    mostrar() {
        this.token = null;
        this.seccion.hidden = false;
        this.formularioEmail.hidden = false;
        this.formularioContrasena.hidden = true;
    }

    mostrarNuevaContrasena(token) {
        this.token = token;
        this.formularioEmail.hidden = true;
        this.formularioContrasena.hidden = false;
    }

    ocultar() {
        this.seccion.hidden = true;
        this.token = null;
        this.formularioEmail.reset();
        this.formularioContrasena.reset();
        this.formularioContrasena.querySelectorAll("input").forEach((campo) => {
            campo.type = "password";
        });
        this.actualizarEtiquetas();
    }
}
