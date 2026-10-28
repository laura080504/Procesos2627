---
type: Sprint
title: Sprint 1
description: Hitos orientativos del apartado 10 y retrospectiva a partir de los commits.
timestamp: 2026-10-28
---

# Sprint 1

Los hitos son los del apartado 10 de la especificación. No hay etiquetas git. El tablero no se copia aquí. Por verificar: URL de Donetonic; no está en el repositorio.

`main` documentado: `77202eb`.

## Hito 1 Esqueleto y backend

**Objetivo.** Repositorio con ramas y pull requests. Integración continua y despliegue continuo desde el primer día, aunque la página sea mínima. Lógica de usuarios en memoria, con pruebas, y una API que la exponga.

**Qué se hizo.** El 2026-10-03, commit `91bd639` y pull requests [#1](https://github.com/laura080504/Procesos2627/pull/1) y [#2](https://github.com/laura080504/Procesos2627/pull/2): README, casos de uso, repositorio en memoria, esquemas y pruebas. El workflow entra en `013c6f6`. Las primeras ejecuciones de Actions de ese día terminaron en verde.

**Pull request y etiqueta.** #1 y #2. Etiqueta: ninguna.

**Desviaciones.** El despliegue continuo no está el primer día; llega el 2026-10-13 (`b0e7946`). El commit inicial va directo a `main`. La rama de los dos pull requests es la misma, `Sprint-1`.

## Hito 2 Frontend y sesión

**Objetivo.** Presentación y comunicación separadas. Registro e inicio locales, hash, cierre y sesión entre recargas. Rutas que rechazan peticiones sin sesión. Los datos siguen en memoria.

**Qué se hizo.** Pull request [#3](https://github.com/laura080504/Procesos2627/pull/3) (2026-10-05): vistas, cliente, login, registro, sesión y bcrypt (commits `246d6f1`, `6159a52`, `8181425`, `9e5e005`, `d3e42b5`, `15c86fa`, `eaea86c`, `eba0bab`). El pull request [#4](https://github.com/laura080504/Procesos2627/pull/4), el mismo día, añade la recuperación de contraseña, que no está en este hito.

**Pull request y etiqueta.** #3 y #4. Etiqueta: ninguna.

**Desviaciones.** Sigue usándose la rama larga `Sprint-1`. La persistencia en memoria se mantiene hasta el hito 3, como pide el objetivo.

## Hito 3 Persistencia y roles

**Objetivo.** Base de datos real sin reescribir la lógica. Secretos en variables de entorno. Roles y restricciones del apartado 4.2 en el servidor. Registro de actividad.

**Qué se hizo.** El pull request [#5](https://github.com/laura080504/Procesos2627/pull/5) (2026-10-06) trae SQLite (commits `13d2250` a `b00ef1e`, entre otros) y se integró con las pruebas en rojo. El [#6](https://github.com/laura080504/Procesos2627/pull/6) renombra carpetas, con el CI en verde. El [#7](https://github.com/laura080504/Procesos2627/pull/7) (2026-10-11) sustituye SQLite por MongoDB Atlas sin tocar los casos de uso. El [#8](https://github.com/laura080504/Procesos2627/pull/8) (2026-10-13) edita datos, muestra rol y estado y bloquea cuentas eliminadas. El registro de actividad está en `registro_actividad.py`. Los secretos se leen del entorno ([RNF-02](requisitos.md)).

**Pull request y etiqueta.** #5, #6, #7 y #8. Etiqueta: ninguna.

**Desviaciones.** El #5 entró en `main` con el CI en rojo. Hubo un motor intermedio (SQLite) antes del definitivo. Los roles de este hito no son los que quedan en `77202eb`: el pull request #11 los parte en profesor y superadministrador.

## Hito 4 Servicios externos y cierre

**Objetivo.** OAuth, confirmación por correo, errores con feedback al usuario, README completo y revisión de la entrega.

**Qué se hizo.** El 2026-10-13 el merge `9fdd9b1` mete la confirmación por correo, Google (`9a03f8e`) y el despliegue (`b0e7946`). El mismo día, `afb9e67` quita el botón de Google (`500ce85`). El 2026-10-14, `5fb3380` pasa el correo a la API de Brevo (`e55d7e2`). Los errores de dominio llegan al cliente como `detail`. El README de `main` cubre tecnologías, ejecución, pruebas, variables, administrador, correo, Google, flujo y despliegue.

**Pull request y etiqueta.** Estos tres merges no son pull requests. El botón de Google vuelve en el pull request #10, ya fuera de este bloque. Etiqueta: ninguna.

**Desviaciones.** El cierre del hito 4 llegó a `main` por merge directo de `Sprint-1`. El README aún describe la ruta `/api/usuarios/{email}/administrador` y el SMTP de Brevo; el código expone `/profesor` y envía por la API.

## Después de los cuatro hitos

Siguen en `main`, ya fuera del reparto semanal:

- Pull request [#9](https://github.com/laura080504/Procesos2627/pull/9) (2026-10-15), rama `Prueba-tecnica-sprint-1`: cálculo de estado sin consultar la base. Ruta `POST /api/prueba/estado`.
- Pull request [#10](https://github.com/laura080504/Procesos2627/pull/10) (2026-10-20), rama `sprint2`.
- Pull request [#11](https://github.com/laura080504/Procesos2627/pull/11) (2026-10-26), rama `sprint2`: agenda, horario y roles.

## Retrospectiva

### Hechos

- Repositorio creado el 2026-10-03 (`91bd639`) y 11 pull requests integrados entre ese día y el 2026-10-26.
- CI desde el 2026-10-03 (`013c6f6`). Despliegue desde el 2026-10-13 (`b0e7946`).
- En el árbol de `77202eb`, `pytest -q` dio 132 passed y `pytest -q Pruebas/PruebasUseCase` dio 76 passed (2026-10-28).
- La persistencia pasó de memoria a SQLite (pull request #5) y de SQLite a MongoDB Atlas (pull request #7, `abc03ff`).
- Confirmación por correo y Google entraron el 2026-10-13 (`9fdd9b1`); el envío pasó a la API de Brevo el 2026-10-14 (`e55d7e2`).
- No hay etiquetas de hito. Tres merges de funcionalidad llegaron a `main` sin pull request.

### Qué funcionó

TODO(alumno): ¿qué parte del flujo (rama, pull request, CI, despliegue) te ahorró tiempo de verdad?

### Qué cambiaría

TODO(alumno): ¿qué harías distinto en el sprint 2: una rama por cambio, etiquetas al cerrar cada hito, y no integrar un pull request con las pruebas en rojo?
