# BITÁCORA DEL PROYECTO

> Registro vivo. Se actualiza al cerrar cada Orden de Trabajo.
> Leer junto con `PLAN-MAESTRO.md` al inicio de cada chat.

**Estado actual:** Fase 0 — Reconocimiento
**OT activa:** OT-02 — Registro de aplicación en Entra ID + flujo OAuth delegado
**OT-01:** ✅ CERRADA (23-ago-2026)
**Repositorio:** `brujula-teams` (publico)
**Nombre del proyecto:** **Brújula**
**Última actualización:** 23 de agosto de 2026

---

## Tablero de Órdenes de Trabajo

| OT | Fase | Título | Estado |
|---|---|---|---|
| OT-01 | F0 | Reconocimiento de plataforma y primer contacto con Graph | ✅ Cerrada |
| OT-02 | F0 | Registro de aplicación en Entra ID + flujo OAuth delegado | 🟡 Activa |
| OT-03 | F1 | Esqueleto FastAPI hexagonal + `POST /chat` con LLM | ⚪ Pendiente |
| OT-04 | F1 | MongoDB Atlas conectado + persistencia de conversación | ⚪ Pendiente |
| OT-05 | F2 | Primer adaptador de fuente: Planner → `Pendiente` | ⚪ Pendiente |

---

## OT-01 — Reconocimiento de plataforma

**Objetivo:** desactivar los riesgos de plataforma **antes** de escribir una sola línea de código, y tener el primer contacto real con Microsoft Graph.

**Regla:** en esta OT no se escribe código. Se investiga y se reporta.

### Tarea 1.1 — ¿La UPB permite apps personalizadas?
Abrir Teams con la cuenta UPB → **Aplicaciones** → buscar "Administrar tus aplicaciones" o "Cargar una aplicación personalizada".
**Reportar:** ¿aparece la opción, sí o no?
*(Informativo. Según ADR-003 no bloquea nada, pero define si habrá prueba de campo real al final.)*

### Tarea 1.2 — Conseguir un tenant propio
Intentar en este orden y reportar hasta dónde se llegó:

1. **Microsoft 365 Developer Program** — sandbox E5 gratuito. La elegibilidad se restringió: hoy suele exigir suscripción Visual Studio Professional/Enterprise *standard*. Verificar si la UPB da acceso a Visual Studio a sus estudiantes (programas de educación de Microsoft).
2. **Prueba gratuita de Microsoft 365 Business Standard** — 30 días, tenant real con Teams y Planner. Sirve para arrancar; hay que decidir después si se paga un usuario (~USD 12/mes) durante el semestre.
3. Si ambas fallan: reportar y se replantea.

**Reportar:** qué opción quedó viable, dominio del tenant y si tiene licencia con Teams y Planner.

### Tarea 1.3 — Primer contacto con Microsoft Graph *(la tarea que más enseña)*
Entrar a **Graph Explorer** (`developer.microsoft.com/graph/graph-explorer`), iniciar sesión y ejecutar:

```
GET https://graph.microsoft.com/v1.0/me
GET https://graph.microsoft.com/v1.0/me/events
GET https://graph.microsoft.com/v1.0/me/todo/lists
GET https://graph.microsoft.com/v1.0/me/planner/tasks
GET https://graph.microsoft.com/v1.0/me/joinedTeams
GET https://graph.microsoft.com/v1.0/me/chats
```

**Reportar por cada llamada:**
- ¿200 OK, 403, 404 o vacío?
- Si pidió consentimiento, ¿qué permiso exacto pidió y quién debía aprobarlo (usuario o admin)?
- Un ejemplo del JSON devuelto (con datos sensibles tachados).

Este es el momento donde el proyecto deja de ser teoría.

### Tarea 1.4 — Confirmar acceso a un LLM
Verificar cuál está disponible: Azure OpenAI (requiere solicitud), OpenAI directo, Google Gemini, Groq u Ollama local.
**Reportar:** cuál quedó confirmado y con qué límite de crédito o de cuota.

### Tarea 1.5 — Repositorio
Crear repo en GitHub con `README.md`, `.gitignore` de Python y carpeta `docs/adr/`. Copiar allí `PLAN-MAESTRO.md`.
**Reportar:** URL del repo.

