class VistaUsuarios {
    constructor({
        alEliminar,
        alRefrescar,
        alEditar,
        alEditarUsuario,
        alVolverAgenda,
        alCambiarPreferenciasAvisos,
        alCrearEvento,
        alGuardarMatricula,
        alAbrirHistorial,
        alGuardarHistorial,
    }) {
        this.seccion = document.getElementById("vistaUsuarios");
        this.vistaAdministrador = document.getElementById("vistaAdministrador");
        this.vistaCuenta = document.getElementById("vistaCuenta");
        this.cuentaActual = document.getElementById("cuentaActual");
        this.contadorUsuarios = document.getElementById("contadorUsuarios");
        this.lista = document.getElementById("listaUsuarios");
        this.numeroUsuarios = document.getElementById("numeroUsuarios");
        this.botonRefrescar = document.getElementById("botonRefrescar");
        this.preferenciasAvisos = document.getElementById("preferenciasAvisos");
        this.formularioEvento = document.getElementById("formularioEventoProfesor");
        this.formCrearEvento = document.getElementById("formCrearEvento");
        this.selectCodigoEvento = document.getElementById("codigoEvento");
        this.dialogoMatricula = document.getElementById("dialogoMatricula");
        this.dialogoResumenMatricula = document.getElementById("dialogoResumenMatricula");
        this.dialogoHistorial = document.getElementById("dialogoHistorial");
        this.listaMatriculaEditable = document.getElementById("listaMatriculaEditable");
        this.listaResumenMatricula = document.getElementById("listaResumenMatricula");
        this.listaHistorialCalificadas = document.getElementById("listaHistorialCalificadas");
        this.listaHistorialPendientes = document.getElementById("listaHistorialPendientes");
        this.resumenHistorial = document.getElementById("resumenHistorial");
        this.formMatricula = document.getElementById("formMatricula");
        this.formHistorial = document.getElementById("formHistorial");
        this.botonEditarMatricula = document.getElementById("botonEditarMatricula");
        this.botonVerMatricula = document.getElementById("botonVerMatricula");
        this.botonHistorial = document.getElementById("botonHistorial");
        this.rolVisor = "usuario";
        this.alEliminar = alEliminar;
        this.alEditarUsuario = alEditarUsuario;
        this.alCambiarPreferenciasAvisos = alCambiarPreferenciasAvisos;
        this.alCrearEvento = alCrearEvento;
        this.alGuardarMatricula = alGuardarMatricula;
        this.alAbrirHistorial = alAbrirHistorial;
        this.alGuardarHistorial = alGuardarHistorial;
        this.textos = TEXTOS.es;
        this.ultimos = [];
        this.emailActual = "";
        this.matricula = null;
        this.expediente = null;
        this.catalogoAsignaturas = [];
        this.gruposMatricula = GRUPOS_MATRICULA;
        document.getElementById("botonRefrescar").addEventListener("click", alRefrescar);
        const eliminarCuenta = () => this.alEliminar(this.emailActual);
        document.getElementById("botonEliminarCuenta").addEventListener("click", eliminarCuenta);
        document.getElementById("botonEliminarSesion").addEventListener("click", eliminarCuenta);
        document.getElementById("botonEditarDatos").addEventListener("click", alEditar);
        document.getElementById("botonEditarCuenta").addEventListener("click", alEditar);
        document.getElementById("botonVolverAgenda").addEventListener("click", alVolverAgenda);
        this.botonEditarMatricula.addEventListener("click", () => this.abrirEditorMatricula());
        this.botonVerMatricula.addEventListener("click", () => this.abrirResumenMatricula());
        this.botonHistorial.addEventListener("click", () => {
            if (this.alAbrirHistorial) {
                this.alAbrirHistorial();
            }
        });
        document.getElementById("botonEditarDesdeResumen").addEventListener("click", () => {
            this.cerrarResumenMatricula();
            this.abrirEditorMatricula();
        });
        document.getElementById("botonAnadirAsignaturaMatricula").addEventListener("click", () => {
            this.anadirFilaMatricula();
        });
        this.formMatricula.addEventListener("submit", (evento) => {
            if (evento.submitter && evento.submitter.value === "guardar") {
                evento.preventDefault();
                this.enviarMatricula();
            }
        });
        this.formHistorial.addEventListener("submit", (evento) => {
            if (evento.submitter && evento.submitter.value === "guardar") {
                evento.preventDefault();
                this.enviarHistorial();
            }
        });
        this.preferenciasAvisos.addEventListener("change", () => this.guardarPreferenciasAvisos());
        this.formCrearEvento.addEventListener("submit", (evento) => {
            evento.preventDefault();
            this.enviarEventoProfesor();
        });
    }

