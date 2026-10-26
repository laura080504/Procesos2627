class VistaUsuarios {
    constructor({ alEliminar, alRefrescar, alEditar, alEditarUsuario, alVolverAgenda }) {
        this.seccion = document.getElementById("vistaUsuarios");
        this.vistaAdministrador = document.getElementById("vistaAdministrador");
        this.vistaCuenta = document.getElementById("vistaCuenta");
        this.cuentaActual = document.getElementById("cuentaActual");
        this.contadorUsuarios = document.getElementById("contadorUsuarios");
        this.lista = document.getElementById("listaUsuarios");
        this.numeroUsuarios = document.getElementById("numeroUsuarios");
        this.botonRefrescar = document.getElementById("botonRefrescar");
        this.rolVisor = "usuario";
        this.alEliminar = alEliminar;
        this.alEditarUsuario = alEditarUsuario;
        this.textos = TEXTOS.es;
        this.ultimos = [];
        this.emailActual = "";
        this.matricula = null;
        document.getElementById("botonRefrescar").addEventListener("click", alRefrescar);
        const eliminarCuenta = () => this.alEliminar(this.emailActual);
        document.getElementById("botonEliminarCuenta").addEventListener("click", eliminarCuenta);
        document.getElementById("botonEliminarSesion").addEventListener("click", eliminarCuenta);
        document.getElementById("botonEditarDatos").addEventListener("click", alEditar);
        document.getElementById("botonEditarCuenta").addEventListener("click", alEditar);
        document.getElementById("botonVolverAgenda").addEventListener("click", alVolverAgenda);
    }

    aplicarTextos(textos) {
        this.textos = textos;
        aplicarTextos(this.seccion, textos);
        if (!this.seccion.hidden) {
            this.pintar(this.ultimos, this.emailActual, this.rolVisor, this.matricula);
        }
    }

    mostrar() {
        this.seccion.hidden = false;
    }

    ocultar() {
        this.seccion.hidden = true;
        this.lista.innerHTML = "";
    }

    pintar(usuarios, emailActual, rolVisor = "usuario", matricula = null) {
        this.ultimos = usuarios;
        this.emailActual = emailActual;
        this.rolVisor = rolVisor;
        this.matricula = matricula;
        const esGestion = rolVisor === "profesor" || rolVisor === "superadministrador";
        this.vistaAdministrador.hidden = !esGestion;
        this.vistaCuenta.hidden = esGestion;
        document.getElementById("tituloVistaUsuarios").textContent = esGestion
            ? this.textos.gestionUsuarios
            : this.textos.perfilEstudiante;
        this.contadorUsuarios.hidden = !esGestion;
        document.getElementById("botonEliminarSesion").hidden = esGestion;
        this.lista.innerHTML = "";
        if (!esGestion) {
            const usuario = usuarios[0];
            if (usuario) {
                pintarDatosUsuario(this.cuentaActual, usuario, this.textos);
            } else {
                this.cuentaActual.replaceChildren();
            }
            this.pintarCurso(matricula);
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
            if (usuario.estado !== "eliminado" && usuario.rol === "usuario" && this.rolVisor === "superadministrador") {
                const editar = document.createElement("button");
                editar.type = "button";
                editar.textContent = this.textos.editar;
                editar.addEventListener("click", () => this.alEditarUsuario(usuario));
                acciones.append(editar);
            }
            if (usuario.estado !== "eliminado" && puedeEliminarCuenta(this.rolVisor, usuario)) {
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

    pintarCurso(matricula) {
        const resumen = document.getElementById("resumenCurso");
        const curso = document.getElementById("cursoAlumno");
        const grafico = document.getElementById("graficoCurso");
        const leyenda = document.getElementById("leyendaCurso");
        if (!matricula || !matricula.tramos.length) {
            resumen.hidden = true;
            grafico.replaceChildren();
            leyenda.replaceChildren();
            return;
        }
        resumen.hidden = false;
        const nombres = {
            primero: this.textos.cursoPrimero,
            segundo: this.textos.cursoSegundo,
            tercero: this.textos.cursoTercero,
            cuarto: this.textos.cursoCuarto,
        };
        curso.textContent = matricula.curso
            ? `${this.textos.cursoAlumno}: ${nombres[matricula.curso]}`
            : this.textos.sinCurso;
        document.getElementById("creditosAprobados").textContent =
            `${this.textos.creditosAprobados}: ${matricula.creditos_aprobados}`;
        const media = document.getElementById("mediaCarrera");
        media.textContent = matricula.media === null || matricula.media === undefined
            ? `${this.textos.mediaCarrera}: ${this.textos.sinMedia}`
            : `${this.textos.mediaCarrera}: ${formatearMedia(matricula.media, this.textos.codigo)}`;
        const colores = {
            primero: "#9d1830",
            segundo: "#c45c6c",
            tercero: "#e4b4bc",
            cuarto: "#5c101c",
        };
        grafico.replaceChildren();
        leyenda.replaceChildren();
        if (matricula.tramos.length === 1) {
            const circulo = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circulo.setAttribute("cx", "21");
            circulo.setAttribute("cy", "21");
            circulo.setAttribute("r", "16");
            circulo.setAttribute("fill", colores[matricula.tramos[0].curso]);
            grafico.append(circulo);
        } else {
            let angulo = 0;
            matricula.tramos.forEach((tramo) => {
                const siguiente = angulo + (tramo.porcentaje / 100) * Math.PI * 2;
                grafico.append(sectorTarta(angulo, siguiente, colores[tramo.curso]));
                angulo = siguiente;
            });
        }
        matricula.tramos.forEach((tramo) => {
            const fila = document.createElement("li");
            const muestra = document.createElement("span");
            muestra.className = "muestra-curso";
            muestra.style.background = colores[tramo.curso];
            fila.append(muestra, document.createTextNode(`${nombres[tramo.curso]} ${tramo.porcentaje}%`));
            leyenda.append(fila);
        });
    }
}

function formatearMedia(media, codigo) {
    return Number(media).toLocaleString(codigo === "EN" ? "en-GB" : "es-ES", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function puedeEliminarCuenta(rolVisor, usuario) {
    if (usuario.rol === "superadministrador") {
        return false;
    }
    if (rolVisor === "superadministrador") {
        return usuario.rol === "usuario" || usuario.rol === "profesor";
    }
    return rolVisor === "profesor" && usuario.rol === "usuario";
}

function sectorTarta(inicio, fin, color) {
    const radio = 16;
    const centro = 21;
    const x1 = centro + radio * Math.cos(inicio - Math.PI / 2);
    const y1 = centro + radio * Math.sin(inicio - Math.PI / 2);
    const x2 = centro + radio * Math.cos(fin - Math.PI / 2);
    const y2 = centro + radio * Math.sin(fin - Math.PI / 2);
    const grande = fin - inicio > Math.PI ? 1 : 0;
    const camino = document.createElementNS("http://www.w3.org/2000/svg", "path");
    camino.setAttribute("d", `M ${centro} ${centro} L ${x1} ${y1} A ${radio} ${radio} 0 ${grande} 1 ${x2} ${y2} Z`);
    camino.setAttribute("fill", color);
    return camino;
}
