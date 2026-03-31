# REPORTE DIAGNÓSTICO DEL PROYECTO OBRAS

**Sistema de Gestión de Accesorios de Izaje v1.2.1**  
**Fecha del Diagnóstico:** 27 de Marzo de 2026  
**Alcance:** Análisis completo del backend (FastAPI), frontend (React), integraciones API, seguridad, configuración y despliegue.

---

## 1. RESUMEN EJECUTIVO

El proyecto **OBRAS** es un sistema web para la gestión de accesorios de izaje (eslingas, grilletes, ganchos) con inspecciones periódicas, semáforo de estado, auditoría y generación de reportes PDF. La arquitectura es un monorepo con backend FastAPI (Python 3.12, PostgreSQL async) y frontend React 18 (TypeScript, Vite, TailwindCSS).

### Estado General

| Área | Estado | Observación |
|------|--------|-------------|
| Backend – Modelos | ✅ Completo | 7 modelos definidos con soft-delete y relaciones |
| Backend – Servicios | ✅ Completo | 9 servicios implementados |
| Backend – Routers API | ✅ Completo | 9 routers con CRUD + operaciones especiales |
| Backend – Autenticación | ⚠️ Parcial | JWT funcional, falta blacklist de tokens y rate limiting real |
| Frontend – Páginas | ❌ Mínimo | Solo LoginPage y DashboardPage (placeholder) |
| Frontend – Servicios API | ⚠️ Parcial | 5 archivos API creados, desalineados con el backend |
| Frontend – Componentes | ❌ Ausente | No existen componentes de UI reutilizables |
| Seguridad | ⚠️ Crítico | Múltiples hallazgos de severidad alta |
| Testing | ❌ Mínimo | Solo 3 tests de health check |
| Despliegue | ⚠️ Parcial | Docker Compose funcional, falta producción |

**Valoración global: 45% de completitud funcional con brechas críticas de seguridad.**

---

## 2. ANÁLISIS DEL BACKEND

### 2.1 Arquitectura y Estructura

```
backend/
├── app/
│   ├── api/v1/          # 9 routers REST
│   ├── core/            # config, security, dependencies
│   ├── db/              # session, base SQLAlchemy
│   ├── models/          # 7 modelos ORM
│   ├── schemas/         # 7 archivos Pydantic
│   └── services/        # 9 servicios de negocio
├── alembic/             # Migraciones DB
├── tests/               # Tests (mínimos)
└── storage/             # Archivos locales
```

**Evaluación:** La estructura sigue principios de capas (Router → Service → Model) de manera adecuada. La separación de responsabilidades es buena.

### 2.2 Modelos de Datos

| Modelo | Tabla | Estado | Observaciones |
|--------|-------|--------|---------------|
| `User` | `users` | ✅ | Roles RBAC, soft-delete |
| `Project` | `projects` | ✅ | M2M con users, soft-delete |
| `Accessory` | `accessories` | ✅ | Optimistic locking con `version` |
| `ExternalInspection` | `external_inspections` | ✅ | Ciclo 6 meses |
| `SiteInspection` | `site_inspections` | ✅ | Ciclo bimestral, usa `ARRAY` de PostgreSQL |
| `DecommissionRecord` | `decommission_records` | ✅ | Unique por accesorio |
| `AuditLog` | `audit_logs` | ✅ | Append-only, JSON diff |

**Hallazgos:**

1. **`datetime.utcnow()` deprecado (ALTA):** Se usa `datetime.utcnow()` en ~20+ ubicaciones (modelos, servicios, security). En Python 3.12+ está marcado como deprecated. Debe reemplazarse con `datetime.now(timezone.utc)`.

2. **Timestamps sin timezone consistente:** Los modelos definen `DateTime(timezone=True)` pero los defaults usan `datetime.utcnow()` que retorna datetimes naive (sin zona horaria). Esto puede causar comparaciones incorrectas con datos de PostgreSQL que sí tienen timezone.

