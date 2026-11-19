const PreferenciasNotificaciones = (() => {
    const CLAVE = "preferenciasNotificaciones";
    const UNIDADES = new Set(["dias", "semanas", "mes", "curso"]);
    const POR_DEFECTO = {
        icono: "campana",
        antelacion: { valor: 2, unidad: "semanas" },
        avisos: {
            examenes: true,
            entregas: true,
            horarioHoy: true,
        },
    };

    function leer() {
        try {
            const crudo = localStorage.getItem(CLAVE);
            if (!crudo) {
                return estructurar(POR_DEFECTO);
            }
            return estructurar(JSON.parse(crudo));
        } catch {
            return estructurar(POR_DEFECTO);
        }
    }

    function guardar(preferencias) {
        const limpias = estructurar(preferencias);
        localStorage.setItem(CLAVE, JSON.stringify(limpias));
        return limpias;
    }

    function unidadValida(unidad) {
        return UNIDADES.has(unidad) ? unidad : "semanas";
    }

    function valorValido(valor, unidad) {
        if (unidad === "curso") {
            return 1;
        }
        const numero = Math.floor(Number(valor));
        if (!Number.isFinite(numero) || numero < 1) {
            return 1;
        }
        if (unidad === "dias") {
            return Math.min(numero, 366);
        }
        if (unidad === "mes") {
            return Math.min(numero, 12);
        }
        return Math.min(numero, 52);
    }

    function antelacionDe(entrada) {
        if (entrada && entrada.antelacion) {
            const unidad = unidadValida(entrada.antelacion.unidad);
            return {
                valor: valorValido(entrada.antelacion.valor, unidad),
                unidad,
            };
        }
        // Compatibilidad con la preferencia antigua de 1/2/3 semanas.
        if (entrada && entrada.semanasAnticipacion) {
            const semanas = Number(entrada.semanasAnticipacion);
            return {
                valor: semanas === 1 || semanas === 2 || semanas === 3 ? semanas : 2,
                unidad: "semanas",
            };
        }
        return { ...POR_DEFECTO.antelacion };
    }

    function estructurar(entrada) {
        const avisos = entrada && entrada.avisos ? entrada.avisos : {};
        return {
            icono: "campana",
            antelacion: antelacionDe(entrada),
            avisos: {
                examenes: avisos.examenes !== false,
                entregas: avisos.entregas !== false,
                horarioHoy: avisos.horarioHoy !== false,
            },
        };
    }

    function finDeCurso(ahora) {
        // Curso académico UCLM: septiembre → junio.
        const anioFin = ahora.getMonth() >= 8 ? ahora.getFullYear() + 1 : ahora.getFullYear();
        const fin = new Date(anioFin, 5, 30);
        if (fin < ahora) {
            return new Date(anioFin + 1, 5, 30);
        }
        return fin;
    }

    function limiteAntelacion(preferencias, ahora = new Date()) {
        const prefs = estructurar(preferencias || leer());
        const inicio = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate());
        const { valor, unidad } = prefs.antelacion;
        if (unidad === "curso") {
            return finDeCurso(inicio);
        }
        if (unidad === "mes") {
            return new Date(inicio.getFullYear(), inicio.getMonth() + valor, inicio.getDate());
        }
        if (unidad === "dias") {
            return new Date(inicio.getFullYear(), inicio.getMonth(), inicio.getDate() + valor);
        }
        return new Date(inicio.getFullYear(), inicio.getMonth(), inicio.getDate() + valor * 7);
    }

    function periodosHasta(limite, desde = new Date()) {
        const periodos = [];
        let anio = desde.getFullYear();
        let mes = desde.getMonth() + 1;
        const anioFin = limite.getFullYear();
        const mesFin = limite.getMonth() + 1;
        while (anio < anioFin || (anio === anioFin && mes <= mesFin)) {
            periodos.push({ anio, mes });
            mes += 1;
            if (mes > 12) {
                mes = 1;
                anio += 1;
            }
            if (periodos.length > 14) {
                break;
            }
        }
        if (!periodos.length) {
            periodos.push({ anio: desde.getFullYear(), mes: desde.getMonth() + 1 });
        }
        return periodos;
    }

    function formatearFecha(iso, textos) {
        if (!iso) {
            return "";
        }
        const [anio, mes, dia] = iso.split("-").map(Number);
        if (!anio || !mes || !dia) {
            return iso;
        }
        const meses = textos.meses || [];
        const nombreMes = meses[mes - 1] || String(mes);
        return `${dia} ${nombreMes} ${anio}`;
    }

    function construirAvisos({
        marcas,
        horario,
        textos,
        preferencias,
        ahora = new Date(),
        mesVista = ahora,
        codigosMatricula = null,
    }) {
        const prefs = estructurar(preferencias || leer());
        const avisos = [];
        const ingles = textos.codigo === "EN";
        const inicioHoy = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate());
        const limite = limiteAntelacion(prefs, ahora);
        const codigos = codigosMatricula ? new Set(codigosMatricula) : null;

        if (prefs.avisos.examenes || prefs.avisos.entregas) {
            (marcas || []).forEach((marca) => {
                (marca.simbolos || []).forEach((simbolo) => {
                    if (codigos && !codigos.has(simbolo.codigo)) {
                        return;
                    }
                    const fechaIso = simbolo.fecha
                        || `${mesVista.getFullYear()}-${String(mesVista.getMonth() + 1).padStart(2, "0")}-${String(marca.dia).padStart(2, "0")}`;
                    const [anio, mes, dia] = fechaIso.split("-").map(Number);
                    const fecha = new Date(anio, mes - 1, dia);
                    if (fecha < inicioHoy || fecha > limite) {
                        return;
                    }
                    if (simbolo.tipo !== "estrella" && simbolo.tipo !== "punto") {
                        return;
                    }
                    const esExamen = simbolo.tipo === "estrella";
                    if (esExamen && !prefs.avisos.examenes) {
                        return;
                    }
                    if (!esExamen && !prefs.avisos.entregas) {
                        return;
                    }
                    const nombre = ingles ? simbolo.nombre_ingles : simbolo.nombre;
                    const tipo = esExamen ? textos.examen : textos.entrega;
                    const fechaTexto = formatearFecha(fechaIso, textos);
                    const fin = `${textos.fechaFinalizacion}: ${fechaTexto}`;
                    const hora = esExamen
                        ? `${simbolo.hora}${simbolo.lugar ? ` · ${simbolo.lugar}` : ""}`
                        : `${textos.hastaLas} ${simbolo.hora}`;
                    avisos.push({
                        id: `${simbolo.tipo}-${fechaIso}-${simbolo.codigo}-${simbolo.hora}`,
                        tipo: esExamen ? "examen" : "entrega",
                        titulo: `${tipo}: ${nombre}`,
                        detalle: `${fin} · ${hora}`,
                        fechaIso,
                    });
                });
            });
        }

        if (prefs.avisos.horarioHoy && horario) {
            const diaSemana = (ahora.getDay() + 6) % 7;
            horario
                .filter((franja) => franja.dia === diaSemana)
                .forEach((franja) => {
                    const nombre = ingles ? franja.nombre_ingles : franja.nombre;
                    const tipo = franja.tipo === "tutoria"
                        ? textos.tutorias
                        : (franja.tipo === "teoria" ? textos.teoria : textos.practicas);
                    avisos.push({
                        id: `horario-${franja.codigo}-${franja.inicio}`,
                        tipo: "horario",
                        titulo: `${textos.avisoHorarioHoy}: ${nombre}`,
                        detalle: `${tipo} · ${franja.inicio}–${franja.fin}`,
                        fechaIso: null,
                    });
                });
        }

        avisos.sort((a, b) => {
            if (a.fechaIso && b.fechaIso && a.fechaIso !== b.fechaIso) {
                return a.fechaIso.localeCompare(b.fechaIso);
            }
            if (a.fechaIso && !b.fechaIso) {
                return -1;
            }
            if (!a.fechaIso && b.fechaIso) {
                return 1;
            }
            return a.titulo.localeCompare(b.titulo);
        });
        return avisos;
    }

    const CLAVE_ESTADO = "estadoAvisosNotificaciones";

    function leerEstado() {
        try {
            const crudo = localStorage.getItem(CLAVE_ESTADO);
            if (!crudo) {
                return { leidos: [], eliminados: [] };
            }
            const entrada = JSON.parse(crudo);
            return {
                leidos: Array.isArray(entrada.leidos) ? entrada.leidos.map(String) : [],
                eliminados: Array.isArray(entrada.eliminados) ? entrada.eliminados.map(String) : [],
            };
        } catch {
            return { leidos: [], eliminados: [] };
        }
    }

    function guardarEstado(estado) {
        const limpio = {
            leidos: [...new Set((estado.leidos || []).map(String))],
            eliminados: [...new Set((estado.eliminados || []).map(String))],
        };
        localStorage.setItem(CLAVE_ESTADO, JSON.stringify(limpio));
        return limpio;
    }

    function filtrarAvisosActivos(avisos) {
        const estado = leerEstado();
        const eliminados = new Set(estado.eliminados);
        return (avisos || []).filter((aviso) => !eliminados.has(String(aviso.id)));
    }

    function estaLeido(id) {
        return leerEstado().leidos.includes(String(id));
    }

    function marcarLeido(id) {
        const estado = leerEstado();
        const clave = String(id);
        if (!estado.leidos.includes(clave)) {
            estado.leidos.push(clave);
        }
        return guardarEstado(estado);
    }

    function marcarTodosLeidos(ids) {
        const estado = leerEstado();
        (ids || []).forEach((id) => {
            const clave = String(id);
            if (!estado.leidos.includes(clave)) {
                estado.leidos.push(clave);
            }
        });
        return guardarEstado(estado);
    }

    function eliminarTodos(ids) {
        const estado = leerEstado();
        (ids || []).forEach((id) => {
            const clave = String(id);
            if (!estado.eliminados.includes(clave)) {
                estado.eliminados.push(clave);
            }
        });
        return guardarEstado(estado);
    }

    return {
        leer,
        guardar,
        construirAvisos,
        estructurar,
        limiteAntelacion,
        periodosHasta,
        leerEstado,
        filtrarAvisosActivos,
        estaLeido,
        marcarLeido,
        marcarTodosLeidos,
        eliminarTodos,
    };
})();