    aplicarTextos(textos) {
        this.textos = textos;
        aplicarTextos(this.seccion, textos);
        if (this.dialogoMatricula) {
            aplicarTextos(this.dialogoMatricula, textos);
        }
        if (this.dialogoResumenMatricula) {
            aplicarTextos(this.dialogoResumenMatricula, textos);
        }
        if (this.dialogoHistorial) {
            aplicarTextos(this.dialogoHistorial, textos);
        }
        if (!this.seccion.hidden) {
            this.pintar(this.ultimos, this.emailActual, this.rolVisor, this.matricula);
        }
    }

    esGestion(rol) {
        return rol === "profesor" || rol === "superadministrador";
    }

    preparar(rolVisor = "usuario") {
        this.rolVisor = rolVisor;
        const gestion = this.esGestion(rolVisor);
        this.vistaAdministrador.hidden = !gestion;
        this.vistaCuenta.hidden = gestion;
        this.formularioEvento.hidden = !gestion;
        this.botonRefrescar.hidden = !gestion;
        this.preferenciasAvisos.hidden = gestion;
        this.contadorUsuarios.hidden = !gestion;
        this.botonEditarMatricula.hidden = gestion;
        this.botonVerMatricula.hidden = gestion;
        this.botonHistorial.hidden = gestion;
        document.getElementById("botonEliminarSesion").hidden = gestion;
        document.getElementById("tituloVistaUsuarios").textContent = gestion
            ? this.textos.gestionUsuarios
            : this.textos.perfilEstudiante;
        if (!gestion) {
            this.lista.innerHTML = "";
        }
    }

    mostrar(rolVisor = this.rolVisor) {
        this.preparar(rolVisor);
        this.seccion.hidden = false;
    }

    ocultar() {
        this.seccion.hidden = true;
        this.vistaAdministrador.hidden = true;
        this.vistaCuenta.hidden = true;
        this.formularioEvento.hidden = true;
        this.botonRefrescar.hidden = true;
        this.lista.innerHTML = "";
    }

