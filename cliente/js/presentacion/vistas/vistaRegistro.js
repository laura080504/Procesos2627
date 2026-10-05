class VistaRegistro {
    constructor({ alEnviar, alIrAInicioSesion, alDictar }) {
        this.seccion = document.getElementById("vistaRegistro");
        this.formulario = document.getElementById("formularioRegistro");
        this.campoActivo = this.formulario.email;

        this.formulario.addEventListener("submit", (evento) => {
            evento.preventDefault();
            const datos = new FormData(this.formulario);
            alEnviar(datos.get("email").trim(), datos.get("nick").trim(), datos.get("contrasena"));
        });
        document.getElementById("enlaceInicioSesion").addEventListener("click", (evento) => {
            evento.preventDefault();
            alIrAInicioSesion();
        });
        document.getElementById("botonVozRegistro").addEventListener("click", () => alDictar(this.campoActivo));
        this.botonVer = this.formulario.querySelector(".ver-contrasena");
        this.botonVer.addEventListener("click", () => this.alternarContrasena());
        this.formulario.querySelectorAll("input").forEach((campo) => {
            campo.addEventListener("focus", () => {
                this.campoActivo = campo;
            });
        });
    }

    aplicarTextos(textos) {
        this.textos = textos;
        aplicarTextos(this.seccion, textos);
        this.actualizarEtiqueta();
    }

    alternarContrasena() {
        const campo = this.formulario.contrasena;
        campo.type = campo.type === "password" ? "text" : "password";
        this.actualizarEtiqueta();
    }

    actualizarEtiqueta() {
        if (!this.textos) {
            return;
        }
        const visible = this.formulario.contrasena.type === "text";
        this.botonVer.setAttribute("aria-label", visible ? this.textos.ocultarContrasena : this.textos.verContrasena);
    }

    mostrar() {
        this.seccion.hidden = false;
    }

    ocultar() {
        this.seccion.hidden = true;
        this.formulario.reset();
        this.formulario.contrasena.type = "password";
        this.actualizarEtiqueta();
    }
}
