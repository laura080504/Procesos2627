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
│ Cliente                 │               │ ApiRest  Controllers → Handlers   │
│   ClientePresentacion   │               │          Schemas, Dependencies    │
│   ClienteComunicacion   │── HTTP/WS ───▶│               │                   │
└─────────────────────────┘               │               ▼                   │
                                          │ Dominio  UseCases, Entities,      │
                                          │          Enums, Exceptions        │
                                          │               │                   │
                                          │               ▼                   │
                                          │ Infra    Repositories, sqlite,    │
                                          │          Migraciones              ┼──▶ aplicacion.db
                                          └───────────────────────────────────┘
```

El backend sirve el frontend desde el mismo origen, y el cliente solo se comunica con el servidor a través de la API. Cada capa solo conoce a la que tiene debajo. Es el mismo recorte que en C# (API, Shared/Domain, Infrastructure, Client), con nombres en español.

### Recorrido de una petición

`POST /api/auth/registro` → `auth_controller` valida la entrada → crea un `RegistrarUsuarioCommand` → lo ejecuta `RegistrarUsuarioUseCase` → guarda la entidad `Usuario` en el repositorio. Si el email ya existe, el use case lanza `UsuarioYaExiste` y el handler lo convierte en un `409`.

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
│       ├── base_datos_sqlite.py
│       ├── registro_actividad.py
│       ├── InfraestructuraRepositories/
│       ├── InfraestructuraMigraciones/MigracionesVersiones/
│       └── aplicacion.db                 # Archivo local, no se sube a git
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
