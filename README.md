# Proyecto de Procesos de Ingeniería del Software (curso 26-27)

Estructura base de una aplicación SaaS organizada en capas y con gestión de usuarios.

## Tecnologías

| Tecnología | Justificación |
|------------|---------------|
| Python 3.13 | Lenguaje sencillo y legible, con un ecosistema muy amplio para desarrollo web y pruebas. |
| FastAPI | Framework web moderno que valida los datos automáticamente y genera la documentación de la API (`/docs`). |
| Uvicorn | Servidor ASGI ligero y rápido, el recomendado para ejecutar FastAPI. |
| HTML + JavaScript plano | Permite separar presentación y comunicación sin depender de frameworks de cliente. |
| pytest | Framework de pruebas estándar en Python, con una sintaxis mínima basada en `assert`. |
| bcrypt | Guarda las contraseñas con hash. Ni la API ni los registros muestran la contraseña en claro. |
| Brevo | Envía el correo de confirmación por SMTP. |
| Google OAuth | Permite crear la cuenta o entrar con una cuenta de Google, sin confirmar el correo. |
| GitHub Actions | Integración continua integrada en el propio repositorio, sin servicios externos. |
| Docker | Empaqueta la aplicación para que se ejecute igual en local y en el proveedor cloud. |
| MongoDB Atlas | Base persistente de la aplicación. Las pruebas usan repositorios en memoria. |

## Arquitectura

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

### Recorrido de una petición

`POST /api/auth/registro` → `auth_controller` valida la entrada → crea un `RegistrarUsuarioCommand` → lo ejecuta `RegistrarUsuarioUseCase`, que guarda el `Usuario` en estado `pendiente` y pide a `EmitirConfirmacionUseCase` el correo con el enlace. Si Brevo no puede enviarlo, se borra el usuario recién creado para que el alta se pueda repetir. Si el email ya existe, el use case lanza `UsuarioYaExiste` y el handler lo convierte en un `409`.

### Convención de nombres

- Las carpetas empiezan por mayúscula y dicen qué hay dentro: `PruebasUseCase`, `DominioUseCases`, `ApiRestControllers`…
- Las capas van en español (`Cliente`, `Servidor`, `Dominio`, `Infraestructura`) y los patrones en inglés (`UseCases`, `Controllers`, `Repositories`).
- Un archivo por clase, con el patrón como sufijo: `registrar_usuario_use_case.py`, `usuario_controller.py`…
- **Commands** modifican el estado. **Queries** solo consultan.

## Estructura

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

### Añadir una funcionalidad nueva

1. `DominioCommands/` o `DominioQueries/`: el objeto con los datos de entrada.
2. `DominioUseCases/`: la regla de negocio.
3. `DominioExceptions/`: los errores nuevos, si los hay.
4. `ApiRestSchemas/`: la entrada y salida de la API.
5. `ApiRestDependencies/`: el proveedor del use case.
6. `ApiRestControllers/`: el endpoint.
7. `ApiRestHandlers/`: la traducción de los errores nuevos a HTTP.
8. `PruebasUseCase/` y `PruebasApi/`: sus pruebas.

## Ejecución en local

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
python main.py
```

- Cliente: http://localhost:8000
- Documentación de la API: http://localhost:8000/docs

## Pruebas

```powershell
pytest
```

## Variables de entorno

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
| `BREVO_SMTP_SERVIDOR` | Servidor SMTP. Con Brevo, `smtp-relay.brevo.com` |
| `BREVO_SMTP_PUERTO` | Puerto SMTP. Con Brevo, `587` |
| `BREVO_SMTP_USUARIO` | Usuario SMTP de Brevo |
| `BREVO_SMTP_CLAVE` | Clave SMTP de Brevo. No se sube al repositorio |
| `BREVO_REMITENTE` | Correo verificado en Brevo desde el que sale la confirmación |
| `BREVO_REMITENTE_NOMBRE` | Nombre que ve quien recibe el correo |
| `GOOGLE_CLIENT_ID` | Identificador del cliente OAuth de Google. Vacío hasta crearlo |
| `GOOGLE_CLIENT_SECRET` | Secreto de ese cliente. No se sube al repositorio |
| `URL_PUBLICA` | Origen público sin barra final. En Cloud Run, la URL del servicio. En local se puede dejar vacía |

## Confirmación por correo

El alta deja la cuenta en `pendiente`. El servidor envía un enlace `{URL}/?confirmar={token}` que caduca a las 24 horas. La página llama a `POST /api/auth/confirmar` y, si el token es válido, pasa la cuenta a `activo`. Hasta ese momento el inicio de sesión responde `403` con el mensaje de cuenta pendiente.

Si el correo no llega, en el login se escribe el mismo email y se pulsa **Reenviar confirmación**. El enlace anterior deja de valer. Una cuenta ya activa o eliminada no recibe otro correo.

Si Brevo rechaza el envío, el alta responde `502` y no deja la cuenta a medias.

## Inicio de sesión con Google

El botón **Entrar con Google** abre `GET /api/auth/google`. Google devuelve el navegador a `GET /api/auth/google/callback`. Si el correo es nuevo, se crea la cuenta ya en `activo`, con una contraseña aleatoria que no se muestra. Si ya estaba pendiente, se activa y se entra. Si estaba eliminada, se vuelve al login con un aviso. Una cuenta activa entra sin cambiar la contraseña.

Para activarlo en Google Cloud Console, credenciales → crear ID de cliente OAuth de tipo aplicación web, y registrar estas URIs de redirección tal cual:

- `http://127.0.0.1:8000/api/auth/google/callback`
- `https://procesos2627-459073742710.europe-west1.run.app/api/auth/google/callback`

