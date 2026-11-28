const VistaAgenda = (() => {
    const HORA_INICIO = 8;
    const HORA_FIN = 20;
    const TONOS_FRANJA = ["#9d1830", "#7a1528", "#c45c6c", "#5c101c", "#a33d4e", "#8e3044"];

    class VistaAgenda {
        constructor({
            alBuscar,
            alAbrirPerfil,
            alCambiarTema,
            alCambiarIdioma,
            alLeer,
            alCambiarMes,
            alAbrirAsignatura,
            alEditarMatricula,
            alActualizarEvento,
            alEliminarEvento,
            alCrearAvisoSecretaria,
            alEliminarAvisoSecretaria,
        }) {
            this.seccion = document.getElementById("vistaAgenda");
            this.lista = document.getElementById("listaAsignaturas");
            this.vacio = document.getElementById("sinAsignaturas");
            this.textoVacio = document.getElementById("textoSinAsignaturas");
            this.botonMatriculaVacia = document.getElementById("botonMatriculaVacia");
            this.buscador = document.getElementById("buscadorAsignatura");
            this.nick = document.getElementById("nickAgenda");
            this.mes = document.getElementById("mesAgenda");
            this.anio = document.getElementById("anioAgenda");
            this.rejilla = document.getElementById("rejillaAgenda");
            this.diasSemana = document.getElementById("diasSemanaAgenda");
            this.ficha = document.getElementById("fichaAsignatura");
            this.fichaContenido = document.getElementById("fichaContenido");
            this.dialogo = document.getElementById("dialogoDiaAgenda");
            this.tituloDialogo = document.getElementById("tituloDialogoDia");
            this.fechaDialogo = document.getElementById("fechaDialogoDia");
            this.listaDialogo = document.getElementById("listaDialogoDia");
            this.dialogoEditarEvento = document.getElementById("dialogoEditarEvento");
            this.formEditarEvento = document.getElementById("formEditarEvento");
            this.idEventoEditar = document.getElementById("idEventoEditar");
            this.codigoEventoEditar = document.getElementById("codigoEventoEditar");
            this.tipoEventoEditar = document.getElementById("tipoEventoEditar");
            this.fechaEventoEditar = document.getElementById("fechaEventoEditar");
            this.horaEventoEditar = document.getElementById("horaEventoEditar");
            this.lugarEventoEditar = document.getElementById("lugarEventoEditar");
            this.dialogoAvisos = document.getElementById("dialogoAvisos");
            this.listaAvisos = document.getElementById("listaAvisos");
            this.sinAvisos = document.getElementById("sinAvisos");
            this.botonMarcarAvisosLeidos = document.getElementById("botonMarcarAvisosLeidos");
            this.botonEliminarAvisos = document.getElementById("botonEliminarAvisos");
            this.botonAvisos = document.getElementById("botonAvisosAgenda");
            this.iconoAvisos = document.getElementById("iconoAvisosAgenda");
            this.contadorAvisos = document.getElementById("contadorAvisos");
            this.avisosActivos = [];
            this.textos = TEXTOS.es;
            this.usuario = null;
            this.asignaturas = [];
            this.marcas = [];
            this.marcasAntelacion = [];
            this.horario = [];
            this.inicioSegundo = null;
            this.cuatrimestreActual = 1;
            this.avisos = [];
            this.preferenciasAvisos = PreferenciasNotificaciones.leer();
            this.abierta = null;
            this.hoy = new Date();
            this.lunes = lunesDe(this.hoy);
            this.reloj = null;
            this.vista = new Date(this.hoy.getFullYear(), this.hoy.getMonth(), 1);
            this.alBuscar = alBuscar;
            this.alCambiarMes = alCambiarMes;
            this.alAbrirAsignatura = alAbrirAsignatura;
            this.alEditarMatricula = alEditarMatricula;
            this.alActualizarEvento = alActualizarEvento;
            this.alEliminarEvento = alEliminarEvento;
            this.alCrearAvisoSecretaria = alCrearAvisoSecretaria;
            this.alEliminarAvisoSecretaria = alEliminarAvisoSecretaria;
            this.preferenciasLeyenda = PreferenciasLeyenda.leer();
            this.panelAvisoSecretaria = document.getElementById("panelAvisoSecretaria");
            this.formAvisoSecretaria = document.getElementById("formAvisoSecretaria");
            this.temporizador = null;
            document.getElementById("botonPerfil").addEventListener("click", alAbrirPerfil);
            this.botonMatriculaVacia.addEventListener("click", () => {
                if (this.alEditarMatricula) {
                    this.alEditarMatricula();
                }
            });
            document.getElementById("botonTemaAgenda").addEventListener("click", alCambiarTema);
            document.getElementById("botonIdiomaAgenda").addEventListener("click", alCambiarIdioma);
            document.getElementById("botonVozAgenda").addEventListener("click", () => alLeer(this.textoEnPantalla()));
            this.botonAvisos.addEventListener("click", () => this.abrirDialogoAvisos());
            this.botonMarcarAvisosLeidos.addEventListener("click", () => this.marcarTodosAvisosLeidos());
            this.botonEliminarAvisos.addEventListener("click", () => this.eliminarTodosAvisos());
            document.getElementById("mesAnterior").addEventListener("click", () => this.cambiarMes(-1));
            document.getElementById("mesSiguiente").addEventListener("click", () => this.cambiarMes(1));
            this.mes.addEventListener("change", () => {
                this.vista = new Date(this.vista.getFullYear(), Number(this.mes.value), 1);
                this.pintarCalendario();
                this.alCambiarMes();
            });
            this.anio.addEventListener("change", () => {
                this.vista = new Date(Number(this.anio.value), this.vista.getMonth(), 1);
                this.pintarCalendario();
                this.alCambiarMes();
            });
            this.buscador.addEventListener("input", () => {
                clearTimeout(this.temporizador);
                this.temporizador = setTimeout(() => this.alBuscar(this.buscador.value), 180);
            });
            document.getElementById("volverAsignaturas").addEventListener("click", () => this.cerrarAsignatura());
            document.getElementById("semanaAnterior").addEventListener("click", () => this.cambiarSemana(-1));
            document.getElementById("semanaSiguiente").addEventListener("click", () => this.cambiarSemana(1));
            this.dialogo.addEventListener("click", (evento) => {
                if (evento.target === this.dialogo) {
                    this.dialogo.close();
                }
            });
            this.dialogoAvisos.addEventListener("click", (evento) => {
                if (evento.target === this.dialogoAvisos) {
                    this.dialogoAvisos.close();
                }
            });
            if (this.dialogoEditarEvento) {
                this.dialogoEditarEvento.addEventListener("click", (evento) => {
                    if (evento.target === this.dialogoEditarEvento) {
                        this.dialogoEditarEvento.close();
                    }
                });
                document.getElementById("cerrarEditarEvento").addEventListener("click", () => {
                    this.dialogoEditarEvento.close();
                });
                this.formEditarEvento.addEventListener("submit", (evento) => {
                    evento.preventDefault();
                    this.enviarEdicionEvento();
                });
            }
            this.prepararLeyenda();
            this.aplicarPreferenciasAvisos(this.preferenciasAvisos);
            if (this.formAvisoSecretaria) {
                this.formAvisoSecretaria.addEventListener("submit", (evento) => {
                    evento.preventDefault();
                    this.enviarAvisoSecretaria();
                });
            }
            window.addEventListener("resize", () => {
                if (this.seccion.hidden) {
                    return;
                }
                clearTimeout(this.redibujo);
                this.redibujo = setTimeout(() => this.pintarHorario(), 120);
            });
        }

        prepararLeyenda() {
            const leyenda = document.getElementById("leyendaCalendario");
            if (!leyenda) {
                return;
            }
            const estrella = leyenda.querySelector(".leyenda-estrella");
            const punto = leyenda.querySelector(".leyenda-punto");
            if (estrella) {
                estrella.replaceChildren(iconoEstrella());
            }
            if (punto) {
                punto.replaceChildren();
                punto.append(iconoPunto());
            }
            const letras = {
                ".cambio-cuatri": this.textos.abrevCambioCuatri || "C",
                ".festivo": this.textos.abrevFestivo || "F",
                ".semana-examenes": this.textos.abrevPeriodo || "P",
                ".secretaria": this.textos.abrevSecretaria || "S",
            };
            Object.entries(letras).forEach(([selector, texto]) => {
                const icono = leyenda.querySelector(`.leyenda-letra${selector}`);
                if (icono) {
                    icono.textContent = texto;
                }
            });
            leyenda.querySelectorAll("[data-filtro]").forEach((item) => {
                if (item.dataset.leyendaListo) {
                    return;
                }
                item.dataset.leyendaListo = "1";
                const activar = () => {
                    this.preferenciasLeyenda = PreferenciasLeyenda.alternar(item.dataset.filtro);
                    this.aplicarEstadoLeyenda();
                    this.pintarCalendario();
                };
                item.addEventListener("click", activar);
                item.addEventListener("keydown", (evento) => {
                    if (evento.key === "Enter" || evento.key === " ") {
                        evento.preventDefault();
                        activar();
                    }
                });
            });
            this.aplicarEstadoLeyenda();
        }

        aplicarEstadoLeyenda() {
            const leyenda = document.getElementById("leyendaCalendario");
            if (!leyenda) {
                return;
            }
            leyenda.querySelectorAll("[data-filtro]").forEach((item) => {
                const activo = PreferenciasLeyenda.visible(item.dataset.filtro, this.preferenciasLeyenda);
                item.classList.toggle("leyenda-activa", activo);
                item.classList.toggle("leyenda-apagada", !activo);
                item.setAttribute("aria-pressed", activo ? "true" : "false");
            });
        }

        mostrar(usuario, textos) {
            this.usuario = usuario;
            this.textos = textos;
            this.seccion.hidden = false;
            this.nick.textContent = usuario.nick;
            aplicarTextos(this.seccion, textos);
            this.prepararLeyenda();
            this.buscador.placeholder = textos.buscarAsignatura;
            this.abierta = null;
            this.ficha.hidden = true;
            this.buscador.closest(".buscador").hidden = false;
            this.lista.hidden = false;
            this.preferenciasAvisos = PreferenciasNotificaciones.leer();
            this.preferenciasLeyenda = PreferenciasLeyenda.leer();
            this.aplicarPreferenciasAvisos(this.preferenciasAvisos);
            this.aplicarEstadoLeyenda();
            this.mostrarPanelSecretaria(usuario?.rol === "superadministrador");
            this.rellenarSelectores();
            this.iniciarReloj();
        }

        mostrarPanelSecretaria(visible) {
            if (this.panelAvisoSecretaria) {
                this.panelAvisoSecretaria.hidden = !visible;
            }
        }

        enviarAvisoSecretaria() {
            if (!this.alCrearAvisoSecretaria || !this.formAvisoSecretaria) {
                return;
            }
            const datos = new FormData(this.formAvisoSecretaria);
            this.alCrearAvisoSecretaria({
                titulo: String(datos.get("titulo") || "").trim(),
                tipo: String(datos.get("tipo") || "aviso"),
                fecha: String(datos.get("fecha") || ""),
                hora: String(datos.get("hora") || "").slice(0, 5),
                lugar: String(datos.get("lugar") || "").trim(),
                url: String(datos.get("url") || "").trim(),
            }, () => {
                this.formAvisoSecretaria.reset();
                const hora = document.getElementById("horaAvisoSecretaria");
                if (hora) {
                    hora.value = "12:00";
                }
            });
        }

        ocultar() {
            this.seccion.hidden = true;
            clearInterval(this.reloj);
            window.speechSynthesis?.cancel();
        }

        iniciarReloj() {
            clearInterval(this.reloj);
            this.reloj = setInterval(() => this.moverLineaAhora(), 15000);
        }

        moverLineaAhora() {
            const ahora = new Date();
            const cambioDeDia = ahora.getDate() !== this.hoy.getDate()
                || ahora.getMonth() !== this.hoy.getMonth()
                || ahora.getFullYear() !== this.hoy.getFullYear();
            this.hoy = ahora;
            const yAhora = topAhora(this.hoy, altoHora());
            const finSemana = new Date(this.lunes.getFullYear(), this.lunes.getMonth(), this.lunes.getDate() + 7);
            const contieneHoy = yAhora !== null && this.hoy >= this.lunes && this.hoy < finSemana;
            const linea = document.querySelector("#rejillaHorario .linea-ahora");
            if (cambioDeDia || (contieneHoy && !linea)) {
                this.pintarHorario();
                return;
            }
            if (!contieneHoy) {
                linea?.remove();
                return;
            }
            const altoCabecera = document.querySelector("#rejillaHorario header")?.offsetHeight || 0;
            linea.style.top = `${altoCabecera + yAhora}px`;
        }

        aplicarTextos(textos) {
            this.textos = textos;
            aplicarTextos(this.seccion, textos);
            this.buscador.placeholder = textos.buscarAsignatura;
            this.botonAvisos.setAttribute("aria-label", textos.abrirAvisos);
            if (this.usuario) {
                this.nick.textContent = this.usuario.nick;
            }
            if (!this.seccion.hidden) {
                if (this.abierta) {
                    this.pintarFicha();
                } else {
                    this.pintarLista();
                }
                this.pintarCalendario();
                this.pintarHorario();
                this.actualizarAvisos();
            }
        }

        textoBusqueda() {
            return this.buscador.value;
        }

        periodo() {
            return { anio: this.vista.getFullYear(), mes: this.vista.getMonth() + 1 };
        }

        pintar(asignaturas, marcas, horario, marcasAntelacion, meta) {
            this.asignaturas = asignaturas;
            this.marcas = marcas;
            if (marcasAntelacion !== undefined) {
                this.marcasAntelacion = marcasAntelacion;
            }
            if (meta) {
                if (meta.inicioSegundo !== undefined) {
                    this.inicioSegundo = meta.inicioSegundo || null;
                }
                if (meta.cuatrimestreActual !== undefined) {
                    this.cuatrimestreActual = meta.cuatrimestreActual || 1;
                }
            }
            const horarioCambio = horario !== undefined;
            if (horarioCambio) {
                this.horario = horario || [];
            }
            if (this.abierta) {
                const sigue = asignaturas.find((asignatura) => asignatura.codigo === this.abierta.codigo);
                if (!sigue) {
                    this.cerrarAsignatura();
                    return;
                }
                this.abierta = sigue;
                this.pintarFicha();
                this.pintarCalendario();
                if (horarioCambio) {
                    this.pintarHorario();
                }
                this.actualizarAvisos();
                return;
            }
            this.pintarLista();
            this.pintarCalendario();
            if (horarioCambio) {
                this.pintarHorario();
            }
            this.actualizarAvisos();
        }

        aplicarPreferenciasAvisos(preferencias) {
            this.preferenciasAvisos = preferencias;
            this.iconoAvisos.replaceChildren(iconoCampana());
            this.botonAvisos.setAttribute("aria-label", this.textos.abrirAvisos || "Abrir avisos");
            this.actualizarAvisos();
        }

        actualizarAvisos() {
            const codigos = this.asignaturas.map((asignatura) => asignatura.codigo);
            const marcasAvisos = this.marcasAntelacion.length
                ? this.filtrarMarcas(this.marcasAntelacion)
                : this.marcasVisibles();
            this.avisos = PreferenciasNotificaciones.construirAvisos({
                marcas: marcasAvisos,
                horario: this.horarioDelCuatrimestre(this.cuatrimestreActual || 1),
                textos: this.textos,
                preferencias: this.preferenciasAvisos,
                ahora: this.hoy,
                mesVista: this.vista,
                codigosMatricula: codigos,
            });
            this.avisosActivos = PreferenciasNotificaciones.filtrarAvisosActivos(this.avisos);
            const noLeidos = this.avisosActivos.filter((aviso) => !PreferenciasNotificaciones.estaLeido(aviso.id));
            const total = noLeidos.length;
            this.contadorAvisos.textContent = String(total);
            this.contadorAvisos.hidden = total === 0;
            this.botonMarcarAvisosLeidos.disabled = total === 0;
            this.botonEliminarAvisos.disabled = this.avisosActivos.length === 0;
        }

        pintarListaAvisos() {
            document.getElementById("tituloDialogoAvisos").textContent = this.textos.tituloAvisos;
            this.botonMarcarAvisosLeidos.textContent = this.textos.marcarAvisosLeidos;
            this.botonEliminarAvisos.textContent = this.textos.eliminarAvisos;
            this.listaAvisos.replaceChildren();
            this.sinAvisos.hidden = this.avisosActivos.length > 0;
            this.avisosActivos.forEach((aviso) => {
                const leido = PreferenciasNotificaciones.estaLeido(aviso.id);
                const item = document.createElement("li");
                item.className = `aviso-item aviso-${aviso.tipo} ${leido ? "aviso-leido" : "aviso-no-leido"}`;
                item.dataset.id = aviso.id;
                item.tabIndex = 0;
                item.setAttribute("role", "button");
                item.setAttribute("aria-pressed", leido ? "true" : "false");
                const punto = document.createElement("span");
                punto.className = "aviso-punto";
                punto.setAttribute("aria-hidden", "true");
                const cuerpo = document.createElement("span");
                cuerpo.className = "aviso-cuerpo";
                const titulo = document.createElement("strong");
                titulo.textContent = aviso.titulo;
                const detalle = document.createElement("span");
                detalle.textContent = aviso.detalle;
                cuerpo.append(titulo, detalle);
                item.append(punto, cuerpo);
                item.addEventListener("click", () => this.marcarAvisoLeido(aviso.id));
                item.addEventListener("keydown", (evento) => {
                    if (evento.key === "Enter" || evento.key === " ") {
                        evento.preventDefault();
                        this.marcarAvisoLeido(aviso.id);
                    }
                });
                this.listaAvisos.append(item);
            });
        }

        abrirDialogoAvisos() {
            this.actualizarAvisos();
            this.pintarListaAvisos();
            this.dialogoAvisos.showModal();
        }

        marcarAvisoLeido(id) {
            PreferenciasNotificaciones.marcarLeido(id);
            this.actualizarAvisos();
            this.pintarListaAvisos();
        }

        marcarTodosAvisosLeidos() {
            PreferenciasNotificaciones.marcarTodosLeidos(this.avisosActivos.map((aviso) => aviso.id));
            this.actualizarAvisos();
            this.pintarListaAvisos();
        }

        eliminarTodosAvisos() {
            PreferenciasNotificaciones.eliminarTodos(this.avisosActivos.map((aviso) => aviso.id));
            this.actualizarAvisos();
            this.pintarListaAvisos();
        }

        pintarLista() {
            const ingles = this.textos.codigo === "EN";
            this.lista.replaceChildren();
            const hayAsignaturas = this.asignaturas.length > 0;
            this.vacio.hidden = hayAsignaturas;
            if (!hayAsignaturas) {
                const buscando = Boolean((this.buscador.value || "").trim());
                this.textoVacio.textContent = buscando
                    ? this.textos.sinAsignaturas
                    : this.textos.sinMatriculaAsignaturas;
                const rol = this.usuario && this.usuario.rol;
                const esGestion = rol === "profesor" || rol === "superadministrador";
                this.botonMatriculaVacia.hidden = buscando || esGestion;
                this.botonMatriculaVacia.textContent = this.textos.irEditarMatricula || this.textos.editarMatricula;
                if (!buscando && rol === "profesor") {
                    this.textoVacio.textContent = this.textos.sinAsignaturasProfesor;
                }
            }
            this.asignaturas.forEach((asignatura) => {
                const nombre = ingles ? asignatura.nombre_ingles : asignatura.nombre;
                const fila = document.createElement("li");
                const boton = document.createElement("button");
                boton.type = "button";
                boton.className = "fila-asignatura";
                const insignia = document.createElement("span");
                insignia.className = "insignia";
                insignia.textContent = nombre.slice(0, 1).toLocaleUpperCase(ingles ? "en" : "es");
                const titulo = document.createElement("span");
                titulo.className = "asignatura-nombre";
                titulo.textContent = nombre;
                boton.append(insignia, titulo);
                boton.addEventListener("click", () => this.abrirAsignatura(asignatura));
                fila.append(boton);
                this.lista.append(fila);
            });
        }

        pintarCalendario() {
            const anio = this.vista.getFullYear();
            const mes = this.vista.getMonth();
            this.rellenarSelectores();
            this.pintarCabeceraSemana();

            const marcasPorDia = new Map(this.marcasVisibles().map((marca) => [marca.dia, marca.simbolos]));
            const lunesSemana = lunesDe(this.hoy);
            const despuesSemana = new Date(lunesSemana.getFullYear(), lunesSemana.getMonth(), lunesSemana.getDate() + 7);
            const inicio = desplazamientoLunes(new Date(anio, mes, 1).getDay());
            const diasMes = new Date(anio, mes + 1, 0).getDate();
            const diasPrevios = new Date(anio, mes, 0).getDate();
            const primeraCelda = new Date(anio, mes, 1 - inicio);

            const fragmento = document.createDocumentFragment();
            for (let indice = 0; indice < 42; indice += 1) {
                const fechaCelda = new Date(
                    primeraCelda.getFullYear(),
                    primeraCelda.getMonth(),
                    primeraCelda.getDate() + indice,
                );
                fragmento.append(this.crearCeldaDia({
                    indice,
                    inicio,
                    diasMes,
                    diasPrevios,
                    anio,
                    mes,
                    fechaCelda,
                    lunesSemana,
                    despuesSemana,
                    marcasPorDia,
                }));
            }
            this.rejilla.replaceChildren(fragmento);
        }

        pintarCabeceraSemana() {
            this.diasSemana.replaceChildren();
            this.textos.diasSemana.forEach((nombre) => {
                const celda = document.createElement("span");
                celda.textContent = nombre;
                this.diasSemana.append(celda);
            });
        }

        crearCeldaDia({
            indice,
            inicio,
            diasMes,
            diasPrevios,
            anio,
            mes,
            fechaCelda,
            lunesSemana,
            despuesSemana,
            marcasPorDia,
        }) {
            const celda = document.createElement("div");
            celda.className = "dia";
            const numero = document.createElement("span");
            numero.className = "numero";

            let diaMes;
            let deEsteMes = false;
            if (indice < inicio) {
                diaMes = diasPrevios - inicio + 1 + indice;
                celda.classList.add("otro");
            } else if (indice >= inicio + diasMes) {
                diaMes = indice - inicio - diasMes + 1;
                celda.classList.add("otro");
            } else {
                diaMes = indice - inicio + 1;
                deEsteMes = true;
                celda.classList.add("dia-actual");
                celda.dataset.dia = String(diaMes);
            }

            if (fechaCelda >= lunesSemana && fechaCelda < despuesSemana) {
                celda.classList.add("semana-hoy");
            }
            const diaSemana = fechaCelda.getDay();
            if (diaSemana === 0 || diaSemana === 6) {
                celda.classList.add("finde");
            }

            numero.textContent = String(diaMes);
            const esHoy = deEsteMes
                && diaMes === this.hoy.getDate()
                && mes === this.hoy.getMonth()
                && anio === this.hoy.getFullYear();
            if (esHoy) {
                numero.classList.add("hoy");
                celda.setAttribute("aria-current", "date");
            }
            celda.append(numero);

            if (deEsteMes && marcasPorDia.has(diaMes)) {
                this.pintarMarcasEnCelda(celda, diaMes, marcasPorDia.get(diaMes), mes);
            }
            return celda;
        }

        pintarMarcasEnCelda(celda, diaMes, simbolos, mes) {
            const ingles = this.textos.codigo === "EN";
            const marcasNodo = document.createElement("span");
            marcasNodo.className = "marcas";
            const estrellas = document.createElement("span");
            const puntos = document.createElement("span");
            estrellas.className = "fila-marcas";
            puntos.className = "fila-marcas";

            if (simbolos.some((simbolo) => simbolo.tipo === "cambio_cuatrimestre")) {
                celda.classList.add("dia-cambio-cuatri");
            }
            if (simbolos.some((simbolo) => simbolo.tipo === "festivo")) {
                celda.classList.add("dia-festivo");
            }
            if (simbolos.some((simbolo) => simbolo.tipo === "vacaciones")) {
                celda.classList.add("dia-vacaciones");
            }
            if (simbolos.some((simbolo) => simbolo.tipo === "secretaria")) {
                celda.classList.add("dia-secretaria");
            }
            if (simbolos.some((simbolo) => simbolo.tipo === "semana_examenes" || simbolo.tipo === "periodo")) {
                celda.classList.add("dia-periodo");
            }

            simbolos.forEach((simbolo) => {
                const nombre = ingles ? simbolo.nombre_ingles : simbolo.nombre;
                if (simbolo.tipo === "estrella" || simbolo.tipo === "punto") {
                    const icono = simbolo.tipo === "estrella" ? iconoEstrella() : iconoPunto();
                    const etiqueta = simbolo.tipo === "estrella" ? this.textos.examen : this.textos.entrega;
                    icono.dataset.tipo = simbolo.tipo;
                    icono.dataset.nombre = nombre;
                    icono.setAttribute("title", `${etiqueta}: ${nombre}`);
                    (simbolo.tipo === "estrella" ? estrellas : puntos).append(icono);
                    return;
                }
                const pastilla = document.createElement("span");
                pastilla.className = `marca-periodo marca-${simbolo.tipo}`;
                pastilla.dataset.tipo = simbolo.tipo;
                pastilla.dataset.nombre = nombre;
                pastilla.setAttribute("title", nombre);
                if (simbolo.tipo === "secretaria") {
                    pastilla.textContent = this.textos.abrevSecretaria || "S";
                } else if (simbolo.tipo === "cambio_cuatrimestre") {
                    pastilla.textContent = this.textos.abrevCambioCuatri || "C";
                } else if (simbolo.tipo === "festivo" || simbolo.tipo === "vacaciones") {
                    pastilla.textContent = this.textos.abrevFestivo || "F";
                } else {
                    pastilla.textContent = this.textos.abrevPeriodo || "P";
                }
                marcasNodo.append(pastilla);
            });

            if (estrellas.childNodes.length) {
                marcasNodo.append(estrellas);
            }
            if (puntos.childNodes.length) {
                marcasNodo.append(puntos);
            }
            celda.append(marcasNodo);
            celda.classList.add("con-marcas");
            celda.tabIndex = 0;
            celda.setAttribute("role", "button");
            celda.setAttribute("aria-label", `${diaMes} ${this.textos.meses[mes]}`);
            celda.addEventListener("click", () => this.abrirDialogoDia(diaMes, simbolos));
            celda.addEventListener("keydown", (evento) => {
                if (evento.key === "Enter" || evento.key === " ") {
                    evento.preventDefault();
                    this.abrirDialogoDia(diaMes, simbolos);
                }
            });
        }

        abrirDialogoDia(dia, simbolos) {
            const ingles = this.textos.codigo === "EN";
            const mes = this.vista.getMonth();
            const anio = this.vista.getFullYear();
            this.tituloDialogo.textContent = this.textos.dialogoDia;
            this.fechaDialogo.textContent = `${dia} ${this.textos.meses[mes]} ${anio}`;
            this.listaDialogo.replaceChildren();
            if (!simbolos.length) {
                const vacio = document.createElement("li");
                vacio.className = "sin-actividades";
                vacio.textContent = this.textos.sinActividades;
                this.listaDialogo.append(vacio);
            } else {
                [...simbolos]
                    .sort((a, b) => (a.hora || "").localeCompare(b.hora || "") || a.codigo.localeCompare(b.codigo))
                    .forEach((simbolo) => {
                        const item = document.createElement("li");
                        item.className = "actividad-dia";
                        const cabecera = document.createElement("div");
                        cabecera.className = "actividad-cabecera";
                        const tipo = document.createElement("strong");
                        tipo.textContent = this.etiquetaSimbolo(simbolo.tipo);
                        const nombre = document.createElement("span");
                        nombre.className = "actividad-nombre";
                        const textoNombre = ingles ? simbolo.nombre_ingles : simbolo.nombre;
                        nombre.textContent = textoNombre;
                        if (simbolo.tipo === "estrella" || simbolo.tipo === "punto") {
                            const icono = simbolo.tipo === "estrella" ? iconoEstrella() : iconoPunto();
                            cabecera.append(icono, tipo, nombre);
                        } else {
                            cabecera.append(tipo, nombre);
                        }
                        item.append(cabecera);
                        let detalleTexto = "";
                        if (simbolo.tipo === "estrella") {
                            detalleTexto = simbolo.lugar
                                ? `${simbolo.hora} · ${simbolo.lugar}`
                                : simbolo.hora;
                        } else if (simbolo.tipo === "punto") {
                            detalleTexto = `${this.textos.hastaLas} ${simbolo.hora}`;
                        } else if (simbolo.tipo === "secretaria") {
                            const partes = [simbolo.hora, simbolo.lugar, simbolo.detalle].filter(Boolean);
                            detalleTexto = partes.join(" · ");
                        }
                        if (detalleTexto && detalleTexto !== textoNombre) {
                            const detalle = document.createElement("p");
                            detalle.className = "actividad-detalle";
                            detalle.textContent = detalleTexto;
                            item.append(detalle);
                        }
                        if (simbolo.tipo === "secretaria" && simbolo.url) {
                            const enlace = document.createElement("a");
                            enlace.href = simbolo.url;
                            enlace.target = "_blank";
                            enlace.rel = "noopener";
                            enlace.className = "actividad-enlace";
                            enlace.textContent = this.textos.verEnEsiiab || "Ver en ESIIAB";
                            item.append(enlace);
                        }
                        if (this.puedeGestionarAvisoSecretaria(simbolo)) {
                            const acciones = document.createElement("div");
                            acciones.className = "actividad-acciones";
                            const eliminar = document.createElement("button");
                            eliminar.type = "button";
                            eliminar.className = "boton-actividad boton-actividad-eliminar";
                            eliminar.textContent = this.textos.eliminarEvento || "Eliminar";
                            eliminar.addEventListener("click", (evento) => {
                                evento.preventDefault();
                                evento.stopPropagation();
                                this.confirmarEliminarAvisoSecretaria(simbolo);
                            });
                            acciones.append(eliminar);
                            item.append(acciones);
                        } else if (this.puedeGestionarEvento(simbolo)) {
                            const acciones = document.createElement("div");
                            acciones.className = "actividad-acciones";
                            const editar = document.createElement("button");
                            editar.type = "button";
                            editar.className = "boton-actividad";
                            editar.textContent = this.textos.editarEvento || "Editar";
                            editar.addEventListener("click", (evento) => {
                                evento.preventDefault();
                                evento.stopPropagation();
                                this.abrirEditarEvento(simbolo);
                            });
                            const eliminar = document.createElement("button");
                            eliminar.type = "button";
                            eliminar.className = "boton-actividad boton-actividad-eliminar";
                            eliminar.textContent = this.textos.eliminarEvento || "Eliminar";
                            eliminar.addEventListener("click", (evento) => {
                                evento.preventDefault();
                                evento.stopPropagation();
                                this.confirmarEliminarEvento(simbolo);
                            });
                            acciones.append(editar, eliminar);
                            item.append(acciones);
                        }
                        this.listaDialogo.append(item);
                    });
            }
            this.dialogo.showModal();
        }

        puedeGestionarAvisoSecretaria(simbolo) {
            return Boolean(
                simbolo
                && simbolo.tipo === "secretaria"
                && simbolo.evento_id
                && this.usuario?.rol === "superadministrador"
                && this.alEliminarAvisoSecretaria,
            );
        }

        confirmarEliminarAvisoSecretaria(simbolo) {
            if (!this.alEliminarAvisoSecretaria || !simbolo.evento_id) {
                return;
            }
            const nombre = this.textos.codigo === "EN" ? simbolo.nombre_ingles : simbolo.nombre;
            const mensaje = (this.textos.confirmarEliminarAvisoSecretaria || "¿Eliminar el aviso «{nombre}»?")
                .replace("{nombre}", nombre);
            if (!window.confirm(mensaje)) {
                return;
            }
            this.alEliminarAvisoSecretaria(simbolo.evento_id, () => {
                this.dialogo.close();
            });
        }

        puedeGestionarEvento(simbolo) {
            if (!simbolo || !simbolo.editable || !simbolo.evento_id || !this.usuario) {
                return false;
            }
            if (simbolo.tipo === "secretaria") {
                return false;
            }
            if (this.usuario.rol !== "profesor") {
                return false;
            }
            return this.asignaturas.some((asignatura) => asignatura.codigo === simbolo.codigo);
        }

        abrirEditarEvento(simbolo) {
            if (!this.dialogoEditarEvento || !this.alActualizarEvento) {
                return;
            }
            this.rellenarAsignaturasEdicion(simbolo.codigo);
            this.idEventoEditar.value = simbolo.evento_id;
            this.tipoEventoEditar.value = simbolo.tipo === "estrella" ? "examen" : "entrega";
            this.fechaEventoEditar.value = simbolo.fecha || "";
            this.horaEventoEditar.value = (simbolo.hora || "").slice(0, 5);
            this.lugarEventoEditar.value = simbolo.lugar || "";
            this.dialogo.close();
            this.dialogoEditarEvento.showModal();
        }

        rellenarAsignaturasEdicion(codigoSeleccionado) {
            const ingles = this.textos.codigo === "EN";
            this.codigoEventoEditar.replaceChildren();
            this.asignaturas.forEach((asignatura) => {
                const opcion = document.createElement("option");
                opcion.value = asignatura.codigo;
                opcion.textContent = ingles ? asignatura.nombre_ingles : asignatura.nombre;
                if (asignatura.codigo === codigoSeleccionado) {
                    opcion.selected = true;
                }
                this.codigoEventoEditar.append(opcion);
            });
            if (![...this.codigoEventoEditar.options].some((opcion) => opcion.value === codigoSeleccionado)) {
                const opcion = document.createElement("option");
                opcion.value = codigoSeleccionado;
                opcion.textContent = codigoSeleccionado;
                opcion.selected = true;
                this.codigoEventoEditar.append(opcion);
            }
        }

        enviarEdicionEvento() {
            if (!this.alActualizarEvento) {
                return;
            }
            const datos = {
                codigo: this.codigoEventoEditar.value,
                tipo: this.tipoEventoEditar.value,
                fecha: this.fechaEventoEditar.value,
                hora: this.horaEventoEditar.value,
                lugar: this.lugarEventoEditar.value.trim() || null,
            };
            this.alActualizarEvento(this.idEventoEditar.value, datos, () => {
                this.dialogoEditarEvento.close();
            });
        }

        confirmarEliminarEvento(simbolo) {
            if (!this.alEliminarEvento || !simbolo.evento_id) {
                return;
            }
            const nombre = this.textos.codigo === "EN" ? simbolo.nombre_ingles : simbolo.nombre;
            const tipo = this.etiquetaSimbolo(simbolo.tipo);
            const mensaje = (this.textos.confirmarEliminarEvento || "¿Eliminar {tipo} de {nombre}?")
                .replace("{tipo}", tipo)
                .replace("{nombre}", nombre);
            if (!window.confirm(mensaje)) {
                return;
            }
            this.alEliminarEvento(simbolo.evento_id, () => {
                this.dialogo.close();
            });
        }

        marcasVisibles() {
            return this.filtrarMarcas(this.marcas);
        }

        filtrarMarcas(marcas) {
            const codigos = new Set(this.asignaturas.map((asignatura) => asignatura.codigo));
            const academicos = new Set([
                "festivo",
                "vacaciones",
                "periodo",
                "semana_examenes",
                "cambio_cuatrimestre",
            ]);
            const esSecretaria = this.usuario?.rol === "superadministrador";
            return (marcas || [])
                .map((marca) => ({
                    dia: marca.dia,
                    simbolos: (marca.simbolos || []).filter((simbolo) => {
                        if (!PreferenciasLeyenda.visible(simbolo.tipo, this.preferenciasLeyenda)) {
                            return false;
                        }
                        if (simbolo.tipo === "secretaria" || simbolo.codigo === "secretaria") {
                            return !this.abierta;
                        }
                        if (academicos.has(simbolo.tipo) || simbolo.codigo === "calendario") {
                            return !this.abierta;
                        }
                        if (esSecretaria) {
                            return !this.abierta;
                        }
                        if (this.abierta) {
                            return simbolo.codigo === this.abierta.codigo;
                        }
                        return codigos.has(simbolo.codigo);
                    }),
                }))
                .filter((marca) => marca.simbolos.length);
        }

        etiquetaSimbolo(tipo) {
            if (tipo === "estrella") {
                return this.textos.examen;
            }
            if (tipo === "punto") {
                return this.textos.entrega;
            }
            if (tipo === "secretaria") {
                return this.textos.leyendaAvisosSecretaria || "Aviso secretaría";
            }
            if (tipo === "cambio_cuatrimestre") {
                return this.textos.leyendaCambioCuatri || "Cambio de cuatrimestre";
            }
            if (tipo === "festivo" || tipo === "vacaciones") {
                return this.textos.leyendaFestivo || "Festivo";
            }
            if (tipo === "semana_examenes") {
                return this.textos.leyendaSemanaExamenes || "Exámenes";
            }
            return this.textos.leyendaPeriodo || "Calendario";
        }

        abrirAsignatura(asignatura) {
            this.abierta = asignatura;
            this.buscador.closest(".buscador").hidden = true;
            this.lista.hidden = true;
            this.vacio.hidden = true;
            this.ficha.hidden = false;
            this.pintarFicha();
            this.pintarCalendario();
            this.pintarHorario();
            if (typeof this.alAbrirAsignatura === "function") {
                this.alAbrirAsignatura(asignatura);
            }
        }

        cerrarAsignatura() {
            this.abierta = null;
            this.ficha.hidden = true;
            this.buscador.closest(".buscador").hidden = false;
            this.lista.hidden = false;
            this.pintarLista();
            this.pintarCalendario();
            this.pintarHorario();
        }

        cuatrimestreSemanaVista() {
            const domingo = new Date(
                this.lunes.getFullYear(),
                this.lunes.getMonth(),
                this.lunes.getDate() + 6,
            );
            return cuatrimestreDeFecha(domingo, this.inicioSegundo);
        }

        horarioDelCuatrimestre(cuatrimestre) {
            return (this.horario || []).filter((franja) => {
                if (!franja.cuatrimestre) {
                    return true;
                }
                return franja.cuatrimestre === cuatrimestre;
            });
        }

        franjasVisibles() {
            const base = this.horarioDelCuatrimestre(this.cuatrimestreSemanaVista());
            if (!this.abierta) {
                return base;
            }
            return base.filter((franja) => franja.codigo === this.abierta.codigo);
        }

        cambiarSemana(delta) {
            this.lunes = new Date(this.lunes.getFullYear(), this.lunes.getMonth(), this.lunes.getDate() + delta * 7);
            this.pintarHorario();
        }

        pintarHorario() {
            pintarRejillaHorario({
                rejilla: document.getElementById("rejillaHorario"),
                titulo: document.getElementById("tituloSemana"),
                franjas: this.franjasVisibles(),
                lunes: this.lunes,
                hoy: this.hoy,
                textos: this.textos,
            });
        }

        pintarFicha() {
            const ingles = this.textos.codigo === "EN";
            const nombre = ingles ? this.abierta.nombre_ingles : this.abierta.nombre;
            const aulasTeoria = (this.abierta.aulas_teoria || []).join(", ") || this.textos.sinAula;
            const aulasPracticas = (this.abierta.aulas_practicas || []).join(", ") || this.textos.sinAula;
            const profesores = this.abierta.profesores || [];
            this.fichaContenido.replaceChildren();
            const cabecera = document.createElement("div");
            cabecera.className = "ficha-cabecera";
            const insignia = document.createElement("span");
            insignia.className = "insignia";
            insignia.textContent = nombre.slice(0, 1).toLocaleUpperCase(ingles ? "en" : "es");
            const titulo = document.createElement("span");
            titulo.className = "asignatura-nombre";
            titulo.textContent = this.abierta.grupo
                ? `${nombre} · ${this.textos.filtroGrupo} ${this.abierta.grupo}`
                : nombre;
            cabecera.append(insignia, titulo);
            const teoria = bloqueGrupo(this.textos.teoria, aulasTeoria, []);
            const practicas = bloqueGrupo(this.textos.practicas, aulasPracticas, []);
            const bloqueProfesores = bloqueGrupo(
                this.textos.profesores,
                "",
                profesores.length
                    ? profesores.map((profesor) => ({
                        nombre: profesor.nombre,
                        lineas: profesor.tutorias || [],
                        url: profesor.url,
                    }))
                    : [{ nombre: this.textos.sinProfesores, lineas: [] }],
            );
            const enlaces = document.createElement("div");
            enlaces.className = "ficha-enlaces";
            if (this.abierta.url_esiiab) {
                enlaces.append(enlaceFicha(this.textos.enlaceEsiiab, this.abierta.url_esiiab));
            }
            enlaces.append(
                enlaceFicha(this.textos.enlaceCampus, "https://campusvirtual.uclm.es/"),
                enlaceFicha(this.textos.enlaceSecretaria, "https://secretaria.uclm.es/"),
            );
            this.fichaContenido.append(cabecera, teoria, practicas, bloqueProfesores, enlaces);
        }

        textoEnPantalla() {
            const nombres = this.abierta
                ? [this.textos.codigo === "EN" ? this.abierta.nombre_ingles : this.abierta.nombre]
                : [...this.lista.querySelectorAll(".asignatura-nombre")].map((nodo) => nodo.textContent);
            const marcas = [...this.rejilla.querySelectorAll(".dia-actual")].flatMap((celda) => {
                const simbolos = [...celda.querySelectorAll(".estrella, .punto")];
                if (!simbolos.length) {
                    return [];
                }
                const piezas = simbolos.map((nodo) => {
                    const etiqueta = nodo.dataset.tipo === "estrella" ? this.textos.examen : this.textos.entrega;
                    return `${etiqueta}: ${nodo.dataset.nombre}`;
                });
                return [`${celda.dataset.dia}: ${piezas.join(", ")}`];
            });
            return [
                this.textos.tituloAgenda,
                this.usuario ? this.usuario.nick : "",
                nombres.join(", "),
                `${this.textos.meses[this.vista.getMonth()]} ${this.vista.getFullYear()}`,
                ...marcas,
            ].filter(Boolean).join(". ");
        }

        cambiarMes(delta) {
            this.vista = new Date(this.vista.getFullYear(), this.vista.getMonth() + delta, 1);
            this.pintarCalendario();
            this.alCambiarMes();
        }

        rellenarSelectores() {
            const mes = this.vista.getMonth();
            const anio = this.vista.getFullYear();
            this.mes.replaceChildren();
            this.textos.meses.forEach((nombre, indice) => {
                const opcion = document.createElement("option");
                opcion.value = String(indice);
                opcion.textContent = nombre;
                this.mes.append(opcion);
            });
            this.mes.value = String(mes);
            this.anio.replaceChildren();
            for (let valor = this.hoy.getFullYear() - 2; valor <= this.hoy.getFullYear() + 3; valor += 1) {
                const opcion = document.createElement("option");
                opcion.value = String(valor);
                opcion.textContent = String(valor);
                this.anio.append(opcion);
            }
            if (![...this.anio.options].some((opcion) => opcion.value === String(anio))) {
                const opcion = document.createElement("option");
                opcion.value = String(anio);
                opcion.textContent = String(anio);
                this.anio.append(opcion);
            }
            this.anio.value = String(anio);
        }
    }

    function altoHora(raiz) {
        const nodo = raiz || document.querySelector(".agenda-horario");
        const crudo = nodo ? getComputedStyle(nodo).getPropertyValue("--alto-hora") : "";
        const valor = parseFloat(crudo);
        return Number.isFinite(valor) && valor > 0 ? valor : 28;
    }

    function pintarRejillaHorario({ rejilla, titulo, franjas, lunes, hoy, textos, raizAlto }) {
        if (!rejilla || !lunes || !textos) {
            return;
        }
        const ingles = textos.codigo === "EN";
        const domingo = new Date(lunes.getFullYear(), lunes.getMonth(), lunes.getDate() + 6);
        if (titulo) {
            const mismoMes = lunes.getMonth() === domingo.getMonth();
            titulo.textContent = mismoMes
                ? `${lunes.getDate()}–${domingo.getDate()} ${textos.meses[lunes.getMonth()]} ${lunes.getFullYear()}`
                : `${lunes.getDate()} ${textos.meses[lunes.getMonth()]} – ${domingo.getDate()} ${textos.meses[domingo.getMonth()]} ${domingo.getFullYear()}`;
        }
        rejilla.replaceChildren();

        const marco = document.createElement("div");
        marco.className = "horario-marco";
        const horas = crearEjeHoras();
        const dias = document.createElement("div");
        dias.className = "horario-dias";
        const pxHora = altoHora(raizAlto);
        const porDia = new Map();
        (franjas || []).forEach((franja) => {
            const lista = porDia.get(franja.dia) || [];
            lista.push(franja);
            porDia.set(franja.dia, lista);
        });
        for (let indice = 0; indice < 7; indice += 1) {
            dias.append(crearColumnaDia(indice, porDia.get(indice) || [], ingles, pxHora, lunes, hoy, textos));
        }
        marco.append(horas, dias);
        rejilla.append(marco);
        dibujarLineaAhora(dias, domingo, pxHora, lunes, hoy);
    }

    function crearEjeHoras() {
        const horas = document.createElement("div");
        horas.className = "horario-horas";
        const hueco = document.createElement("span");
        hueco.className = "horario-hueco";
        horas.append(hueco);
        for (let hora = HORA_INICIO; hora < HORA_FIN; hora += 1) {
            const etiqueta = document.createElement("span");
            etiqueta.className = "horario-hora";
            etiqueta.textContent = String(hora);
            horas.append(etiqueta);
        }
        return horas;
    }

    function crearColumnaDia(indice, franjasDelDia, ingles, pxHora, lunes, hoy, textos) {
        const fecha = new Date(lunes.getFullYear(), lunes.getMonth(), lunes.getDate() + indice);
        const columna = document.createElement("div");
        columna.className = "horario-dia";
        const cabecera = document.createElement("header");
        const letra = document.createElement("span");
        letra.textContent = textos.diasHorario[indice];
        const numero = document.createElement("span");
        numero.className = "horario-fecha";
        numero.textContent = String(fecha.getDate());
        const referencia = hoy || new Date();
        const esHoy = fecha.getDate() === referencia.getDate()
            && fecha.getMonth() === referencia.getMonth()
            && fecha.getFullYear() === referencia.getFullYear();
        if (esHoy) {
            numero.classList.add("hoy");
            columna.classList.add("hoy");
        }
        cabecera.append(letra, numero);

        const pista = document.createElement("div");
        pista.className = "horario-pista";
        pista.style.height = `${(HORA_FIN - HORA_INICIO) * pxHora}px`;
        layoutFranjas(franjasDelDia, pxHora).forEach((franja) => {
            pista.append(crearBloqueFranja(franja, ingles, textos));
        });
        columna.append(cabecera, pista);
        return columna;
    }

    function crearBloqueFranja(franja, ingles, textos) {
        const bloque = document.createElement("div");
        bloque.className = "franja";
        bloque.dataset.codigo = franja.codigo;
        bloque.style.top = `${franja.y0}px`;
        bloque.style.height = `${franja.alto}px`;
        bloque.style.maxHeight = `${franja.alto}px`;
        bloque.style.left = `calc(${(franja.columna * 100) / franja.columnasVisibles}% + 1px)`;
        bloque.style.width = `calc(${100 / franja.columnasVisibles}% - 2px)`;
        bloque.style.zIndex = String(2 + Math.floor(minutosFranja(franja.inicio) / 30));
        bloque.style.background = tonoFranja(franja.codigo);
        const nombre = ingles ? franja.nombre_ingles : franja.nombre;
        const tipo = franja.tipo === "tutoria"
            ? textos.tutorias
            : (franja.tipo === "teoria" ? textos.teoria : textos.practicas);
        if (franja.tipo === "tutoria") {
            bloque.classList.add("franja-tutoria");
        }
        const grupo = franja.grupo ? ` · ${franja.grupo}` : "";
        const aula = franja.aula ? ` · ${franja.aula}` : "";
        bloque.title = `${nombre} · ${tipo}${grupo}${aula} · ${franja.inicio}–${franja.fin}`;
        const fuerte = document.createElement("strong");
        fuerte.textContent = nombre;
        const detalle = document.createElement("span");
        detalle.textContent = franja.grupo ? `${tipo} · ${franja.grupo}` : tipo;
        bloque.append(fuerte, detalle);
        return bloque;
    }

    function dibujarLineaAhora(dias, domingo, pxHora, lunes, hoy) {
        const referencia = hoy || new Date();
        const yAhora = topAhora(referencia, pxHora);
        const finDia = new Date(domingo.getFullYear(), domingo.getMonth(), domingo.getDate() + 1);
        const contieneHoy = yAhora !== null && referencia >= lunes && referencia < finDia;
        if (!contieneHoy) {
            return;
        }
        const linea = document.createElement("div");
        linea.className = "linea-ahora";
        const altoCabecera = dias.querySelector("header")?.offsetHeight || 0;
        linea.style.top = `${altoCabecera + yAhora}px`;
        dias.append(linea);
    }

    function lunesDe(fecha) {
        const delta = fecha.getDay() === 0 ? -6 : 1 - fecha.getDay();
        return new Date(fecha.getFullYear(), fecha.getMonth(), fecha.getDate() + delta);
    }

    /** Cuatrimestre de una fecha: usa inicio del 2.º del calendario ESIIAB si viene en la matrícula. */
    function cuatrimestreDeFecha(fecha, inicioSegundoIso) {
        if (inicioSegundoIso) {
            const partes = String(inicioSegundoIso).slice(0, 10).split("-").map(Number);
            if (partes.length === 3 && partes.every((n) => Number.isFinite(n))) {
                const inicio = new Date(partes[0], partes[1] - 1, partes[2]);
                const dia = new Date(fecha.getFullYear(), fecha.getMonth(), fecha.getDate());
                return dia >= inicio ? 2 : 1;
            }
        }
        const mes = fecha.getMonth() + 1;
        return mes >= 9 || mes === 1 ? 1 : 2;
    }

    function desplazamientoLunes(diaJs) {
        return diaJs === 0 ? 6 : diaJs - 1;
    }

    function minutosFranja(hora) {
        const [horas, minutos] = String(hora).split(":").map(Number);
        return horas * 60 + minutos;
    }

    function topFranja(hora, pxHora) {
        return ((minutosFranja(hora) - HORA_INICIO * 60) / 60) * pxHora;
    }

    function topAhora(fecha, pxHora) {
        const minutos = fecha.getHours() * 60 + fecha.getMinutes();
        if (minutos < HORA_INICIO * 60 || minutos > HORA_FIN * 60) {
            return null;
        }
        return ((minutos - HORA_INICIO * 60) / 60) * pxHora;
    }

    function tonoFranja(codigo) {
        return TONOS_FRANJA[Number(codigo) % TONOS_FRANJA.length];
    }

    // ESIIAB a veces choca 5 min (p.ej. Gestión 16:00-17:35 y Procesos 17:30-19:00).
    // Eso no debe partir la columna a la mitad: se tratan como consecutivas.
    const SOLAPE_MINIMO_MINUTOS = 6;

    function minutosSolape(una, otra) {
        const inicio = Math.max(minutosFranja(una.inicio), minutosFranja(otra.inicio));
        const fin = Math.min(minutosFranja(una.fin), minutosFranja(otra.fin));
        return Math.max(0, fin - inicio);
    }

    function solapan(una, otra) {
        return minutosSolape(una, otra) >= SOLAPE_MINIMO_MINUTOS;
    }

    function colocarFranjas(franjas) {
        const ordenadas = [...franjas].sort(
            (a, b) => a.inicio.localeCompare(b.inicio) || a.fin.localeCompare(b.fin) || a.codigo.localeCompare(b.codigo),
        );
        const n = ordenadas.length;
        if (n === 0) {
            return [];
        }

        // Componentes conexos solo por solapes reales (>= SOLAPE_MINIMO_MINUTOS).
        const padre = ordenadas.map((_, indice) => indice);
        const encontrar = (i) => {
            let actual = i;
            while (padre[actual] !== actual) {
                padre[actual] = padre[padre[actual]];
                actual = padre[actual];
            }
            return actual;
        };
        const unir = (i, j) => {
            const a = encontrar(i);
            const b = encontrar(j);
            if (a !== b) {
                padre[b] = a;
            }
        };
        for (let i = 0; i < n; i += 1) {
            for (let j = i + 1; j < n; j += 1) {
                if (solapan(ordenadas[i], ordenadas[j])) {
                    unir(i, j);
                }
            }
        }

        const grupos = new Map();
        ordenadas.forEach((franja, indice) => {
            const raiz = encontrar(indice);
            const lista = grupos.get(raiz) || [];
            lista.push(indice);
            grupos.set(raiz, lista);
        });

        const resultado = new Array(n);
        grupos.forEach((indices) => {
            // Columnas 0..k solo dentro del grupo: un solape de tarde no estrecha la mañana.
            const finPorColumna = [];
            const locales = indices
                .slice()
                .sort((a, b) => ordenadas[a].inicio.localeCompare(ordenadas[b].inicio)
                    || ordenadas[a].fin.localeCompare(ordenadas[b].fin)
                    || ordenadas[a].codigo.localeCompare(ordenadas[b].codigo));
            locales.forEach((indice) => {
                const franja = ordenadas[indice];
                let columna = finPorColumna.findIndex(
                    (fin) => minutosFranja(fin) <= minutosFranja(franja.inicio),
                );
                if (columna < 0) {
                    columna = finPorColumna.length;
                    finPorColumna.push(franja.fin);
                } else {
                    finPorColumna[columna] = franja.fin;
                }
                resultado[indice] = {
                    ...franja,
                    columna,
                    columnasVisibles: 1,
                };
            });
            const total = Math.max(finPorColumna.length, 1);
            locales.forEach((indice) => {
                resultado[indice].columnasVisibles = total;
            });
        });
        return resultado;
    }

    function layoutFranjas(franjas, pxHora) {
        const HUECO = 4;
        const colocadas = colocarFranjas(franjas).map((franja) => {
            const y0 = Math.round(topFranja(franja.inicio, pxHora));
            const y1 = Math.round(topFranja(franja.fin, pxHora));
            return {
                ...franja,
                y0,
                y1,
                alto: Math.max(y1 - y0 - HUECO, 12),
            };
        });
        // En la misma columna, una franja nunca puede pintar encima de la siguiente
        // (consecutivas 13:05|13:05 o redondeos de píxel).
        const porColumna = new Map();
        colocadas.forEach((franja, indice) => {
            const lista = porColumna.get(franja.columna) || [];
            lista.push(indice);
            porColumna.set(franja.columna, lista);
        });
        porColumna.forEach((indices) => {
            indices.sort((a, b) => colocadas[a].y0 - colocadas[b].y0 || colocadas[a].y1 - colocadas[b].y1);
            for (let i = 0; i < indices.length - 1; i += 1) {
                const actual = colocadas[indices[i]];
                const siguiente = colocadas[indices[i + 1]];
                const maxAlto = Math.max(siguiente.y0 - actual.y0 - HUECO, 10);
                if (actual.alto > maxAlto) {
                    actual.alto = maxAlto;
                }
            }
        });
        return colocadas;
    }

    function iconoCampana() {
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("viewBox", "0 0 24 24");
        svg.setAttribute("aria-hidden", "true");
        const cuerpo = document.createElementNS("http://www.w3.org/2000/svg", "path");
        cuerpo.setAttribute("d", "M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9");
        cuerpo.setAttribute("fill", "none");
        cuerpo.setAttribute("stroke", "currentColor");
        cuerpo.setAttribute("stroke-width", "1.6");
        cuerpo.setAttribute("stroke-linecap", "round");
        cuerpo.setAttribute("stroke-linejoin", "round");
        const badajo = document.createElementNS("http://www.w3.org/2000/svg", "path");
        badajo.setAttribute("d", "M10.3 21a1.94 1.94 0 0 0 3.4 0");
        badajo.setAttribute("fill", "none");
        badajo.setAttribute("stroke", "currentColor");
        badajo.setAttribute("stroke-width", "1.6");
        badajo.setAttribute("stroke-linecap", "round");
        badajo.setAttribute("stroke-linejoin", "round");
        svg.append(cuerpo, badajo);
        return svg;
    }

    function iconoEstrella() {
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("viewBox", "0 0 12 12");
        svg.setAttribute("class", "estrella");
        svg.setAttribute("aria-hidden", "true");
        const trazo = document.createElementNS("http://www.w3.org/2000/svg", "path");
        trazo.setAttribute("d", "M6 0.8l1.35 3.05 3.3.28-2.5 2.15.78 3.22L6 8.05 2.07 9.5l.78-3.22L.35 4.13l3.3-.28z");
        trazo.setAttribute("fill", "currentColor");
        svg.append(trazo);
        return svg;
    }

    function iconoPunto() {
        const punto = document.createElement("span");
        punto.className = "punto";
        return punto;
    }

    function bloqueGrupo(titulo, aula, personas) {
        const bloque = document.createElement("section");
        bloque.className = "ficha-bloque";
        const cabecera = document.createElement("div");
        cabecera.className = "ficha-titulo";
        const nombre = document.createElement("span");
        nombre.textContent = titulo;
        cabecera.append(nombre);
        if (aula) {
            const lugar = document.createElement("span");
            lugar.textContent = aula;
            cabecera.append(lugar);
        }
        bloque.append(cabecera);
        personas.forEach((persona) => {
            const fila = document.createElement("div");
            fila.className = "ficha-persona";
            const insignia = document.createElement("span");
            insignia.className = "insignia";
            insignia.append(iconoPersona());
            const cuerpo = document.createElement("div");
            cuerpo.className = "ficha-persona-cuerpo";
            const texto = persona.url ? enlaceFicha(persona.nombre, persona.url) : document.createElement("span");
            if (!persona.url) {
                texto.textContent = persona.nombre;
            }
            texto.classList.add("ficha-persona-nombre");
            cuerpo.append(texto);
            const lineas = persona.lineas || [];
            if (lineas.length) {
                const tutorias = document.createElement("div");
                tutorias.className = "ficha-tutorias";
                lineas.forEach((linea) => {
                    const franja = document.createElement("div");
                    franja.className = "ficha-tutoria";
                    franja.textContent = linea;
                    tutorias.append(franja);
                });
                cuerpo.append(tutorias);
            } else if (persona.lado) {
                const lado = document.createElement("span");
                lado.className = "ficha-lado";
                lado.textContent = persona.lado;
                cuerpo.append(lado);
            }
            fila.append(insignia, cuerpo);
            bloque.append(fila);
        });
        return bloque;
    }

    function enlaceFicha(texto, href) {
        const enlace = document.createElement("a");
        enlace.href = href;
        enlace.target = "_blank";
        enlace.rel = "noopener noreferrer";
        enlace.textContent = texto;
        return enlace;
    }

    function iconoPersona() {
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("viewBox", "0 0 24 24");
        svg.setAttribute("aria-hidden", "true");
        const cabeza = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        cabeza.setAttribute("cx", "12");
        cabeza.setAttribute("cy", "8");
        cabeza.setAttribute("r", "3.2");
        cabeza.setAttribute("fill", "none");
        cabeza.setAttribute("stroke", "currentColor");
        cabeza.setAttribute("stroke-width", "1.6");
        const cuerpo = document.createElementNS("http://www.w3.org/2000/svg", "path");
        cuerpo.setAttribute("d", "M5.5 19.2c1.2-3 3.4-4.4 6.5-4.4s5.3 1.4 6.5 4.4");
        cuerpo.setAttribute("fill", "none");
        cuerpo.setAttribute("stroke", "currentColor");
        cuerpo.setAttribute("stroke-width", "1.6");
        cuerpo.setAttribute("stroke-linecap", "round");
        svg.append(cabeza, cuerpo);
        return svg;
    }

    VistaAgenda.pintarRejillaHorario = pintarRejillaHorario;
    VistaAgenda.lunesDe = lunesDe;
    VistaAgenda.cuatrimestreDeFecha = cuatrimestreDeFecha;

    return VistaAgenda;
})();
