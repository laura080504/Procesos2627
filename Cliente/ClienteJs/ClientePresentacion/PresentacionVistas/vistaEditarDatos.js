class VistaEditarDatos {
    constructor({ alGuardar, alVolver, alNoCoinciden, alAsignarRol }) {
        this.seccion = document.getElementById("vistaEditarDatos");
        this.formulario = document.getElementById("formularioEditarDatos");
        this.rol = document.getElementById("rolEditar");
        this.resumen = document.getElementById("resumenEditarAlumno");
        this.campoAdmin = document.getElementById("campoHacerAdmin");
        this.casillaAdmin = document.getElementById("hacerAdministrador");
        this.panelSecretaria = document.getElementById("panelSecretariaEditar");
        this.campoDelegado = document.getElementById("campoDelegadoEditar");
        this.casillaDelegado = document.getElementById("casillaDelegadoEditar");
        this.botonAsignarRol = document.getElementById("botonAsignarRolEditar");
        this.listaMatricula = document.getElementById("listaMatriculaSecretaria");
        this.botonAnadirAsignatura = document.getElementById("botonAnadirAsignaturaSecretaria");
        this.camposContrasena = document.getElementById("camposContrasenaEditar");
        this.botonGuardar = this.formulario.querySelector("button[type='submit']");
        this.alNoCoinciden = alNoCoinciden;
        this.alAsignarRol = alAsignarRol;
        this.usuario = null;
        this.opciones = { propio: true };
        this.catalogoAsignaturas = [];
        this.gruposMatricula = typeof GRUPOS_MATRICULA !== "undefined" ? GRUPOS_MATRICULA : [];
        this.textos = typeof TEXTOS !== "undefined" ? TEXTOS.es : {};
        this.formulario.addEventListener("submit", (evento) => {
            evento.preventDefault();
            if (this.opciones.modoSecretaria) {
                const datos = new FormData(this.formulario);
                const puedeDelegado = !this.campoDelegado?.hidden;
                alGuardar({
                    propio: false,
                    modoSecretaria: true,
                    email: this.usuario.email,
                    nick: datos.get("nick").trim(),
                    emailNuevo: datos.get("email").trim(),
                    delegado: puedeDelegado ? Boolean(this.casillaDelegado?.checked) : false,
                    tocarDelegado: puedeDelegado,
                    asignaturas: this.leerMatricula(),
                });
                return;
            }
            if (!this.opciones.propio) {
                alGuardar({ propio: false, hacerAdmin: this.casillaAdmin.checked });
                return;
            }
            const datos = new FormData(this.formulario);
            const contrasena = (datos.get("contrasena") || "").trim();
            const confirmar = (datos.get("confirmar") || "").trim();
            if (contrasena !== confirmar) {
                this.alNoCoinciden();
                return;
            }
            alGuardar({
                propio: true,
                email: datos.get("email").trim(),
                nick: datos.get("nick").trim(),
                contrasena,
            });
        });
        document.getElementById("botonVolverEditar").addEventListener("click", () => alVolver());
        this.formulario.querySelectorAll(".ver-contrasena").forEach((boton) => {
            boton.addEventListener("click", () => this.alternarContrasena(boton));
        });
        if (this.botonAsignarRol) {
            this.botonAsignarRol.addEventListener("click", () => {
                if (this.usuario && this.alAsignarRol) {
                    this.alAsignarRol(this.usuario.email);
                }
            });
        }
        if (this.botonAnadirAsignatura) {
            this.botonAnadirAsignatura.addEventListener("click", () => this.anadirFilaMatricula());
        }
    }

    aplicarTextos(textos) {
        this.textos = textos;
        aplicarTextos(this.seccion, textos);
        this.actualizarEtiquetas();
        if (!this.seccion.hidden && this.usuario) {
            this.mostrar(this.usuario, this.opciones, this.opciones.matricula);
        }
    }

    alternarContrasena(boton) {
        const campo = boton.closest(".linea").querySelector("input");
        campo.type = campo.type === "password" ? "text" : "password";
        this.actualizarEtiquetas();
    }

    actualizarEtiquetas() {
        if (!this.textos) {
            return;
        }
        this.formulario.querySelectorAll(".ver-contrasena").forEach((boton) => {
            const visible = boton.closest(".linea").querySelector("input").type === "text";
            boton.setAttribute("aria-label", visible ? this.textos.ocultarContrasena : this.textos.verContrasena);
        });
    }

    cargarCatalogo(asignaturas) {
        this.catalogoAsignaturas = asignaturas || [];
    }

    mostrar(usuario, opciones = { propio: true }, matricula = null) {
        this.usuario = usuario;
        this.opciones = { ...opciones, matricula };
        this.formulario.reset();
        this.formulario.email.value = usuario.email;
        this.formulario.nick.value = usuario.nick;
        const propio = Boolean(opciones.propio);
        const modoSecretaria = Boolean(opciones.modoSecretaria);
        const puedeAsignar = Boolean(opciones.puedeAsignarProfesor);
        // Email fijo en edición de secretaría: la matrícula queda ligada a ese correo.
        this.formulario.email.readOnly = !propio || modoSecretaria;
        this.formulario.nick.readOnly = !propio && !modoSecretaria;
        this.camposContrasena.hidden = !propio;
        this.campoAdmin.hidden = !puedeAsignar || modoSecretaria;
        this.casillaAdmin.checked = false;
        this.casillaAdmin.disabled = !puedeAsignar;
        if (this.panelSecretaria) {
            this.panelSecretaria.hidden = !modoSecretaria;
        }
        if (this.resumen) {
            this.resumen.hidden = !modoSecretaria;
            if (modoSecretaria) {
                const curso = usuario.curso
                    ? etiquetaCursoCorto(usuario.curso, this.textos)
                    : this.textos.sinCursoAsignado;
                this.resumen.textContent = [
                    `${this.textos.etiquetaRol}: ${this.textos.rolUsuario}`,
                    `${this.textos.filtrarPorCurso}: ${curso}`,
                    usuario.delegado_curso
                        ? `${this.textos.etiquetaDelegado}: ${etiquetaCursoCorto(usuario.delegado_curso, this.textos)}`
                        : null,
                ].filter(Boolean).join(" · ");
            }
        }
        if (modoSecretaria && this.campoDelegado && this.casillaDelegado) {
            const esDelegado = Boolean(usuario.delegado_curso);
            const tieneCurso = Boolean(usuario.curso);
            const cursoOcupado = Boolean(opciones.delegadoCursoOcupado) && !esDelegado;
            this.campoDelegado.hidden = !tieneCurso || cursoOcupado;
            this.casillaDelegado.checked = esDelegado;
        }
        if (modoSecretaria) {
            const filas = (matricula?.asignaturas || []).map((asignatura) => ({
                codigo: asignatura.codigo,
                grupo: asignatura.grupo,
            }));
            this.pintarMatricula(filas.length ? filas : [{ codigo: "", grupo: "" }]);
        }
        this.rol.hidden = true;
        this.rol.textContent = "";
        this.botonGuardar.hidden = !propio && !puedeAsignar && !modoSecretaria;
        this.formulario.querySelectorAll("input[name='contrasena'], input[name='confirmar']").forEach((campo) => {
            campo.type = "password";
        });
        this.actualizarEtiquetas();
        this.seccion.hidden = false;
    }

    pintarMatricula(filas) {
        if (!this.listaMatricula) {
            return;
        }
        this.listaMatricula.replaceChildren();
        filas.forEach((fila) => this.anadirFilaMatricula(fila.codigo, fila.grupo));
    }

    anadirFilaMatricula(codigo = "", grupo = "") {
        if (!this.listaMatricula) {
            return;
        }
        const fila = document.createElement("div");
        fila.className = "fila-matricula";
        const combo = document.createElement("div");
        combo.className = "combo-asignatura";
        const buscar = document.createElement("input");
        buscar.type = "text";
        buscar.className = "buscar-asignatura";
        buscar.autocomplete = "off";
        buscar.placeholder = this.textos.elegirAsignatura || "Buscar…";
        const codigoOculto = document.createElement("input");
        codigoOculto.type = "hidden";
        codigoOculto.className = "codigo-matricula";
        const sugerencias = document.createElement("ul");
        sugerencias.className = "sugerencias-asignatura";
        sugerencias.hidden = true;
        const ingles = this.textos.codigo === "EN";
        const etiquetaDe = (asignatura) =>
            `${asignatura.codigo} · ${ingles ? asignatura.nombre_ingles : asignatura.nombre}`;
        if (codigo) {
            const elegida = this.catalogoAsignaturas.find((asignatura) => asignatura.codigo === codigo);
            codigoOculto.value = codigo;
            buscar.value = elegida ? etiquetaDe(elegida) : codigo;
        }
        const cerrar = () => {
            sugerencias.hidden = true;
            sugerencias.replaceChildren();
        };
        const elegir = (asignatura) => {
            codigoOculto.value = asignatura.codigo;
            buscar.value = etiquetaDe(asignatura);
            cerrar();
        };
        buscar.addEventListener("input", () => {
            codigoOculto.value = "";
            const coincidencias = (typeof filtrarAsignaturas === "function"
                ? filtrarAsignaturas(this.catalogoAsignaturas, buscar.value, ingles)
                : this.catalogoAsignaturas
            ).slice(0, 12);
            sugerencias.replaceChildren();
            coincidencias.forEach((asignatura) => {
                const item = document.createElement("li");
                const boton = document.createElement("button");
                boton.type = "button";
                boton.textContent = etiquetaDe(asignatura);
                boton.addEventListener("mousedown", (evento) => {
                    evento.preventDefault();
                    elegir(asignatura);
                });
                item.append(boton);
                sugerencias.append(item);
            });
            sugerencias.hidden = !coincidencias.length;
        });
        combo.append(buscar, codigoOculto, sugerencias);
        const grupoSelect = document.createElement("select");
        grupoSelect.className = "grupo-matricula";
        const vacio = document.createElement("option");
        vacio.value = "";
        vacio.textContent = this.textos.elegirGrupo || "Grupo";
        grupoSelect.append(vacio);
        this.gruposMatricula.forEach((opcionGrupo) => {
            const opcion = document.createElement("option");
            opcion.value = opcionGrupo.valor;
            opcion.textContent = opcionGrupo.etiqueta;
            grupoSelect.append(opcion);
        });
        const grupoNormalizado = typeof normalizarGrupoCampus === "function"
            ? normalizarGrupoCampus(grupo)
            : (grupo || "");
        if (grupoNormalizado) {
            grupoSelect.value = grupoNormalizado;
        }
        const quitar = document.createElement("button");
        quitar.type = "button";
        quitar.className = "quitar-matricula";
        quitar.textContent = this.textos.quitarAsignaturaMatricula || "Quitar";
        quitar.addEventListener("click", () => {
            fila.remove();
            if (!this.listaMatricula.children.length) {
                this.anadirFilaMatricula();
            }
        });
        fila.append(combo, grupoSelect, quitar);
        this.listaMatricula.append(fila);
    }

    leerMatricula() {
        if (!this.listaMatricula) {
            return [];
        }
        return [...this.listaMatricula.querySelectorAll(".fila-matricula")]
            .map((fila) => ({
                codigo: fila.querySelector(".codigo-matricula")?.value || "",
                grupo: (fila.querySelector(".grupo-matricula")?.value || "").trim(),
            }))
            .filter((item) => item.codigo && item.grupo);
    }

    ocultar() {
        this.seccion.hidden = true;
        this.usuario = null;
        this.formulario.reset();
        this.formulario.email.readOnly = false;
        this.formulario.nick.readOnly = false;
        this.camposContrasena.hidden = false;
        this.campoAdmin.hidden = true;
        if (this.panelSecretaria) {
            this.panelSecretaria.hidden = true;
        }
        if (this.campoDelegado) {
            this.campoDelegado.hidden = true;
        }
        if (this.resumen) {
            this.resumen.hidden = true;
        }
        this.rol.hidden = true;
        this.botonGuardar.hidden = false;
        this.formulario.querySelectorAll("input[name='contrasena'], input[name='confirmar']").forEach((campo) => {
            campo.type = "password";
        });
        this.actualizarEtiquetas();
    }
}
