---
type: Requisitos
title: Requisitos del sprint 1 (cierre en sprint 2)
description: Estado de cada requisito de la especificación del sprint 1, cerrado al terminar el sprint 2.
timestamp: 2026-11-19
---

# Requisitos

La especificación es la del sprint 1 (apartados 3 a 7). El estado refleja el código tras el cierre del sprint 2 ([PR #17](https://github.com/laura080504/Procesos2627/pull/17), `5b63fc0`).

Cifras históricas (2026-10-28, árbol `77202eb`): `pytest -q` → 132 passed; UseCase → 76 passed.  
Cifra de comprobación (2026-11-19, `main` actual): `pytest -q` → **164 passed, 1 failed** (`prueba_google_sin_configurar_avisa`).

| ID | Requisito | Estado | Evidencia |
|----|-----------|--------|-----------|
| ARQ-01 | Separación cliente-servidor y mismo origen | hecho | `Servidor/aplicacion.py` sirve `Cliente/` con `StaticFiles` en `/`. `clienteHttp.js` llama a `/api` con `credentials: "same-origin"`. No hay cliente de base de datos en `Cliente/`. |
| ARQ-02 | Capas del backend: API, lógica y datos | hecho | Carpetas `ApiRest`, `Dominio` e `Infraestructura`. Los controllers no contienen las reglas; los casos de uso no importan FastAPI. Ver [arquitectura](arquitectura.md#frontera). |
| ARQ-03 | Capas del frontend: presentación y comunicación | hecho | `Cliente/ClienteJs/ClientePresentacion/` y `Cliente/ClienteJs/ClienteComunicacion/` (`clienteHttp.js`, `clienteRest.js`, `errorApi.js`). |
| RF-01 | Registro de usuario local | hecho | `RegistrarUsuarioUseCase` guarda la cuenta en `pendiente` y hashea la contraseña. `POST /api/auth/registro`. Pruebas: `Pruebas/PruebasUseCase/prueba_registrar_usuario_use_case.py` y `prueba_el_registro_deja_la_cuenta_pendiente_hasta_confirmar` en `prueba_auth_controller.py`. |
| RF-02 | Confirmación de cuenta por correo | hecho | `EmitirConfirmacionUseCase` pide a `EnviadorCorreoBrevo` el envío por la API HTTPS. El enlace caduca a las 24 horas. `POST /api/auth/confirmar` pasa la cuenta a `activo`. Si el envío falla, se borra el alta y la API responde 502. Pruebas: `prueba_confirmar_cuenta_use_case.py`, `prueba_enviador_correo_brevo.py` (el envío real está sustituido por un doble). |
| RF-03 | Inicio de sesión local | hecho | `IniciarSesionUseCase` y `POST /api/auth/inicio-sesion`. Rechaza contraseña incorrecta, cuenta pendiente y cuenta eliminada. Pruebas: `prueba_iniciar_sesion_use_case.py`. |
| RF-04 | Inicio de sesión con OAuth | hecho | `GET /api/auth/google` y `GET /api/auth/google/callback`. `IniciarSesionGoogleUseCase` crea la cuenta ya en `activo`, o activa una pendiente. Una cuenta eliminada no entra. Commit `9a03f8e`. Pruebas en `prueba_confirmar_cuenta_use_case.py` y `prueba_google_crea_la_sesion_de_un_usuario_nuevo` en `prueba_auth_controller.py`. |
| RF-05 | Cierre de sesión | hecho | `CerrarSesionUseCase` borra la sesión y el controller borra la cookie. Pruebas: `prueba_cerrar_sesion_use_case.py` y `prueba_cierre_sesion_invalida_el_token`. |
| RF-06 | Mantenimiento de la sesión entre recargas | hecho | Cookie `sesion` (`httponly`, `samesite=lax`). `ControlWeb.iniciar` llama a `GET /api/auth/sesion` y, si vale, abre la aplicación. Prueba: `prueba_la_sesion_se_mantiene_entre_peticiones`. |
| RF-07 | Listar usuarios (administrador) | hecho | `GET /api/usuarios` exige profesor o superadministrador (`obtener_gestor`). Usuario normal → 403. La especificación pedía un solo administrador; [D-11](decisiones.md#d-11-tres-roles) (PR #11) sustituye ese rol por profesor/superadministrador. Evidencia: `usuario_controller.py`, `prueba_un_usuario_no_lista_usuarios`. |
| RF-08 | Comprobar si un usuario está activo (administrador) | hecho | `UsuarioActivoUseCase` solo con estado `activo`. Misma sustitución [D-11](decisiones.md#d-11-tres-roles). Pruebas: `prueba_usuario_activo_use_case.py`. |
| RF-09 | Eliminar usuario | hecho | Reglas en `EliminarUsuarioUseCase` (usuario propio; profesor → usuarios; superadministrador → usuarios y profesores; nadie borra al superadministrador). Sustitución del “administrador elimina a cualquiera” por [D-11](decisiones.md#d-11-tres-roles). Pruebas: `prueba_eliminar_usuario_use_case.py`. |
| RF-10 | Creación del primer administrador | hecho | Si `ADMIN_EMAIL` y `ADMIN_PASSWORD` están definidos y no hay superadministrador, el arranque lo crea en `activo` o promociona ese email (`AsegurarAdministradorUseCase`, `repositorio_dependencies.py`). No pasa por el correo. Pruebas: `prueba_asegurar_administrador_use_case.py`. El motivo está en el README, sección «Acceso como administrador». El rol que crea hoy es superadministrador ([D-11](decisiones.md#d-11-tres-roles)). |
| RNF-01 | Persistencia en una base de datos real | hecho | Con `DATOS_MOTOR=mongo` se usan los repositorios mongo. El commit `abc03ff` (pull request #7) sustituye SQLite y no toca `DominioUseCases`. El workflow de despliegue fija `DATOS_MOTOR=mongo`. Las pruebas usan memoria. |
| RNF-02 | Secretos fuera del código y .env.example | hecho | `configuracion.py` lee el entorno. `.env` está en `.gitignore` y no está en el índice. `.env.example` trae los nombres, sin valores. La lista de nombres está en el [README](../README.md). |
| RNF-03 | Hash seguro de contraseñas | hecho | `HasherContrasenas` usa bcrypt, 12 rondas. `prueba_la_contrasena_se_guarda_con_hash`. |
| RNF-04 | Rutas protegidas por sesión y rol | hecho | Sin cookie, `obtener_usuario_actual` lanza `SesionNoValida` (401). Sin rol de gestor, `PermisoInsuficiente` (403). Prueba: `prueba_rutas_de_usuarios_rechazan_peticiones_sin_sesion`. `POST /api/prueba/estado` y `WS /ws` no piden sesión; la especificación obliga a proteger las rutas que requieren usuario, no todas. |
| RNF-05 | Despliegue en cloud con URL pública | hecho | `.github/workflows/ci.yml`, job `desplegar`, solo en push a `main` y después de `pruebas`. Commit `b0e7946`. La URL está en el README. El 2026-10-28 una petición HEAD a esa URL respondió 200. |
| RNF-06 | Pruebas unitarias de la lógica (5 o más) | hecho | 76 passed en `Pruebas/PruebasUseCase`, dentro de las 132 de `pytest -q`. Hay casos de error: email duplicado, cuenta pendiente, un usuario que intenta borrar a otro. Comando documentado en el README: `pytest`. |
| RNF-07 | Manejo de errores con feedback al usuario | hecho | Los handlers devuelven `detail`. `clienteHttp.js` lo convierte en `ErrorApi` y `controlWeb.js` lo muestra con `mostrarMensaje`. Un 422 sin detalle dice que hay que revisar los datos. |
| RNF-08 | Registro de actividad (log) | hecho | `registro_actividad.py` registra alta, inicio, confirmación, cierre, edición, borrado, cambio de rol y fallo. Lo llaman controllers y handlers. El nivel sale de `LOG_NIVEL`. |
| PRO-01 | Flujo de trabajo GitHub Flow | parcial | En sprint 1: PR #1–#8 desde `Sprint-1` y tres merges sin PR. En sprint 2: PR #10–#17 desde `sprint2` (todos por PR). Sigue sin rama corta por cambio y sin etiquetas de hito (`git tag` vacío el 2026-11-19). |
| PRO-02 | Integración continua | hecho | `.github/workflows/ci.yml` ejecuta `pytest` en PR y push a `main`. El #5 del sprint 1 se integró en rojo; en el tramo del sprint 2 (#10–#17) no hay evidencia en el historial de merge con CI en rojo. Por verificar: protección de rama en GitHub. |
| PRO-03 | Despliegue continuo | hecho | El job `desplegar` depende de `pruebas` y solo corre en push a `main`. Llegó el 2026-10-13 (`b0e7946`); ver [hito 1](sprint-1.md#hito-1-esqueleto-y-backend). |
