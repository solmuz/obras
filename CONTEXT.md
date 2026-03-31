# OBRAS — Tech Stack & Library Definitions
## Sistema de Gestión de Accesorios de Izaje v1.2.1

---
*Aplicación Web Responsiva — Módulo de Inspecciones y Certificaciones*
Versión 1.2.1 | Marzo 2026
 
---
 
## 1. Objetivo
 
Diseñar y desarrollar una aplicación web responsiva para gestionar proyectos de construcción, sus accesorios de izaje asignados y las inspecciones requeridas, con control de acceso por perfiles de usuario, visibilidad restringida por proyecto, seguimiento automatizado de certificaciones, historial completo de la hoja de vida de cada accesorio y un audit trail íntegro de todas las operaciones realizadas en el sistema.
 
---
 
## 2. Alcance
 
### 2.1 Módulos del sistema
 
- Autenticación y control de acceso
- Administración de usuarios
- Gestión de proyectos de construcción
- Gestión de equipos / Hoja de vida del accesorio
- Inspecciones externas (certificadas)
- Inspecciones en sitio (Programa Código de Color)
- Acta de baja del accesorio
- Panel de estado / Reportes y exportación PDF
- Auditoría (Audit Trail)
 
### 2.2 Usuarios objetivo
 
- Administrador
- Ingeniero / HSE (Seguridad y Medio Ambiente)
- Consulta
 
### 2.3 Entorno tecnológico
 
- Aplicación web responsiva, accesible desde campo (dispositivos móviles y tablets)
- Compatibilidad con navegadores modernos (Chrome, Firefox, Edge, Safari)
- Funcionalidad offline básica para consulta de fichas en campo
 
---
 
## 3. Definiciones y Reglas de Negocio
 
### 3.1 Sistema de semáforo — Estado del equipo
 
Cada accesorio tendrá un estado visual calculado automáticamente según el estado de sus inspecciones:
 
| Color | Condición | Descripción / Acción recomendada |
|---|---|---|
| 🟢 **VERDE** | Inspecciones vigentes (externa + en sitio) | El equipo puede seguir operando sin restricciones. |
| 🟡 **AMARILLO** | Alguna inspección vence en ≤ 30 días | Programar inspección próximamente. Alerta visible al usuario. |
| 🔴 **ROJO** | Inspección vencida o equipo desincorporado (Tag Rojo) | Equipo fuera de servicio. No debe usarse hasta regularización o acta de baja registrada. |
 
### 3.2 Ciclos de inspección
 
- **Inspección Externa (Certificada):** cada 6 meses desde la última fecha registrada.
- **Inspección en Sitio (Programa Código de Color):** cada 2 meses desde la última fecha registrada.
- El sistema calculará automáticamente la fecha de próxima inspección y el estado (vigente / vencida).
 
### 3.3 Identificadores del sistema
 
- **Equipo/Accesorio:** Cada accesorio se registra con un código interno único de la empresa. Este código no se duplica.
- **Inspecciones:** Identificadas por fecha + inspector + tipo de inspección.
- **Nota:** El número del certificado externo puede coincidir con el código interno del accesorio — el sistema debe permitirlo sin conflicto.
 
### 3.4 Estado de uso del accesorio
 
- **En Uso:** El accesorio se encuentra activo en campo.
- **En Stock:** El accesorio está disponible en almacén del proyecto.
- **Tag Rojo:** El accesorio está fuera de servicio. Este estado se activa automáticamente al registrar el Acta de Baja, o manualmente por inspección fallida.
 
### 3.5 Proyectos de construcción
 
Los accesorios de izaje pertenecen a proyectos de construcción. Las reglas que gobiernan esta relación son:
 
- Cada proyecto tiene un conjunto de accesorios asignados y un conjunto de empleados (Ingenieros / HSE) designados para su seguimiento.
- Un empleado puede estar asignado a más de un proyecto simultáneamente (relación muchos-a-muchos).
- Solo el Administrador puede crear proyectos, asignar empleados a proyectos y asignar / reasignar accesorios entre proyectos. Los empleados pueden ser de rol Ingeniero / HSE o Consulta.
- Un Ingeniero / HSE puede ver y registrar inspecciones de los accesorios de sus proyectos asignados.
- Un usuario de rol Consulta solo puede visualizar el estado de los equipos y exportar reportes de sus proyectos asignados. No puede crear ni modificar registros.
- Si un empleado es removido de un proyecto, pierde acceso a los registros futuros, pero su historial previo se conserva en el audit trail.
- Un accesorio puede ser reasignado de un proyecto a otro; el historial de inspecciones lo sigue.
 
### 3.6 Marca del accesorio
 
Existen 3 marcas de fabricante disponibles en el sistema. La marca se selecciona al registrar el accesorio y se despliega en inspecciones y reportes de forma automática.
 
### 3.7 Timestamps y Audit Trail
 
- Toda creación, modificación o eliminación de registros debe guardar fecha/hora UTC y el usuario responsable.
- El audit trail por equipo documenta: usuario, fecha/hora, tipo de acción (creación / edición / eliminación), detalle del cambio (valor anterior → valor nuevo).
- Zona horaria configurable por administrador. Valor por defecto: `America/Bogota`.
 
---
 
## 4. Módulos Funcionales
 
| ID | Módulo | Descripción / Funcionalidad |
|---|---|---|
| **MOD-01** | Autenticación y control de acceso | Login seguro, gestión de sesiones, control por perfil (Admin, Ingeniero / HSE, Consulta). El acceso de cada usuario queda limitado a los proyectos que le fueron asignados. |
| **MOD-02** | Administración de usuarios | CRUD de usuarios, asignación de roles (Admin / Ingeniero / HSE / Consulta), activación/desactivación de cuentas. Solo el Administrador puede crear usuarios y asignarlos a proyectos. |
| **MOD-03** | Gestión de proyectos | CRUD de proyectos de construcción. Asignación de empleados (Ingenieros / HSE) a proyectos — relación muchos-a-muchos. Asignación y reasignación de accesorios entre proyectos. Solo el Administrador gestiona estas relaciones. |
| **MOD-04** | Gestión de equipos (Hoja de vida) | Registro de información general fija: tipo de elemento, marca, serial, material, capacidad, longitud, diámetro, ramales. Código interno único. Estado de uso: En Uso / En Stock / Tag Rojo. Registro fotográfico. Cada accesorio está vinculado a un proyecto activo. |
| **MOD-05** | Inspecciones Externas (Certificadas) | Registro de: fecha, fecha próxima inspección, estado (vigente/vencida), empresa responsable, criterio final, adjuntar PDF del certificado (visualizable). Periodicidad: cada 6 meses. Solo visible para usuarios con acceso al proyecto correspondiente. |
| **MOD-06** | Inspecciones en Sitio (Código de Color) | Registro de: fecha, criterio final (buen estado / mal estado / observaciones), responsable, registro fotográfico. Periodicidad: cada 2 meses. Solo visible para usuarios con acceso al proyecto correspondiente. |
| **MOD-07** | Acta de Baja del Accesorio | Registro de: fecha de baja, motivo, registro fotográfico, responsable. Al registrarse, el equipo pasa automáticamente a Tag Rojo. |
| **MOD-08** | Panel de estado / Reportes | Vista de semáforo por equipo (Verde / Amarillo / Rojo). Filtros por estado, proyecto, tipo de elemento, marca. El Administrador ve todos los proyectos; Ingenieros y HSE solo ven sus proyectos asignados. Exportación a PDF. |
| **MOD-09** | Auditoría (Audit Trail) | Registro inmutable de toda creación, modificación o eliminación. Campos: usuario, fecha/hora, acción, detalle (antes/después). Zona horaria configurable (default: `America/Bogota`). |
 
