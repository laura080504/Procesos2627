---
type: Decisiones
title: Decisiones detectadas
description: Elecciones que se ven en el README, en los commits o en el código de main.
timestamp: 2026-10-28
---

# Decisiones

Si el mensaje del commit o el README no dan el motivo, queda un `TODO(alumno)`.

## D-01 Stack

**Qué se decidió.** Python, FastAPI, Uvicorn, HTML y JavaScript plano, y pytest.

**Por qué.** El [README](../README.md), tabla «Tecnologías», justifica cada una en una frase.

**Estado.** Vigente.

## D-02 Hash con bcrypt

**Qué se decidió.** Las contraseñas se guardan con bcrypt, 12 rondas (`HasherContrasenas`).

**Por qué.** El README dice: «Guarda las contraseñas con hash. Ni la API ni los registros muestran la contraseña en claro.»

**Estado.** Vigente.

## D-03 SQLite

**Qué se decidió.** Persistencia con SQLite y el módulo sqlite3. Commit `13d2250`: «T28: Elegir SQLite y sqlite3». Llegó en el pull request #5.

**Por qué.** TODO(alumno): ¿por qué elegiste SQLite para el hito 3?

**Estado.** Sustituida por [D-04](#d-04-base-atlas).

## D-04 Base Atlas

**Qué se decidió.** Sustituir SQLite por MongoDB Atlas. Commit `abc03ff`, pull request #7. El diff de ese commit no toca `DominioUseCases`. Las pruebas siguen en memoria.

**Por qué.** TODO(alumno): ¿por qué dejaste SQLite? El mensaje del commit solo dice que se sustituye.

**Estado.** Vigente.

## D-05 Correo por SMTP

**Qué se decidió.** Enviar la confirmación con el SMTP de Brevo. La tabla de tecnologías del README sigue diciendo «Envía el correo de confirmación por SMTP». `.env.example` conserva las variables `BREVO_SMTP_SERVIDOR`, `BREVO_SMTP_PUERTO`, `BREVO_SMTP_USUARIO` y `BREVO_SMTP_CLAVE`.

**Por qué.** TODO(alumno): ¿por qué el primer diseño fue SMTP?

**Estado.** Sustituida por [D-06](#d-06-correo-por-api). El código que envía es `EnviadorCorreoBrevo`, y no usa esas variables SMTP.

## D-06 Correo por API

**Qué se decidió.** Enviar la confirmación por la API HTTPS de Brevo. Commit `e55d7e2`.

**Por qué.** El mensaje del commit: «para no depender de la IP».

**Estado.** Vigente. Llegó a `main` en el merge `5fb3380`, sin pull request.

## D-07 OAuth con Google

**Qué se decidió.** Entrar con Google. Si el correo es nuevo, la cuenta nace en `activo`. Si estaba pendiente, se activa. Commit `9a03f8e`.

**Por qué.** El README: «Permite crear la cuenta o entrar con una cuenta de Google, sin confirmar el correo.»

**Estado.** Vigente en el backend. El botón se quitó en [D-08](#d-08-quitar-el-botón-de-google) y volvió en [D-09](#d-09-volver-a-mostrar-google).

## D-08 Quitar el botón de Google

**Qué se decidió.** Quitar el botón de Google de la pantalla de acceso. Commit `500ce85`, merge `afb9e67`.

**Por qué.** TODO(alumno): ¿por qué quitaste el botón si el callback seguía en el servidor?

**Estado.** Sustituida por [D-09](#d-09-volver-a-mostrar-google).

## D-09 Volver a mostrar Google

**Qué se decidió.** Mostrar otra vez el acceso con Google, con sus colores. Pull request #10, merge `769d3c5`.

**Por qué.** TODO(alumno): ¿por qué volviste a mostrarlo, y por qué con esos colores?

**Estado.** Vigente.

## D-10 Primer administrador por variables de entorno

**Qué se decidió.** Crear el primer administrador al arrancar con `ADMIN_EMAIL` y `ADMIN_PASSWORD`, ya en `activo`, sin correo de confirmación.

**Por qué.** El README, sección «Acceso como administrador»: la contraseña no se sube al repositorio y esa cuenta no pasa por la confirmación.

**Estado.** Vigente. El rol que escribe el código actual es superadministrador; ver [D-11](#d-11-tres-roles).

## D-11 Tres roles

**Qué se decidió.** Los roles son usuario, profesor y superadministrador. Si en la base el valor antiguo es `administrador`, `rol_desde_almacen` lo lee como profesor. Pull request #11.

**Por qué.** TODO(alumno): ¿por qué partiste el rol administrador de la especificación en profesor y superadministrador?

**Estado.** Vigente. Cambia el alcance de [RF-07](requisitos.md), [RF-08](requisitos.md) y [RF-09](requisitos.md).

## D-12 Sesión en cookie

**Qué se decidió.** La sesión viaja en una cookie `httponly`, `samesite=lax`, con duración `SESION_DURACION_HORAS`. `COOKIE_SEGURA` la marca segura.

**Por qué.** TODO(alumno): ¿por qué cookie de servidor y no un identificador guardado en el navegador?

**Estado.** Vigente. Código: `_poner_sesion` en `auth_controller.py`.

## D-13 Recuperación de contraseña

**Qué se decidió.** Un flujo de recuperación que no está en la especificación del sprint 1. Pull request #4. `POST /api/auth/recuperacion` devuelve el identificador en la respuesta; no se ve un envío de correo en ese caso de uso.

**Por qué.** TODO(alumno): ¿por qué añadiste la recuperación en el sprint 1, y por qué el identificador sale en la respuesta de la API?

**Estado.** Vigente.

## D-14 Cloud Run después de las pruebas

**Qué se decidió.** Empaquetar con Docker y desplegar en Cloud Run cuando el cambio llega a `main`, solo si las pruebas del workflow han pasado. Commit `b0e7946`. GitHub Actions ejecuta el CI.

**Por qué.** El README justifica Docker («se ejecute igual en local y en el proveedor cloud») y GitHub Actions («sin servicios externos»). TODO(alumno): ¿por qué Cloud Run y no otro proveedor de la capa gratuita?

**Estado.** Vigente. El merge que lo trajo a `main` (`9fdd9b1`) no es un pull request.
