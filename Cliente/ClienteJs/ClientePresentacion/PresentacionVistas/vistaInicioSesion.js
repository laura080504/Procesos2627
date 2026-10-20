class VistaInicioSesion {
        constructor({ alEnviar, alIrARegistro, alRecuperar, alReenviar, alDictar }) {
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
        this.avisoPendiente = document.getElementById("avisoPendiente");
        document.getElementById("enlaceReenviar").addEventListener("click", () => {
            alReenviar(this.formulario.email.value.trim());
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

    mostrarReenvio(visible) {
        this.avisoPendiente.hidden = !visible;
    }

    mostrar() {
        this.seccion.hidden = false;
        this.mostrarReenvio(false);
        const email = localStorage.getItem("emailRecordado");
        if (email) {
            this.formulario.email.value = email;
            this.formulario.recordarme.checked = true;
        }
    }

    ocultar() {
        this.seccion.hidden = true;
        this.mostrarReenvio(false);
        this.formulario.reset();
        this.formulario.contrasena.type = "password";
        this.actualizarEtiqueta();
    }
}
