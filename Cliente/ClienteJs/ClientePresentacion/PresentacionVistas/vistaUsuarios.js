class VistaUsuarios {
    constructor({ alEliminar, alRefrescar, alEditar, alEditarUsuario }) {
        this.seccion = document.getElementById("vistaUsuarios");
        this.vistaAdministrador = document.getElementById("vistaAdministrador");
        this.vistaCuenta = document.getElementById("vistaCuenta");
        this.cuentaActual = document.getElementById("cuentaActual");
        this.contadorUsuarios = document.getElementById("contadorUsuarios");
        this.lista = document.getElementById("listaUsuarios");
        this.numeroUsuarios = document.getElementById("numeroUsuarios");
        this.botonRefrescar = document.getElementById("botonRefrescar");
        this.esAdministrador = false;
        this.alEliminar = alEliminar;
        this.alEditarUsuario = alEditarUsuario;
        this.textos = TEXTOS.es;
        this.ultimos = [];
        this.emailActual = "";
        document.getElementById("botonRefrescar").addEventListener("click", alRefrescar);
        const eliminarCuenta = () => this.alEliminar(this.emailActual);
        document.getElementById("botonEliminarCuenta").addEventListener("click", eliminarCuenta);
        document.getElementById("botonEliminarSesion").addEventListener("click", eliminarCuenta);
        document.getElementById("botonEditarDatos").addEventListener("click", alEditar);
        document.getElementById("botonEditarCuenta").addEventListener("click", alEditar);
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
        this.contadorUsuarios.hidden = !esAdministrador;
        this.lista.innerHTML = "";
        if (!esAdministrador) {
            const usuario = usuarios[0];
            if (usuario) {
                pintarDatosUsuario(this.cuentaActual, usuario, this.textos);
            } else {
                this.cuentaActual.replaceChildren();
            }
            return;
        }
        usuarios.forEach((usuario) => {
            const elemento = document.createElement("li");
            const texto = document.createElement("span");
            texto.className = "usuario-ficha";
            pintarDatosUsuario(texto, usuario, this.textos);
            elemento.append(texto);
            const acciones = document.createElement("span");
            acciones.className = "acciones-usuario";
            if (usuario.estado !== "eliminado") {
                const editar = document.createElement("button");
                editar.type = "button";
                editar.textContent = this.textos.editar;
                editar.addEventListener("click", () => this.alEditarUsuario(usuario));
                acciones.append(editar);
                const boton = document.createElement("button");
                boton.type = "button";
                boton.textContent = this.textos.eliminar;
                boton.addEventListener("click", () => this.alEliminar(usuario.email));
                acciones.append(boton);
            }
            if (acciones.childNodes.length) {
                elemento.append(acciones);
            }
            this.lista.appendChild(elemento);
        });
        this.numeroUsuarios.textContent = usuarios.length;
    }
}