---
 
## 5. Especificaciones de Datos por Módulo
 
### 5.0 Proyectos de Construcción
 
Entidad central que agrupa accesorios y empleados. Sus campos son:
 
| Campo | Tipo de Dato | Observaciones | Obligatoriedad |
|---|---|---|---|
| Nombre del proyecto | Texto | Único y descriptivo | Requerido |
| Descripción | Texto largo | Breve descripción del proyecto | Opcional |
| Estado | Enum: Activo / Inactivo | Solo proyectos activos admiten nuevos registros | Requerido |
| Fecha de inicio | Fecha | — | Requerido |
| Empleados asignados | Lista de usuarios (Ing./HSE) | Muchos-a-muchos; el Admin gestiona la asignación | Gestionado por Admin |
| Accesorios asignados | Lista de accesorios (código interno) | Un accesorio pertenece a un proyecto a la vez | Gestionado por Admin |
 
**Relaciones del modelo de datos:**
 
- **Proyecto — Accesorio:** un proyecto tiene muchos accesorios; un accesorio pertenece a un proyecto activo a la vez (puede reasignarse).
- **Proyecto — Empleado:** relación muchos-a-muchos gestionada por tabla intermedia `Empleado_Proyecto` (empleado, proyecto, fecha_asignación, fecha_remoción).
 
### 5.1 Información General del Accesorio (Hoja de Vida — Datos Fijos)
 
Los siguientes campos corresponden a la sección INFORMACIÓN GENERAL de la hoja de vida. Una vez registrados, estos datos no cambian (salvo las excepciones indicadas):
 
| Campo | Tipo de Dato | Observaciones | ¿Editable? |
|---|---|---|---|
| Código Interno | Texto | Único por empresa | No cambia |
| Tipo de Elemento | Lista (Eslingas, Grilletes, Ganchos, otros) | — | No cambia |
| Marca / Fabricante | Lista (3 marcas disponibles) | — | No cambia |
| Serial | Texto | — | No cambia |
| Material | Texto | — | No cambia |
| Capacidad (TON) | Texto / Numérico | Vertical, Choker, Basket | No cambia |
| Longitud (m) | Numérico | — | No cambia |
| Diámetro (pulg.) | Texto | — | No cambia |
| Cantidad de Ramales | Entero | Solo aplica para eslingas | No cambia |
| Proyecto (Ubicación) | Texto / Lista | Fluctúa; puede cambiar | Editable |
| Estado de Uso | Enum: En Uso / En Stock / Tag Rojo | Tag Rojo activa alerta | Editable |
| Foto del accesorio | Imagen | — | Editable |
| Foto etiqueta fabricante | Imagen | — | Editable |
| Foto marcación proveedor | Imagen | — | Editable |
 
### 5.2 Inspecciones Externas Certificadas
 
Cada accesorio puede tener múltiples registros de inspecciones externas a lo largo del tiempo:
 
| Campo | Tipo de Dato | Observaciones | Obligatoriedad |
|---|---|---|---|
| Fecha de inspección | Fecha | — | Requerido |
| Fecha próxima inspección | Fecha | Calculada automáticamente (+6 meses) | Auto-calculado |
| Estado de inspección | Enum: Vigente / Vencida | Calculado vs. fecha actual | Auto-calculado |
| Empresa responsable | Texto | Empresa certificadora | Requerido |
| Criterio final (Certificado) | Texto / Lista | Resultado de la inspección | Requerido |
| Certificado PDF | Archivo PDF | Visualizable con clic. Mismo N° puede coincidir con código interno | Requerido |
| Código Interno (referencia) | Texto | Vinculado al equipo | Automático |
| Proyecto | Texto | Proyecto donde está el equipo | Requerido |
| Empresa | Enum: GEO / SBCIMAS / PREFA / BESSAC | Empresa que tiene el accesorio de izaje | Requerido |
| Estado del aparejo | Enum: En Uso / En Stock / Tag Rojo | — | Requerido |
 
### 5.3 Inspecciones en Sitio — Programa Código de Color
 
Se registran cada 2 meses, asociadas al período bimestral correspondiente (Ene-Feb, Mar-Abr, May-Jun, Jul-Ago, Sep-Oct, Nov-Dic):
 
| Campo | Tipo de Dato | Observaciones | Obligatoriedad |
|---|---|---|---|
| Fecha de inspección | Fecha | — | Requerido |
| Criterio final | Enum: Buen Estado / Mal Estado / Observaciones | — | Requerido |
| Responsable de la inspección | Texto / Usuario | — | Requerido |
| Registro fotográfico | Imágenes | Múltiples fotos permitidas | Requerido |
| Proyecto | Texto | — | Requerido |
| Empresa | Enum: GEO / SBCIMAS / PREFA / BESSAC | Empresa que tiene el accesorio de izaje | Requerido |
| Estado del aparejo | Enum: En Uso / En Stock / Tag Rojo | — | Requerido |
| Estado de inspección | Enum: Vigente / Vencida | Calculado vs. fecha actual (+2 meses) | Auto-calculado |
| Período de color | Enum: Ene-Feb / Mar-Abr / May-Jun / Jul-Ago / Sep-Oct / Nov-Dic | Calculado por fecha de inspección | Automático |
 
> **Nota sobre períodos de color:** Solo los períodos activos según la fecha de la inspección deben estar habilitados para edición. Los períodos pasados quedan como histórico de solo lectura. El período Marzo-Abril será el primer período activo a agregar en la nueva versión del sistema.
 