### Resultados registrados — 23-ago-2026

**Bautizo del proyecto: `Brújula`.**
Razón: el plan define que el sistema "no resuelve las tareas; orienta, contextualiza y enlaza".
Eso es exactamente una brújula: no camina por ti, te ubica y te señala el norte.
Sirve además como respuesta a la pregunta de sustentación "¿por qué no Copilot?" — Copilot pilotea, la brújula ubica.

#### Tarea 1.1 — ✅ CERRADA. La UPB NO permite sideload.

Teams (cuenta UPB) → Aplicaciones → Administrar las aplicaciones → "Carga una aplicación"
muestra **una sola** opción: *"Enviar una aplicación a su organización — Envía una aplicación a tu
administrador de TI para tu aprobación"*. **No existe** la opción de cargar un paquete propio.

**Evidencia:** captura del diálogo. Pendiente guardarla en `docs/adr/` como respaldo de ADR-003.
ADR-003 deja de ser hipótesis y pasa a estar respaldado por evidencia.

**Por qué se descarta la vía de aprobación de TI (razonamiento del cierre):**
no es un trámite, es **un trámite por cada iteración**. Durante el desarrollo el paquete se resube
decenas de veces; si cada subida entra en una cola de aprobación, el ciclo de retroalimentación
pasa de minutos a días. **Regla adoptada: nunca poner una dependencia humana externa dentro del
ciclo de iteración.** Al final, para desplegar una vez, sí; durante el desarrollo, jamás.

**Reposicionamiento:** la UPB pasa de *entorno de desarrollo* a *cliente potencial* (modelo ISV, ADR-003).

#### Tarea 1.2 — ✅ CERRADA. Tenant propio operativo.

| Vía intentada | Resultado |
|---|---|
| M365 Developer Program (sandbox E5) | ❌ *"You don't currently qualify for a Microsoft 365 Developer Program sandbox subscription."* |
| Suscripción Visual Studio (requisito de elegibilidad) | ❌ Solo **Dev Essentials** (nivel gratuito). No es Professional ni Enterprise. |
| **M365 Business Standard — prueba 30 días** | ✅ **Tenant creado** |

- **Dominio:** `brujulateams.onmicrosoft.com`
- **Organización:** Proyecto TIC1
- **Cuenta admin:** `proyectotic1@brujulateams.onmicrosoft.com`
- **Rol:** Iker es administrador global. Acceso confirmado a admin.cloud.microsoft.
- **Costo tras la prueba:** 16,80 USD/usuario/mes.
- ⚠️ **FECHA CRÍTICA — cancelar o decidir pago antes del 15 de septiembre de 2026.**

**Requisito de arquitectura derivado (no negociable):**
cambiar de tenant debe costar **solo variables de entorno** — `TENANT_ID`, `CLIENT_ID`,
`CLIENT_SECRET`, `REDIRECT_URI`. **Cero identificadores de tenant escritos en el código.**
Es la promesa de ADR-004 aplicada a la infraestructura.

**Deuda operativa identificada:** lo que NO transfiere entre tenants no es código, son datos y
registro: la app de Entra ID (nuevo CLIENT_ID y secreto, redirect URIs, consentimientos), los
usuarios de prueba, el plan de Planner con tareas, los eventos de calendario y el equipo de Teams.
Reconstruir eso a mano son horas de clics.
**Mitigación acordada:** escribir `scripts/seed_tenant.py` que siembre todo vía Graph.
Convierte la reconstrucción de un tenant en un comando, hace los tests reproducibles y es un
artefacto de valor para el portafolio.

**Riesgo anotado:** encadenar pruebas gratuitas sucesivas es frágil — Microsoft las ata al método de
pago, teléfono y dominio. **No se construye el cronograma sobre eso.** La sustentación es en
noviembre; un tenant caído ese día deja al proyecto sin demo.

**Nota de gobernanza:** quien crea el tenant queda como administrador global. Ese rol **no se
delega por conveniencia** al equipo. A Julián y Antonio se les puede delegar el seed de datos,
nunca las llaves del tenant. (Mínimo privilegio, ADR-002, aplicado puertas adentro.)

