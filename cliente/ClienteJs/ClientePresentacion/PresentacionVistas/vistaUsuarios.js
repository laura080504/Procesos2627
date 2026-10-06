class VistaUsuarios {
    constructor({ alEliminar, alRefrescar }) {
        this.seccion = document.getElementById("vistaUsuarios");
        this.vistaAdministrador = document.getElementById("vistaAdministrador");
        this.vistaCuenta = document.getElementById("vistaCuenta");
        this.cuentaActual = document.getElementById("cuentaActual");
        this.lista = document.getElementById("listaUsuarios");
        this.numeroUsuarios = document.getElementById("numeroUsuarios");
        this.botonRefrescar = document.getElementById("botonRefrescar");
        this.esAdministrador = false;
        this.alEliminar = alEliminar;
        this.textos = TEXTOS.es;
        this.ultimos = [];
        this.emailActual = "";
        document.getElementById("botonRefrescar").addEventListener("click", alRefrescar);
        const eliminarCuenta = () => this.alEliminar(this.emailActual);
        document.getElementById("botonEliminarCuenta").addEventListener("click", eliminarCuenta);
        document.getElementById("botonEliminarSesion").addEventListener("click", eliminarCuenta);
    }

    aplicarTextos(textos) {
        this.textos = textos;
        aplicarTextos(this.seccion, textos);
        if (!this.seccion.hidden) {
            this.pintar(this.ultimos, this.emailActual, this.esAdministrador);
        }
    }

    mostrar() {
        this.seccion.hidden = false;
    }

    ocultar() {
        this.seccion.hidden = true;
        this.lista.innerHTML = "";
    }

    pintar(usuarios, emailActual, esAdministrador = false) {
        this.ultimos = usuarios;
        this.emailActual = emailActual;
        this.esAdministrador = esAdministrador;
        this.vistaAdministrador.hidden = !esAdministrador;
        this.vistaCuenta.hidden = esAdministrador;
        this.lista.innerHTML = "";
        if (!esAdministrador) {
            const usuario = usuarios[0];
            this.cuentaActual.textContent = usuario ? `${usuario.nick} (${usuario.email})` : "";
            return;
        }
        usuarios.forEach((usuario) => {
            const elemento = document.createElement("li");
            const texto = document.createElement("span");
            texto.textContent = `${usuario.nick} · ${usuario.email}`;

            const boton = document.createElement("button");
            boton.type = "button";
            boton.textContent = this.textos.eliminar;
            boton.addEventListener("click", () => this.alEliminar(usuario.email));

            elemento.append(texto, boton);
            this.lista.appendChild(elemento);
        });
        this.numeroUsuarios.textContent = usuarios.length;
    }
}
