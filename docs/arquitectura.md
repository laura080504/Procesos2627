---
type: Arquitectura
title: Arquitectura en main
description: Capas del backend y del frontend, la frontera entre ellas y los endpoints que hay en main.
timestamp: 2026-10-28
---

# Arquitectura

El mapa de tecnologías y el recorrido de un alta están en el [README](../README.md). Aquí está la frontera que se ve en el código de `77202eb`.

## Backend

### Capa API

Traduce HTTP a comandos o consultas y las excepciones a códigos HTTP.

- `Servidor/aplicacion.py` monta los routers y, al final, el cliente estático.
- `Servidor/ApiRest/ApiRestControllers/`: `auth_controller.py`, `usuario_controller.py`, `agenda_controller.py`, `prueba_controller.py`.
- `Servidor/ApiRest/ApiRestHandlers/`: `auth_handler.py`, `usuario_handler.py`.
- `Servidor/ApiRest/ApiRestSchemas/`: entrada y salida de la API.
- `Servidor/ApiRest/ApiRestDependencies/`: composición e inyección.
- `Servidor/ApiWs/ApiWsControllers/websocket_controller.py`.

### Capa de lógica

Reglas de usuarios, sesión, confirmación, OAuth, agenda y la prueba técnica.

- `Servidor/Dominio/DominioUseCases/`
- `Servidor/Dominio/DominioEntities/`, `Servidor/Dominio/DominioEnums/`, `Servidor/Dominio/DominioExceptions/`, `Servidor/Dominio/DominioCommands/`, `Servidor/Dominio/DominioQueries/`, `Servidor/Dominio/DominioResults/`
- `Servidor/Dominio/DominioServices/`: `hasher_contrasenas.py`, `calcular_estado_usuario.py` y los servicios de agenda y horario.

Los casos de uso no importan FastAPI. Reciben repositorios y el enviador por el constructor.

### Capa de datos y servicios externos

- Interfaces e implementaciones en `Servidor/Infraestructura/InfraestructuraRepositories/`. Hay versión en memoria y versión mongo de usuarios, sesiones, recuperaciones, confirmaciones, cursos, asignaturas, eventos y matrículas.
- `Servidor/Infraestructura/base_datos_mongo.py`
- `Servidor/Infraestructura/enviador_correo_brevo.py` y `enviador_correo_memoria.py`
- `Servidor/Infraestructura/cliente_google.py`
- `Servidor/Infraestructura/registro_actividad.py`
- `Servidor/configuracion.py` lee el entorno. Los nombres de variables están en el [README](../README.md).

`crear_repositorios` elige memoria o mongo según `DATOS_MOTOR`. Las pruebas fijan `memoria` en `Pruebas/conftest.py`.

Al arrancar, si hay `ADMIN_EMAIL` y `ADMIN_PASSWORD`, `AsegurarAdministradorUseCase` crea o promociona un superadministrador. También se aseguran catálogo, eventos de muestra y matrículas de muestra. Si el motor es mongo y existe la colección `asignaturas`, el arranque la borra (`repositorio_dependencies.py`).

## Frontend

### Presentación

- `Cliente/index.html`
- `Cliente/ClienteJs/inicio.js` crea `ClienteRest` y `ControlWeb`.
- `Cliente/ClienteJs/ClientePresentacion/controlWeb.js`, `dictadoVoz.js`
- `Cliente/ClienteJs/ClientePresentacion/PresentacionVistas/`: acceso, registro, recuperación, usuarios, edición, agenda, cabecera y barra.
- `Cliente/ClienteShared/`: estilos y textos.

### Comunicación

- `Cliente/ClienteJs/ClienteComunicacion/clienteHttp.js`: `fetch` con `credentials: "same-origin"`.
- `clienteRest.js`: métodos de la API, sin pintar pantallas.
- `errorApi.js`.

El cliente no abre la base de datos. La base de las peticiones es `/api`, mismo origen que la página servida por el backend.

## Frontera

`Cliente/ClienteJs/ClientePresentacion/` llama a `ClienteRest`. `ClienteRest` solo usa `ClienteHttp`.

Un controller valida la entrada, construye un command o una query y llama al caso de uso que le inyecta `ApiRestDependencies`. El caso de uso habla con la interfaz del repositorio. La implementación memoria o mongo se elige en `repositorio_dependencies.py`, no dentro del caso de uso.

Las excepciones de dominio las convierten en JSON los handlers. El cliente muestra `detail` en `mostrarMensaje`.

Los casos de uso importan las interfaces desde `Infraestructura`, no desde un paquete de dominio aparte. Esa es la frontera real del repositorio.

## Endpoints

| Método | Ruta | Quién puede |
|--------|------|-------------|
| POST | `/api/auth/registro` | Sin sesión |
| POST | `/api/auth/inicio-sesion` | Sin sesión |
| POST | `/api/auth/cierre-sesion` | Sin sesión; si hay cookie, invalida esa sesión |
| GET | `/api/auth/sesion` | Sesión válida |
| POST | `/api/auth/recuperacion` | Sin sesión |
| POST | `/api/auth/nueva-contrasena` | Sin sesión; hace falta el identificador de recuperación |
| POST | `/api/auth/confirmar` | Sin sesión; hace falta el identificador del enlace |
| POST | `/api/auth/reenviar-confirmacion` | Sin sesión |
| GET | `/api/auth/google` | Sin sesión |
| GET | `/api/auth/google/callback` | Sin sesión; lo devuelve el proveedor |
| GET | `/api/usuarios` | Profesor o superadministrador |
| PATCH | `/api/usuarios/me` | Sesión válida |
| GET | `/api/usuarios/numero` | Profesor o superadministrador |
| POST | `/api/usuarios/{email}/profesor` | Superadministrador |
| GET | `/api/usuarios/{email}/activo` | Profesor o superadministrador |
| DELETE | `/api/usuarios/{email}` | Sesión válida; la regla de a quién puede borrar está en `EliminarUsuarioUseCase` |
| GET | `/api/asignaturas` | Sesión válida |
| GET | `/api/matricula` | Sesión válida |
| GET | `/api/agenda/marcas` | Sesión válida |
| POST | `/api/prueba/estado` | Sin sesión |
| WS | `/ws` | Sin sesión |

El [README](../README.md) todavía nombra `POST /api/usuarios/{email}/administrador`. El controller expone `POST /api/usuarios/{email}/profesor`.