#### Tarea 1.3 — ✅ EJECUTADA en tenant propio (23-ago-2026)

**Hallazgo central:** en el primer intento, **solo `/me` respondió 200**. Las otras cinco dieron **403**.
La causa no era la cuenta ni el tenant: el token de Graph Explorer arranca con el mínimo
(`openid, profile, User.Read, email`). **Faltaban los scopes, no los privilegios.**

**Estado inicial (sin consentir permisos):**

| Endpoint | Estado | Código de error |
|---|---|---|
| `/me` | 200 OK | — |
| `/me/events` | 403 | `ErrorAccessDenied` |
| `/me/todo/lists` | 403 | `notAllowed` / `ErrorAccessDenied` |
| `/me/planner/tasks` | 403 | *"You do not have the required permissions"* |
| `/me/joinedTeams` | 403 | `Forbidden` — **listó los scopes requeridos** |
| `/me/chats` | 403 | `Forbidden` — **listó los scopes requeridos** |

**Estado final (tras consentir):** las 6 en **200 OK**. La mayoría con `"value": []` porque el tenant
está recién creado y sin datos sembrados.

**Permisos identificados y consentidos (todos de solo lectura):**

| Permiso | Habilita | Alimenta `fuente` de `Pendiente` |
|---|---|---|
| `User.Read` | Identidad del usuario | — (contexto) |
| `Calendars.Read` | Eventos propios | `CALENDARIO` |
| `Tasks.Read` | To Do **y** Planner (permiso compartido) | `TODO`, `PLANNER` |
| `Team.ReadBasic.All` | Lista de equipos del usuario | previo a `MENSAJE` |
| `Chat.Read` | Contenido de chats | `MENSAJE` |

**Ni un solo `ReadWrite`.** Brújula orienta, no escribe. Mínimo privilegio verificable (ADR-002).

**Modelo mental adoptado — `Recurso.Acción.Alcance`:**
el sufijo `.All` es la frontera entre "leo lo mío" y "leo lo de la organización", y es lo que
dispara el requisito de consentimiento de administrador. `Team.ReadBasic.All` es el único con `.All`
en la lista; se pudo consentir **porque Iker es admin global de su propio tenant**.
En el tenant de la UPB ese permiso habría sido inalcanzable. **Validación en vivo de ADR-003.**

**Observación de diseño — errores heterogéneos:** Graph no responde igual en todos los servicios.
Exchange (`/me/events`) devuelve `ErrorAccessDenied` sin detalle; Teams (`/me/joinedTeams`, `/me/chats`)
devuelve el listado exacto de scopes faltantes. El adaptador de Graph deberá normalizar formatos de
error distintos según el servicio de origen.

**⚠️ REGLA DEL ADAPTADOR (no negociable):**
**nunca traducir un error de permisos a un resultado vacío.**
`200 OK` con `[]` → devolver lista vacía. `403` → **lanzar excepción**.
Colapsar ambos casos produce el peor bug posible de este proyecto: Brújula diría
*"no tienes pendientes"* cuando la verdad es *"no pude preguntar"*. El usuario confía, no estudia y
pierde la entrega. En un sistema cuyo valor es la confianza, **el silencio por error es la falla más cara**.

#### Tarea 1.3 (bis) — Comparativa contra el tenant de la UPB ✅

Misma batería, autenticado con la cuenta `@upb.edu.co`:

| Endpoint | `brujulateams` (propio) | UPB |
|---|---|---|
| `/me` | 200 OK | 200 OK |
| `/me/joinedTeams` | 200 OK | 200 OK |
| `/me/events` | 200 OK | ❌ 403 — requiere administrador |
| `/me/todo/lists` | 200 OK | ❌ 403 — requiere administrador |
| `/me/planner/tasks` | 200 OK | ❌ 403 — requiere administrador |
| `/me/chats` | 200 OK | ❌ 403 — requiere administrador |

**HALLAZGO CRÍTICO — la UPB tiene deshabilitado el consentimiento de usuario para aplicaciones.**

`Calendars.Read`, `Tasks.Read` y `Chat.Read` son permisos sobre los **datos propios del usuario** y,
en un tenant con configuración por defecto, **cualquier usuario puede consentirlos sin pasar por TI**.
Que la UPB los bloquee no es un permiso faltante: es una **política de tenant** que impide a
cualquier estudiante autorizar cualquier aplicación de terceros sobre su propia cuenta.

