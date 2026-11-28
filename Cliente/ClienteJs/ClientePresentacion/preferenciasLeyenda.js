const PreferenciasLeyenda = (() => {
    const CLAVE = "preferenciasLeyendaCalendario";
    const POR_DEFECTO = {
        estrella: true,
        punto: true,
        secretaria: true,
        cambio_cuatrimestre: true,
        festivo: true,
        vacaciones: true,
        semana_examenes: true,
        periodo: true,
    };

    function leer() {
        try {
            const crudo = localStorage.getItem(CLAVE);
            if (!crudo) {
                return { ...POR_DEFECTO };
            }
            return { ...POR_DEFECTO, ...JSON.parse(crudo) };
        } catch {
            return { ...POR_DEFECTO };
        }
    }

    function guardar(preferencias) {
        localStorage.setItem(CLAVE, JSON.stringify({ ...POR_DEFECTO, ...preferencias }));
    }

    function alternar(clave) {
        const actual = leer();
        if (!(clave in POR_DEFECTO)) {
            return actual;
        }
        actual[clave] = !actual[clave];
        if (clave === "festivo") {
            actual.vacaciones = actual.festivo;
        }
        if (clave === "semana_examenes") {
            actual.periodo = actual.semana_examenes;
        }
        guardar(actual);
        return actual;
    }

    function visible(tipo, preferencias = null) {
        const prefs = preferencias || leer();
        if (tipo === "vacaciones") {
            return prefs.festivo !== false;
        }
        if (tipo === "periodo") {
            return prefs.semana_examenes !== false;
        }
        return prefs[tipo] !== false;
    }

    return { leer, guardar, alternar, visible, POR_DEFECTO };
})();
