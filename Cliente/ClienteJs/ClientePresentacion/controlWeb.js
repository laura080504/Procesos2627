class ControlWeb {
    constructor(clienteRest) {
        this.rest = clienteRest;
        this.usuarioActual = null;
        this.matricula = null;
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
            alReenviar: (email) => this.reenviarConfirmacion(email),
            alDictar: (campo) => this.dictar(campo),
        });
        this.vistaRegistro = new VistaRegistro({
            alEnviar: (email, nick, contrasena) => this.registrar(email, nick, contrasena),
            alIrAInicioSesion: () => this.mostrarInicioSesion(),
            alDictar: (campo) => this.dictar(campo),
            alNoCoinciden: () => this.mostrarMensaje(this.textos.contrasenasNoCoinciden, true),
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
            alEditar: () => this.mostrarEditarDatos(this.usuarioActual),
            alEditarUsuario: (usuario) => this.mostrarEditarDatos(usuario),
            alVolverAgenda: () => this.mostrarAgenda(),
        });
        this.vistaAgenda = new VistaAgenda({
            alBuscar: (nombre) => this.buscarAsignaturas(nombre),
            alAbrirPerfil: () => this.mostrarPanel(),
            alCambiarTema: () => this.alternarTema(),
            alCambiarIdioma: () => this.alternarIdioma(),
            alLeer: (texto) => this.leerPantalla(texto),
            alCambiarMes: () => this.cargarMarcas(),
        });
        this.vistaEditarDatos = new VistaEditarDatos({
            alGuardar: (datos) => this.guardarEdicion(datos),
            alVolver: () => this.mostrarPanel(),
            alNoCoinciden: () => this.mostrarMensaje(this.textos.contrasenasNoCoinciden, true),
        });
        this.aplicarIdioma();
    }

    get textos() {
        return TEXTOS[this.idioma];
    }

    async iniciar() {
        const params = new URLSearchParams(location.search);
        const confirmar = params.get("confirmar");
        const aviso = params.get("aviso");
        if (confirmar || aviso) {
            history.replaceState({}, "", location.pathname);
        }
        const avisoPendiente = await this.avisoInicial(confirmar, aviso);
        try {
            this.usuarioActual = await this.rest.obtenerSesion();
            await this.abrirTrasSesion();
        } catch {
            this.mostrarInicioSesion();
        }
        if (avisoPendiente) {
            this.mostrarMensaje(avisoPendiente.texto, avisoPendiente.error);
        }
    }

    async avisoInicial(confirmar, aviso) {
        if (confirmar) {
            try {
                await this.rest.confirmarCuenta(confirmar);
                return { texto: this.textos.cuentaConfirmada, error: false };
            } catch (error) {
                return { texto: error.message, error: true };
            }
        }
        const avisos = {
            "google-no-configurado": this.textos.googleNoConfigurado,
            "google-error": this.textos.googleError,
            "cuenta-eliminada": this.textos.usuarioEliminado,
        };
        if (avisos[aviso]) {
            return { texto: avisos[aviso], error: true };
        }
        return null;
    }

    async reenviarConfirmacion(email) {
        if (!email) {
            this.mostrarMensaje(this.textos.emailParaReenviar, true);
            return;
        }
        try {
            await this.rest.reenviarConfirmacion(email);
            this.mostrarMensaje(this.textos.correoReenviado);
        } catch (error) {
            this.mostrarMensaje(error.message, true);
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
        this.vistaEditarDatos.aplicarTextos(this.textos);
        this.vistaAgenda.aplicarTextos(this.textos);
        if (this.usuarioActual) {
            this.cabecera.mostrar(this.usuarioActual, this.textos);
        }
    }

    dictar(campo) {
        this.dictado.dictar(campo, this.idioma, () => {
            this.mostrarMensaje(this.textos.vozNoDisponible, true);
        });
    }

    leerPantalla(texto) {
        this.dictado.leer(texto, this.idioma, () => {
            this.mostrarMensaje(this.textos.lecturaNoDisponible, true);
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
        this.vistaEditarDatos.ocultar();
        this.vistaAgenda.ocultar();
        document.body.classList.remove("con-agenda");
        document.body.classList.remove("en-perfil");
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

    async abrirTrasSesion() {
        if (this.esGestion(this.usuarioActual.rol)) {
            await this.mostrarPanel();
            return;
        }
        await this.mostrarAgenda();
    }

    async mostrarAgenda() {
        this.ocultarVistas();
        document.body.classList.add("con-agenda");
        this.vistaAgenda.mostrar(this.usuarioActual, this.textos);
        await this.cargarAgenda();
    }

    async cargarAgenda() {
        const periodo = this.vistaAgenda.periodo();
        try {
            const [matricula, marcas] = await Promise.all([
                this.rest.obtenerMatricula(this.vistaAgenda.textoBusqueda()),
                this.rest.obtenerMarcas(periodo.anio, periodo.mes),
            ]);
            this.matricula = matricula;
            this.vistaAgenda.pintar(matricula.asignaturas, marcas, matricula.horario);
        } catch (error) {
            this.gestionarError(error);
        }
    }

    async cargarMarcas() {
        const periodo = this.vistaAgenda.periodo();
        try {
            const marcas = await this.rest.obtenerMarcas(periodo.anio, periodo.mes);
            this.vistaAgenda.pintar(this.vistaAgenda.asignaturas, marcas);
        } catch (error) {
            this.gestionarError(error);
        }
    }

    async buscarAsignaturas(nombre) {
        try {
            const matricula = await this.rest.obtenerMatricula(nombre);
            this.vistaAgenda.pintar(matricula.asignaturas, this.vistaAgenda.marcas, matricula.horario);
        } catch (error) {
            this.gestionarError(error);
        }
    }

    async mostrarPanel() {
        this.ocultarVistas();
        document.body.classList.add("en-perfil");
        this.cabecera.mostrar(this.usuarioActual, this.textos);
        this.vistaUsuarios.mostrar();
        await this.refrescarUsuarios();
    }

    esGestion(rol) {
        return rol === "profesor" || rol === "superadministrador";
    }

    mostrarEditarDatos(usuario) {
        const propio = usuario.email === this.usuarioActual.email;
        this.ocultarVistas();
        this.vistaEditarDatos.mostrar(usuario, {
            propio,
            puedeAsignarProfesor: !propio && this.usuarioActual.rol === "superadministrador" && usuario.rol === "usuario",
        });
    }

    async guardarEdicion(datos) {
        if (!datos.propio) {
            if (!datos.hacerAdmin) {
                await this.mostrarPanel();
                return;
            }
            await this.asignarAdministrador(this.vistaEditarDatos.usuario.email);
            return;
        }
        await this.editarDatos(datos.email, datos.nick, datos.contrasena);
    }

    async editarDatos(email, nick, contrasena) {
        try {
            this.usuarioActual = await this.rest.editarDatos(email, nick, contrasena);
            await this.mostrarPanel();
            this.mostrarMensaje(this.textos.datosActualizados);
        } catch (error) {
            if (error.estado === 409) {
                this.mostrarMensaje(this.textos.emailYaRegistrado, true);
                return;
            }
            this.gestionarError(error);
        }
    }

    async asignarAdministrador(email) {
        try {
            await this.rest.asignarAdministrador(email);
            await this.mostrarPanel();
            this.mostrarMensaje(this.textos.rolActualizado);
        } catch (error) {
            this.gestionarError(error);
        }
    }

    async registrar(email, nick, contrasena) {
        try {
            await this.rest.registrar(email, nick, contrasena);
            this.mostrarInicioSesion();
            this.mostrarMensaje(this.textos.cuentaCreada);
        } catch (error) {
            if (error.estado === 409) {
                this.mostrarMensaje(this.textos.emailYaRegistrado, true);
                return;
            }
            this.mostrarMensaje(error.message, true);
        }
    }

    async solicitarRecuperacion(email) {
        try {
            const recuperacion = await this.rest.solicitarRecuperacion(email);
            this.vistaRecuperacion.mostrarNuevaContrasena(recuperacion.token);
            this.mostrarMensaje(this.textos.introduceNuevaContrasena);
        } catch (error) {
            this.mostrarMensaje(this.mensajeCuentaEliminada(error, true) || error.message, true);
        }
    }

    async restablecerContrasena(token, contrasena) {
        try {
            await this.rest.restablecerContrasena(token, contrasena);
            this.mostrarInicioSesion();
            this.mostrarMensaje(this.textos.contrasenaActualizada);
        } catch (error) {
            this.mostrarMensaje(this.mensajeCuentaEliminada(error, true) || error.message, true);
        }
    }

    async iniciarSesion(email, contrasena) {
        try {
            this.usuarioActual = await this.rest.iniciarSesion(email, contrasena);
            this.vistaInicioSesion.mostrarReenvio(false);
            this.limpiarMensaje();
            await this.abrirTrasSesion();
        } catch (error) {
            const pendiente = error.estado === 403 && /pendiente/i.test(error.message || "");
            this.vistaInicioSesion.mostrarReenvio(pendiente);
            this.mostrarMensaje(this.mensajeCuentaEliminada(error, false) || error.message, true);
        }
    }

    mensajeCuentaEliminada(error, esRecuperacion) {
        if (error.estado !== 403 || !/eliminado/i.test(error.message || "")) {
            return "";
        }
        return esRecuperacion ? this.textos.usuarioEliminadoRecuperar : this.textos.usuarioEliminado;
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
        const esGestion = this.esGestion(this.usuarioActual.rol);
        if (!esGestion) {
            try {
                this.matricula = await this.rest.obtenerMatricula("");
            } catch (error) {
                this.gestionarError(error);
                return;
            }
            this.vistaUsuarios.pintar([this.usuarioActual], this.usuarioActual.email, this.usuarioActual.rol, this.matricula);
            return;
        }
        try {
            const usuarios = await this.rest.obtenerUsuarios();
            this.vistaUsuarios.pintar(usuarios, this.usuarioActual.email, this.usuarioActual.rol);
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
