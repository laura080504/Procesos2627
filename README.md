# Proyecto de Procesos de Ingeniería del Software (curso 26-27)

Agenda académica de la UCLM (ESIIAB Albacete): matrícula, horario, avisos y expediente del alumno. Aplicación web en capas (FastAPI + MongoDB Atlas + cliente HTML/JS).

<details>
<summary><strong>Índice rápido</strong> (pulsa para abrir)</summary>

| Quiero… | Ve a |
|---------|------|
| Entender el proyecto en 2 minutos | [Qué es esto](#qué-es-esto) |
| Probar la app ya desplegada | [Enlaces útiles](#enlaces-útiles) |
| Saber qué puede hacer cada rol | [Qué puede hacer cada persona](#qué-puede-hacer-cada-persona) |
| Arrancarlo en mi PC | [Cómo arrancarlo en local](#cómo-arrancarlo-en-local) |
| Entrar con Google o con la cuenta UCLM | [Cómo se entra](#cómo-se-entra) |
| Ver arquitectura, carpetas y API | [Parte técnica](#parte-técnica) |
| Variables de entorno, CI y Cloud Run | [Despliegue y configuración](#despliegue-y-configuración) |

</details>

---

## Qué es esto

Es una **agenda académica** pensada para el grado de Ingeniería Informática en Albacete. El alumno entra, ve su horario del cuatrimestre, gestiona la matrícula, anota notas en el historial y recibe avisos (exámenes, entregas, clases de hoy). El profesor puede avisar a sus alumnos; el administrador gestiona usuarios y roles.

No hace falta saber programar para usarla: abre la URL, crea una cuenta (o entra con Google / UCLM) y ya estás dentro.

### Enlaces útiles

| Qué | Dónde |
|-----|--------|
| App en producción | https://procesos2627-459073742710.europe-west1.run.app |
| Documentación interactiva de la API | `/docs` (en local o en la URL de arriba) |
| Arranque en tu máquina | [Cómo arrancarlo en local](#cómo-arrancarlo-en-local) |

### Qué puede hacer cada persona

| Rol | Qué ve / qué hace |
|-----|-------------------|
| **Alumno** | Su agenda, matrícula, historial e intensificación |
| **Profesor** | Avisos solo en las asignaturas que imparte y listado de sus alumnos matriculados |
| **Superadministrador** | Gestión de todos los usuarios y del rol de profesor |

#### Funciones del alumno (resumen)

1. **Agenda**: horario del cuatrimestre vigente, fichas ESIIAB (aulas, profesores, tutorías) y calendario de exámenes/entregas.
2. **Matrícula**: ver y editar asignaturas/grupos reales; la tarta del perfil refleja **solo este curso**.
3. **Intensificación** (desplegable arriba del perfil): Software, Computadores, Computación o TI. Filtra las asignaturas “que te quedan” para no mezclar menciones.
4. **Historial**: notas a mano (las oficiales de secretaría van como TODO). Créditos y media del perfil salen de ahí. **Las notas no viven en el código**: solo en la BBDD del usuario autenticado.
5. **Notificaciones**: preferencias de avisos (exámenes, entregas, clases de hoy) y antelación.

### Cómo se entra

En el login puedes:

1. **Email y contraseña** (registro + confirmación por correo).
2. **Entrar con Google**.
3. **Entrar con UCLM** (cuenta institucional de la universidad; el botón está al lado del de Google). En el futuro se prevé que esta sea la vía principal de acceso.

Si pulsas Google o UCLM y aún no están configurados en el servidor, vuelves al login con un aviso claro. Con las credenciales bien puestas, el flujo es el mismo: el proveedor te identifica y la app crea o activa la sesión.

### Cómo arrancarlo en local

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
python main.py
```

- Cliente: http://localhost:8000
- Documentación de la API: http://localhost:8000/docs

Pruebas:

```powershell
pytest
```

Copia `.env.example` a `.env` y rellena lo que necesites (Mongo, Brevo, Google, UCLM…). Los secretos **no** se suben al repositorio.

---

## Parte técnica

A partir de aquí: arquitectura, carpetas, OAuth, variables y API. Pensado para quien ya programa o va a tocar el código.

### Tecnologías

| Tecnología | Justificación |
|------------|---------------|
| Python 3.13 | Lenguaje sencillo y legible, con un ecosistema muy amplio para desarrollo web y pruebas. |
| FastAPI | Framework web moderno que valida los datos automáticamente y genera la documentación de la API (`/docs`). |
| Uvicorn | Servidor ASGI ligero y rápido, el recomendado para ejecutar FastAPI. |
| HTML + JavaScript plano | Permite separar presentación y comunicación sin depender de frameworks de cliente. |
| pytest | Framework de pruebas estándar en Python, con una sintaxis mínima basada en `assert`. |
| bcrypt | Guarda las contraseñas con hash. Ni la API ni los registros muestran la contraseña en claro. |
| Brevo | Envía el correo de confirmación por SMTP/API. |
| Google OAuth | Permite crear la cuenta o entrar con una cuenta de Google, sin confirmar el correo. |
| UCLM OAuth (adAS) | Entrada con la cuenta institucional UCLM (`adas.uclm.es`). Misma lógica de sesión que Google. |
| GitHub Actions | Integración continua integrada en el propio repositorio, sin servicios externos. |
| Docker | Empaqueta la aplicación para que se ejecute igual en local y en el proveedor cloud. |
| MongoDB Atlas | Base persistente de la aplicación. Las pruebas usan repositorios en memoria. |

### Arquitectura

```
FRONT (navegador)                         BACK (servidor FastAPI)
┌─────────────────────────┐               ┌───────────────────────────────────┐
│ Cliente                 │               │ ApiRest  Controllers → Handlers   │
│   ClientePresentacion   │               │          Schemas, Dependencies    │
│   ClienteComunicacion   │── HTTP/WS ───▶│               │                   │
└─────────────────────────┘               │               ▼                   │
                                          │ Dominio  UseCases, Entities,      │
                                          │          Enums, Exceptions        │
                                          │               │                   │
                                          │               ▼                   │
                                          │ Infra    Repositories, Mongo      │
                                          │          Atlas                    ┼──▶ MongoDB Atlas
                                          └───────────────────────────────────┘
```

El backend sirve el frontend desde el mismo origen, y el cliente solo se comunica con el servidor a través de la API. Cada capa solo conoce a la que tiene debajo. Es el mismo recorte que en C# (API, Shared/Domain, Infrastructure, Client), con nombres en español.

#### Recorrido de una petición

`POST /api/auth/registro` → `auth_controller` valida la entrada → crea un `RegistrarUsuarioCommand` → lo ejecuta `RegistrarUsuarioUseCase`, que guarda el `Usuario` en estado `pendiente` y pide a `EmitirConfirmacionUseCase` el correo con el enlace. Si Brevo no puede enviarlo, se borra el usuario recién creado para que el alta se pueda repetir. Si el email ya existe, el use case lanza `UsuarioYaExiste` y el handler lo convierte en un `409`.

#### Convención de nombres

- Las carpetas empiezan por mayúscula y dicen qué hay dentro: `PruebasUseCase`, `DominioUseCases`, `ApiRestControllers`…
- Las capas van en español (`Cliente`, `Servidor`, `Dominio`, `Infraestructura`) y los patrones en inglés (`UseCases`, `Controllers`, `Repositories`).
- Un archivo por clase, con el patrón como sufijo: `registrar_usuario_use_case.py`, `usuario_controller.py`…
- **Commands** modifican el estado. **Queries** solo consultan.

### Estructura

```
Procesos2627/
├── Cliente/                              # CLIENT / APP
│   ├── index.html
│   ├── ClienteImg/
│   ├── ClienteShared/                    # Colores, estilos y textos
│   └── ClienteJs/
│       ├── ClientePresentacion/          # Páginas y componentes
│       │   └── PresentacionVistas/
│       ├── ClienteComunicacion/          # Cliente HTTP hacia la API
│       └── inicio.js
├── Servidor/
│   ├── aplicacion.py
│   ├── ApiRest/                          # API REST
│   │   ├── ApiRestControllers/
│   │   ├── ApiRestHandlers/
│   │   ├── ApiRestSchemas/
│   │   └── ApiRestDependencies/
│   ├── ApiWs/
│   │   └── ApiWsControllers/
│   ├── Dominio/                          # SHARED / DOMAIN
│   │   ├── DominioEntities/
│   │   ├── DominioEnums/
│   │   ├── DominioExceptions/
│   │   ├── DominioCommands/
│   │   ├── DominioQueries/
│   │   └── DominioUseCases/
│   └── Infraestructura/                  # INFRASTRUCTURE
│       ├── base_datos_mongo.py
│       ├── registro_actividad.py
│       ├── cliente_google.py
│       ├── cliente_uclm.py
│       └── InfraestructuraRepositories/
├── Pruebas/
│   ├── PruebasApi/
│   ├── PruebasUseCase/
│   └── PruebasDatos/
├── main.py                               # Punto de entrada
├── Dockerfile
├── .env.example
├── requirements.txt
└── requirements-dev.txt
```

#### Añadir una funcionalidad nueva

1. `DominioCommands/` o `DominioQueries/`: el objeto con los datos de entrada.
2. `DominioUseCases/`: la regla de negocio.
3. `DominioExceptions/`: los errores nuevos, si los hay.
4. `ApiRestSchemas/`: la entrada y salida de la API.
5. `ApiRestDependencies/`: el proveedor del use case.
6. `ApiRestControllers/`: el endpoint.
7. `ApiRestHandlers/`: la traducción de los errores nuevos a HTTP.
8. `PruebasUseCase/` y `PruebasApi/`: sus pruebas.

### Seguridad del login (resumen)

- Framework: **FastAPI** + MongoDB. Contraseñas con **bcrypt** (coste 12); política NIST (8–128, sin listas comunes).
- Email normalizado (`strip().lower()`); índice único por email. `contrasena_hash` puede ser `null` (solo Google/UCLM). Campo `proveedores` (`local` / `google` / `uclm`).
- Cookie de sesión `HttpOnly` + `SameSite=Lax` (+ `Secure` en producción). **Recuérdame**: 2 h (sesión corta) o 30 días (persistente); al cambiar contraseña se invalidan todas las sesiones.
- OAuth Google/UCLM con `state` (anti-CSRF, `compare_digest`) y **PKCE** (`code_challenge` / `code_verifier` en cookie `oauth_pkce`). Solo se confía en el email si el IdP indica `email_verified`.
- Identidad única: registro local sobre cuenta OAuth → aviso de entrar por Google/UCLM; OAuth sobre cuenta local **activa** → vincula proveedor; OAuth sobre cuenta **pendiente** → no vincula (anti takeover).
- Recuperación: respuesta siempre `200` con mensaje genérico; en BD solo el **hash SHA-256** del token (15 min, un solo uso). Cuentas solo OAuth reciben aviso por correo sin token de cambio.
- Límite de intentos por IP y email en login/registro/recuperación/OAuth. Login: mensaje único «Credenciales incorrectas».
- Cabeceras básicas: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`.

### Confirmación por correo

El alta deja la cuenta en `pendiente`. El servidor envía el correo con la API de Brevo por HTTPS, así que la lista de IPs del SMTP no interviene. El enlace es `{URL}/?confirmar={token}` y caduca a las 24 horas. La página llama a `POST /api/auth/confirmar` y, si el token es válido, pasa la cuenta a `activo`. Hasta ese momento el inicio de sesión responde `403` con el mensaje de cuenta pendiente.

Si el correo no llega, en el login se escribe el mismo email y se pulsa **Reenviar confirmación**. El enlace anterior deja de valer. Una cuenta ya activa o eliminada no recibe otro correo.

Si Brevo rechaza el envío, el alta responde `502` y no deja la cuenta a medias.

La recuperación de contraseña usa el mismo canal: `POST /api/auth/recuperacion` responde siempre `200` con un mensaje genérico y, si la cuenta tiene contraseña local, envía `{URL}/?recuperar={token}` (15 minutos).

### Inicio de sesión con Google

El botón **Entrar con Google** abre `GET /api/auth/google` (con `state` + PKCE). Google vuelve a `GET /api/auth/google/callback`. Si el correo es nuevo y está verificado, se crea la cuenta en `activo` **sin** `contrasena_hash` y con proveedor `google`. Si ya existía una cuenta local **activa**, se vincula Google. Si estaba **pendiente**, no se vincula ni se activa (hay que confirmar el correo). Si estaba eliminada, se vuelve al login con aviso.

Para activarlo en Google Cloud Console, credenciales → crear ID de cliente OAuth de tipo aplicación web, y registrar estas URIs de redirección tal cual:

- `http://127.0.0.1:8000/api/auth/google/callback`
- `https://procesos2627-459073742710.europe-west1.run.app/api/auth/google/callback`

El identificador y el secreto van en `.env` y, al desplegar, en las variables de Cloud Run. Sin esas dos variables el botón vuelve al login y explica que Google todavía no está configurado.

### Inicio de sesión con cuenta UCLM

El botón **Entrar con UCLM** (junto al de Google) abre `GET /api/auth/uclm` (también con `state` + PKCE). El SSO institucional (adAS) autentica al usuario y el navegador vuelve a `GET /api/auth/uclm/callback`. Reutiliza `IniciarSesionGoogleUseCase` con proveedor `uclm`: cuenta nueva → `activo` sin contraseña local; local activa → vincula UCLM; pendiente → no vincula; eliminada → aviso en el login.

URIs de redirección a registrar en el cliente OAuth de la UCLM:

- `http://127.0.0.1:8000/api/auth/uclm/callback`
- `https://procesos2627-459073742710.europe-west1.run.app/api/auth/uclm/callback`

Variables en `.env` / Cloud Run:

| Variable | Uso |
|----------|-----|
| `UCLM_CLIENT_ID` | Identificador del cliente OAuth UCLM |
| `UCLM_CLIENT_SECRET` | Secreto (no se sube al repositorio) |
| `UCLM_URL_AUTORIZACION` | Por defecto `https://adas.uclm.es/OAUTH2/authserver.php` |
| `UCLM_URL_TOKEN` | Por defecto `https://adas.uclm.es/OAUTH2/token.php` |
| `UCLM_URL_PERFIL` | Por defecto `https://adas.uclm.es/OAUTH2/userinfo.php` |

Sin `UCLM_CLIENT_ID` y `UCLM_CLIENT_SECRET` el botón vuelve al login con el aviso de que UCLM aún no está configurado. Las URLs se pueden cambiar si el servicio de la universidad las actualiza.

Cliente HTTP: `Servidor/Infraestructura/cliente_uclm.py`.

### Acceso como administrador

Si `ADMIN_EMAIL` y `ADMIN_PASSWORD` están definidos y todavía no hay un administrador, el arranque crea esa cuenta en estado `activo` o, si el email ya existe, solo le asigna el rol. Esa cuenta no pasa por la confirmación por correo. La contraseña no se sube al repositorio.

El superadministrador lista todos los usuarios, edita los de los demás y puede hacer profesor a otro desde esa edición. Un profesor solo ve a los alumnos matriculados en las asignaturas que imparte, con el rol y las asignaturas compartidas, y solo puede publicar avisos en esas asignaturas. El aviso se envía a los alumnos matriculados en esa asignatura que estén conectados; el resto lo verá en su panel de avisos. Un usuario normal solo ve su cuenta, edita la suya y solo puede eliminar la suya. `activo` significa que el correo está confirmado o que entró con Google/UCLM, y que la cuenta no está eliminada. `pendiente` no puede iniciar sesión. `eliminado` tampoco, y no se puede volver a registrar ese correo.

### API REST

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/registro` | Alta. Deja la cuenta `pendiente` y envía el correo de confirmación |
| POST | `/api/auth/inicio-sesion` | Entra con email y contraseña. Crea la cookie `sesion` |
| POST | `/api/auth/cierre-sesion` | Cierra la sesión |
| GET | `/api/auth/sesion` | Usuario de la cookie actual |
| POST | `/api/auth/recuperacion` | Solicita el correo de recuperación (siempre `200`, mensaje genérico) |
| POST | `/api/auth/nueva-contrasena` | Guarda la contraseña nueva y cierra las sesiones |
| POST | `/api/auth/confirmar` | Activa la cuenta con el token del enlace |
| POST | `/api/auth/reenviar-confirmacion` | Vuelve a enviar el enlace a una cuenta `pendiente` |
| GET | `/api/auth/google` | Redirige a Google |
| GET | `/api/auth/google/callback` | Recibe el código de Google y crea la sesión |
| GET | `/api/auth/uclm` | Redirige al SSO UCLM (adAS) |
| GET | `/api/auth/uclm/callback` | Recibe el código UCLM y crea la sesión |
| POST | `/api/eventos` | Publica un examen/entrega (profesor o secretaría) |
| PUT | `/api/eventos/{id}` | Edita un examen/entrega propio |
| DELETE | `/api/eventos/{id}` | Elimina un examen/entrega propio |
| GET | `/api/usuarios` | Lista usuarios. El profesor, solo los alumnos de sus asignaturas; el superadministrador, todos |
| PATCH | `/api/usuarios/me` | Edita el email, el nombre y, si se envía, la contraseña propios |
| GET | `/api/usuarios/numero` | Número de usuarios |
| POST | `/api/usuarios/{email}/administrador` | Un administrador convierte esa cuenta en administrador |
| GET | `/api/usuarios/{email}/activo` | Indica si esa cuenta está activa |
| DELETE | `/api/usuarios/{email}` | Marca la cuenta como eliminada y cierra sus sesiones |
| GET | `/api/asignaturas` | Catálogo del grado (plan 406 Albacete) |
| GET | `/api/matricula` | Matrícula activa, horario, créditos/media e intensificación |
| PUT | `/api/matricula` | Guarda la matrícula del curso (conserva notas del historial) |
| GET | `/api/expediente` | Historial: calificadas, pendientes (según mención), media |
| PUT | `/api/expediente` | Guarda notas y/o intensificación (solo del usuario en sesión) |
| GET | `/api/agenda/marcas` | Marcas del mes (exámenes, entregas, festivos) |
| GET | `/api/agenda/marcas-rango` | Marcas de varios meses |
| WS | `/ws` | Canal WebSocket (avisos en tiempo real) |

Las rutas de matrícula y expediente exigen cookie de sesión y solo operan sobre `usuario.email`: nadie ve las notas de otro alumno.

---

## Despliegue y configuración

### Variables de entorno

| Nombre | Descripción |
|--------|-------------|
| `HOST` | Interfaz en la que escucha el servidor |
| `PORT` | Puerto del servidor |
| `RECARGAR` | `true` para reiniciar el servidor al guardar cambios (solo en desarrollo) |
| `DATOS_MOTOR` | `mongo` en la app, `memoria` en las pruebas |
| `MONGO_URI` | Cadena de Atlas (`mongodb+srv://...`), obligatoria si el motor es `mongo`. Puede ir sin usuario y contraseña |
| `MONGO_USUARIO` | Usuario de Database Access de Atlas, si no va en la URI |
| `MONGO_CONTRASENA` | Contraseña de ese usuario de Atlas |
| `MONGO_DB` | Nombre de la base en Atlas. Por defecto `procesos` |
| `LOG_NIVEL` | `DEBUG`, `INFO`, `WARNING` o `ERROR` |
| `SESION_DURACION_HORAS` | Duración de la cookie de sesión. Por defecto `8` |
| `COOKIE_SEGURA` | `true` en Cloud Run, para que la cookie solo viaje por HTTPS |
| `ADMIN_EMAIL` | Correo del primer administrador. Se crea al arrancar si todavía no hay uno |
| `ADMIN_PASSWORD` | Contraseña de ese administrador, entre 8 y 64 caracteres |
| `BREVO_API_CLAVE` | Clave API de Brevo. El correo sale por HTTPS y no depende de la IP. No se sube al repositorio |
| `BREVO_REMITENTE` | Correo verificado en Brevo desde el que sale la confirmación |
| `BREVO_REMITENTE_NOMBRE` | Nombre que ve quien recibe el correo |
| `GOOGLE_CLIENT_ID` | Identificador del cliente OAuth de Google. Vacío hasta crearlo |
| `GOOGLE_CLIENT_SECRET` | Secreto de ese cliente. No se sube al repositorio |
| `UCLM_CLIENT_ID` | Identificador del cliente OAuth UCLM. Vacío hasta crearlo |
| `UCLM_CLIENT_SECRET` | Secreto UCLM. No se sube al repositorio |
| `UCLM_URL_AUTORIZACION` | Endpoint de autorización adAS (tiene valor por defecto) |
| `UCLM_URL_TOKEN` | Endpoint de token adAS (tiene valor por defecto) |
| `UCLM_URL_PERFIL` | Endpoint de perfil adAS (tiene valor por defecto) |
| `URL_PUBLICA` | Origen público sin barra final. En Cloud Run, la URL del servicio. En local se puede dejar vacía |

### Flujo de trabajo (GitHub Flow)

1. Crear una rama por cambio a partir de `main`.
2. Ejecutar `pytest` en local antes de abrir el pull request.
3. Abrir un pull request hacia `main`; el CI ejecuta las pruebas automáticamente.
4. Integrar solo con el CI en verde. El workflow despliega ese commit en Cloud Run.

### Despliegue

Al integrar en `main`, el workflow `.github/workflows/ci.yml` ejecuta las pruebas y, si pasan, despliega el `Dockerfile` en el servicio `procesos2627` de Cloud Run, región `europe-west1`.

URL pública: https://procesos2627-459073742710.europe-west1.run.app

La misma dirección sale al final de la ejecución, en la pestaña Actions del repositorio. Un pull request solo lanza las pruebas y no publica.

La autenticación usa el secreto `GCP_CREDENTIALS` de GitHub: el JSON de una cuenta de servicio del mismo proyecto, con los roles Cloud Run Source Developer, Service Usage Consumer y Service Account User. Esa clave no se sube al repositorio.

El despliegue deja `DATOS_MOTOR=mongo` y `URL_PUBLICA` con la URL de arriba. `COOKIE_SEGURA=true` va en la imagen. El resto de variables (Mongo, administrador, Brevo, Google y UCLM) se configuran una vez en el servicio de Cloud Run y se conservan en los despliegues siguientes.