**Consecuencia:** Brújula **no puede funcionar en el tenant de la UPB sin intervención de TI**,
ni siquiera para leer el calendario del propio usuario.
Cierra el círculo con la Tarea 1.1: **dos candados independientes** — no se puede instalar la app
(1.1) y tampoco se podría autorizar aunque se instalara (1.3 bis).
ADR-003 queda demostrado con datos, no argumentado.

**Corrección registrada — predicción fallida del mentor:** se predijo que fallarían los permisos
con `.All` y pasarían los personales. Ocurrió **exactamente al revés** (`joinedTeams`, que lleva
`.All`, sí pasó). La documentación describe lo que es *posible*; solo la prueba revela lo que está
*permitido en un tenant concreto*.
**Lección de arquitectura: la política de un tenant no se predice, se mide.**

#### Tarea 1.4 — ✅ CERRADA. LLM confirmado.

**Decisión: Google Gemini API (capa gratuita) como proveedor principal.**
API key generada en `aistudio.google.com`. Sin tarjeta de crédito.
Límites: ~1.500 peticiones/día en modelos Flash, contexto de 1M tokens. Suficiente con margen
para el MVP y coherente con ADR-008 (modelo rápido y barato para la lista breve).

**Descartado — Azure OpenAI:** los créditos de Azure for Students (USD 100) **no se pueden aplicar
a Azure OpenAI**; es una exclusión explícita del programa. Es exactamente el escenario que ADR-006
anticipó al no hipotecar el proyecto a un proveedor incierto. Los créditos de Azure se reservan
para hospedar el backend.

**Contingencia — Ollama local** sobre el PC con GPU de Iker. No es plan B de emergencia:
desarrollo sin conexión, sin cuota y sin costo, y **demuestra ADR-006 en el repo** al correr el
sistema con varios proveedores sin tocar el núcleo.

**Hugging Face — rol asignado:** no como proveedor de chat, sino como fuente de modelos de
*embeddings* (`sentence-transformers`) ejecutados **localmente en GPU** para F3 (RAG). Elimina el
costo recurrente más peligroso de un sistema RAG. Los vectores van a MongoDB Atlas Vector Search (ADR-007).

**Detalle técnico adoptado:** Gemini, Groq y Ollama exponen API **compatible con el SDK de OpenAI**.
El adaptador se escribe contra esa forma; cambiar de proveedor = cambiar `base_url` y `api_key`.

**Reencuadre de mentoría registrado:** el valor de portafolio no está en llamar a una API de LLM
(ocho líneas, lo hace cualquiera), sino en tres cosas:
1. Proveedor intercambiable tras un puerto `LLMProvider` (ADR-006).
2. `FakeLLMProvider` determinista → tests sin red, sin costo, sin aleatoriedad. Demuestra que se
   entiende un LLM como dependencia externa no determinista.
3. Capacidad de **medir** la calidad de las respuestas (golden dataset). Es la pregunta 3 de
   sustentación, "la que tumba proyectos de IA".

#### Decisión de arquitectura anticipada para OT-02 (multi-tenant)

Al registrar la app en Entra ID hay que elegir **"Cuentas en cualquier directorio organizativo"
(multiinquilino)**. Elegir "solo mi organización" ata el `CLIENT_ID` a `brujulateams` para siempre
y ninguna otra empresa podría instalar Brújula. **Es un radio button difícil de revertir.**

El mecanismo de adopción por una organización cliente es el **admin consent**: el administrador de
TI abre una URL, revisa la lista exacta de permisos y aprueba una vez para todo su tenant.
Esa URL + esa lista **son** la *Guía de Instalación para el Administrador de TI* (entregable ADR-003).

**Corolario:** que la lista de permisos no tenga ni un solo `ReadWrite` no es purismo — es lo que
hace la app aprobable. Un admin que ve "escritura en chats" en la pantalla de consentimiento no aprueba.

#### Tarea 1.5 — ✅ CERRADA. Repositorio creado.

