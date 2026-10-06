class ControlWeb {
    constructor(clienteRest) {
        this.rest = clienteRest;
        this.usuarioActual = null;
        this.mensaje = document.getElementById("mensaje");
        this.temporizadorAviso = null;
        this.idioma = localStorage.getItem("idioma") === "en" ? "en" : "es";
        this.tema = localStorage.getItem("tema") === "oscuro" ? "oscuro" : "claro";
        this.dictado = new DictadoVoz();
        document.body.classList.toggle("oscuro", this.tema === "oscuro");

        this.barra = new VistaBarraHerramientas({
            alCambiarTema: () => this.alternarTema(),
            alCambiarIdioma: () => this.alternarIdioma(),
        });
        this.cabecera = new VistaCabecera({
            alCerrarSesion: () => this.cerrarSesion(),
        });
        this.vistaInicioSesion = new VistaInicioSesion({
            alEnviar: (email, contrasena) => this.iniciarSesion(email, contrasena),
            alIrARegistro: () => this.mostrarRegistro(),
            alRecuperar: () => this.mostrarRecuperacion(),
            alDictar: (campo) => this.dictar(campo),
        });
        this.vistaRegistro = new VistaRegistro({
            alEnviar: (email, nick, contrasena) => this.registrar(email, nick, contrasena),
            alIrAInicioSesion: () => this.mostrarInicioSesion(),
            alDictar: (campo) => this.dictar(campo),
        });
        this.vistaRecuperacion = new VistaRecuperacion({
            alSolicitar: (email) => this.solicitarRecuperacion(email),
            alGuardar: (token, contrasena) => this.restablecerContrasena(token, contrasena),
            alVolver: () => this.mostrarInicioSesion(),
            alNoCoinciden: () => this.mostrarMensaje(this.textos.contrasenasNoCoinciden, true),
        });
        this.vistaUsuarios = new VistaUsuarios({
            alEliminar: (email) => this.eliminarUsuario(email),
            alRefrescar: () => this.refrescarUsuarios(),
        });
        this.aplicarIdioma();
    }

    get textos() {
        return TEXTOS[this.idioma];
    }

    async iniciar() {
        try {
            this.usuarioActual = await this.rest.obtenerSesion();
            await this.mostrarPanel();
        } catch {
            this.mostrarInicioSesion();
        }
    }

    alternarTema() {
        this.tema = this.tema === "oscuro" ? "claro" : "oscuro";
        localStorage.setItem("tema", this.tema);
        document.body.classList.toggle("oscuro", this.tema === "oscuro");
    }

    alternarIdioma() {
        this.idioma = this.idioma === "es" ? "en" : "es";
        localStorage.setItem("idioma", this.idioma);
        this.aplicarIdioma();
    }

    aplicarIdioma() {
        document.documentElement.lang = this.idioma;
        this.barra.aplicar(this.textos);
        this.vistaInicioSesion.aplicarTextos(this.textos);
        this.vistaRegistro.aplicarTextos(this.textos);
        this.vistaRecuperacion.aplicarTextos(this.textos);
        this.vistaUsuarios.aplicarTextos(this.textos);
    }

    dictar(campo) {
        this.dictado.dictar(campo, this.idioma, () => {
            this.mostrarMensaje(this.textos.vozNoDisponible, true);
        });
    }

    mostrarMensaje(texto, esError = false) {
        clearTimeout(this.temporizadorAviso);
        this.mensaje.textContent = texto;
        this.mensaje.className = esError ? "error" : "exito";
        this.mensaje.hidden = !texto;
        if (!texto) {
            return;
        }
        this.temporizadorAviso = setTimeout(() => this.limpiarMensaje(), 5000);
    }

    limpiarMensaje() {
        this.mostrarMensaje("");
    }

    ocultarVistas() {
        this.vistaInicioSesion.ocultar();
        this.vistaRegistro.ocultar();
        this.vistaRecuperacion.ocultar();
        this.vistaUsuarios.ocultar();
    }

    mostrarInicioSesion() {
        this.ocultarVistas();
        this.cabecera.ocultar();
        this.limpiarMensaje();
        this.vistaInicioSesion.mostrar();
    }

    mostrarRegistro() {
        this.ocultarVistas();
        this.limpiarMensaje();
        this.vistaRegistro.mostrar();
    }

    mostrarRecuperacion() {
        this.ocultarVistas();
        this.cabecera.ocultar();
        this.limpiarMensaje();
        this.vistaRecuperacion.mostrar();
    }

    async mostrarPanel() {
        this.ocultarVistas();
        this.cabecera.mostrar(this.usuarioActual);
        this.vistaUsuarios.mostrar();
        await this.refrescarUsuarios();
    }

    async registrar(email, nick, contrasena) {
        try {
            await this.rest.registrar(email, nick, contrasena);
            this.mostrarInicioSesion();
            this.mostrarMensaje(this.textos.cuentaCreada);
        } catch (error) {
            this.mostrarMensaje(error.message, true);
        }
    }

    async solicitarRecuperacion(email) {
        try {
            const recuperacion = await this.rest.solicitarRecuperacion(email);
            this.vistaRecuperacion.mostrarNuevaContrasena(recuperacion.token);
            this.mostrarMensaje(this.textos.introduceNuevaContrasena);
        } catch (error) {
            this.mostrarMensaje(error.message, true);
        }
    }

    async restablecerContrasena(token, contrasena) {
        try {
            await this.rest.restablecerContrasena(token, contrasena);
            this.mostrarInicioSesion();
            this.mostrarMensaje(this.textos.contrasenaActualizada);
        } catch (error) {
            this.mostrarMensaje(error.message, true);
        }
    }

    async iniciarSesion(email, contrasena) {
        try {
            this.usuarioActual = await this.rest.iniciarSesion(email, contrasena);
            this.limpiarMensaje();
            await this.mostrarPanel();
        } catch (error) {
            this.mostrarMensaje(error.message, true);
        }
    }

    async cerrarSesion() {
        try {
            await this.rest.cerrarSesion();
        } finally {
            this.usuarioActual = null;
            this.mostrarInicioSesion();
            this.mostrarMensaje(this.textos.sesionCerrada);
        }
    }

    async refrescarUsuarios() {
        const esAdministrador = this.usuarioActual.rol === "administrador";
        if (!esAdministrador) {
            this.vistaUsuarios.pintar([this.usuarioActual], this.usuarioActual.email, false);
            return;
        }
        try {
            const usuarios = await this.rest.obtenerUsuarios();
            this.vistaUsuarios.pintar(usuarios, this.usuarioActual.email, true);
        } catch (error) {
            this.gestionarError(error);
        }
    }

    async eliminarUsuario(email) {
        const pregunta = this.textos.confirmarEliminar.replace("{email}", email);
        if (!confirm(pregunta)) {
            return;
        }
        try {
            await this.rest.eliminarUsuario(email);
            if (email === this.usuarioActual.email) {
                this.usuarioActual = null;
                this.mostrarInicioSesion();
                this.mostrarMensaje(this.textos.cuentaEliminada);
                return;
            }
            await this.refrescarUsuarios();
        } catch (error) {
            this.gestionarError(error);
        }
    }

    gestionarError(error) {
        if (error.estado === 401) {
            this.usuarioActual = null;
            this.mostrarInicioSesion();
            this.mostrarMensaje(this.textos.sesionCaducada, true);
            return;
        }
        this.mostrarMensaje(error.message, true);
    }
}
