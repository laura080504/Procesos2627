class ClienteRest {
    constructor(clienteHttp) {
        this.clienteHttp = clienteHttp;
    }

    registrar(email, nick, contrasena) {
        return this.clienteHttp.peticion("POST", "/auth/registro", { email, nick, contrasena });
    }

    iniciarSesion(email, contrasena, recordar = false) {
        return this.clienteHttp.peticion("POST", "/auth/inicio-sesion", { email, contrasena, recordar });
    }

    cerrarSesion() {
        return this.clienteHttp.peticion("POST", "/auth/cierre-sesion");
    }

    obtenerSesion() {
        return this.clienteHttp.peticion("GET", "/auth/sesion");
    }

    obtenerUsuarios() {
        return this.clienteHttp.peticion("GET", "/usuarios");
    }

    numeroUsuarios() {
        return this.clienteHttp.peticion("GET", "/usuarios/numero");
    }

    usuarioActivo(email) {
        return this.clienteHttp.peticion("GET", `/usuarios/${encodeURIComponent(email)}/activo`);
    }

    eliminarUsuario(email) {
        return this.clienteHttp.peticion("DELETE", `/usuarios/${encodeURIComponent(email)}`);
    }

    editarDatos(email, nick, contrasena) {
        const cuerpo = { email, nick };
        if (contrasena) {
            cuerpo.contrasena = contrasena;
        }
        return this.clienteHttp.peticion("PATCH", "/usuarios/me", cuerpo);
    }

    asignarAdministrador(email) {
        return this.clienteHttp.peticion("POST", `/usuarios/${encodeURIComponent(email)}/profesor`);
    }

    solicitarRecuperacion(email) {
        return this.clienteHttp.peticion("POST", "/auth/recuperacion", { email });
    }

    restablecerContrasena(token, contrasena) {
        return this.clienteHttp.peticion("POST", "/auth/nueva-contrasena", { token, contrasena });
    }

    confirmarCuenta(token) {
        return this.clienteHttp.peticion("POST", "/auth/confirmar", { token });
    }

    reenviarConfirmacion(email) {
        return this.clienteHttp.peticion("POST", "/auth/reenviar-confirmacion", { email });
    }

    listarAsignaturas(nombre) {
        const ruta = nombre ? `/asignaturas?nombre=${encodeURIComponent(nombre)}` : "/asignaturas";
        return this.clienteHttp.peticion("GET", ruta);
    }

    obtenerMatricula(nombre) {
        const ruta = nombre ? `/matricula?nombre=${encodeURIComponent(nombre)}` : "/matricula";
        return this.clienteHttp.peticion("GET", ruta);
    }

    guardarMatricula(asignaturas) {
        return this.clienteHttp.peticion("PUT", "/matricula", { asignaturas });
    }

    obtenerExpediente() {
        return this.clienteHttp.peticion("GET", "/expediente");
    }

    guardarExpediente(calificaciones, intensificacion) {
        const cuerpo = { calificaciones };
        if (intensificacion !== undefined) {
            cuerpo.intensificacion = intensificacion;
        }
        return this.clienteHttp.peticion("PUT", "/expediente", cuerpo);
    }

    obtenerMarcas(anio, mes) {
        return this.clienteHttp.peticion("GET", `/agenda/marcas?anio=${anio}&mes=${mes}`);
    }

    obtenerMarcasRango(anio, mes, cantidad) {
        return this.clienteHttp.peticion(
            "GET",
            `/agenda/marcas-rango?anio=${anio}&mes=${mes}&cantidad=${cantidad}`,
        );
    }

    crearEvento({ codigo, tipo, fecha, hora, lugar }) {
        const cuerpo = { codigo, tipo, fecha, hora };
        if (lugar) {
            cuerpo.lugar = lugar;
        }
        return this.clienteHttp.peticion("POST", "/eventos", cuerpo);
    }

    actualizarEvento(eventoId, { codigo, tipo, fecha, hora, lugar }) {
        const cuerpo = { codigo, tipo, fecha, hora };
        if (lugar) {
            cuerpo.lugar = lugar;
        } else {
            cuerpo.lugar = null;
        }
        return this.clienteHttp.peticion(
            "PUT",
            `/eventos/${encodeURIComponent(eventoId)}`,
            cuerpo,
        );
    }

    eliminarEvento(eventoId) {
        return this.clienteHttp.peticion("DELETE", `/eventos/${encodeURIComponent(eventoId)}`);
    }
}