3. **`BrandEnum` genérica:** Las marcas son `BRAND_1`, `BRAND_2`, `BRAND_3` — valores placeholder que no reflejan marcas reales de equipos de izaje.

4. **Falta índice compuesto:** En `project_users` no hay índice explícito más allá de la PK compuesta. Para queries de empleados por proyecto se beneficiaría de un índice adicional.

5. **`SiteInspection.photo_urls` usa `ARRAY`:** El tipo `ARRAY` de PostgreSQL no es portable. Si se migra a otro DBMS, este campo fallará.

### 2.3 Servicios de Negocio

| Servicio | Métodos | Estado | Observaciones |
|----------|---------|--------|---------------|
| `AuthService` | 5 | ✅ | Login, tokens, refresh |
| `UserService` | ~8 | ✅ | CRUD completo con soft-delete |
| `ProjectService` | ~8 | ✅ | CRUD + asignar/remover empleados |
| `AccessoryService` | ~6 | ✅ | CRUD + fotos + optimistic locking |
| `ExternalInspectionService` | ~5 | ✅ | CRUD + cálculo automático de `next_date` |
| `SiteInspectionService` | ~5 | ✅ | CRUD + cálculo de `color_period` |
| `DecommissionService` | ~5 | ✅ | Creación atómica (decommission + TAG_ROJO) |
| `AuditService` | ~5 | ✅ | Append-only con RBAC |
| `ReportService` | ~5 | ✅ | Semáforo + PDF |

**Hallazgos:**

6. **Rendimiento del semáforo N+1:** `ReportService.get_global_semaforo_summary()` ejecuta una query por accesorio (`calculate_accessory_semaforo()` por cada uno). Con 1000 accesorios serían ~3000 queries. Necesita una query batch.

7. **`get_global_semaforo_summary` no acepta filtros:** La ruta `/reports/semaforo` del router acepta filtros (`project_id`, `element_type`, etc.), pero la firma del servicio `get_global_semaforo_summary()` no recibe estos parámetros. **Discrepancia funcional.**

8. **Transacciones parciales:** Algunos servicios hacen `commit()` individualmente en lugar de manejar la transacción a nivel de router/endpoint. Si el `AuditService.log_create()` falla después del `commit()` del servicio principal, se pierden datos de auditoría.

9. **Validación de archivos insuficiente:** El upload de fotos en accessories no valida MIME type real del archivo, solo confía en la extensión/Content-Type del cliente.

### 2.4 Routers API (v1)

| Router | Prefix | Endpoints | RBAC |
|--------|--------|-----------|------|
| `auth` | `/auth` | login, refresh, logout, profile | Público (login), autenticado (profile) |
| `users` | `/users` | list, get, create, update, soft-delete | `require_admin` para escritura |
| `projects` | `/projects` | list, get, create, update, delete, assign/remove employee | `get_current_user` |
| `accessories` | `/accessories` | list, get, create, update, delete, upload photos | `get_current_user` |
| `inspections_external` | `/inspections/external` | list, get, create, update, delete, upload cert | `get_current_user` |
| `inspections_site` | `/inspections/site` | list, get, create, update, delete, upload photos | `get_current_user` |
| `decommissions` | `/decommissions` | list, get, create, update, delete, upload photos | `get_current_user` |
| `reports` | `/reports` | semaforo, semaforo/by-project, export-pdf | `get_current_user` |
| `audit` | `/audit-logs` | list, get | RBAC (ADMIN full, HSE filtrado, CONSULTA denegado) |

**Hallazgos:**

10. **RBAC incompleto en endpoints críticos:** Los routers de `projects`, `accessories`, `inspections_external`, `inspections_site`, `decommissions` y `reports` solo verifican `get_current_user` (usuario autenticado), pero no restringen por rol. Un usuario `CONSULTA` puede **crear, modificar y eliminar** accesorios, inspecciones y proyectos. Solo `users` y `audit` implementan RBAC apropiado.