El identificador y el secreto van en `.env` y, al desplegar, en las variables de Cloud Run. Sin esas dos variables el botón vuelve al login y explica que Google todavía no está configurado.

## Flujo de trabajo (GitHub Flow)

1. Crear una rama por cambio a partir de `main`.
2. Ejecutar `pytest` en local antes de abrir el pull request.
3. Abrir un pull request hacia `main`; el CI ejecuta las pruebas automáticamente.
4. Integrar solo con el CI en verde. El workflow despliega ese commit en Cloud Run.

## Despliegue

Al integrar en `main`, el workflow `.github/workflows/ci.yml` ejecuta las pruebas y, si pasan, despliega el `Dockerfile` en el servicio `procesos2627` de Cloud Run, región `europe-west1`.

URL pública: https://procesos2627-459073742710.europe-west1.run.app

La misma dirección sale al final de la ejecución, en la pestaña Actions del repositorio. Un pull request solo lanza las pruebas y no publica.

La autenticación usa el secreto `GCP_CREDENTIALS` de GitHub: el JSON de una cuenta de servicio del mismo proyecto, con los roles Cloud Run Source Developer, Service Usage Consumer y Service Account User. Esa clave no se sube al repositorio.

El despliegue deja `DATOS_MOTOR=mongo` y `URL_PUBLICA` con la URL de arriba. `COOKIE_SEGURA=true` va en la imagen. El resto de variables (Mongo, administrador, Brevo y Google) se configuran una vez en el servicio de Cloud Run y se conservan en los despliegues siguientes. En Brevo, la restricción por IP solo deja enviar desde las direcciones autorizadas: el correo de confirmación en Cloud Run necesita que esa restricción esté desactivada, porque la IP de salida del servicio cambia.

## Acceso como administrador

Si `ADMIN_EMAIL` y `ADMIN_PASSWORD` están definidos y todavía no hay un administrador, el arranque crea esa cuenta en estado `activo` o, si el email ya existe, solo le asigna el rol. Esa cuenta no pasa por la confirmación por correo. La contraseña no se sube al repositorio.

El administrador lista los usuarios, edita los de los demás y puede hacer administrador a otro desde esa edición. Un usuario normal solo ve su cuenta, edita la suya y solo puede eliminar la suya. `activo` significa que el correo está confirmado o que entró con Google, y que la cuenta no está eliminada. `pendiente` no puede iniciar sesión. `eliminado` tampoco, y no se puede volver a registrar ese correo.

## API REST

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/registro` | Alta. Deja la cuenta `pendiente` y envía el correo de confirmación |
| POST | `/api/auth/inicio-sesion` | Entra con email y contraseña. Crea la cookie `sesion` |
| POST | `/api/auth/cierre-sesion` | Cierra la sesión |
| GET | `/api/auth/sesion` | Usuario de la cookie actual |
| POST | `/api/auth/recuperacion` | Pide el token para cambiar la contraseña |
| POST | `/api/auth/nueva-contrasena` | Guarda la contraseña nueva y cierra las sesiones |
| POST | `/api/auth/confirmar` | Activa la cuenta con el token del enlace |
| POST | `/api/auth/reenviar-confirmacion` | Vuelve a enviar el enlace a una cuenta `pendiente` |
| GET | `/api/auth/google` | Redirige a Google |
| GET | `/api/auth/google/callback` | Recibe el código de Google y crea la sesión |
| GET | `/api/usuarios` | Lista usuarios. Un usuario normal solo se ve a sí mismo |
| PATCH | `/api/usuarios/me` | Edita el email, el nombre y, si se envía, la contraseña propios |
| GET | `/api/usuarios/numero` | Número de usuarios |
| POST | `/api/usuarios/{email}/administrador` | Un administrador convierte esa cuenta en administrador |
| GET | `/api/usuarios/{email}/activo` | Indica si esa cuenta está activa |
| DELETE | `/api/usuarios/{email}` | Marca la cuenta como eliminada y cierra sus sesiones |
| WS | `/ws` | Canal WebSocket |
