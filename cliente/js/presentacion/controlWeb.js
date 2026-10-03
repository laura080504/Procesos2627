class ControlWeb {
    constructor(clienteRest) {
        this.rest = clienteRest;
        this.campoNick = document.getElementById("nick");
        this.mensaje = document.getElementById("mensaje");
        this.lista = document.getElementById("listaUsuarios");
        this.numeroUsuarios = document.getElementById("numeroUsuarios");

        document.getElementById("botonAgregar").onclick = () => this.agregarUsuario();
        document.getElementById("botonRefrescar").onclick = () => this.refrescarUsuarios();
    }

    mostrarMensaje(texto, esError = false) {
        this.mensaje.textContent = texto;
        this.mensaje.className = esError ? "error" : "";
    }

    async refrescarUsuarios() {
        const usuarios = await this.rest.obtenerUsuarios();
        this.lista.innerHTML = "";
        usuarios.forEach((usuario) => {
            const elemento = document.createElement("li");
            elemento.textContent = `${usuario.nick} (${usuario.rol}, ${usuario.estado}) `;
            const boton = document.createElement("button");
            boton.textContent = "Eliminar";
            boton.onclick = () => this.eliminarUsuario(usuario.nick);
            elemento.appendChild(boton);
            this.lista.appendChild(elemento);
        });
        this.numeroUsuarios.textContent = usuarios.length;
    }

    async agregarUsuario() {
        const nick = this.campoNick.value.trim();
        if (!nick) {
            return this.mostrarMensaje("Introduce un nick", true);
        }
        try {
            await this.rest.agregarUsuario(nick);
            this.mostrarMensaje(`Usuario ${nick} agregado`);
            this.campoNick.value = "";
            await this.refrescarUsuarios();
        } catch (error) {
            this.mostrarMensaje(error.message, true);
        }
    }

    async eliminarUsuario(nick) {
        try {
            await this.rest.eliminarUsuario(nick);
            await this.refrescarUsuarios();
        } catch (error) {
            this.mostrarMensaje(error.message, true);
        }
    }
}
