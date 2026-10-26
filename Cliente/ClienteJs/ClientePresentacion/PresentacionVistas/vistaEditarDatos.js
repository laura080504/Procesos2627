class VistaEditarDatos {
    constructor({ alGuardar, alVolver, alNoCoinciden }) {
        this.seccion = document.getElementById("vistaEditarDatos");
        this.formulario = document.getElementById("formularioEditarDatos");
        this.rol = document.getElementById("rolEditar");
        this.campoAdmin = document.getElementById("campoHacerAdmin");
        this.casillaAdmin = document.getElementById("hacerAdministrador");
        this.camposContrasena = document.getElementById("camposContrasenaEditar");
        this.botonGuardar = this.formulario.querySelector("button[type='submit']");
        this.alNoCoinciden = alNoCoinciden;
        this.usuario = null;
        this.opciones = { propio: true };
        this.formulario.addEventListener("submit", (evento) => {
            evento.preventDefault();
            if (!this.opciones.propio) {
                alGuardar({ propio: false, hacerAdmin: this.casillaAdmin.checked });
                return;
            }
            const datos = new FormData(this.formulario);
            const contrasena = (datos.get("contrasena") || "").trim();
            const confirmar = (datos.get("confirmar") || "").trim();
            if (contrasena !== confirmar) {
                this.alNoCoinciden();
                return;
            }
            alGuardar({
                propio: true,
                email: datos.get("email").trim(),
                nick: datos.get("nick").trim(),
                contrasena,
            });
        });
        document.getElementById("enlaceVolverEditar").addEventListener("click", (evento) => {
            evento.preventDefault();
            alVolver();
        });
        this.formulario.querySelectorAll(".ver-contrasena").forEach((boton) => {
            boton.addEventListener("click", () => this.alternarContrasena(boton));
        });
    }

    aplicarTextos(textos) {
        this.textos = textos;
        aplicarTextos(this.seccion, textos);
        this.actualizarEtiquetas();
        if (!this.seccion.hidden && this.usuario) {
            this.mostrar(this.usuario, this.opciones);
        }
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

    mostrar(usuario, opciones = { propio: true }) {
        this.usuario = usuario;
        this.opciones = opciones;
        this.formulario.reset();
        this.formulario.email.value = usuario.email;
        this.formulario.nick.value = usuario.nick;
        const propio = opciones.propio;
        const puedeAsignar = Boolean(opciones.puedeAsignarProfesor);
        this.formulario.email.readOnly = !propio;
        this.formulario.nick.readOnly = !propio;
        this.camposContrasena.hidden = !propio;
        this.campoAdmin.hidden = !puedeAsignar;
        this.casillaAdmin.checked = false;
        this.casillaAdmin.disabled = !puedeAsignar;
        this.rol.hidden = true;
        this.rol.textContent = "";
        this.botonGuardar.hidden = !propio && !puedeAsignar;
        this.formulario.querySelectorAll("input[name='contrasena'], input[name='confirmar']").forEach((campo) => {
            campo.type = "password";
        });
        this.actualizarEtiquetas();
        this.seccion.hidden = false;
    }

    ocultar() {
        this.seccion.hidden = true;
        this.usuario = null;
        this.formulario.reset();
        this.formulario.email.readOnly = false;
        this.formulario.nick.readOnly = false;
        this.camposContrasena.hidden = false;
        this.campoAdmin.hidden = true;
        this.rol.hidden = true;
        this.botonGuardar.hidden = false;
        this.formulario.querySelectorAll("input[name='contrasena'], input[name='confirmar']").forEach((campo) => {
            campo.type = "password";
        });
        this.actualizarEtiquetas();
    }
}
