class VistaRegistro {
    constructor({ alEnviar, alIrAInicioSesion, alDictar, alNoCoinciden }) {
        this.seccion = document.getElementById("vistaRegistro");
        this.formulario = document.getElementById("formularioRegistro");
        this.campoActivo = this.formulario.email;
        this.alNoCoinciden = alNoCoinciden;

        this.formulario.addEventListener("submit", (evento) => {
            evento.preventDefault();
            const datos = new FormData(this.formulario);
            const contrasena = datos.get("contrasena");
            if (contrasena !== datos.get("confirmar")) {
                this.alNoCoinciden();
                return;
            }
            alEnviar(datos.get("email").trim(), datos.get("nick").trim(), contrasena);
        });
        document.getElementById("enlaceInicioSesion").addEventListener("click", (evento) => {
            evento.preventDefault();
            alIrAInicioSesion();
        });
        document.getElementById("botonVozRegistro").addEventListener("click", () => alDictar(this.campoActivo));
        this.formulario.querySelectorAll(".ver-contrasena").forEach((boton) => {
            boton.addEventListener("click", () => this.alternarContrasena(boton));
        });
        this.formulario.querySelectorAll("input").forEach((campo) => {
            campo.addEventListener("focus", () => {
                this.campoActivo = campo;
            });
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
        this.formulario.querySelectorAll(".ver-contrasena").forEach((boton) => {
            const visible = boton.closest(".linea").querySelector("input").type === "text";
            boton.setAttribute("aria-label", visible ? this.textos.ocultarContrasena : this.textos.verContrasena);
        });
    }

    mostrar() {
        this.seccion.hidden = false;
    }

    ocultar() {
        this.seccion.hidden = true;
        this.formulario.reset();
        this.formulario.querySelectorAll("input[name='contrasena'], input[name='confirmar']").forEach((campo) => {
            campo.type = "password";
        });
        this.actualizarEtiquetas();
    }
}
