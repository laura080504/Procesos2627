class ClienteAvisos {
    constructor() {
        this.socket = null;
    }

    conectar(alMensaje) {
        this.desconectar();
        const protocolo = location.protocol === "https:" ? "wss" : "ws";
        this.socket = new WebSocket(`${protocolo}://${location.host}/ws`);
        this.socket.addEventListener("message", (evento) => alMensaje(evento));
    }

    desconectar() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }
}
