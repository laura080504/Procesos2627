class VistaInicioSesion {
    constructor({ alEnviar, alIrARegistro, alRecuperar, alDictar }) {
        this.seccion = document.getElementById("vistaInicioSesion");
        this.formulario = document.getElementById("formularioInicioSesion");
        this.campoActivo = this.formulario.email;

        this.formulario.addEventListener("submit", (evento) => {
            evento.preventDefault();
            const datos = new FormData(this.formulario);
            const email = datos.get("email").trim();
            if (this.formulario.recordarme.checked) {
                localStorage.setItem("emailRecordado", email);
            } else {
                localStorage.removeItem("emailRecordado");
            }
            alEnviar(email, datos.get("contrasena"));
        });
        document.getElementById("enlaceRegistro").addEventListener("click", (evento) => {
            evento.preventDefault();
            alIrARegistro();
        });
        document.getElementById("enlaceRecuperar").addEventListener("click", (evento) => {
            evento.preventDefault();
            alRecuperar();
        });
        document.getElementById("botonVozLogin").addEventListener("click", () => alDictar(this.campoActivo));
        this.botonVer = this.formulario.querySelector(".ver-contrasena");
        this.botonVer.addEventListener("click", () => this.alternarContrasena());
        this.formulario.querySelectorAll("input:not([type=checkbox])").forEach((campo) => {
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
        const email = localStorage.getItem("emailRecordado");
        if (email) {
            this.formulario.email.value = email;
            this.formulario.recordarme.checked = true;
        }
    }

    ocultar() {
        this.seccion.hidden = true;
        this.formulario.reset();
        this.formulario.contrasena.type = "password";
        this.actualizarEtiqueta();
    }
}