11. **PATCH de inspecciones usa schema `Create`:** Los endpoints `update_external_inspection` y `update_site_inspection` reciben `ExternalInspectionCreate` / `SiteInspectionCreate` en lugar de sus respectivos schemas `Update`. Aunque existen `ExternalInspectionUpdate` y `SiteInspectionUpdate`, no se usan.

12. **Endpoint de update usa PUT en frontend pero PATCH en backend:** El frontend `projectsApi.updateProject()` usa `apiClient.put()`, pero el backend define `@router.patch()`. Esto causará errores 405 Method Not Allowed.

### 2.5 Schemas Pydantic

**Hallazgos:**

13. **Validación de enums case-sensitive:** El `ProjectStatusEnum` requiere `"ACTIVO"` exacto. El frontend envía `"Activo"`. Se agregó un `field_validator` parcial, pero el mismo problema existe en **todos los enums** del frontend (ver sección 4).

14. **Sin validación de contraseña:** `UserCreate.password` acepta cualquier string sin restricción de longitud mínima, complejidad ni fuerza. Un password vacío (`""`) es técnicamente válido.

15. **`ExternalInspectionOut.certificate_pdf` es obligatorio:** Pero el endpoint de creación no gestiona la subida del archivo PDF al crear. Se requiere crear la inspección con un string vacío o path placeholder.

---

## 3. ANÁLISIS DEL FRONTEND

### 3.1 Arquitectura y Estado Actual

```
frontend/src/
├── hooks/         # useAuth.ts
├── pages/         # LoginPage.tsx, DashboardPage.tsx
├── routes/        # ProtectedRoute.tsx
├── services/      # api.ts, authApi.ts, projectsApi.ts, accessoriesApi.ts, usersApi.ts
├── store/         # authStore.ts, uiStore.ts
├── styles/        # index.css (Tailwind)
├── types/         # index.ts
└── utils/         # semaforoUtils.ts, pdfUtils.ts, dateUtils.ts
```

### 3.2 Páginas Implementadas

| Página | Estado | Funcionalidad |
|--------|--------|---------------|
| `LoginPage` | ✅ Funcional | Login con email/password, manejo de errores |
| `DashboardPage` | ⚠️ Placeholder | Sidebar con módulos, tarjetas con datos hardcoded (0) |
| Proyectos | ❌ No existe | — |
| Accesorios | ❌ No existe | — |
| Inspecciones Externas | ❌ No existe | — |
| Inspecciones en Sitio | ❌ No existe | — |
| Bajas/Decomisionamientos | ❌ No existe | — |
| Reportes/Semáforo | ❌ No existe | — |
| Usuarios (Admin) | ❌ No existe | — |
| Auditoría | ❌ No existe | — |

**El frontend tiene ~10% de las páginas necesarias implementadas.** Solo existe autenticación y un dashboard placeholder vacío.

### 3.3 Componentes Reutilizables

**No existen componentes reutilizables.** No hay:
- Tablas de datos con paginación
- Formularios con validación (react-hook-form + zod están instalados pero no se usan)
- Modales de confirmación
- Componentes de carga de archivos (react-dropzone instalado pero no se usa)
- Componentes de semáforo/indicadores de color
- Layout compartido (sidebar/header)
- Componentes de filtrado

### 3.4 Servicios API del Frontend

**Hallazgos:**

16. **Métodos HTTP incorrectos:**
    - `projectsApi.updateProject()` → usa `PUT` pero el backend espera `PATCH`
    - `accessoriesApi.updateAccessory()` → usa `PUT` pero el backend espera `PATCH`
    - `usersApi.updateUser()` → usa `PUT` pero el backend espera `PATCH`

