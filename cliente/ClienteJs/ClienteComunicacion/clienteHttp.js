class ClienteHttp {
    constructor(urlBase = "/api") {
        this.urlBase = urlBase;
    }

    async peticion(metodo, ruta, cuerpo) {
        const opciones = {
            method: metodo,
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
        };
        if (cuerpo !== undefined) {
            opciones.body = JSON.stringify(cuerpo);
        }

        const respuesta = await fetch(this.urlBase + ruta, opciones);
        if (!respuesta.ok) {
            const error = await respuesta.json().catch(() => ({}));
            throw new ErrorApi(respuesta.status, this.mensajeError(respuesta.status, error.detail));
        }
        return respuesta.status === 204 ? null : respuesta.json();
    }

    mensajeError(estado, detalle) {
        if (typeof detalle === "string") {
            return detalle;
        }
        if (estado === 422) {
            return "Revisa los datos introducidos";
        }
        return `Error ${estado}`;
    }
}
