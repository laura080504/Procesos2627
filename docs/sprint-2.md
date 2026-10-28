---
type: Sprint
title: Sprint 2
description: Objetivo aún por definir y requisitos del sprint 1 que no están cerrados.
timestamp: 2026-10-28
---

# Sprint 2

## Objetivo

Por definir.

`main` ya contiene trabajo de la rama `sprint2`: el pull request #10 (2026-10-20) y el #11 (2026-10-26, agenda, horario y roles). Eso no sustituye el objetivo de este sprint. Las tareas del día a día siguen en el tablero. Por verificar: URL de Donetonic.

## Requisitos que pasan

Salen de [requisitos.md](requisitos.md). No hay ninguno en estado pendiente. Estos están en parcial:

- **RF-07** y **RF-08**. Listar usuarios y comprobar si están activos lo pueden hacer el profesor y el superadministrador. La especificación pide solo el administrador. Depende de [D-11](decisiones.md#d-11-tres-roles): o se recorta a un rol, o se escribe el motivo y se da el requisito por sustituido.
- **RF-09**. El borrado no permite que un administrador elimine a cualquiera. Un profesor no borra a otro profesor y nadie borra al superadministrador.
- **PRO-01**. Hizo falta una rama por cambio, integrar solo por pull request y etiquetar cada hito. Los pull requests #1 a #8 reutilizan `Sprint-1`. Los merges `9fdd9b1`, `afb9e67` y `5fb3380` no son pull requests. `git tag` no devolvió etiquetas.
- **PRO-02**. El workflow ya ejecuta las pruebas, pero el pull request #5 se integró con ese paso en rojo. Por verificar: protección de `main` y el mensaje concreto de los tres fallos de Actions.

Al cerrar uno, se actualizan el estado en `requisitos.md`, la evidencia y esta lista, en el mismo pull request que el código.
