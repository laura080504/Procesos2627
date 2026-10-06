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
| GitHub Actions | Integración continua integrada en el propio repositorio, sin servicios externos. |
| Docker | Empaqueta la aplicación para que se ejecute igual en local y en el proveedor cloud. |

## Arquitectura

```
FRONT (navegador)                         BACK (servidor FastAPI)
┌─────────────────────────┐               ┌───────────────────────────────────┐
│ cliente / App           │               │ API      controllers → handlers   │
│   presentacion          │               │          schemas, dependencies    │
│   comunicacion          │── HTTP/WS ───▶│               │                   │
└─────────────────────────┘               │               ▼                   │
                                          │ DOMINIO  use_cases, entities,     │
                                          │          enums, exceptions        │
                                          │               │                   │
                                          │               ▼                   │
                                          │ INFRA    repositories, sqlite,    │
                                          │          migraciones              ┼──▶ aplicacion.db
                                          └───────────────────────────────────┘
```

El backend sirve el frontend desde el mismo origen, y el cliente solo se comunica con el servidor a través de la API. Cada capa solo conoce a la que tiene debajo. Es el mismo recorte que en C# (API, Shared/Domain, Infrastructure, Client), con nombres en español.

### Recorrido de una petición

`POST /api/auth/registro` → `auth_controller` valida la entrada → crea un `RegistrarUsuarioCommand` → lo ejecuta `RegistrarUsuarioUseCase` → guarda la entidad `Usuario` en el repositorio. Si el email ya existe, el use case lanza `UsuarioYaExiste` y el handler lo convierte en un `409`.

### Convención de nombres

- Las carpetas de capa van en español: `cliente`, `api_rest`, `dominio`, `infraestructura`, `presentacion`, `comunicacion`.
- Las carpetas de patrón van en inglés: `controllers`, `handlers`, `schemas`, `dependencies`, `use_cases`, `commands`, `queries`, `entities`, `enums`, `exceptions`, `repositories`.
- Un archivo por clase, con el patrón como sufijo: `registrar_usuario_use_case.py`, `usuario_controller.py`…
- **Commands** modifican el estado. **Queries** solo consultan.

## Estructura

```
Procesos2627/
├── cliente/                          # CLIENT / APP
│   ├── index.html
│   ├── shared/                       # Colores, estilos y textos de la interfaz
│   └── js/
│       ├── presentacion/             # Páginas y componentes (el equivalente a Razor)
│       ├── comunicacion/             # Cliente HTTP hacia la API
│       └── inicio.js
├── servidor/
│   ├── aplicacion.py
│   ├── api_rest/                     # API (controllers)
│   │   ├── controllers/
│   │   ├── handlers/
│   │   ├── schemas/                  # DTOs de entrada y salida
│   │   └── dependencies/
│   ├── api_ws/
│   ├── dominio/                      # SHARED / DOMAIN
│   │   ├── entities/
│   │   ├── enums/
│   │   ├── exceptions/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── use_cases/
│   └── infraestructura/              # INFRASTRUCTURE
│       ├── base_datos_sqlite.py
│       ├── registro_actividad.py
│       ├── repositories/
│       ├── migraciones/versiones/
│       └── aplicacion.db             # Archivo local, no se sube a git
├── pruebas/
│   ├── api/
│   ├── dominio/
│   └── datos/
├── main.py                           # Punto de entrada
├── Dockerfile
├── .env.example
├── requirements.txt
└── requirements-dev.txt
```

### Añadir una funcionalidad nueva

1. `dominio/commands/` o `dominio/queries/`: el objeto con los datos de entrada.
2. `dominio/use_cases/`: la regla de negocio.
3. `dominio/exceptions/`: los errores nuevos, si los hay.
4. `api_rest/schemas/`: la entrada y salida de la API.
5. `api_rest/dependencies/`: el proveedor del use case.
6. `api_rest/controllers/`: el endpoint.
7. `api_rest/handlers/`: la traducción de los errores nuevos a HTTP.
8. `pruebas/dominio/` y `pruebas/api/`: sus pruebas.

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

## Flujo de trabajo (GitHub Flow)

1. Crear una rama por cambio a partir de `main`.
2. Ejecutar `pytest` en local antes de abrir el pull request.
3. Abrir un pull request hacia `main`; el CI ejecuta las pruebas automáticamente.
4. Integrar solo con el CI en verde. Cada cambio en `main` se despliega automáticamente.

## Despliegue

La aplicación se despliega con el `Dockerfile` en Google Cloud Run, conectado al repositorio para desplegar cada cambio en `main`.

URL pública: _pendiente_

## Acceso como administrador

Si `ADMIN_EMAIL` y `ADMIN_PASSWORD` están definidos en `.env` y todavía no hay un administrador, el arranque crea esa cuenta o, si el email ya existe, solo le asigna el rol. La contraseña no se sube al repositorio.

El administrador lista los usuarios y puede eliminar cualquiera. Un usuario normal solo ve su cuenta y solo puede eliminar la suya. `estado = activo` significa que la cuenta puede entrar, no que tenga una sesión abierta.

## API REST

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/usuarios` | Agregar usuario `{ "nick": "..." }` |
| GET | `/api/usuarios` | Listar usuarios |
| GET | `/api/usuarios/numero` | Número de usuarios |
| GET | `/api/usuarios/{nick}/activo` | Comprobar si un usuario está activo |
| DELETE | `/api/usuarios/{nick}` | Eliminar usuario |
| WS | `/ws` | Canal WebSocket |
