const VistaAgenda = (() => {
    const HORA_INICIO = 8;
    const HORA_FIN = 20;
    const TONOS_FRANJA = ["#9d1830", "#7a1528", "#c45c6c", "#5c101c", "#a33d4e", "#8e3044"];

    class VistaAgenda {
        constructor({ alBuscar, alAbrirPerfil, alCambiarTema, alCambiarIdioma, alLeer, alCambiarMes }) {
            this.seccion = document.getElementById("vistaAgenda");
            this.lista = document.getElementById("listaAsignaturas");
            this.vacio = document.getElementById("sinAsignaturas");
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
            this.avisos = [];
            this.preferenciasAvisos = PreferenciasNotificaciones.leer();
            this.abierta = null;
            this.hoy = new Date();
            this.lunes = lunesDe(this.hoy);
            this.reloj = null;
            this.vista = new Date(this.hoy.getFullYear(), this.hoy.getMonth(), 1);
            this.alBuscar = alBuscar;
            this.alCambiarMes = alCambiarMes;
            this.temporizador = null;
            document.getElementById("botonPerfil").addEventListener("click", alAbrirPerfil);
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
            this.prepararLeyenda();
            this.aplicarPreferenciasAvisos(this.preferenciasAvisos);
            window.addEventListener("resize", () => {
                if (this.seccion.hidden) {
                    return;
                }
                clearTimeout(this.redibujo);
                this.redibujo = setTimeout(() => this.pintarHorario(), 120);
            });
        }

        prepararLeyenda() {
            const iconos = document.querySelectorAll("#leyendaCalendario .leyenda-icono");
            if (!iconos.length) {
                return;
            }
            iconos[0].replaceChildren(iconoEstrella());
            if (iconos[1]) {
                iconos[1].classList.add("punto");
            }
        }

        mostrar(usuario, textos) {
            this.usuario = usuario;
            this.textos = textos;
            this.seccion.hidden = false;
            this.nick.textContent = usuario.nick;
            aplicarTextos(this.seccion, textos);
            this.buscador.placeholder = textos.buscarAsignatura;
            this.abierta = null;
            this.ficha.hidden = true;
            this.buscador.closest(".buscador").hidden = false;
            this.lista.hidden = false;
            this.preferenciasAvisos = PreferenciasNotificaciones.leer();
            this.aplicarPreferenciasAvisos(this.preferenciasAvisos);
            this.rellenarSelectores();
            this.pintarCalendario();
            this.pintarHorario();
            this.actualizarAvisos();
            this.iniciarReloj();
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
            const yAhora = topAhora(this.hoy);
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

        pintar(asignaturas, marcas, horario, marcasAntelacion) {
            this.asignaturas = asignaturas;
            this.marcas = marcas;
            if (marcasAntelacion !== undefined) {
                this.marcasAntelacion = marcasAntelacion;
            }
            if (horario) {
                this.horario = horario;
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
                this.pintarHorario();
                this.actualizarAvisos();
                return;
            }
            this.pintarLista();
            this.pintarCalendario();
            this.pintarHorario();
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
                horario: this.franjasVisibles(),
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
            this.vacio.hidden = this.asignaturas.length > 0;
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

            this.rejilla.replaceChildren();
            for (let indice = 0; indice < 42; indice += 1) {
                const fechaCelda = new Date(
                    primeraCelda.getFullYear(),
                    primeraCelda.getMonth(),
                    primeraCelda.getDate() + indice,
                );
                const celda = this.crearCeldaDia({
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
                });
                this.rejilla.append(celda);
            }
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

            simbolos.forEach((simbolo) => {
                const icono = simbolo.tipo === "estrella" ? iconoEstrella() : iconoPunto();
                const nombre = ingles ? simbolo.nombre_ingles : simbolo.nombre;
                const etiqueta = simbolo.tipo === "estrella" ? this.textos.examen : this.textos.entrega;
                icono.dataset.tipo = simbolo.tipo;
                icono.dataset.nombre = nombre;
                icono.setAttribute("title", `${etiqueta}: ${nombre}`);
                (simbolo.tipo === "estrella" ? estrellas : puntos).append(icono);
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
                        const icono = simbolo.tipo === "estrella" ? iconoEstrella() : iconoPunto();
                        const tipo = document.createElement("strong");
                        tipo.textContent = simbolo.tipo === "estrella" ? this.textos.examen : this.textos.entrega;
                        const nombre = document.createElement("span");
                        nombre.className = "actividad-nombre";
                        nombre.textContent = ingles ? simbolo.nombre_ingles : simbolo.nombre;
                        cabecera.append(icono, tipo, nombre);
                        const detalle = document.createElement("p");
                        detalle.className = "actividad-detalle";
                        if (simbolo.tipo === "estrella") {
                            detalle.textContent = simbolo.lugar
                                ? `${simbolo.hora} · ${simbolo.lugar}`
                                : simbolo.hora;
                        } else {
                            detalle.textContent = `${this.textos.hastaLas} ${simbolo.hora}`;
                        }
                        item.append(cabecera, detalle);
                        this.listaDialogo.append(item);
                    });
            }
            this.dialogo.showModal();
        }

        marcasVisibles() {
            return this.filtrarMarcas(this.marcas);
        }

        filtrarMarcas(marcas) {
            const codigos = new Set(this.asignaturas.map((asignatura) => asignatura.codigo));
            return (marcas || [])
                .map((marca) => ({
                    dia: marca.dia,
                    simbolos: (marca.simbolos || []).filter((simbolo) => {
                        if (this.abierta) {
                            return simbolo.codigo === this.abierta.codigo;
                        }
                        return codigos.has(simbolo.codigo);
                    }),
                }))
                .filter((marca) => marca.simbolos.length);
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

        franjasVisibles() {
            if (!this.abierta) {
                return this.horario;
            }
            return this.horario.filter((franja) => franja.codigo === this.abierta.codigo);
        }

        cambiarSemana(delta) {
            this.lunes = new Date(this.lunes.getFullYear(), this.lunes.getMonth(), this.lunes.getDate() + delta * 7);
            this.pintarHorario();
        }

        pintarHorario() {
            const rejilla = document.getElementById("rejillaHorario");
            const titulo = document.getElementById("tituloSemana");
            const ingles = this.textos.codigo === "EN";
            const domingo = new Date(this.lunes.getFullYear(), this.lunes.getMonth(), this.lunes.getDate() + 6);
            const mismoMes = this.lunes.getMonth() === domingo.getMonth();
            titulo.textContent = mismoMes
                ? `${this.lunes.getDate()}–${domingo.getDate()} ${this.textos.meses[this.lunes.getMonth()]} ${this.lunes.getFullYear()}`
                : `${this.lunes.getDate()} ${this.textos.meses[this.lunes.getMonth()]} – ${domingo.getDate()} ${this.textos.meses[domingo.getMonth()]} ${domingo.getFullYear()}`;
            rejilla.replaceChildren();

            const marco = document.createElement("div");
            marco.className = "horario-marco";
            const horas = this.crearEjeHoras();
            const dias = document.createElement("div");
            dias.className = "horario-dias";

            const porDia = new Map();
            this.franjasVisibles().forEach((franja) => {
                const lista = porDia.get(franja.dia) || [];
                lista.push(franja);
                porDia.set(franja.dia, lista);
            });

            for (let indice = 0; indice < 7; indice += 1) {
                dias.append(this.crearColumnaDia(indice, porDia.get(indice) || [], ingles));
            }

            marco.append(horas, dias);
            rejilla.append(marco);
            this.dibujarLineaAhora(dias, domingo);
        }

        crearEjeHoras() {
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

        crearColumnaDia(indice, franjasDelDia, ingles) {
            const fecha = new Date(this.lunes.getFullYear(), this.lunes.getMonth(), this.lunes.getDate() + indice);
            const columna = document.createElement("div");
            columna.className = "horario-dia";
            const cabecera = document.createElement("header");
            const letra = document.createElement("span");
            letra.textContent = this.textos.diasHorario[indice];
            const numero = document.createElement("span");
            numero.className = "horario-fecha";
            numero.textContent = String(fecha.getDate());
            const esHoy = fecha.getDate() === this.hoy.getDate()
                && fecha.getMonth() === this.hoy.getMonth()
                && fecha.getFullYear() === this.hoy.getFullYear();
            if (esHoy) {
                numero.classList.add("hoy");
                columna.classList.add("hoy");
            }
            cabecera.append(letra, numero);

            const pista = document.createElement("div");
            pista.className = "horario-pista";
            pista.style.height = `${(HORA_FIN - HORA_INICIO) * altoHora()}px`;
            colocarFranjas(franjasDelDia).forEach((franja) => {
                pista.append(this.crearBloqueFranja(franja, ingles));
            });
            columna.append(cabecera, pista);
            return columna;
        }

        crearBloqueFranja(franja, ingles) {
            const bloque = document.createElement("div");
            bloque.className = "franja";
            bloque.dataset.codigo = franja.codigo;
            bloque.style.top = `${topFranja(franja.inicio)}px`;
            bloque.style.height = `${Math.max(topFranja(franja.fin) - topFranja(franja.inicio) - 2, 16)}px`;
            bloque.style.left = `calc(${(franja.columna * 100) / franja.columnasVisibles}% + 1px)`;
            bloque.style.width = `calc(${100 / franja.columnasVisibles}% - 2px)`;
            bloque.style.background = tonoFranja(franja.codigo);
            const nombre = ingles ? franja.nombre_ingles : franja.nombre;
            const tipo = franja.tipo === "teoria" ? this.textos.teoria : this.textos.practicas;
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

        dibujarLineaAhora(dias, domingo) {
            const yAhora = topAhora(this.hoy);
            const finDia = new Date(domingo.getFullYear(), domingo.getMonth(), domingo.getDate() + 1);
            const contieneHoy = yAhora !== null && this.hoy >= this.lunes && this.hoy < finDia;
            if (!contieneHoy) {
                return;
            }
            const linea = document.createElement("div");
            linea.className = "linea-ahora";
            const altoCabecera = dias.querySelector("header")?.offsetHeight || 0;
            linea.style.top = `${altoCabecera + yAhora}px`;
            dias.append(linea);
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

    function altoHora() {
        const crudo = getComputedStyle(document.querySelector(".agenda-horario")).getPropertyValue("--alto-hora");
        const valor = parseFloat(crudo);
        return Number.isFinite(valor) && valor > 0 ? valor : 18;
    }

    function lunesDe(fecha) {
        const delta = fecha.getDay() === 0 ? -6 : 1 - fecha.getDay();
        return new Date(fecha.getFullYear(), fecha.getMonth(), fecha.getDate() + delta);
    }

    function desplazamientoLunes(diaJs) {
        return diaJs === 0 ? 6 : diaJs - 1;
    }

    function minutosFranja(hora) {
        const [horas, minutos] = hora.split(":").map(Number);
        return horas * 60 + minutos;
    }

    function topFranja(hora) {
        return ((minutosFranja(hora) - HORA_INICIO * 60) / 60) * altoHora();
    }

    function topAhora(fecha) {
        const minutos = fecha.getHours() * 60 + fecha.getMinutes();
        if (minutos < HORA_INICIO * 60 || minutos > HORA_FIN * 60) {
            return null;
        }
        return ((minutos - HORA_INICIO * 60) / 60) * altoHora();
    }

    function tonoFranja(codigo) {
        return TONOS_FRANJA[Number(codigo) % TONOS_FRANJA.length];
    }

    function solapan(una, otra) {
        return una.inicio < otra.fin && otra.inicio < una.fin;
    }

    function colocarFranjas(franjas) {
        // 1) Ordenar por inicio.
        const ordenadas = [...franjas].sort(
            (a, b) => a.inicio.localeCompare(b.inicio) || a.codigo.localeCompare(b.codigo),
        );
        // 2) Asignar la primera columna libre (finPorColumna guarda hasta cuándo está ocupada).
        const finPorColumna = [];
        const conColumna = ordenadas.map((franja) => {
            let columna = finPorColumna.findIndex((fin) => fin <= franja.inicio);
            if (columna < 0) {
                columna = finPorColumna.length;
                finPorColumna.push(franja.fin);
            } else {
                finPorColumna[columna] = franja.fin;
            }
            return { ...franja, columna };
        });
        // 3) El ancho depende de cuántas columnas usa el grupo que solapa.
        return conColumna.map((franja) => {
            const grupo = conColumna.filter((otra) => solapan(franja, otra));
            const columnasVisibles = Math.max(...grupo.map((otra) => otra.columna)) + 1;
            return { ...franja, columnasVisibles };
        });
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

    return VistaAgenda;
})();
