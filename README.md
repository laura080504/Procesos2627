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
│ presentacion            │               │ API      controllers → handlers   │
│   controlWeb.js         │               │          schemas, dependencies    │
│        │                │               │               │                   │
│        ▼                │               │               ▼                   │
│ comunicacion            │── HTTP/WS ───▶│ LÓGICA   use_cases                │
│   clienteRest.js        │               │          commands / queries       │
│   clienteHttp.js        │               │          entities, enums,         │
└─────────────────────────┘               │          exceptions               │
                                          │               │                   │
                                          │               ▼                   │
                                          │ DATOS    repositories             │
                                          │   ├─ memoria (local)              │
                                          │   └─ servicio ────────────────────┼──▶ BBDD externa
                                          └───────────────────────────────────┘
```

El backend sirve el frontend desde el mismo origen, y el cliente solo se comunica con el servidor a través de la API. Cada capa solo conoce a la que tiene debajo.

### Recorrido de una petición

`POST /api/usuarios` → `usuario_controller` valida la entrada con `UsuarioEntrada` → crea un `AgregarUsuarioCommand` → lo ejecuta `AgregarUsuarioUseCase` → guarda la entidad `Usuario` en el `RepositorioUsuarios`. Si el nick ya existe, el use case lanza `UsuarioYaExiste` y `usuario_handler` lo convierte en un `409`.

### Convención de nombres

- Las carpetas de capa siguen el PDF y van en español: `servidor`, `cliente`, `api_rest`, `logica`, `datos`, `presentacion`, `comunicacion`.
- Las carpetas de patrón van en inglés: `controllers`, `handlers`, `schemas`, `dependencies`, `use_cases`, `commands`, `queries`, `entities`, `enums`, `exceptions`, `repositories`.
- Un archivo por clase, con el patrón como sufijo: `agregar_usuario_use_case.py`, `agregar_usuario_command.py`, `usuario_controller.py`…
- **Commands** modifican el estado (agregar, eliminar). **Queries** solo consultan (listar, activo, número).

## Estructura

```
Procesos2627/
├── .github/workflows/ci.yml          # Integración continua
├── cliente/                          # FRONTEND
│   ├── index.html
│   ├── css/estilos.css
│   └── js/
│       ├── presentacion/             # Capa de presentación (GUI)
│       │   └── controlWeb.js
│       ├── comunicacion/             # Cliente de comunicación con el servidor
│       │   ├── clienteRest.js
│       │   └── clienteHttp.js
│       └── inicio.js                 # Crea las instancias y arranca la vista
├── servidor/                         # BACKEND
│   ├── aplicacion.py                 # Monta la app FastAPI
│   ├── api_rest/                     # CAPA API
│   │   ├── controllers/              # Endpoints HTTP
│   │   ├── handlers/                 # Excepciones de dominio → respuestas HTTP
│   │   ├── schemas/                  # Modelos de entrada y salida
│   │   └── dependencies/             # Inyección de use cases y repositorios
│   ├── api_ws/                       # CAPA API (WebSocket)
│   │   ├── controllers/
│   │   └── gestor_conexiones.py
│   ├── logica/                       # CAPA LÓGICA
│   │   ├── use_cases/                # Un caso de uso por archivo
│   │   ├── commands/                 # Datos de entrada de operaciones que modifican
│   │   ├── queries/                  # Datos de entrada de consultas
│   │   ├── entities/                 # Usuario
│   │   ├── enums/                    # Rol, EstadoUsuario
│   │   └── exceptions/               # Errores de dominio
│   └── datos/                        # CAPA DE DATOS
│       └── repositories/
│           ├── repositorio_usuarios.py            # Interfaz
│           ├── repositorio_usuarios_memoria.py    # Implementación en memoria
│           └── repositorio_usuarios_servicio.py   # BBDD externa (hito 3)
├── pruebas/
│   ├── conftest.py                   # Fixtures compartidas
│   ├── logica/                       # Pruebas unitarias de los use cases
│   └── api/                          # Pruebas de los controllers
├── main.py                           # Punto de entrada
├── Dockerfile
├── .env.example
├── requirements.txt
└── requirements-dev.txt
```

### Añadir una funcionalidad nueva

1. `logica/commands/` o `logica/queries/`: el objeto con los datos de entrada.
2. `logica/use_cases/`: la regla de negocio.
3. `logica/exceptions/`: los errores nuevos, si los hay.
4. `api_rest/schemas/`: la entrada y salida de la API.
5. `api_rest/dependencies/`: el proveedor del use case.
6. `api_rest/controllers/`: el endpoint.
7. `api_rest/handlers/`: la traducción de los errores nuevos a HTTP.
8. `pruebas/logica/` y `pruebas/api/`: sus pruebas.

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

Pendiente (hito 3). Las credenciales de prueba se enviarán junto con la entrega.

## API REST

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/usuarios` | Agregar usuario `{ "nick": "..." }` |
| GET | `/api/usuarios` | Listar usuarios |
| GET | `/api/usuarios/numero` | Número de usuarios |
| GET | `/api/usuarios/{nick}/activo` | Comprobar si un usuario está activo |
| DELETE | `/api/usuarios/{nick}` | Eliminar usuario |
| WS | `/ws` | Canal WebSocket |