### 5.4 Acta de Baja del Accesorio
 
Cuando un accesorio es dado de baja definitiva, se registra el acta correspondiente. Al guardar este registro, el sistema debe cambiar automáticamente el estado del accesorio a **Tag Rojo**:
 
| Campo | Tipo de Dato | Observaciones |
|---|---|---|
| Fecha de baja | Fecha | Requerido |
| Motivo de la baja | Texto largo | Descripción detallada del motivo. Requerido |
| Registro fotográfico del elemento | Imágenes | Múltiples fotos. Requerido |
| Responsable de la dada de baja | Texto / Usuario | Requerido |
 
---
 
## 6. Perfiles y Permisos
 
| Funcionalidad | Administrador | Ingeniero / HSE | Consulta | Notas |
|---|---|---|---|---|
| Iniciar sesión | ✓ | ✓ | ✓ | |
| Ver proyectos asignados | ✓ (todos) | Solo los propios | Solo los propios | Admin ve todos los proyectos |
| Crear / editar proyectos | ✓ | ✗ | ✗ | |
| Asignar empleados a proyectos | ✓ | ✗ | ✗ | Relación muchos-a-muchos |
| Asignar / reasignar accesorios a proyectos | ✓ | ✗ | ✗ | |
| Ver equipos y estado (semáforo) | ✓ (todos) | Solo proyectos propios | Solo proyectos propios | |
| Agregar nuevo equipo | ✓ | ✓ | ✗ | |
| Editar datos del equipo | ✓ | ✓ | ✗ | |
| Registrar inspección externa | ✓ | ✓ | ✗ | Solo en proyectos asignados |
| Registrar inspección en sitio | ✓ | ✓ | ✗ | Solo en proyectos asignados |
| Subir certificado PDF | ✓ | ✓ | ✗ | Visualizable al hacer clic |
| Subir fotos de inspección | ✓ | ✓ | ✗ | |
| Generar acta de baja del accesorio | ✓ | ✓ | ✗ | Activa Tag Rojo automáticamente |
| Ver reportes por estado / proyecto | ✓ (todos) | Solo proyectos propios | Solo proyectos propios | |
| Exportar reportes (PDF) | ✓ | ✓ | ✓ | |
| Ver Audit Trail | ✓ | Solo sus inspecciones | ✗ | |
| Administrar usuarios | ✓ | ✗ | ✗ | |
| Configurar ciclos de inspección | ✓ | ✗ | ✗ | |
 
---
 
## 7. Requerimientos Funcionales y No Funcionales
 
### 7.1 Usabilidad
 
- La interfaz debe ser responsiva y operable desde dispositivos móviles en campo.
- El estado semáforo del accesorio debe ser visible de forma prominente en la vista de listado.
- Los certificados PDF deben poder visualizarse en el navegador con un solo clic, sin descarga obligatoria.
 
### 7.2 Seguridad
 
- Autenticación requerida para todas las rutas del sistema.
- Control de acceso basado en roles (RBAC) estricto en frontend y backend.
- Los archivos adjuntos (PDF, imágenes) deben estar protegidos y solo accesibles para usuarios autenticados.
 
### 7.3 Integridad de datos
 
- El código interno del accesorio debe ser único en todo el sistema.
- Las operaciones de eliminación deben ser lógicas (soft delete), no físicas, para preservar el audit trail.
- La transición a Tag Rojo al registrar el Acta de Baja debe ser atómica (en la misma transacción).
 
### 7.4 Trazabilidad
 
- Cada acción de escritura en el sistema genera automáticamente un registro de auditoría.
- El audit trail no puede ser editado ni eliminado por ningún perfil de usuario.
 
### 7.5 Disponibilidad y rendimiento
 
- La aplicación debe soportar acceso simultáneo de múltiples usuarios en campo.
- La carga de la lista de equipos con estado semáforo debe completarse en menos de 3 segundos para hasta 500 registros.
 
---
 
## 8. Consideraciones de Migración desde la Hoja de Vida Excel
 
El sistema actual utiliza un sistema distinto para la "Hoja de Vida Accesorios de Izaje" para registrar la información. La migración al nuevo sistema debe contemplar los siguientes aspectos:
 
### 8.1 Datos a migrar
 
- Información general del accesorio (datos fijos).
- Historial de inspecciones externas registradas.
- Historial de inspecciones en sitio por período de color.
- Actas de baja ya registradas (si aplica).
 
### 8.2 Cambios estructurales identificados respecto al Excel actual
 
- Columnas PROYECTO, MARCA y ESTADO DEL APAREJO se agregan como campos propios de cada inspección (externa y en sitio), no solo de la información general.
- La columna 'Criterio final de la inspección realizada (Certificado)' de la sección de inspecciones externas será eliminada del formato de campo libre y reemplazada por un campo estructurado en el sistema.
- El período Enero-Febrero de inspecciones en sitio queda como histórico. El período Marzo-Abril es el primer período activo a registrar.
- Se eliminan de la hoja de vida los campos que el sistema calculará automáticamente (fecha próxima inspección, estado vigente/vencida).
 
### 8.3 Validaciones durante la migración
 
- Verificar unicidad del código interno antes de importar.
- Validar formato de fechas.
- Mapear el estado actual (Tag Rojo / En Uso / En Stock) según el estado en Excel.
 
---
 
## 9. Glosario
 
| Término | Definición |
|---|---|
| **Accesorio / Aparejo de izaje** | Elemento o equipo utilizado para izar cargas: eslingas, grilletes, ganchos, entre otros. |
| **Código Interno** | Identificador único asignado por la empresa a cada accesorio. |
| **Proyecto de construcción** | Unidad organizativa que agrupa accesorios de izaje y empleados responsables de su seguimiento. |
| **Asignación empleado-proyecto** | Relación que otorga a un empleado acceso a los accesorios e inspecciones de un proyecto específico. Un empleado puede estar asignado a más de un proyecto. |
| **Inspección Externa** | Inspección certificada realizada por una empresa competente. Vigencia: 6 meses. |
| **Inspección en Sitio** | Inspección visual realizada en obra como parte del Programa Código de Color. Vigencia: 2 meses. |
| **Código de Color** | Programa bimestral de inspección visual de accesorios en obra. |
| **Tag Rojo** | Estado que indica que el accesorio está fuera de servicio y no debe utilizarse. |
| **Acta de Baja** | Documento formal que registra la desincorporación definitiva de un accesorio. |
| **Semáforo** | Indicador visual de estado: Verde (vigente), Amarillo (por vencer), Rojo (vencido o dado de baja). |
| **Audit Trail** | Registro inmutable de todas las operaciones realizadas en el sistema, con fecha, usuario y detalle. |
| **HSE** | Health, Safety & Environment — Ingeniero de Seguridad y Medio Ambiente. |
| **Ingeniero / HSE** | Rol unificado que agrupa a Ingenieros y personal HSE. Puede registrar y editar inspecciones en los proyectos asignados. |
| **Consulta** | Rol de solo lectura. Puede ver el estado de los equipos y exportar reportes, pero no puede crear ni modificar registros de inspección. |
 