- **Repo:** `brujula-teams`, público, con `README.md` y `.gitignore` de Python desde el commit uno.
- `PLAN-COMPLETO.md` y `BITACORA.md` viven dentro del repo, en `docs/`.
- Se descartó `brujula` a secas: `brujula-teams` deja claro el dominio del proyecto sin abrir el repo.

**Beneficio adquirido:** `git log` sobre `docs/BITACORA.md` es el historial fechado de todas las
decisiones del proyecto. Evidencia de proceso, no solo de resultado.

**Incidencia corregida:** quedaron temporalmente **dos copias** de `BITACORA.md` (raíz del disco y
repo). Se eliminó la de la raíz. **Dos fuentes de verdad son cero fuentes de verdad.**

#### Protocolo de trabajo con IA adoptado (23-ago-2026)

**Principio: los chats son memoria de trabajo; los archivos son el estado.**
Un chat es un trabajador desechable: lee el estado desde disco, ejecuta una OT, escribe el
resultado en disco y muere. El conocimiento del proyecto **nunca** vive en un chat.

**Regla operativa:** *nada existe hasta que está escrito en `BITACORA.md`.*

1. Un chat por OT. Se cierra al cerrar la OT.
2. No mantener un "chat principal" largo: se degrada y arrastra confusiones viejas.
   Un chat corto que lee archivos frescos siempre está mejor informado.
3. Ritual de cierre obligatorio: *"actualiza la bitácora con lo de hoy y dime cuál es la siguiente OT"*.
4. Mantener la carpeta del proyecto conectada en cada chat nuevo.

**Paralelo con el propio proyecto:** es el mismo problema que resuelve Brújula. Un LLM no tiene
memoria entre sesiones; se le da contexto recuperándolo de una fuente externa confiable.
Aquí esa fuente es la bitácora; en el producto serán Graph y el vector store.
**Se está usando la arquitectura que se está construyendo.**

### Criterio de aceptación de la OT-01
- [x] Se sabe si la UPB permite sideload → **NO permite**
- [x] Existe un tenant propio con Teams y Planner → **`brujulateams.onmicrosoft.com`**
- [x] Las 6 llamadas de Graph están ejecutadas y reportadas → **en ambos tenants, con comparativa**
- [x] Hay un LLM confirmado y accesible → **Gemini API (free tier)**, contingencia Ollama local
- [x] El repo existe y es público → `brujula-teams`

---

## Registro de aprendizaje

> Cada OT cerrada exige responder preguntas de comprensión. No basta con que funcione:
> hay que entender por qué. Aquí se registran las respuestas y las brechas detectadas.

### 23-ago-2026 — Cierre de OT-01: 1/3

Mejora respecto a la verificación previa (0/3): las tres respuestas se movieron al plano de
**gobernanza y guía de instalación**, que era justo el patrón a corregir. Persisten dos huecos de fondo.

| # | Tema | Respuesta de Iker | Corrección |
|---|---|---|---|
| 1 | Por qué la UPB bloquea el consentimiento de usuario | ✅ Acertó la consecuencia (la guía debe listar permisos). ❌ No supo la causa: *"depende del negocio"*. | El ataque se llama **illicit consent grant / consent phishing**: una app maliciosa obtiene un token legítimo por consentimiento del usuario. **Ese token sobrevive al cambio de contraseña y al MFA**, porque no hubo hackeo — hubo aprobación. Por eso las organizaciones lo apagan en bloque. |
| 2 | Por qué el `FakeLLMProvider` debe ser determinista | ❌ Confundió `FakeLLMProvider` con **Ollama**. | Ollama **es un LLM real**: lento, con GPU y **no determinista**. El Fake son ~20 líneas que devuelven una cadena fija; no hay IA adentro. Determinista porque un test afirma *"esta entrada → exactamente esta salida"*. Con salida variable los tests **fallan al azar**, y el rojo intermitente enseña a ignorar el rojo: el día que algo se rompe de verdad, nadie se entera. Además: milisegundos en vez de segundos, sin cuota, y ejecutable en CI sin GPU ni API key. |
| 3 | Regla general tras la predicción fallida | ❌ Repitió el caso (*"depende de la organización"*) sin extraer la regla. | **La política de una plataforma externa no se deduce de la documentación, se verifica ejecutándola.** La doc dice qué es *posible*; solo la prueba dice qué está *permitido aquí*. Corolario: toda dependencia externa se prueba en un experimento chico y desechable **antes** de escribir código que dependa de ella. Es la razón de ser de toda la Fase 0. |

