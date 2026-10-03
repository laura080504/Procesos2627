class ClienteHttp {
    constructor(urlBase = "/api") {
        this.urlBase = urlBase;
    }

    async peticion(metodo, ruta, cuerpo) {
        const opciones = { method: metodo, headers: { "Content-Type": "application/json" } };
        if (cuerpo !== undefined) {
            opciones.body = JSON.stringify(cuerpo);
        }

        const respuesta = await fetch(this.urlBase + ruta, opciones);
        if (!respuesta.ok) {
            const error = await respuesta.json().catch(() => ({}));
            throw new Error(typeof error.detail === "string" ? error.detail : `Error ${respuesta.status}`);
        }
        return respuesta.status === 204 ? null : respuesta.json();
    }
}