---
 
## 10. Control de Versiones del Documento
 
| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0 | Marzo 2026 | Equipo del Proyecto | Versión inicial del documento de requerimientos. |
| 1.1 | Marzo 2026 | Equipo del Proyecto | Se incorpora módulo de Gestión de Proyectos: modelo muchos-a-muchos empleado-proyecto, asignación de accesorios por proyecto, restricción de visibilidad por proyecto asignado. Actualización de permisos y especificaciones de datos. |
| 1.2.1 | Marzo 2026 | Equipo del Proyecto | Reestructuración de roles: HSE se fusiona con Ingeniero en rol unificado Ingeniero / HSE. Se crea nuevo rol Consulta (solo lectura y exportación de reportes, sin capacidad de registro ni modificación). Actualización de matriz de permisos, módulos y reglas de negocio. |
 

## 11. Frontend

### Core Framework
| Library | Version | Purpose |
|---|---|---|
| `react` | ^18.3 | UI framework |
| `react-dom` | ^18.3 | DOM rendering |
| `typescript` | ^5.4 | Static typing |
| `vite` | ^5.2 | Build tool & dev server |

### Routing
| Library | Version | Purpose |
|---|---|---|
| `react-router-dom` | ^6.23 | Client-side routing, protected routes, role-based guards |

### State Management
| Library | Version | Purpose |
|---|---|---|
| `zustand` | ^4.5 | Global client state (auth session, user profile, active project) |
| `@tanstack/react-query` | ^5.40 | Server state, caching, background refetch for equipment status |

### Styling
| Library | Version | Purpose |
|---|---|---|
| `tailwindcss` | ^3.4 | Utility-first responsive CSS (mobile/tablet/desktop) |
| `@headlessui/react` | ^2.1 | Accessible UI primitives (modals, dropdowns, dialogs) |
| `lucide-react` | ^0.390 | Icon set (semáforo icons, status indicators, action buttons) |

### Forms & Validation
| Library | Version | Purpose |
|---|---|---|
| `react-hook-form` | ^7.51 | Performant form state management |
| `zod` | ^3.23 | Schema validation — mirrors backend Pydantic schemas |
| `@hookform/resolvers` | ^3.6 | Connects Zod schemas to React Hook Form |

### HTTP Client
| Library | Version | Purpose |
|---|---|---|
| `axios` | ^1.7 | API requests; interceptor for JWT Bearer token injection and 401 handling |

### PDF & File Handling
| Library | Version | Purpose |
|---|---|---|
| `react-pdf` | ^7.7 | In-browser PDF viewer for inspection certificates (MOD-05) |
| `jspdf` | ^2.5 | Client-side PDF export for status reports and equipment sheets (MOD-08) |
| `jspdf-autotable` | ^3.8 | Table rendering inside exported PDFs |
| `react-dropzone` | ^14.2 | Drag-and-drop file upload for certificates and photos |

### Date Handling
| Library | Version | Purpose |
|---|---|---|
| `date-fns` | ^3.6 | Date formatting, interval calculations (próxima inspección, vencimiento) |
| `date-fns-tz` | ^3.1 | Timezone-aware display (America/Bogota default, configurable by admin) |

### Offline Support
| Library | Version | Purpose |
|---|---|---|
| `workbox-webpack-plugin` | ^7.1 | Service Worker for basic offline access to equipment sheets (MOD-04) |

---

## 12. Backend

### Core Framework
| Library | Version | Purpose |
|---|---|---|
| `fastapi` | ^0.111 | REST API framework |
| `uvicorn[standard]` | ^0.30 | ASGI server |
| `python` | ^3.12 | Runtime |

### Authentication & Security — JWT
| Library | Version | Purpose |
|---|---|---|
| `python-jose[cryptography]` | ^3.3 | JWT creation, signing, and verification (`HS256` / `RS256`) |
| `passlib[bcrypt]` | ^1.7 | Password hashing with bcrypt |
| `python-multipart` | ^0.0.9 | Form data parsing (required for OAuth2 password flow) |

**JWT Flow:** FastAPI's `OAuth2PasswordBearer` + `python-jose` issues access tokens (short TTL) and refresh tokens (long TTL). All routes use a `get_current_user` dependency that decodes the Bearer token and enforces the RBAC role matrix (Admin / Ingeniero-HSE / Consulta).

### Database ORM
| Library | Version | Purpose |
|---|---|---|
| `sqlalchemy` | ^2.0 | ORM with async support |
| `alembic` | ^1.13 | Database migrations |
| `asyncpg` | ^0.29 | Async PostgreSQL driver |
| `psycopg2-binary` | ^2.9 | Sync driver (for Alembic CLI and scripts) |

### Data Validation
| Library | Version | Purpose |
|---|---|---|
| `pydantic` | ^2.7 | Request/response schemas, environment settings |
| `pydantic-settings` | ^2.2 | `.env` configuration via `BaseSettings` |

### File Storage
| Library | Version | Purpose |
|---|---|---|
| `python-multipart` | ^0.0.9 | Multipart file upload handling |
| `aiofiles` | ^23.2 | Async file I/O for saving uploads |
| `pillow` | ^10.3 | Image validation and thumbnail generation (MOD-04, MOD-06, MOD-07) |

> **Storage backend:** Local filesystem for development; pluggable to AWS S3 / MinIO via an abstract `StorageService` interface for production.

### PDF Generation (Server-side)
| Library | Version | Purpose |
|---|---|---|
| `reportlab` | ^4.2 | Server-side PDF report generation (MOD-08 — full equipment status report) |
| `pypdf` | ^4.2 | Read/validate uploaded inspection certificate PDFs (MOD-05) |

### Background Tasks & Scheduling
| Library | Version | Purpose |
|---|---|---|
| `apscheduler` | ^3.10 | Cron job: nightly recalculation of semáforo status (Verde/Amarillo/Rojo) and generation of expiry alerts |

### CORS & Middleware
| Library | Version | Purpose |
|---|---|---|
| `fastapi` (built-in) | — | `CORSMiddleware` for React dev server origin |

---

## 13. Database