17. **Faltan servicios API completos:**
    - No existe `inspectionsApi.ts` (externas ni en sitio)
    - No existe `decommissionsApi.ts`
    - No existe `reportsApi.ts`
    - No existe `auditApi.ts`

18. **`accessoriesApi.uploadPhoto()` incompleto:** No envía el parámetro obligatorio `photo_type` (query param requerido por el backend).

19. **`usersApi` tiene endpoints inexistentes:** `activateUser()` y `deactivateUser()` llaman a rutas `/users/{id}/activate` y `/users/{id}/deactivate` que no existen en el backend.

---

## 4. BRECHAS EN INTEGRACIONES API (Frontend ↔ Backend)

### 4.1 Desalineación de Tipos

| Campo | Frontend (`types/index.ts`) | Backend (schema/modelo) | Estado |
|-------|-----------------------------|------------------------|--------|
| `Project.status` | `'Activo' \| 'Inactivo'` | `'ACTIVO' \| 'INACTIVO'` | ❌ **Mismatch** |
| `AccessoryStatus` | `'En Uso' \| 'En Stock' \| 'Tag Rojo'` | `'EN_USO' \| 'EN_STOCK' \| 'TAG_ROJO'` | ❌ **Mismatch** |
| `ExternalInspection.status` | `'Vigente' \| 'Vencida'` | `'VIGENTE' \| 'VENCIDA'` | ❌ **Mismatch** |
| `SiteInspection.result` | `'Buen Estado' \| 'Mal Estado' \| 'Observaciones'` | `'BUEN_ESTADO' \| 'MAL_ESTADO' \| 'OBSERVACIONES'` | ❌ **Mismatch** |
| `Accessory.type` | `string` | `ElementTypeEnum` (ESLINGAS, etc.) | ❌ **Tipo incorrecto** |
| `Accessory.capacity` | `string` (single) | 3 campos separados (vertical, choker, basket) | ❌ **Estructura diferente** |
| `Accessory.photos` | `string[]` (array) | 3 campos separados (accessory, label, marking) | ❌ **Estructura diferente** |

### 4.2 Hallazgos Críticos de Integración

20. **Todos los enums del frontend usan formato display ("En Uso") cuando el backend requiere formato código ("EN_USO").** Toda petición de escritura que incluya enums fallará con 422 Unprocessable Entity.

21. **Campo `created_by` en Project:** El frontend lo define como `string`, pero el backend no lo expone en `ProjectOut` — viene de la relación interna.

22. **Falta `employee_count` y `accessory_count` en tipo `Project`:** El backend los incluye en `ProjectOut`, el frontend no los tiene.

23. **`TokenResponse.refresh_token` puede ser undefined en refresh:** El endpoint `/auth/refresh` del backend puede retornar sin `refresh_token` (solo genera nuevo `access_token`), pero el frontend siempre espera ambos tokens.

---

## 5. IMPLEMENTACIONES CRÍTICAS FALTANTES

### 5.1 Backend — Prioridad Alta

| # | Implementación | Impacto | Esfuerzo |
|---|---------------|---------|----------|
| 1 | **Rate limiting en login** | Seguridad: brute force | Medio |
| 2 | **Token blacklist en logout** | Seguridad: tokens válidos post-logout | Medio |
| 3 | **RBAC en todos los routers** | Seguridad: escalación de privilegios | Alto |
| 4 | **Validación de contraseñas** | Seguridad: passwords débiles | Bajo |
| 5 | **Validación MIME real de uploads** | Seguridad: file upload attacks | Medio |
| 6 | **Batch query en semáforo** | Rendimiento: N+1 queries | Alto |
| 7 | **Job automático de expiración** | Funcional: status inspecciones no se actualiza automáticamente | Medio |

### 5.2 Frontend — Prioridad Alta

