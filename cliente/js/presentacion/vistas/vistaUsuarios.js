class VistaUsuarios {
    constructor({ alEliminar, alRefrescar }) {
        this.seccion = document.getElementById("vistaUsuarios");
        this.lista = document.getElementById("listaUsuarios");
        this.numeroUsuarios = document.getElementById("numeroUsuarios");
        this.alEliminar = alEliminar;
        this.textos = TEXTOS.es;
        this.ultimos = [];
        this.emailActual = "";
        document.getElementById("botonRefrescar").addEventListener("click", alRefrescar);
    }

    aplicarTextos(textos) {
        this.textos = textos;
        aplicarTextos(this.seccion, textos);
        if (!this.seccion.hidden) {
            this.pintar(this.ultimos, this.emailActual);
        }
    }

    mostrar() {
        this.seccion.hidden = false;
    }

    ocultar() {
        this.seccion.hidden = true;
        this.lista.innerHTML = "";
    }

    pintar(usuarios, emailActual) {
        this.ultimos = usuarios;
        this.emailActual = emailActual;
        this.lista.innerHTML = "";
        usuarios.forEach((usuario) => {
            const elemento = document.createElement("li");
            const texto = document.createElement("span");
            texto.textContent = `${usuario.nick} · ${usuario.email}`;

            const boton = document.createElement("button");
            boton.type = "button";
            boton.textContent = usuario.email === emailActual ? this.textos.eliminarCuenta : this.textos.eliminar;
            boton.addEventListener("click", () => this.alEliminar(usuario.email));

            elemento.append(texto, boton);
            this.lista.appendChild(elemento);
        });
        this.numeroUsuarios.textContent = usuarios.length;
    }
}
