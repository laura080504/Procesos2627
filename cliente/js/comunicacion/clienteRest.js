class ClienteRest {
    constructor(clienteHttp) {
        this.clienteHttp = clienteHttp;
    }

    agregarUsuario(nick) {
        return this.clienteHttp.peticion("POST", "/usuarios", { nick });
    }

    obtenerUsuarios() {
        return this.clienteHttp.peticion("GET", "/usuarios");
    }

    numeroUsuarios() {
        return this.clienteHttp.peticion("GET", "/usuarios/numero");
    }

    usuarioActivo(nick) {
        return this.clienteHttp.peticion("GET", `/usuarios/${encodeURIComponent(nick)}/activo`);
    }

    eliminarUsuario(nick) {
        return this.clienteHttp.peticion("DELETE", `/usuarios/${encodeURIComponent(nick)}`);
    }
}