**Distinción clave que faltaba (pregunta 2):** en los tests unitarios **no se prueba el modelo, se
prueba el código propio** — orquestador, adaptadores, construcción de `Pendiente`. El LLM es una
dependencia externa que hay que anular para poder ver la lógica propia.
Medir la **calidad del modelo** es un problema distinto, con herramienta distinta: el **golden
dataset**, que corre aparte y con poca frecuencia. **Confundir ambos tipos de prueba es el error
clásico de los proyectos de IA.**

**Regla adoptada (pregunta 1):** *no se diseña para el usuario final, se diseña para el
administrador de TI que decide si la app entra.* Ese es el verdadero portero.

**Requisitos derivados para la Guía de Instalación:**
- Cada permiso justificado en una línea: qué dato lee y para qué.
- Énfasis en **cero `ReadWrite`** — es el argumento más fuerte ante un admin.
- Almacenamiento y ciclo de vida de los tokens (ADR-002).
- URL de admin consent **y procedimiento de revocación** (un admin confía en lo que puede desinstalar).
- **Verified Publisher** en Entra ID: es lo que distingue la app de una de phishing a ojos del admin.

**Riesgos reclasificados de "asumido" a "por medir" (pregunta 3):**
| Dependencia | Qué se está asumiendo | Cuándo medirlo |
|---|---|---|
| SDK de bot de Teams para Python (R4) | Que funciona | **Hola-mundo desechable en F1, no en F4.** Es el riesgo más caro del plan. |
| MongoDB Atlas Vector Search (tier gratuito) | Que alcanza | Antes de F3 |
| Cuota gratuita de Gemini | Que aguanta la demo real | Antes de la sustentación |
| Créditos de Azure for Students | Qué más excluyen además de Azure OpenAI | Antes de decidir hosting |

**Patrón raíz — actualización:** el reflejo de razonar en lo técnico ante problemas de gobernanza
**mejoró**. El patrón nuevo a vigilar es distinto: **quedarse en el caso particular sin extraer la
regla general.** Un arquitecto convierte cada incidente en una regla reutilizable.

### 15-ago-2026 — Verificación inicial (previa a OT-01): 0/3

Brechas detectadas. **Repasar antes de la sustentación.**

| # | Tema | Error cometido | Corrección |
|---|---|---|---|
| 1 | Permisos de Graph | Razonó en términos de *rendimiento* ("las peticiones duran mucho") ante un problema de **gobernanza** | El bloqueo es: Protected API + consentimiento de admin + mínimo privilegio. En integraciones empresariales frena el permiso, no la técnica. |
| 2 | Campo `confianza` | No identificó su función | Distingue **hecho** (Planner, `1.0`) de **inferencia del LLM** (mensaje de canal, `<1.0`). Es el seguro contra alucinaciones y la defensa ante "¿y si alucina una fecha?". |
| 3 | Capa de bot delgada | Respondió *por qué eligió* Python, no *cómo mitiga* el riesgo | Mitigación = adaptador de bot sin lógica de negocio. Ignorarla implica: acoplamiento al SDK débil, imposibilidad de testear sin Teams y **muerte del plan de contingencia Angular**. |

**Patrón raíz identificado:** tendencia a razonar en términos de *rendimiento y técnica* cuando el problema es de *gobernanza, seguridad o riesgo*. Es el reflejo típico de un buen desarrollador que aún no piensa como arquitecto. Vigilar en cada OT.

**Aporte válido de Iker que se incorporó al plan:** el *bus factor* del equipo como criterio para elegir Python (ADR-001, razón 3). Buen argumento de arquitectura.

---

## Decisiones pendientes

- ¿Se paga un usuario de M365 durante el semestre si no hay sandbox gratuito?
- ¿El frontend de contingencia se hace en Angular (fortaleza de Iker) o React (lo que decía la propuesta)?
- ¿Qué métrica exacta se usará para evaluar la calidad de las respuestas? (Definir antes de F3.)