| Component | Technology | Notes |
|---|---|---|
| Primary DB | **PostgreSQL 16** | Main relational store |
| Async driver | `asyncpg` | Used by SQLAlchemy async sessions |
| Migrations | `alembic` | Version-controlled schema changes |

Key design considerations:
- **Soft deletes** (`deleted_at` timestamp) on all entities to preserve audit trail (RQ 7.3).
- **Audit Trail table** — append-only, no UPDATE/DELETE permissions granted at DB level (RQ 7.4).
- **Many-to-many** `project_user` and `project_accessory` join tables (RQ 3.5).

---

## 14. DevOps & Tooling

| Tool | Purpose |
|---|---|
| `docker` + `docker-compose` | Containerized local dev environment (API + DB + storage) |
| `pytest` + `httpx` | Backend unit and integration testing |
| `pytest-asyncio` | Async test support for FastAPI routes |
| `eslint` + `prettier` | Frontend code quality |
| `vitest` + `@testing-library/react` | Frontend component testing |

---

## 15. Summary Architecture Diagram

```
Browser (React 18 + TypeScript)
  │
  │  HTTPS + JWT Bearer Token
  ▼
FastAPI (Uvicorn ASGI)
  ├── Auth router    → python-jose  →  JWT issue / verify
  ├── Users router   → SQLAlchemy   →  PostgreSQL
  ├── Projects router
  ├── Equipment router  → Pillow    →  Image storage
  ├── Inspections router → pypdf   →  Certificate storage
  ├── Reports router    → ReportLab → PDF generation
  └── Audit router   (append-only reads)
        │
        ▼
  PostgreSQL 16
  (asyncpg driver, Alembic migrations)
```

---

## 15.1 Critical Implementation Decisions

### 1. Semáforo State Calculation Strategy

**Decision:** Hybrid lazy + scheduled recalculation approach
- **On-read (lazy):** Calculate Verde/Amarillo/Rojo dynamically when querying accessories or reports
- **Scheduled (nightly):** APScheduler job recalculates at 02:00 UTC to pre-populate cache and trigger background alerts
- **Rationale:** Ensures users always see current state without day-long delays; scheduled job reduces real-time compute load

**Implementation:**
```python
# In report_service.py — compute dynamically on query
def calculate_semaforo(accessory, today: date) -> str:
    ext_inspection = accessory.external_inspections[-1] or None
    site_inspection = accessory.site_inspections[-1] or None
    
    # Tag Rojo takes priority
    if accessory.status == "TAG_ROJO":
        return "ROJO"
    
    # Check both inspections vigent + within 30 days
    ext_next = ext_inspection.next_date if ext_inspection else None
    site_next = site_inspection.next_date if site_inspection else None
    
    if not ext_next or not site_next:
        return "ROJO"  # Missing inspection
    
    days_ext = (ext_next - today).days
    days_site = (site_next - today).days
    
    if days_ext < 0 or days_site < 0:
        return "ROJO"  # Expired
    
    if days_ext <= 30 or days_site <= 30:
        return "AMARILLO"  # Within 30 days
    
    return "VERDE"
```

**Cache Invalidation:** Invalidate accessory cache on inspection creation; rebuild during nightly scheduler.

---

### 2. Concurrency Control & Race Conditions

**Decision:** Optimistic locking with version field + database constraints
- Add `version` integer field to `Accessory`, `ExternalInspection`, `SiteInspection` tables
- On UPDATE, enforce: `WHERE id = ? AND version = ?` then increment if successful
- Return 409 Conflict if version mismatch (concurrent edit detected)
- For atomic Tag Rojo transition on decommission: use database transaction with `FOR UPDATE` lock

**SQL Implementation (Alembic migration):**
```sql
ALTER TABLE accessories ADD COLUMN version INTEGER DEFAULT 1;
ALTER TABLE external_inspections ADD COLUMN version INTEGER DEFAULT 1;
ALTER TABLE site_inspections ADD COLUMN version INTEGER DEFAULT 1;
```

**Application logic (SQLAlchemy):**
```python
# In accessory_service.py — optimistic update
stmt = update(Accessory).where(
    (Accessory.id == accessory_id) & (Accessory.version == current_version)
).values(status=new_status, version=Accessory.version + 1)

result = await db.execute(stmt)
if result.rowcount == 0:
    raise HTTPException(status_code=409, detail="Conflict: concurrent edit detected")
```

---

### 3. File Storage Security & Lifecycle

**Decision:** Abstract `StorageService` interface with development (local FS) + production (S3) backends

**Development (Local Filesystem):**
- Store files in `backend/storage/{certificates|photos|reports}/`
- Serve via FastAPI static file route with auth check
- Max file size: 50 MB per upload
- Allowed MIME types: `application/pdf`, `image/jpeg`, `image/png`

**Production (AWS S3 + CloudFront):**
- Use boto3 to upload to S3 bucket with server-side encryption (AES-256)
- Generate signed URLs (15-min expiry) for downloads
- CloudFront distribution as CDN to reduce S3 API calls
- Enable versioning on bucket for accidental deletion recovery

**Implementation:**
```python
# app/services/storage_service.py — abstract interface
class StorageService(ABC):
    @abstractmethod
    async def upload(self, file: UploadFile, folder: str) -> str:
        """Returns file URL or key"""
    
    @abstractmethod
    async def get_download_url(self, key: str, ttl_seconds: int = 900) -> str:
        """Returns signed URL"""
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Soft delete or hard delete"""

# LocalStorageService (dev) + S3StorageService (prod)
```

**Image Processing:**
- Validate with Pillow (reject corrupted files)
- Generate thumbnail (200x200px) for list views
- Max dimensions: 4000x4000px (prevent DoS via huge images)

---

### 4. JWT Token Lifecycle & Session Management

**Decision:** Dual-token strategy with refresh token rotation

**Token Configuration:**
| Token Type | TTL | Storage | Use Case |
|---|---|---|---|
| Access Token | 15 minutes | Memory (Zustand) | API requests (Bearer header) |
| Refresh Token | 7 days | HttpOnly secure cookie | Silent renewal |

**Backend (`app/core/security.py`):**
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
TOKEN_ALGORITHM = "HS256"