| # | Implementación | Impacto | Esfuerzo |
|---|---------------|---------|----------|
| 8 | **Páginas de CRUD completas** | Funcional: la app no es usable | Muy Alto |
| 9 | **Vista de Semáforo con dashboard real** | Funcional: feature principal del sistema | Alto |
| 10 | **Formularios con validación (zod)** | UX: ya hay dependencias instaladas sin usar | Alto |
| 11 | **Gestión de archivos/fotos**  | Funcional: uploads de inspecciones | Alto |
| 12 | **Alinear tipos con backend** | Bug: toda escritura falla | Medio |
| 13 | **Rutas por módulo** | Navegación: solo existe /login y /dashboard | Alto |
| 14 | **Manejo de errores global** | UX: errores no se muestran consistentemente | Medio |

### 5.3 General

| # | Implementación | Impacto |
|---|---------------|---------|
| 15 | **Tests unitarios y de integración** | Calidad: solo 3 tests de health |
| 16 | **Migraciones Alembic reales** | DB: la migración inicial está vacía (empty upgrade/downgrade) |
| 17 | **CI/CD pipeline** | DevOps: no existe |
| 18 | **Manejo de errores centralizado** | Backend: mensajes genéricos "Error" |

---

## 6. BRECHAS DE SEGURIDAD Y CONFIGURACIÓN

### 6.1 Seguridad — Severidad Crítica

| # | Hallazgo | Severidad | Descripción |
|---|----------|-----------|-------------|
| S1 | **JWT Secret hardcoded** | 🔴 CRÍTICA | `JWT_SECRET = "your-secret-key-change-this..."` como default en `config.py`. Si no se configura `.env`, cualquiera puede forjar tokens. |
| S2 | **Sin rate limiting implementado** | 🔴 CRÍTICA | `slowapi` está en `requirements.txt` y la config existe, pero **nunca se aplica a ningún endpoint**. Login es vulnerable a brute force. |
| S3 | **RBAC insuficiente** | 🔴 CRÍTICA | 7 de 9 routers no verifican roles. Un usuario CONSULTA puede crear/borrar datos. |
| S4 | **Sin token blacklist** | 🟡 ALTA | El endpoint `/logout` está vacío (solo `pass`). Los tokens siguen siendo válidos hasta expirar. |
| S5 | **Password sin validación** | 🟡 ALTA | Se acepta cualquier string como password en `UserCreate`, incluyendo strings vacíos. |
| S6 | **bcrypt import dual** | 🟡 MEDIA | `requirements.txt` incluye `passlib[bcrypt]` pero `security.py` importa `bcrypt` directamente. Conflicto potencial de versiones. |
| S7 | **Credenciales demo en LoginPage** | 🟡 MEDIA | Email y password pre-rellenados en el formulario de login (`admin@example.com` / `ChangeMe123!`). |
| S8 | **Tokens en localStorage** | 🟡 MEDIA | Los tokens JWT se guardan en `localStorage`, vulnerable a XSS. Mejor práctica: `httpOnly` cookies para refresh tokens. |
| S9 | **CORS wildcard en métodos** | 🟡 MEDIA | `allow_methods=["*"]` permite todos los métodos HTTP. Debería restringirse a los necesarios. |
| S10 | **Healthcheck usa `requests` sin instalar** | 🟢 BAJA | El Dockerfile hace healthcheck con `python -c "import requests; ..."` pero `requests` no está en `requirements.txt`. |

### 6.2 Configuración y Despliegue

