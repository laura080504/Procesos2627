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
        this.socketAvisos = null;
        this.cacheMarcas = new Map();
        this.cacheMatricula = null;
        this.peticionMatricula = null;
        this.cargandoMarcas = null;
        this.temporizadorMes = null;
        this.refrescoFichas = null;
        this.vistaUsuarios = new VistaUsuarios({
            alEliminar: (email) => this.eliminarUsuario(email),
            alRefrescar: () => this.refrescarUsuarios(),
            alEditar: () => this.mostrarEditarDatos(this.usuarioActual),
            alEditarUsuario: (usuario) => this.mostrarEditarDatos(usuario),
            alVolverAgenda: () => this.mostrarAgenda(),
            alCambiarPreferenciasAvisos: (preferencias) => this.cambiarPreferenciasAvisos(preferencias),
            alCrearEvento: (datos) => this.crearEventoProfesor(datos),
            alGuardarMatricula: (asignaturas) => this.guardarMatriculaAlumno(asignaturas),
            alAbrirHistorial: () => this.abrirHistorialAlumno(),
            alGuardarHistorial: (calificaciones, intensificacion) =>
                this.guardarHistorialAlumno(calificaciones, intensificacion),
            alGuardarIntensificacion: (intensificacion) => this.guardarIntensificacionAlumno(intensificacion),
        });
        this.vistaAgenda = new VistaAgenda({
            alBuscar: (nombre) => this.buscarAsignaturas(nombre),
            alAbrirPerfil: () => this.mostrarPanel(),
            alCambiarTema: () => this.alternarTema(),
            alCambiarIdioma: () => this.alternarIdioma(),
            alLeer: (texto) => this.leerPantalla(texto),
            alCambiarMes: () => this.programarCargaMarcas(),
            alAbrirAsignatura: (asignatura) => this.asegurarFichaAsignatura(asignatura),
            alEditarMatricula: () => this.abrirEdicionMatriculaDesdeAgenda(),
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
        this.conectarAvisos();
        // Profesores/admins entran a la agenda (solo sus asignaturas); la gestión va en el perfil.
        await this.mostrarAgenda();
    }

    conectarAvisos() {
        this.desconectarAvisos();
        const protocolo = location.protocol === "https:" ? "wss" : "ws";
        this.socketAvisos = new WebSocket(`${protocolo}://${location.host}/ws`);
        this.socketAvisos.addEventListener("message", (evento) => this.recibirAvisoProfesor(evento));
    }

    desconectarAvisos() {
        if (this.socketAvisos) {
            this.socketAvisos.close();
            this.socketAvisos = null;
        }
    }

    async recibirAvisoProfesor(evento) {
        let mensaje;
        try {
            mensaje = JSON.parse(evento.data);
        } catch {
            return;
        }
        if (!mensaje || mensaje.tipo !== "evento_nuevo") {
            return;
        }
        const codigos = (this.matricula && this.matricula.asignaturas)
            ? this.matricula.asignaturas.map((asignatura) => asignatura.codigo)
            : (this.vistaAgenda.asignaturas || []).map((asignatura) => asignatura.codigo);
        if (codigos.length && !codigos.includes(mensaje.codigo)) {
            return;
        }
        if (this.esGestion(this.usuarioActual?.rol)) {
            return;
        }
        const ingles = this.textos.codigo === "EN";
        const nombre = ingles ? mensaje.nombre_ingles : mensaje.nombre;
        const tipo = mensaje.tipo_evento === "examen" ? this.textos.examen : this.textos.entrega;
        const fecha = mensaje.fecha || "";
        this.mostrarMensaje(
            `${this.textos.avisoNuevoRecibido}: ${tipo} · ${nombre} · ${this.textos.fechaFinalizacion}: ${fecha}`,
        );
        if (!this.vistaAgenda.seccion.hidden) {
            this.invalidarCacheMarcas();
            await this.cargarMarcas();
            this.vistaAgenda.actualizarAvisos();
        }
    }

    async crearEventoProfesor(datos) {
        try {
            await this.rest.crearEvento(datos);
            this.vistaUsuarios.limpiarFormularioEvento();
            this.mostrarMensaje(this.textos.avisoPublicado);
        } catch (error) {
            this.gestionarError(error);
        }
    }

    async mostrarAgenda() {
        this.ocultarVistas();
        document.body.classList.add("con-agenda");
        this.vistaAgenda.mostrar(this.usuarioActual, this.textos);
        await this.cargarAgenda();
    }

    periodosAntelacion() {
        const prefs = PreferenciasNotificaciones.leer();
        const ahora = new Date();
        const limite = PreferenciasNotificaciones.limiteAntelacion(prefs, ahora);
        const periodos = PreferenciasNotificaciones.periodosHasta(limite, ahora);
        const visto = this.vistaAgenda.periodo();
        if (!periodos.some((periodo) => periodo.anio === visto.anio && periodo.mes === visto.mes)) {
            periodos.unshift(visto);
        }
        return periodos;
    }

    claveMarcas(anio, mes) {
        return `${anio}-${mes}`;
    }

    invalidarCacheMarcas() {
        this.cacheMarcas.clear();
    }

    async obtenerMarcasMes(anio, mes) {
        const clave = this.claveMarcas(anio, mes);
        if (this.cacheMarcas.has(clave)) {
            return this.cacheMarcas.get(clave);
        }
        const marcas = await this.rest.obtenerMarcas(anio, mes);
        this.cacheMarcas.set(clave, marcas);
        return marcas;
    }

    resumenMarcasCache() {
        const periodoVista = this.vistaAgenda.periodo();
        const marcasVista = this.cacheMarcas.get(this.claveMarcas(periodoVista.anio, periodoVista.mes)) || [];
        const marcasAntelacion = [];
        this.periodosAntelacion().forEach((periodo) => {
            const marcas = this.cacheMarcas.get(this.claveMarcas(periodo.anio, periodo.mes));
            if (marcas) {
                marcasAntelacion.push(...marcas);
            }
        });
        return { marcasVista, marcasAntelacion };
    }

    guardarPeriodosMarcas(periodos) {
        Object.entries(periodos || {}).forEach(([clave, marcas]) => {
            this.cacheMarcas.set(clave, marcas);
        });
    }

    async obtenerMarcasAntelacion({ soloVista = false } = {}) {
        const periodoVista = this.vistaAgenda.periodo();
        if (soloVista) {
            await this.obtenerMarcasMes(periodoVista.anio, periodoVista.mes);
            return this.resumenMarcasCache();
        }
        const periodos = this.periodosAntelacion();
        const faltan = periodos.some(
            (periodo) => !this.cacheMarcas.has(this.claveMarcas(periodo.anio, periodo.mes)),
        );
        if (faltan) {
            const primero = periodos[0];
            const respuesta = await this.rest.obtenerMarcasRango(primero.anio, primero.mes, periodos.length);
            this.guardarPeriodosMarcas(respuesta.periodos);
        }
        return this.resumenMarcasCache();
    }

    programarCargaMarcas() {
        clearTimeout(this.temporizadorMes);
        this.temporizadorMes = setTimeout(() => this.cargarMarcas({ soloVista: true }), 50);
    }

    async cambiarPreferenciasAvisos(preferencias) {
        this.vistaAgenda.aplicarPreferenciasAvisos(preferencias);
        this.invalidarCacheMarcas();
        if (!this.vistaAgenda.seccion.hidden) {
            await this.cargarMarcas();
        }
    }

    metaHorario(matricula) {
        const datos = matricula || this.matricula || {};
        return {
            inicioSegundo: datos.inicio_segundo || null,
            cuatrimestreActual: datos.cuatrimestre_actual || 1,
        };
    }

    async cargarAgenda() {
        try {
            const periodo = this.vistaAgenda.periodo();
            const [matricula, marcasVista] = await Promise.all([
                this.obtenerMatriculaCacheada(this.vistaAgenda.textoBusqueda()),
                this.obtenerMarcasMes(periodo.anio, periodo.mes),
            ]);
            this.matricula = matricula;
            this.vistaAgenda.pintar(
                matricula.asignaturas,
                marcasVista,
                matricula.horario,
                marcasVista,
                this.metaHorario(matricula),
            );
            this.programarRefrescoFichas();
            // Avisos del resto de meses en segundo plano (una sola petición).
            this.obtenerMarcasAntelacion().then((marcas) => {
                if (this.vistaAgenda.seccion.hidden) {
                    return;
                }
                this.vistaAgenda.pintar(
                    this.vistaAgenda.asignaturas,
                    marcas.marcasVista,
                    undefined,
                    marcas.marcasAntelacion,
                );
            }).catch(() => {});
        } catch (error) {
            this.gestionarError(error);
        }
    }

    async obtenerMatriculaCacheada(nombre = "", { forzar = false } = {}) {
        const clave = (nombre || "").trim().toLowerCase();
        if (
            !forzar
            && this.cacheMatricula
            && this.cacheMatricula.clave === clave
            && Date.now() - this.cacheMatricula.en < 15000
        ) {
            return this.cacheMatricula.datos;
        }
        if (
            this.peticionMatricula
            && this.peticionMatricula.clave === clave
            && !forzar
        ) {
            return this.peticionMatricula.promesa;
        }
        const promesa = this.rest.obtenerMatricula(nombre).then((datos) => {
            this.cacheMatricula = { clave, datos, en: Date.now() };
            this.matricula = datos;
            if (this.peticionMatricula && this.peticionMatricula.promesa === promesa) {
                this.peticionMatricula = null;
            }
            return datos;
        }).catch((error) => {
            if (this.peticionMatricula && this.peticionMatricula.promesa === promesa) {
                this.peticionMatricula = null;
            }
            throw error;
        });
        this.peticionMatricula = { clave, promesa };
        return promesa;
    }

    programarRefrescoFichas() {
        clearTimeout(this.refrescoFichas);
        const faltan = (this.matricula?.asignaturas || []).some(
            (asignatura) => !asignatura.profesores || asignatura.profesores.length === 0,
        );
        if (!faltan) {
            return;
        }
        this.refrescoFichas = setTimeout(() => {
            this.obtenerMatriculaCacheada(this.vistaAgenda.textoBusqueda(), { forzar: true })
                .then((matricula) => {
                    if (this.vistaAgenda.seccion.hidden) {
                        return;
                    }
                    this.vistaAgenda.pintar(
                        matricula.asignaturas,
                        this.vistaAgenda.marcas,
                        matricula.horario,
                        this.vistaAgenda.marcasAntelacion,
                        this.metaHorario(matricula),
                    );
                })
                .catch(() => {});
        }, 700);
    }

    async asegurarFichaAsignatura(asignatura) {
        if (!asignatura) {
            return;
        }
        if (asignatura.profesores && asignatura.profesores.length) {
            return;
        }
        try {
            const matricula = await this.obtenerMatriculaCacheada(this.vistaAgenda.textoBusqueda(), { forzar: true });
            const actualizada = matricula.asignaturas.find((item) => item.codigo === asignatura.codigo);
            if (!actualizada || this.vistaAgenda.seccion.hidden) {
                return;
            }
            if (this.vistaAgenda.abierta?.codigo === asignatura.codigo) {
                this.vistaAgenda.abierta = actualizada;
                this.vistaAgenda.pintarFicha();
            }
            this.vistaAgenda.pintar(
                matricula.asignaturas,
                this.vistaAgenda.marcas,
                matricula.horario,
                this.vistaAgenda.marcasAntelacion,
                this.metaHorario(matricula),
            );
        } catch {
            /* silencioso: la ficha se completará en el siguiente refresco */
        }
    }

    async cargarMarcas({ soloVista = false } = {}) {
        const peticion = this.obtenerMarcasAntelacion({ soloVista });
        this.cargandoMarcas = peticion;
        try {
            const marcas = await peticion;
            if (this.cargandoMarcas !== peticion) {
                return;
            }
            this.vistaAgenda.pintar(
                this.vistaAgenda.asignaturas,
                marcas.marcasVista,
                undefined,
                marcas.marcasAntelacion,
            );
        } catch (error) {
            if (this.cargandoMarcas === peticion) {
                this.gestionarError(error);
            }
        }
    }

    async buscarAsignaturas(nombre) {
        try {
            const texto = (nombre || "").trim().toLowerCase();
            if (
                this.cacheMatricula
                && this.cacheMatricula.clave === ""
                && Date.now() - this.cacheMatricula.en < 15000
            ) {
                const filtradas = texto
                    ? this.cacheMatricula.datos.asignaturas.filter((asignatura) => {
                        const es = (asignatura.nombre || "").toLowerCase();
                        const en = (asignatura.nombre_ingles || "").toLowerCase();
                        return es.includes(texto) || en.includes(texto);
                    })
                    : this.cacheMatricula.datos.asignaturas;
                this.vistaAgenda.pintar(
                    filtradas,
                    this.vistaAgenda.marcas,
                    this.cacheMatricula.datos.horario,
                    this.vistaAgenda.marcasAntelacion,
                    this.metaHorario(this.cacheMatricula.datos),
                );
                return;
            }
            const matricula = await this.obtenerMatriculaCacheada(nombre);
            this.vistaAgenda.pintar(
                matricula.asignaturas,
                this.vistaAgenda.marcas,
                matricula.horario,
                this.vistaAgenda.marcasAntelacion,
                this.metaHorario(matricula),
            );
        } catch (error) {
            this.gestionarError(error);
        }
    }

    async mostrarPanel() {
        this.ocultarVistas();
        document.body.classList.add("en-perfil");
        // Primero se fija la vista según el rol para no enseñar gestión al alumno ni un instante.
        this.vistaUsuarios.mostrar(this.usuarioActual.rol);
        if (this.esGestion(this.usuarioActual.rol)) {
            this.cabecera.mostrar(this.usuarioActual, this.textos);
            try {
                const asignaturas = await this.rest.listarAsignaturas("");
                this.vistaUsuarios.cargarCatalogoAsignaturas(asignaturas);
            } catch (error) {
                this.gestionarError(error);
            }
        } else {
            this.vistaUsuarios.pintarIdentidadEstudiante(this.usuarioActual);
        }
        await this.refrescarUsuarios();
    }

    async abrirEdicionMatriculaDesdeAgenda() {
        await this.mostrarPanel();
        if (!this.esGestion(this.usuarioActual.rol)) {
            this.vistaUsuarios.abrirEditorMatricula();
        }
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
            this.desconectarAvisos();
            this.usuarioActual = null;
            this.mostrarInicioSesion();
            this.mostrarMensaje(this.textos.sesionCerrada);
        }
    }

    async guardarMatriculaAlumno(asignaturas) {
        if (!asignaturas || !asignaturas.length) {
            this.mostrarMensaje(this.textos.matriculaVacia, true);
            return;
        }
        try {
            const matricula = await this.rest.guardarMatricula(asignaturas);
            this.matricula = matricula;
            this.cacheMatricula = { clave: "", datos: matricula, en: Date.now() };
            this.invalidarCacheMarcas();
            this.vistaUsuarios.cerrarEditorMatricula();
            this.vistaUsuarios.pintar(
                [this.usuarioActual],
                this.usuarioActual.email,
                this.usuarioActual.rol,
                matricula,
            );
            if (!this.vistaAgenda.seccion.hidden) {
                this.vistaAgenda.pintar(
                    matricula.asignaturas,
                    this.vistaAgenda.marcas,
                    matricula.horario,
                    this.vistaAgenda.marcasAntelacion,
                    this.metaHorario(matricula),
                );
            }
            this.mostrarMensaje(this.textos.matriculaGuardada);
            this.cargarMarcas().catch(() => {});
        } catch (error) {
            this.gestionarError(error);
        }
    }

    async abrirHistorialAlumno() {
        try {
            const expediente = await this.rest.obtenerExpediente();
            this.vistaUsuarios.abrirHistorial(expediente);
        } catch (error) {
            this.gestionarError(error);
        }
    }

    async guardarHistorialAlumno(calificaciones, intensificacion) {
        try {
            await this.rest.guardarExpediente(calificaciones || [], intensificacion ?? "");
            this.cacheMatricula = { clave: "", datos: null, en: 0 };
            const matricula = await this.obtenerMatriculaCacheada("", { forzar: true });
            this.matricula = matricula;
            this.vistaUsuarios.cerrarHistorial();
            this.vistaUsuarios.pintar(
                [this.usuarioActual],
                this.usuarioActual.email,
                this.usuarioActual.rol,
                matricula,
            );
            this.mostrarMensaje(this.textos.historialGuardado);
        } catch (error) {
            this.gestionarError(error);
        }
    }

    async guardarIntensificacionAlumno(intensificacion) {
        try {
            await this.rest.guardarExpediente([], intensificacion ?? "");
            this.cacheMatricula = { clave: "", datos: null, en: 0 };
            const matricula = await this.obtenerMatriculaCacheada("", { forzar: true });
            this.matricula = matricula;
            this.vistaUsuarios.pintar(
                [this.usuarioActual],
                this.usuarioActual.email,
                this.usuarioActual.rol,
                matricula,
            );
            this.mostrarMensaje(this.textos.intensificacionGuardada);
        } catch (error) {
            this.gestionarError(error);
        }
    }

    async refrescarUsuarios() {
        const esGestion = this.esGestion(this.usuarioActual.rol);
        if (!esGestion) {
            try {
                this.matricula = await this.rest.obtenerMatricula("");
                this.cacheMatricula = { clave: "", datos: this.matricula, en: Date.now() };
                if (!this.vistaUsuarios.catalogoAsignaturas.length) {
                    this.vistaUsuarios.cargarCatalogoAsignaturas(await this.rest.listarAsignaturas(""));
                }
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
