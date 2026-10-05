class ErrorApi extends Error {
    constructor(estado, mensaje) {
        super(mensaje);
        this.estado = estado;
    }
}