| # | Hallazgo | Severidad | Descripción |
|---|----------|-----------|-------------|
| C1 | **Sin Dockerfile para frontend** | 🟡 ALTA | Solo existe Dockerfile para backend. El frontend no tiene build de producción containerizado. |
| C2 | **`docker-compose` usa `fastapi dev`** | 🟡 ALTA | Comando de desarrollo (`fastapi dev`) en lugar de producción (`uvicorn --workers`). |
| C3 | **Sin configuración Nginx/proxy** | 🟡 ALTA | No hay reverse proxy para servir frontend y backend bajo un mismo dominio. |
| C4 | **Migración Alembic vacía** | 🟡 MEDIA | El archivo `5a5fa7d85afc_create_initial_schema.py` tiene funciones `upgrade()` y `downgrade()` vacías. Se depende de `create_all()` en el startup. |
| C5 | **`create_all()` en producción** | 🟡 MEDIA | `main.py` ejecuta `Base.metadata.create_all()` en cada arranque. En producción esto debería manejarse exclusivamente con migraciones Alembic. |
| C6 | **Sin variables de entorno para producción** | 🟡 MEDIA | No hay `.env.production` ni documentación de las variables requeridas en producción vs desarrollo. |
| C7 | **`DB_ECHO = False` default correcto** | 🟢 OK | Logging SQL deshabilitado por defecto. |

---

## 7. RESUMEN DE HALLAZGOS

### Por Severidad

| Severidad | Cantidad | Ejemplos Clave |
|-----------|----------|----------------|
| 🔴 Crítica | 3 | JWT secret hardcoded, sin rate limiting, RBAC insuficiente |
| 🟡 Alta | 11 | Frontend sin páginas, tipos desalineados, sin token blacklist, métodos HTTP incorrectos |
| 🟡 Media | 8 | N+1 queries, migraciones vacías, tokens en localStorage |
| 🟢 Baja | 3 | BrandEnum placeholder, healthcheck dependency, credentials en UI |

### Por Área

| Área | Hallazgos Críticos | Hallazgos Totales |
|------|-------------------|-------------------|
| Seguridad | 3 | 10 |
| Frontend | 0 | 7 |
| Integración API | 0 | 4 |
| Backend Lógica | 0 | 6 |
| Configuración/Deploy | 0 | 6 |

### Métricas de Código

| Métrica | Backend | Frontend |
|---------|---------|----------|
| Archivos Python/TS | 35 | 14 |
| Tests | 3 (solo health) | 0 |
| Cobertura estimada | <5% | 0% |
| Endpoints API | ~35 | — |
| Páginas funcionales | — | 2 de ~10 |
| Componentes reutilizables | — | 0 |

---

## 8. CONCLUSIÓN

El proyecto OBRAS tiene un **backend bien estructurado y mayoritariamente funcional** con una arquitectura de capas sólida, modelos de datos apropiados para el dominio y servicios de negocio que cubren los requerimientos funcionales principales (CRUD, inspecciones, semáforo, auditoría, reportes PDF).

Sin embargo, existen **tres brechas fundamentales** que deben abordarse antes de considerar el sistema apto para uso:

1. **Seguridad:** El JWT secret hardcoded, la ausencia de rate limiting real (a pesar de tener la dependencia instalada), y la falta de RBAC en la mayoría de endpoints representan riesgos que permitirían acceso no autorizado y manipulación de datos en producción.

2. **Frontend incompleto (~10%):** Solo existe login y un dashboard placeholder. Todas las funcionalidades de gestión (proyectos, accesorios, inspecciones, bajas, reportes) carecen de interfaz. Los tipos del frontend están desalineados con el backend, garantizando errores 422 en toda operación de escritura.

3. **Calidad y Testing:** Con 3 tests y 0% de cobertura en frontend, no hay red de seguridad para prevenir regresiones. Las migraciones Alembic están vacías y se depende de `create_all()`, lo cual es insostenible para evolución del esquema en producción.

### Prioridades Recomendadas

1. **Inmediata:** Corregir brechas de seguridad críticas (S1, S2, S3)
2. **Corto plazo:** Alinear tipos frontend ↔ backend y corregir métodos HTTP
3. **Medio plazo:** Implementar páginas de CRUD y dashboard funcional
4. **Continuo:** Agregar tests y configurar migraciones Alembic reales

---

*Generado automáticamente como diagnóstico del proyecto OBRAS al 27/03/2026.*