    pintar(usuarios, emailActual, rolVisor = "usuario", matricula = null) {
        this.ultimos = usuarios;
        this.emailActual = emailActual;
        this.matricula = matricula;
        this.preparar(rolVisor);
        this.lista.innerHTML = "";
        if (!this.esGestion(rolVisor)) {
            const usuario = usuarios[0];
            if (usuario) {
                this.pintarIdentidadEstudiante(usuario);
            } else {
                this.cuentaActual.replaceChildren();
            }
            this.pintarCurso(matricula);
            this.pintarPreferenciasAvisos();
            return;
        }
        if (!this.formularioEvento.hidden) {
            this.pintarSelectAsignaturas();
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

    pintarIdentidadEstudiante(usuario) {
        this.cuentaActual.replaceChildren();
        const nick = document.createElement("span");
        nick.className = "perfil-nick";
        nick.textContent = usuario.nick;
        const email = document.createElement("a");
        email.className = "perfil-email";
        email.href = `mailto:${usuario.email}`;
        email.textContent = usuario.email;
        this.cuentaActual.append(nick, email);
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
        const intensificacion = document.getElementById("intensificacionAlumno");
        intensificacion.textContent = `${this.textos.intensificacion}: ${etiquetaIntensificacion(matricula.intensificacion, this.textos)}`;
        document.getElementById("creditosAprobados").textContent =
            `${this.textos.creditosAprobados}: ${matricula.creditos_aprobados}`;
        const convalidados = document.getElementById("creditosConvalidados");
        const cuantosConvalidados = matricula.creditos_convalidados || 0;
        convalidados.textContent = `${this.textos.creditosConvalidados}: ${cuantosConvalidados}`;
        convalidados.hidden = cuantosConvalidados === 0;
        const media = document.getElementById("mediaCarrera");
        media.textContent = matricula.media === null || matricula.media === undefined
            ? `${this.textos.mediaCarrera}: ${this.textos.sinMedia}`
            : `${this.textos.mediaCarrera}: ${formatearMedia(matricula.media, this.textos.codigo)}`;
        const colores = {
            primero: "#f3c6ce",
            segundo: "#e08a98",
            tercero: "#c45c6c",
            cuarto: "#6b1424",
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

    pintarPreferenciasAvisos() {
        this.preferenciasAvisos.hidden = false;
        this.formularioEvento.hidden = true;
        const prefs = PreferenciasNotificaciones.leer();
        document.getElementById("avisoExamenes").checked = prefs.avisos.examenes;
        document.getElementById("avisoEntregas").checked = prefs.avisos.entregas;
        document.getElementById("avisoHorarioHoy").checked = prefs.avisos.horarioHoy;
        const valor = document.getElementById("antelacionValor");
        const unidad = document.getElementById("antelacionUnidad");
        unidad.value = prefs.antelacion.unidad;
        valor.value = String(prefs.antelacion.valor);
        valor.disabled = prefs.antelacion.unidad === "curso";
    }

    guardarPreferenciasAvisos() {
        const unidad = document.getElementById("antelacionUnidad").value;
        const valorInput = document.getElementById("antelacionValor");
        valorInput.disabled = unidad === "curso";
        const preferencias = PreferenciasNotificaciones.guardar({
            icono: "campana",
            antelacion: {
                valor: Number(valorInput.value),
                unidad,
            },
            avisos: {
                examenes: document.getElementById("avisoExamenes").checked,
                entregas: document.getElementById("avisoEntregas").checked,
                horarioHoy: document.getElementById("avisoHorarioHoy").checked,
            },
        });
        if (this.alCambiarPreferenciasAvisos) {
            this.alCambiarPreferenciasAvisos(preferencias);
        }
    }

    cargarCatalogoAsignaturas(asignaturas) {
        this.catalogoAsignaturas = asignaturas || [];
        if (!this.formularioEvento.hidden) {
            this.pintarSelectAsignaturas();
        }
    }

    pintarSelectAsignaturas() {
        const ingles = this.textos.codigo === "EN";
        const valor = this.selectCodigoEvento.value;
        this.selectCodigoEvento.replaceChildren();
        this.catalogoAsignaturas.forEach((asignatura) => {
            const opcion = document.createElement("option");
            opcion.value = asignatura.codigo;
            opcion.textContent = `${asignatura.codigo} · ${ingles ? asignatura.nombre_ingles : asignatura.nombre}`;
            this.selectCodigoEvento.append(opcion);
        });
        if (valor && [...this.selectCodigoEvento.options].some((opcion) => opcion.value === valor)) {
            this.selectCodigoEvento.value = valor;
        }
    }

    enviarEventoProfesor() {
        const datos = new FormData(this.formCrearEvento);
        const hora = String(datos.get("hora") || "").slice(0, 5);
        if (this.alCrearEvento) {
            this.alCrearEvento({
                codigo: String(datos.get("codigo") || ""),
                tipo: String(datos.get("tipo") || "entrega"),
                fecha: String(datos.get("fecha") || ""),
                hora,
                lugar: String(datos.get("lugar") || "").trim(),
            });
        }
    }

    limpiarFormularioEvento() {
        this.formCrearEvento.reset();
        document.getElementById("horaEvento").value = "23:59";
    }

    abrirEditorMatricula() {
        if (!this.dialogoMatricula) {
            return;
        }
        const filas = (this.matricula?.asignaturas || []).map((asignatura) => ({
            codigo: asignatura.codigo,
            grupo: normalizarGrupoCampus(asignatura.grupo),
        }));
        this.pintarEditorMatricula(filas.length ? filas : [{ codigo: "", grupo: "" }]);
        if (this.dialogoMatricula.open) {
            return;
        }
        try {
            this.dialogoMatricula.showModal();
        } catch {
            this.dialogoMatricula.setAttribute("open", "");
        }
    }

    abrirResumenMatricula() {
        if (!this.dialogoResumenMatricula) {
            return;
        }
        this.pintarResumenMatricula();
        if (this.dialogoResumenMatricula.open) {
            return;
        }
        try {
            this.dialogoResumenMatricula.showModal();
        } catch {
            this.dialogoResumenMatricula.setAttribute("open", "");
        }
    }

    pintarResumenMatricula() {
        this.listaResumenMatricula.replaceChildren();
        const asignaturas = this.matricula?.asignaturas || [];
        if (!asignaturas.length) {
            const vacio = document.createElement("li");
            vacio.className = "resumen-vacio";
            vacio.textContent = this.textos.matriculaSinAsignaturas;
            this.listaResumenMatricula.append(vacio);
            return;
        }
        const ingles = this.textos.codigo === "EN";
        asignaturas.forEach((asignatura) => {
            const item = document.createElement("li");
            const nombre = document.createElement("span");
            nombre.className = "resumen-nombre";
            const ficha = this.catalogoAsignaturas.find((a) => a.codigo === asignatura.codigo);
            const titulo = ficha
                ? `${ficha.codigo} · ${ingles ? ficha.nombre_ingles : ficha.nombre}`
                : `${asignatura.codigo} · ${ingles ? asignatura.nombre_ingles || asignatura.nombre : asignatura.nombre}`;
            nombre.textContent = titulo;
            const grupo = document.createElement("span");
            grupo.className = "resumen-grupo";
            grupo.textContent = etiquetaGrupoCampus(asignatura.grupo);
            item.append(nombre, grupo);
            this.listaResumenMatricula.append(item);
        });
    }

    pintarEditorMatricula(filas) {
        this.listaMatriculaEditable.replaceChildren();
        filas.forEach((fila) => this.anadirFilaMatricula(fila.codigo, fila.grupo));
    }

    anadirFilaMatricula(codigo = "", grupo = "") {
        const fila = document.createElement("div");
        fila.className = "fila-matricula";

        const combo = document.createElement("div");
        combo.className = "combo-asignatura";
        const buscar = document.createElement("input");
        buscar.type = "text";
        buscar.className = "buscar-asignatura";
        buscar.autocomplete = "off";
        buscar.placeholder = this.textos.elegirAsignatura;
        buscar.setAttribute("aria-label", this.textos.elegirAsignatura);
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

        const cerrarSugerencias = () => {
            sugerencias.hidden = true;
            sugerencias.replaceChildren();
        };

        const elegirAsignatura = (asignatura) => {
            codigoOculto.value = asignatura.codigo;
            buscar.value = etiquetaDe(asignatura);
            cerrarSugerencias();
        };

        const pintarSugerencias = (texto) => {
            const coincidencias = filtrarAsignaturas(this.catalogoAsignaturas, texto, ingles).slice(0, 12);
            sugerencias.replaceChildren();
            if (!coincidencias.length) {
                cerrarSugerencias();
                return;
            }
            coincidencias.forEach((asignatura) => {
                const item = document.createElement("li");
                const boton = document.createElement("button");
                boton.type = "button";
                boton.textContent = etiquetaDe(asignatura);
                boton.addEventListener("mousedown", (evento) => {
                    evento.preventDefault();
                    elegirAsignatura(asignatura);
                });
                item.append(boton);
                sugerencias.append(item);
            });
            sugerencias.hidden = false;
        };

        buscar.addEventListener("input", () => {
            codigoOculto.value = "";
            pintarSugerencias(buscar.value);
        });
        buscar.addEventListener("focus", () => pintarSugerencias(buscar.value));
        buscar.addEventListener("blur", () => {
            window.setTimeout(cerrarSugerencias, 120);
        });
        buscar.addEventListener("keydown", (evento) => {
            if (evento.key === "Escape") {
                cerrarSugerencias();
            }
        });

        combo.append(buscar, codigoOculto, sugerencias);

        const grupoSelect = document.createElement("select");
        grupoSelect.className = "grupo-matricula";
        grupoSelect.setAttribute("aria-label", this.textos.grupoMatricula);
        const vacio = document.createElement("option");
        vacio.value = "";
        vacio.textContent = this.textos.elegirGrupo;
        grupoSelect.append(vacio);
        this.gruposMatricula.forEach((opcionGrupo) => {
            const opcion = document.createElement("option");
            opcion.value = opcionGrupo.valor;
            opcion.textContent = opcionGrupo.etiqueta;
            grupoSelect.append(opcion);
        });
        const grupoNormalizado = normalizarGrupoCampus(grupo);
        if (grupoNormalizado) {
            grupoSelect.value = grupoNormalizado;
        }

        const quitar = document.createElement("button");
        quitar.type = "button";
        quitar.className = "quitar-matricula";
        quitar.textContent = this.textos.quitarAsignaturaMatricula;
        quitar.addEventListener("click", () => {
            fila.remove();
            if (!this.listaMatriculaEditable.children.length) {
                this.anadirFilaMatricula();
            }
        });

        fila.append(combo, grupoSelect, quitar);
        this.listaMatriculaEditable.append(fila);
    }

    leerMatriculaEditor() {
        return [...this.listaMatriculaEditable.querySelectorAll(".fila-matricula")]
            .map((fila) => ({
                codigo: fila.querySelector(".codigo-matricula")?.value || "",
                grupo: (fila.querySelector(".grupo-matricula")?.value || "").trim(),
            }))
            .filter((item) => item.codigo && item.grupo);
    }

    enviarMatricula() {
        if (this.alGuardarMatricula) {
            this.alGuardarMatricula(this.leerMatriculaEditor());
        }
    }

    cerrarEditorMatricula() {
        if (this.dialogoMatricula?.open) {
            this.dialogoMatricula.close();
        }
    }

    cerrarResumenMatricula() {
        if (this.dialogoResumenMatricula?.open) {
            this.dialogoResumenMatricula.close();
        }
    }

    abrirHistorial(expediente) {
        if (!this.dialogoHistorial) {
            return;
        }
        this.expediente = expediente || { calificadas: [], pendientes: [], media: null, creditos_aprobados: 0 };
        this.pintarHistorial(this.expediente);
        if (this.dialogoHistorial.open) {
            return;
        }
        try {
            this.dialogoHistorial.showModal();
        } catch {
            this.dialogoHistorial.setAttribute("open", "");
        }
    }

    cerrarHistorial() {
        if (this.dialogoHistorial?.open) {
            this.dialogoHistorial.close();
        }
    }

    pintarHistorial(expediente) {
        const select = document.getElementById("selectIntensificacion");
        if (select) {
            select.value = expediente?.intensificacion || "";
        }
        this.pintarResumenHistorial(expediente);
        this.listaHistorialCalificadas.replaceChildren();
        const calificadas = expediente?.calificadas || [];
        if (!calificadas.length) {
            const vacio = document.createElement("p");
            vacio.className = "historial-vacio";
            vacio.textContent = this.textos.historialSinCalificadas;
            this.listaHistorialCalificadas.append(vacio);
        } else {
            calificadas.forEach((asignatura) => this.anadirFilaHistorial(asignatura));
        }

        this.listaHistorialPendientes.replaceChildren();
        const pendientes = expediente?.pendientes || [];
        if (!pendientes.length) {
            const vacio = document.createElement("p");
            vacio.className = "historial-vacio";
            vacio.textContent = this.textos.historialSinPendientes;
            this.listaHistorialPendientes.append(vacio);
            return;
        }
        const ingles = this.textos.codigo === "EN";
        pendientes.forEach((asignatura) => {
            const fila = document.createElement("div");
            fila.className = "fila-historial-pendiente";
            const nombre = document.createElement("span");
            nombre.textContent = `${asignatura.codigo} · ${ingles ? asignatura.nombre_ingles : asignatura.nombre}`;
            const boton = document.createElement("button");
            boton.type = "button";
            boton.textContent = this.textos.anadirNotaPendiente;
            boton.addEventListener("click", () => {
                const vacio = this.listaHistorialCalificadas.querySelector(".historial-vacio");
                if (vacio) {
                    vacio.remove();
                }
                this.anadirFilaHistorial({ ...asignatura, nota: null, convalidada: false });
                fila.remove();
                if (!this.listaHistorialPendientes.children.length) {
                    const mensaje = document.createElement("p");
                    mensaje.className = "historial-vacio";
                    mensaje.textContent = this.textos.historialSinPendientes;
                    this.listaHistorialPendientes.append(mensaje);
                }
            });
            fila.append(nombre, boton);
            this.listaHistorialPendientes.append(fila);
        });
    }

    pintarResumenHistorial(expediente) {
        this.resumenHistorial.replaceChildren();
        const media = document.createElement("p");
        media.textContent = expediente?.media === null || expediente?.media === undefined
            ? `${this.textos.mediaCarrera}: ${this.textos.sinMedia}`
            : `${this.textos.mediaCarrera}: ${formatearMedia(expediente.media, this.textos.codigo)}`;
        const creditos = document.createElement("p");
        creditos.textContent = `${this.textos.creditosAprobados}: ${expediente?.creditos_aprobados || 0}`;
        this.resumenHistorial.append(media, creditos);
        if (expediente?.creditos_convalidados) {
            const convalidados = document.createElement("p");
            convalidados.textContent = `${this.textos.creditosConvalidados}: ${expediente.creditos_convalidados}`;
            this.resumenHistorial.append(convalidados);
        }
    }

    anadirFilaHistorial(asignatura) {
        const ingles = this.textos.codigo === "EN";
        const fila = document.createElement("div");
        fila.className = "fila-historial";
        fila.dataset.codigo = asignatura.codigo;

        const nombre = document.createElement("span");
        nombre.className = "historial-nombre";
        nombre.textContent = `${asignatura.codigo} · ${ingles ? asignatura.nombre_ingles : asignatura.nombre}`;

        const nota = document.createElement("input");
        nota.type = "number";
        nota.min = "0";
        nota.max = "10";
        nota.step = "0.01";
        nota.className = "nota-historial";
        nota.setAttribute("aria-label", this.textos.notaAsignatura);
        if (asignatura.nota !== null && asignatura.nota !== undefined && !asignatura.convalidada) {
            nota.value = String(asignatura.nota);
        }

        const label = document.createElement("label");
        label.className = "historial-convalidada";
        const check = document.createElement("input");
        check.type = "checkbox";
        check.className = "convalidada-historial";
        check.checked = Boolean(asignatura.convalidada);
        label.append(check, document.createTextNode(` ${this.textos.convalidada}`));
        const sincronizar = () => {
            nota.disabled = check.checked;
            if (check.checked) {
                nota.value = "";
            }
        };
        check.addEventListener("change", sincronizar);
        sincronizar();

        const quitar = document.createElement("button");
        quitar.type = "button";
        quitar.className = "quitar-historial";
        quitar.textContent = this.textos.quitarNotaHistorial;
        quitar.addEventListener("click", () => {
            fila.remove();
            if (!this.listaHistorialCalificadas.querySelector(".fila-historial")) {
                const vacio = document.createElement("p");
                vacio.className = "historial-vacio";
                vacio.textContent = this.textos.historialSinCalificadas;
                this.listaHistorialCalificadas.append(vacio);
            }
            const vacioPendiente = this.listaHistorialPendientes.querySelector(".historial-vacio");
            if (vacioPendiente) {
                vacioPendiente.remove();
            }
            const pendiente = document.createElement("div");
            pendiente.className = "fila-historial-pendiente";
            const texto = document.createElement("span");
            texto.textContent = nombre.textContent;
            const boton = document.createElement("button");
            boton.type = "button";
            boton.textContent = this.textos.anadirNotaPendiente;
            boton.addEventListener("click", () => {
                const vacio = this.listaHistorialCalificadas.querySelector(".historial-vacio");
                if (vacio) {
                    vacio.remove();
                }
                this.anadirFilaHistorial({
                    codigo: asignatura.codigo,
                    nombre: asignatura.nombre,
                    nombre_ingles: asignatura.nombre_ingles,
                    nota: null,
                    convalidada: false,
                });
                pendiente.remove();
                if (!this.listaHistorialPendientes.children.length) {
                    const mensaje = document.createElement("p");
                    mensaje.className = "historial-vacio";
                    mensaje.textContent = this.textos.historialSinPendientes;
                    this.listaHistorialPendientes.append(mensaje);
                }
            });
            pendiente.append(texto, boton);
            this.listaHistorialPendientes.prepend(pendiente);
        });

        fila.append(nombre, nota, label, quitar);
        this.listaHistorialCalificadas.append(fila);
    }

    leerHistorialEditor() {
        return [...this.listaHistorialCalificadas.querySelectorAll(".fila-historial")].map((fila) => {
            const convalidada = fila.querySelector(".convalidada-historial")?.checked;
            const crudo = fila.querySelector(".nota-historial")?.value;
            return {
                codigo: fila.dataset.codigo,
                convalidada: Boolean(convalidada),
                nota: convalidada || crudo === "" || crudo === undefined ? null : Number(crudo),
            };
        });
    }

    leerIntensificacionHistorial() {
        return document.getElementById("selectIntensificacion")?.value || "";
    }

    enviarHistorial() {
        if (this.alGuardarHistorial) {
            this.alGuardarHistorial(this.leerHistorialEditor(), this.leerIntensificacionHistorial());
        }
    }
}

const GRUPOS_MATRICULA = [
    { valor: "10", etiqueta: "A-10" },
    { valor: "11", etiqueta: "B-11" },
    { valor: "12", etiqueta: "C-12" },
    { valor: "13", etiqueta: "I-13" },
    { valor: "14", etiqueta: "ING. SOFTWARE-14" },
    { valor: "17", etiqueta: "O1-17" },
];

const MAPA_GRUPO_CAMPUS = {
    A: "10",
    10: "10",
    B: "11",
    11: "11",
    C: "12",
    12: "12",
    I: "13",
    13: "13",
    "ING. SOFTWARE": "14",
    14: "14",
    O1: "17",
    17: "17",
};

function normalizarGrupoCampus(grupo) {
    const crudo = String(grupo || "").trim().toUpperCase();
    return MAPA_GRUPO_CAMPUS[crudo] || "";
}

function etiquetaGrupoCampus(grupo) {
    const valor = normalizarGrupoCampus(grupo) || String(grupo || "").trim();
    const hallado = GRUPOS_MATRICULA.find((opcion) => opcion.valor === valor);
    return hallado ? hallado.etiqueta : (valor || "—");
}

function normalizarBusqueda(texto) {
    return String(texto || "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
}

function filtrarAsignaturas(catalogo, texto, ingles) {
    const consulta = normalizarBusqueda(texto);
    if (!consulta) {
        return catalogo.slice();
    }
    return catalogo.filter((asignatura) => {
        const nombre = normalizarBusqueda(ingles ? asignatura.nombre_ingles : asignatura.nombre);
        const codigo = normalizarBusqueda(asignatura.codigo);
        return codigo.startsWith(consulta)
            || nombre.startsWith(consulta)
            || nombre.includes(` ${consulta}`)
            || nombre.includes(consulta);
    });
}

function formatearMedia(media, codigo) {
    return Number(media).toLocaleString(codigo === "EN" ? "en-GB" : "es-ES", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function etiquetaIntensificacion(valor, textos) {
    const claves = {
        software: textos.intensificacionSoftware,
        computadores: textos.intensificacionComputadores,
        computacion: textos.intensificacionComputacion,
        tecnologias_informacion: textos.intensificacionTI,
    };
    return claves[valor] || textos.sinIntensificacion;
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
