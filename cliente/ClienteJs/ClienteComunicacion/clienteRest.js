class ClienteRest {
    constructor(clienteHttp) {
        this.clienteHttp = clienteHttp;
    }

    registrar(email, nick, contrasena) {
        return this.clienteHttp.peticion("POST", "/auth/registro", { email, nick, contrasena });
    }

    iniciarSesion(email, contrasena) {
        return this.clienteHttp.peticion("POST", "/auth/inicio-sesion", { email, contrasena });
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

    solicitarRecuperacion(email) {
        return this.clienteHttp.peticion("POST", "/auth/recuperacion", { email });
    }

    restablecerContrasena(token, contrasena) {
        return this.clienteHttp.peticion("POST", "/auth/nueva-contrasena", { token, contrasena });
    }
}