def create_tokens(user: User) -> dict:
    access = create_jwt(
        {"sub": user.id, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh = create_jwt(
        {"sub": user.id, "type": "refresh"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return {"access_token": access, "refresh_token": refresh}
```

**Frontend Token Handling (Zustand):**
- Access token stored in memory (lost on page reload — security best practice)
- Refresh token stored in httpOnly cookie (set by backend with `Set-Cookie` header)
- Login: POST `/api/v1/auth/login` → get tokens + set cookie
- Token expiry: Axios interceptor catches 401, POST `/api/v1/auth/refresh` → get new access token
- Logout: DELETE `/api/v1/auth/logout` → clear refresh cookie + clear memory, redirect to `/login`

**Rate Limiting on Auth:**
- Flask-Limiter: 5 login attempts per IP per minute
- 429 Too Many Requests response after threshold

---

### 5. Performance Optimization Strategy

**Database Indexes (Alembic migration):**
```sql
CREATE INDEX idx_accessories_project_id ON accessories(project_id);
CREATE INDEX idx_accessories_code ON accessories(code_internal);
CREATE INDEX idx_external_inspections_accessory_id ON external_inspections(accessory_id);
CREATE INDEX idx_external_inspections_created_at ON external_inspections(created_at DESC);
CREATE INDEX idx_site_inspections_accessory_id ON site_inspections(accessory_id);
CREATE INDEX idx_site_inspections_created_at ON site_inspections(created_at DESC);
CREATE INDEX idx_project_users_user_id ON project_users(user_id, project_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
```

**API Response Pagination (MOD-08 Semáforo Dashboard):**
```python
# GET /api/v1/accessories?project_id=123&page=1&page_size=50
# Returns: {"data": [...], "total": 342, "page": 1, "page_size": 50}
```

**Frontend Optimization:**
- Lazy-load photo thumbnails in detail views (only load full image on click)
- TanStack Query caching: cache equipment list for 5 minutes, stale-while-revalidate
- Lighthouse target: Cumulative Layout Shift < 0.1, First Contentful Paint < 2s

**Target SLA:** <3 seconds for 500 accessories on slow 3G network

---

### 6. Timezone Handling & Date Calculation

**Decision:** Store all timestamps in UTC; display in user's configured timezone

**Backend Configuration (`app/core/config.py`):**
```python
from zoneinfo import ZoneInfo

DEFAULT_TIMEZONE = "America/Bogota"  # Admin can override per-user in future

class Settings(BaseSettings):
    TIMEZONE: str = "America/Bogota"  # From .env
    
    def get_user_now(self) -> datetime:
        return datetime.now(ZoneInfo("UTC")).astimezone(ZoneInfo(self.TIMEZONE))
```

**Inspection Date Calculations:**
```python
# All stored as UTC, but "next inspection" logic uses timezone-aware dates
def calculate_next_external_inspection(inspection_date: datetime, tz: str):
    return (inspection_date + timedelta(days=180)).replace(tzinfo=ZoneInfo(tz))

# Yellow status: "within 30 days from today in user's timezone"
today_in_tz = datetime.now(ZoneInfo(tz)).date()
yellow_until = today_in_tz + timedelta(days=30)
```

**Frontend (`src/utils/dateUtils.ts`):**
```typescript
import { formatInTimeZone } from "date-fns-tz";

export const formatDateInTZ = (date: Date, tz: string = "America/Bogota"): string =>
  formatInTimeZone(date, tz, "yyyy-MM-dd HH:mm:ss");
```

**Critical:** Test edge cases:
- Midnight transitions (inspection on 23:59 in Bogota = yellow status change)
- Daylight saving time (if applicable)

---

### 7. Standard Error Response Contract

**Decision:** Consistent error schema across all endpoints

**Error Response Format:**
```json
{
  "detail": "string (human-readable message)",
  "error_code": "string (UNIQUE_CODE_FOR_ERROR)",
  "timestamp": "2026-03-20T14:35:22Z",
  "path": "/api/v1/accessories",
  "request_id": "uuid (for logging correlation)"
}
```

**Common Error Codes:**
| Code | HTTP Status | Description |
|---|---|---|
| `INVALID_CREDENTIALS` | 401 | Username or password incorrect |
| `TOKEN_EXPIRED` | 401 | Access token TTL elapsed |
| `INSUFFICIENT_PERMISSIONS` | 403 | User role lacks required permission |
| `PROJECT_NOT_FOUND` | 404 | Referenced project doesn't exist |
| `ACCESSORY_NOT_FOUND` | 404 | Equipment code not found |
| `UNIQUE_CONSTRAINT_VIOLATION` | 409 | Equipment code already exists |
| `CONCURRENT_EDIT` | 409 | Version mismatch (optimistic lock) |
| `FILE_UPLOAD_INVALID` | 400 | File size > 50MB, wrong MIME type |
| `VALIDATION_ERROR` | 422 | Request body schema mismatch (Pydantic) |
| `INTERNAL_SERVER_ERROR` | 500 | Unhandled exception |

**Backend Implementation (FastAPI exception handlers):**
```python
# In app/main.py
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.headers.get("error_code", "UNKNOWN"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url.path),
            "request_id": request.headers.get("x-request-id", str(uuid4()))
        }
    )
```

---

### 8. Testing Strategy & Fixtures

**Database Test Fixtures (`backend/tests/conftest.py`):**
```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def test_db():
    """In-memory SQLite for testing (or test PostgreSQL container)"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
async def admin_user(test_db) -> User:
    """Seeded admin user"""
    user = User(id="admin-1", email="admin@test.local", role="ADMIN", ...)
    test_db.add(user)
    await test_db.commit()
    return user

@pytest.fixture
async def project_with_accessories(test_db, admin_user) -> Project:
    """Seeded project with 5 accessories and inspection history"""
    project = Project(name="Test Project", created_by=admin_user.id)
    
    accessories = [
        Accessory(code=f"ACC-{i:03d}", brand="Brand1", status="EN_USO", project=project)
        for i in range(5)
    ]
    
    # Add inspection history
    accessories[0].external_inspections.append(
        ExternalInspection(inspection_date=date.today() - timedelta(days=100), ...)
    )
    
    test_db.add(project)
    await test_db.commit()
    return project
```

**Test Coverage Matrix:**
| Module | Unit Tests | Integration Tests | Notes |
|---|---|---|---|
| Auth | Login, token refresh, role validation | 401/403 handling | 5 tests |
| Accessories | CRUD, uniqueness, soft-delete | Permission checks | 12 tests |
| Inspections | Date auto-calc, color period logic | Version conflict simulations | 15 tests |
| Semáforo | Verde/Amarillo/Rojo calculation | Concurrent inspection updates | 8 tests |
| Decommission | Tag Rojo transition | Atomic rollback on failure | 4 tests |
| Reports | Filter queries, PDF generation | Large dataset (500 records) | 6 tests |

**Frontend Component Tests (`frontend/src/__tests__`):**
- SemaforoBadge: Render correct color + label
- AccessoryTable: Pagination, sort, filter
- LoginForm: Submit validation, error display

**E2E Scenarios (Cypress/Playwright):**
- Admin creates project → assigns employees → employees add accessories → inspections → reports

---

## 16. Dependency Files

### `frontend/package.json` (key dependencies)
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "zustand": "^4.5.2",
    "@tanstack/react-query": "^5.40.0",
    "axios": "^1.7.2",
    "react-hook-form": "^7.51.5",
    "zod": "^3.23.8",
    "@hookform/resolvers": "^3.6.0",
    "tailwindcss": "^3.4.4",
    "@headlessui/react": "^2.1.1",
    "lucide-react": "^0.390.0",
    "react-pdf": "^7.7.1",
    "jspdf": "^2.5.1",
    "jspdf-autotable": "^3.8.2",
    "react-dropzone": "^14.2.3",
    "date-fns": "^3.6.0",
    "date-fns-tz": "^3.1.3"
  },
  "devDependencies": {
    "typescript": "^5.4.5",
    "vite": "^5.2.13",
    "@vitejs/plugin-react": "^4.3.0",
    "vitest": "^1.6.0",
    "@testing-library/react": "^16.0.0",
    "eslint": "^9.4.0",
    "prettier": "^3.3.0"
  }
}
```

### `backend/requirements.txt`
```
# Framework
fastapi==0.111.0
uvicorn[standard]==0.30.1

# Auth & JWT
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9

# Database
sqlalchemy==2.0.30
alembic==1.13.1
asyncpg==0.29.0
psycopg2-binary==2.9.9

# Validation & Config
pydantic==2.7.3
pydantic-settings==2.2.1

# File Handling
aiofiles==23.2.1
pillow==10.3.0

# PDF
reportlab==4.2.2
pypdf==4.2.0

# Scheduling
apscheduler==3.10.4

# Testing
pytest==8.2.2
pytest-asyncio==0.23.7
httpx==0.27.0
```
## 17. Folder Structure

### backend: 
```
backend/
├── app/
│   ├── main.py                          # FastAPI app entry point, middleware, CORS, router registration
│   │
│   ├── core/                            # Global config, security, and cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── config.py                    # Pydantic BaseSettings (.env: DB URL, JWT secret, timezone, etc.)
│   │   ├── security.py                  # JWT creation/verification (python-jose), password hashing (bcrypt)
│   │   └── dependencies.py             # Shared FastAPI dependencies: get_current_user, require_role()
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py                  # MOD-01 — Login, refresh token, logout
│   │       ├── users.py                 # MOD-02 — CRUD users, role assignment, activate/deactivate
│   │       ├── projects.py              # MOD-03 — CRUD projects, assign employees, assign accessories
│   │       ├── accessories.py           # MOD-04 — CRUD accessories (hoja de vida), photo upload
│   │       ├── inspections_external.py  # MOD-05 — External certified inspections, PDF certificate upload
│   │       ├── inspections_site.py      # MOD-06 — On-site color-code inspections, photo upload
│   │       ├── decommissions.py         # MOD-07 — Acta de baja, triggers Tag Rojo atomically
│   │       ├── reports.py               # MOD-08 — Semáforo dashboard, filters, PDF export
│   │       └── audit.py                 # MOD-09 — Audit trail read-only endpoints
│   │
│   ├── models/                          # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                      # User, Role enum
│   │   ├── project.py                   # Project, ProjectEmployee (M2M), ProjectAccessory (M2M)
│   │   ├── accessory.py                 # Accessory (hoja de vida), UsageStatus enum, Brand enum
│   │   ├── inspection_external.py       # ExternalInspection, InspectionStatus enum
│   │   ├── inspection_site.py           # SiteInspection, ColorPeriod enum, SiteInspectionResult enum
│   │   ├── decommission.py              # DecommissionRecord
│   │   └── audit_log.py                 # AuditLog (append-only, no UPDATE/DELETE at DB level)
│   │
│   ├── schemas/                         # Pydantic v2 schemas for request/response validation
│   │   ├── __init__.py
│   │   ├── auth.py                      # TokenResponse, LoginRequest, RefreshRequest
│   │   ├── user.py                      # UserCreate, UserUpdate, UserOut, RoleEnum
│   │   ├── project.py                   # ProjectCreate, ProjectUpdate, ProjectOut, AssignEmployeeIn
│   │   ├── accessory.py                 # AccessoryCreate, AccessoryUpdate, AccessoryOut, StatusEnum
│   │   ├── inspection_external.py       # ExternalInspectionCreate, ExternalInspectionOut
│   │   ├── inspection_site.py           # SiteInspectionCreate, SiteInspectionOut, ColorPeriodEnum
│   │   ├── decommission.py              # DecommissionCreate, DecommissionOut
│   │   ├── report.py                    # ReportFilterParams, SemaforoRow, ReportOut
│   │   └── audit_log.py                 # AuditLogOut
│   │
│   ├── services/                        # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py              # Authenticate user, issue/refresh JWT tokens
│   │   ├── user_service.py              # User CRUD, role management, project assignment
│   │   ├── project_service.py           # Project CRUD, employee/accessory relationship management
│   │   ├── accessory_service.py         # Accessory CRUD, status transitions, photo management
│   │   ├── inspection_external_service.py  # Create/update external inspections, auto-calc next date
│   │   ├── inspection_site_service.py   # Create/update site inspections, color period logic
│   │   ├── decommission_service.py      # Register acta de baja, atomic Tag Rojo transition
│   │   ├── report_service.py            # Semáforo calculation, filter queries, PDF generation (ReportLab)
│   │   ├── audit_service.py             # Write audit entries, query audit trail with role filters
│   │   ├── storage_service.py           # Abstract file storage (local FS dev / S3 prod)
│   │   └── scheduler.py                 # APScheduler jobs: nightly semáforo recalculation, expiry alerts
│   │
│   └── db/                              # Database connection and session management
│       ├── __init__.py
│       ├── base.py                      # SQLAlchemy declarative Base, imports all models for Alembic
│       └── session.py                   # Async engine, AsyncSessionLocal, get_db() dependency
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Pytest fixtures: test DB, test client, seeded users/projects
│   ├── test_auth.py                     # Login, token refresh, role-based route protection
│   ├── test_users.py                    # CRUD users, role assignment, activate/deactivate
│   ├── test_projects.py                 # CRUD projects, employee/accessory assignment
│   ├── test_accessories.py              # CRUD accessories, status transitions, photo upload
│   ├── test_inspections_external.py     # Create inspections, date auto-calc, PDF upload
│   ├── test_inspections_site.py         # Create inspections, color period logic, photo upload
│   ├── test_decommissions.py            # Acta de baja, atomic Tag Rojo transition
│   ├── test_reports.py                  # Semáforo filter logic, PDF export
│   └── test_audit.py                    # Audit trail immutability, role-based visibility
│
├── alembic/
│   ├── env.py                           # Alembic env using async engine from app.db.session
│   ├── script.py.mako
│   └── versions/                        # Auto-generated migration files
│       └── .gitkeep
│
├── storage/                             # Local file storage (dev only — gitignored)
│   ├── certificates/                    # Uploaded PDF certificates (MOD-05)
│   ├── photos/                          # Accessory and inspection photos (MOD-04, MOD-06, MOD-07)
│   └── reports/                         # Generated PDF reports (MOD-08)
│
├── requirements.txt
├── alembic.ini
└── .env.example                         # Template for required environment variables
```
### frontend:

```
frontend/
├── public/
│   └── favicon.ico
│
├── src/
│   ├── main.tsx                         # React entry point
│   ├── App.tsx                          # Root component, router setup, QueryClientProvider
│   │
│   ├── routes/                          # Route definitions and guards
│   │   ├── index.tsx                    # All route declarations (React Router v6)
│   │   ├── ProtectedRoute.tsx           # Redirects to /login if no valid session
│   │   └── RoleGuard.tsx                # Blocks access based on role (Admin / Ing-HSE / Consulta)
│   │
│   ├── pages/                           # One folder per module/page
│   │   ├── auth/
│   │   │   └── LoginPage.tsx            # MOD-01 — Login form
│   │   ├── users/
│   │   │   ├── UsersPage.tsx            # MOD-02 — User list + management (Admin only)
│   │   │   └── UserFormPage.tsx         # Create / edit user
│   │   ├── projects/
│   │   │   ├── ProjectsPage.tsx         # MOD-03 — Project list
│   │   │   ├── ProjectFormPage.tsx      # Create / edit project
│   │   │   └── ProjectDetailPage.tsx    # Employees + accessories assigned to project
│   │   ├── accessories/
│   │   │   ├── AccessoriesPage.tsx      # MOD-04 — Accessory list with semáforo badges
│   │   │   ├── AccessoryFormPage.tsx    # Create / edit accessory (hoja de vida)
│   │   │   └── AccessoryDetailPage.tsx  # Full hoja de vida: data + inspection history
│   │   ├── inspections/
│   │   │   ├── ExternalInspectionForm.tsx   # MOD-05 — Register external inspection + PDF upload
│   │   │   └── SiteInspectionForm.tsx       # MOD-06 — Register site inspection + photo upload
│   │   ├── decommissions/
│   │   │   └── DecommissionForm.tsx     # MOD-07 — Register acta de baja
│   │   ├── reports/
│   │   │   └── ReportsPage.tsx          # MOD-08 — Semáforo dashboard, filters, PDF export
│   │   └── audit/
│   │       └── AuditPage.tsx            # MOD-09 — Audit trail viewer
│   │
│   ├── components/                      # Reusable UI components
│   │   ├── layout/
│   │   │   ├── AppShell.tsx             # Sidebar + topbar wrapper
│   │   │   ├── Sidebar.tsx              # Role-aware nav links
│   │   │   └── TopBar.tsx               # User info, logout button
│   │   ├── semaforo/
│   │   │   ├── SemaforoBadge.tsx        # 🟢🟡🔴 status pill component
│   │   │   └── SemaforoFilter.tsx       # Filter bar for status dashboard
│   │   ├── tables/
│   │   │   ├── AccessoryTable.tsx       # Accessories list with semáforo column
│   │   │   ├── InspectionTable.tsx      # Inspection history rows
│   │   │   └── AuditTable.tsx           # Audit log rows
│   │   ├── forms/
│   │   │   ├── FileUpload.tsx           # react-dropzone wrapper for PDF + photo uploads
│   │   │   └── DateField.tsx            # Date input with date-fns-tz formatting
│   │   ├── pdf/
│   │   │   └── CertificateViewer.tsx    # react-pdf inline viewer for inspection certificates
│   │   └── ui/
│   │       ├── Modal.tsx                # Headless UI Dialog wrapper
│   │       ├── ConfirmDialog.tsx        # Destructive action confirmation (e.g., Tag Rojo)
│   │       └── StatusChip.tsx           # En Uso / En Stock / Tag Rojo chip
│   │
│   ├── hooks/                           # Custom React hooks
│   │   ├── useAuth.ts                   # Read auth state from Zustand store
│   │   ├── useProjects.ts               # TanStack Query hooks for project data
│   │   ├── useAccessories.ts            # TanStack Query hooks for accessory data
│   │   ├── useInspections.ts            # TanStack Query hooks for inspections
│   │   └── useReports.ts                # Report query + PDF export trigger
│   │
│   ├── store/                           # Zustand global state
│   │   ├── authStore.ts                 # JWT tokens, user profile, role
│   │   └── uiStore.ts                   # Sidebar open/close, active project context
│   │
│   ├── services/                        # Axios API client functions
│   │   ├── api.ts                       # Axios instance with JWT interceptor + 401 handler
│   │   ├── authApi.ts                   # Login, refresh, logout
│   │   ├── usersApi.ts                  # Users CRUD
│   │   ├── projectsApi.ts               # Projects CRUD + assignments
│   │   ├── accessoriesApi.ts            # Accessories CRUD + photo upload
│   │   ├── inspectionsApi.ts            # External + site inspections, PDF upload
│   │   ├── decommissionsApi.ts          # Acta de baja
│   │   ├── reportsApi.ts                # Semáforo data + PDF export
│   │   └── auditApi.ts                  # Audit trail queries
│   │
│   ├── types/                           # TypeScript interfaces mirroring backend schemas
│   │   ├── auth.ts
│   │   ├── user.ts
│   │   ├── project.ts
│   │   ├── accessory.ts
│   │   ├── inspection.ts
│   │   ├── decommission.ts
│   │   ├── report.ts
│   │   └── audit.ts
│   │
│   └── utils/                           # Pure utility functions
│       ├── semaforoUtils.ts             # Calculate Verde/Amarillo/Rojo from dates
│       ├── dateUtils.ts                 # date-fns-tz formatting helpers (America/Bogota)
│       └── pdfUtils.ts                  # jsPDF export helpers for reports
│
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── tsconfig.node.json
└── .env.example                         # VITE_API_BASE_URL, etc.
```
ROOT

```
obras/                                   # Monorepo root
├── backend/                             # (see above)
├── frontend/                            # (see above)
├── docker-compose.yml                   # Services: api, db (postgres), storage (minio, optional)
├── .gitignore
└── README.md
```