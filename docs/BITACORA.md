# BITÁCORA DEL PROYECTO

> Registro vivo. Se actualiza al cerrar cada Orden de Trabajo.
> Leer junto con `PLAN-MAESTRO.md` al inicio de cada chat.

**Estado actual:** **F1 — Plomería de Teams + esqueleto** (2–16 sep)
**OT activa:** OT-02A ejecutada al 80% (falta sideload en Teams) → sigue **OT-02B**
**OT-01:** ✅ CERRADA (23-ago-2026)
**Repositorio:** `brujula-teams` (público) — `github.com/Ikeracevedo/brujula-teams`
**Nombre del proyecto:** **Brújula**
**⏰ ENTREGA FINAL: 28 DE OCTUBRE DE 2026.** Checkpoints: 16 sep · 30 sep · 14 oct · 28 oct
**Última actualización:** 2 de septiembre de 2026 (sesión de tarde — ejecución de OT-02A)

---

## Tablero de Órdenes de Trabajo

| OT | Fase | Título | Estado |
|---|---|---|---|
| OT-01 | F0 | Reconocimiento de plataforma y primer contacto con Graph | ✅ Cerrada |
| **OT-02A** | F1 | **Spike desechable: ver un bot vivo en Teams** | 🟢 **80% — R4 resuelto; falta sideload** |
| **OT-02B** | F1 | **Esqueleto hexagonal + app de Entra ID multiinquilino** | 🟡 Activa (tras 02A) |
| OT-03 | F2 | Puerto `LLMProvider` + adaptador Gemini + `FakeLLMProvider` | ⚪ Pendiente |
| OT-04 | F2 | Conectar el bot al núcleo. MongoDB Atlas + historial | ⚪ Pendiente |
| OT-05 | F3 | Puerto `TaskSource` + adaptador Planner → `Pendiente` | ⚪ Pendiente |

---

## Auditoría del 2-sep-2026 — Hallazgo crítico de planeación

**Se leyó por primera vez `Definicion del curso.pdf`.** Estaba en la carpeta desde el 15 de agosto.
El plan original se construyó **sin leer la rúbrica**. Fallo de planeación del mentor, registrado.

**Consecuencias:**

| Hallazgo | Impacto |
|---|---|
| Entrega final **2 sep – 28 oct**, no noviembre | El plan tenía **6 semanas de más**. Hoja de ruta reescrita a 8 semanas. |
| Entregas parciales **cada dos semanas** | Concepto ausente del plan. Checkpoints incorporados. |
| Rúbrica exige *"responsive (Desk y Mobile)"* | El bot de Teams no lo cumple de forma literal → **ADR-009**, riesgo aceptado con disparador al 30-sep. |
| Exige diagramas de clases, casos de uso y BD | No existían en el plan. Incorporados a F4. |
| E2, E3 y E4 del curso sin verificar | **Deuda abierta.** El tech lead decide postergar la verificación. Se registra como riesgo R8. |

**Lección de proceso (aplica a mentor y a tech lead por igual):**
*antes de planear, leer todo lo que ya está sobre la mesa.* El documento que define cómo te
califican no es contexto opcional: es el requisito de más alta prioridad del proyecto.

**Decisiones del tech lead registradas:**
1. Teams es el canal primario y se ataca primero (**ADR-009**).
2. El frontend es **React**, no Angular — corrección respecto a la propuesta original.
3. La verificación de E2/E3/E4 se posterga; prioridad al avance técnico.
4. El RAG sobre documentos sale del alcance calificado.

**Incidencia menor:** `.gitignore` aparece con 218 líneas modificadas y contenido idéntico —
diferencia de fin de línea CRLF/LF de Windows. Se corrige con un `.gitattributes` que fije
`* text=auto eol=lf`. Diffs ruidosos ocultan diffs reales.

---

## OT-02A — Spike desechable: ver un bot vivo en Teams

**Objetivo:** responder **una sola pregunta** — *¿puedo hacer que un bot responda dentro de Teams
en el tenant `brujulateams`?* Nada más.

**Time-box: 6 horas.** Si a las 6 horas no hay un bot respondiendo, se detiene, se documenta dónde
se atascó y se decide. Un spike sin límite de tiempo deja de ser spike y se vuelve un pozo.

> 💡 **Spike**: experimento acotado y **desechable** cuyo producto no es código, sino
> **conocimiento**. Se mide por lo que enseña, no por lo que queda.

### Reglas no negociables
1. Vive en `spikes/teams-hello/`. **Esa carpeta se borra al terminar.**
2. **Puede estar en TypeScript o C# si el Toolkit los soporta mejor que Python.** Como se bota, el
   lenguaje da igual. Lo único que prueba es la plomería: túnel → registro del bot → sideload.
3. **Cero lógica de negocio.** Un bot *echo* que devuelva el mensaje en mayúsculas es suficiente.
4. El scaffold del Toolkit **jamás** se convierte en la base del proyecto (ADR-001, ADR-004).

### Pasos
1. **Habilitar carga de apps personalizadas** en el tenant propio: Centro de administración de Teams
   → Aplicaciones de Teams → Directivas de configuración → Global → *"Cargar aplicaciones
   personalizadas"* = **Activado**. Iker es admin global; puede hacerlo. *(La propagación puede
   tardar horas. Hacerlo primero.)*
2. Instalar en VS Code la extensión **Microsoft 365 Agents Toolkit** (antes *Teams Toolkit*) y
   Node.js LTS.
3. Crear un proyecto desde plantilla: **Bot básico / Echo Bot**. Anotar qué lenguajes ofrece la
   plantilla — **ese dato es evidencia directa sobre el riesgo R4**.
4. Iniciar sesión con `proyectotic1@brujulateams.onmicrosoft.com`.
5. Ejecutar *Provision* y luego *Debug (Preview in Teams)*. El Toolkit levanta un túnel de
   desarrollo y hace el sideload solo.
6. Escribirle al bot en Teams. Capturar pantalla.

### Qué reportar (esto es el entregable real)
- ✅/❌ ¿Respondió el bot? Captura.
- **¿Qué lenguajes ofrecía la plantilla y había Python?** → veredicto sobre R4.
- ¿Qué recursos creó el Toolkit en Azure y en Entra ID? (Azure Bot Service, app de Entra, etc.)
- ¿Qué archivos del scaffold contienen el `APP_ID`, el `BOT_ENDPOINT` y el manifiesto?
- **¿Qué URL exacta recibe el mensaje del usuario?** ← el dato más importante: ese es el único punto
  donde el adaptador de bot tocará el núcleo.
- Dónde se atascó, si se atascó.

### Verificación adicional (2 min en Graph Explorer, alto valor)

La OT-01 probó `/me/joinedTeams` (los equipos) pero **nunca los mensajes dentro de un canal**.
Esa es la frontera real de "que la IA lea todo el Teams del usuario". Ejecutar:

```
GET /me/joinedTeams
GET /teams/{team-id}/channels
GET /teams/{team-id}/channels/{channel-id}/messages
```

**Reportar:** ¿la tercera responde 200 o 403? ¿Qué permiso pide exactamente y quién lo aprueba?

**Por qué importa:** `Chat.Read` (ya confirmado ✅) cubre chats 1-a-1 y grupales.
Los mensajes de **canal** van por `ChannelMessage.Read.All` — Protected API con consentimiento de
administrador. Y es justo ahí donde vive el contenido académico: el anuncio del profesor en el canal
de la materia. **Es la fuente `MENSAJE` de la entidad `Pendiente` (ADR-005).**

Si sale 403: la vía es **RSC** (*Resource-Specific Consent*) — el dueño del equipo autoriza la app
sobre **ese** equipo, sin pasar por el admin del tenant. Encaja perfecto con el modelo ISV (ADR-003)
y con el hecho de que Iker es dueño de los equipos de su propio tenant.

**Consecuencia si no se resuelve:** Brújula agrega Planner + To Do + Calendario, pero pierde el
diferenciador frente a Copilot — detectar compromisos implícitos en la conversación.
Mejor saberlo hoy que en octubre.

### Criterio de aceptación
- [ ] Carga de apps personalizadas habilitada en el tenant
- [ ] Bot *echo* respondiendo dentro de Teams (con captura)
- [ ] Veredicto documentado sobre el soporte de Python (riesgo R4)
- [ ] Identificado el punto de entrada del mensaje (endpoint y forma del payload)
- [ ] `spikes/teams-hello/` marcado como desechable en el README

---

---

## OT-02A — RESULTADOS REGISTRADOS (2-sep-2026, sesión de tarde)

> **Estado: ejecutada al 80%. Pendiente únicamente la prueba de sideload en Teams real.**
> Duración: ~3 h de las 6 del time-box. El time-box **no se agotó**: se detuvo por una
> dependencia externa (propagación de directiva), no por bloqueo técnico.

### Resumen ejecutivo

El spike respondió su pregunta sobre el SDK, y lo hizo **mejor de lo esperado**: el riesgo R4,
clasificado como *"el más caro del plan"*, **baja de 🔴 rojo a 🟢 verde**. No solo existe SDK de
Python: está en GA y **corre sobre la misma pila que el ADR-001 ya había elegido**.

Ningún hallazgo salió de un tutorial. Todos salieron de **leer lo que las herramientas ya estaban
diciendo**: una lista de un asistente, un `requirements.txt`, un mensaje de error de `pip`, un
árbol de dependencias y un panel de logs.

---

### Línea de tiempo de la sesión

| Hora | Hecho |
|---|---|
| 15:24 | *"Cargar aplicaciones personalizadas" = **Activado*** en la directiva Global del tenant. Inicia propagación (hasta 24 h). |
| ~16:00 | Toolkit instalado. Scaffold generado en `spikes/teams-hello/`. |
| ~16:30 | Auditoría del scaffold. Hallazgos de SDK y dependencias. |
| ~16:45 | `pip install` → falla → **entrega el catálogo real de versiones**. Se corrige y se instala limpio. |
| 16:47 | **Playground conectado a `http://127.0.0.1:3978/api/messages`.** El bot responde 200. |

---

### Hallazgo 1 — La taxonomía de Microsoft en 2026 (y dónde encaja Brújula)

El asistente *Create a New Agent/App* ofrece tres familias:

| Familia | Opciones | Requiere licencia Copilot |
|---|---|---|
| Agents for Microsoft 365 Copilot | Declarative Agent · **Custom Engine Agent** · Copilot connectors | **Sí** |
| Apps for Microsoft 365 | Blank Copilot app/agent | — |
| *(sin etiqueta)* | **Teams Agents and Apps** · Office Add-in | No |

**Brújula es, en la nomenclatura oficial de Microsoft, un *custom engine agent*:** orquestación
propia y LLM propio. Microsoft le puso nombre a la categoría del proyecto.

Se implementa hoy sobre la superficie **Teams** (ADR-009) porque el tenant de prueba
—M365 Business Standard— **no tiene licencia de Copilot**.

**Vía de expansión documentada:** exponer el mismo núcleo como *custom engine agent* dentro de
Copilot es escribir **un adaptador nuevo**, no reescribir el sistema (ADR-004).

> **Munición para la pregunta 1 de sustentación** (*"¿por qué no Copilot?"*): la respuesta deja de
> ser defensiva. **Copilot no es un competidor: es una superficie más donde Brújula puede
> publicarse.** Copilot pilotea; la brújula ubica; y el mismo núcleo sirve a ambos canales.

**Observación de riesgo:** dentro de *Teams Agents and Apps*, la opción de bot simple **ya no
existe como categoría de primer nivel**: está enterrada bajo *"Other Teams Capabilities"* →
*"Simple Bot"*. Las tres opciones destacadas traen IA precargada (Teams AI Library + LLM).

> **Lectura de arquitecto:** cuando un proveedor mueve tu caso de uso a la categoría *"otros"*, te
> está diciendo dónde va a invertir su documentación y su soporte. Es una señal de riesgo a mediano
> plazo, no una molestia de interfaz.

**Descartadas conscientemente:** `Tab` (es el frontend web de F4), `Message Extension` (acción
sobre un mensaje, no conversación), `General Teams Agent` (trae orquestación propia → violaría la
regla de "cero lógica" del spike, y en F2 competiría con el orquestador del ADR-004).

---

### Hallazgo 2 — Veredicto sobre el riesgo R4: 🟢 VERDE

**Evolución del veredicto en una sola tarde. Cada paso, una fuente de evidencia distinta:**

| Momento | Fuente | Veredicto |
|---|---|---|
| Plan original | Suposición | 🔴 *"¿existe SDK de Python?"* |
| Documentación de Microsoft | `learn.microsoft.com` | 🟠 existe; hay **tres generaciones** |
| Diálogo del Toolkit | UI de la herramienta | 🟠 `Python` aparece, etiquetado **`Preview`** |
| `requirements.txt` generado | Scaffold | 🟠 pina `microsoft-teams-apps==2.0.0a8` → **alpha** |
| **Error de `pip`** | **PyPI, dato real** | 🟢 **existe `2.0.0` estable; la serie va en `2.0.16`** |

**Tres generaciones de SDK conviven:**

| Gen | Paquete | Estado |
|---|---|---|
| 1ª — Bot Framework | `botbuilder-*` | Legacy. Microsoft publica guía de migración. |
| 2ª — Agents SDK | `microsoft-agents-*` | Presentado en los docs como "el reemplazo oficial". |
| 3ª — **Teams SDK v2** | **`microsoft-teams-apps`** | **Lo que el Toolkit genera. GA en `2.0.x`.** |

**VEREDICTO FINAL R4:** *el SDK de bot de Teams para Python **es viable y está en GA**. El riesgo
residual no es de disponibilidad sino de **ecosistema**: tres SDKs en rotación en pocos años y
escasez de material de terceros para la generación vigente en Python. **Se busca en la
documentación oficial y en el código del paquete, no en Stack Overflow** — el 95% de los resultados
son de la 1ª generación y llevan a callejones sin salida.*

**El scaffold del Toolkit está desactualizado respecto a su propio SDK**: genera contra una alpha
que quedó ~70 releases atrás y que además exige `Python >=3.12,<3.14`, incompatible con el
Python 3.14.3 instalado. La versión GA `2.0.16` sí es compatible.

> **REGLA ADOPTADA:** *un mensaje de error de un gestor de paquetes no es un obstáculo: es una
> consulta al repositorio remoto que devolvió el estado real del ecosistema. **Se lee entero antes
> de intentar arreglarlo.*** Aquí, el error de `pip` fue la fuente más confiable de toda la sesión —
> más que la documentación oficial.

---

### Hallazgo 3 — 🎯 El SDK está construido sobre FastAPI. El ADR-001 queda confirmado.

Árbol de dependencias real de `microsoft-teams-apps==2.0.16`:

```
fastapi>=0.115.13      uvicorn>=0.34.3      starlette
pydantic>=2.9.0        dependency-injector>=4.48.1
httpx                  pyjwt[crypto]        pydantic-settings
```

| Antes (temor) | Ahora (dato verificado) |
|---|---|
| El SDK exigiría `aiohttp` → dos servidores, dos procesos, un puente | **El bot ES una app FastAPI** |
| ADR-001 en tensión con la herramienta | **ADR-001 confirmado por el ecosistema** |
| Pydantic era disciplina autoimpuesta (ADR-001) | **Pydantic es la base del propio SDK** |
| Inyección de dependencias era teoría de los ADR | **`dependency-injector` viene en el SDK** |

> **Material directo de sustentación.** Ante *"¿por qué FastAPI?"* la respuesta ya no es "porque es
> popular", sino: **"porque el SDK oficial de Teams para Python está construido sobre él — mi capa
> de bot y mi núcleo comparten servidor, modelo de datos y contenedor de dependencias."**
>
> La decisión del ADR-001 se tomó en agosto por razones de portafolio y *bus factor*. La evidencia
> técnica de septiembre la respalda **por un camino independiente**. Una decisión que sobrevive a
> información que no existía cuando se tomó es una decisión bien fundamentada.

---

### Hallazgo 4 — El punto de entrada, deducido y luego verificado

**Deducido** leyendo `m365agents.local.yml`:

```yaml
- uses: botFramework/create
  with:
    messagingEndpoint: ${{BOT_ENDPOINT}}/api/messages
```

**Verificado** en el log del Playground a las 16:47:

```
Connecting to your application at http://127.0.0.1:3978/api/messages ... Connected.
installationUpdate 200 · conversationUpdate 200
```

**Cadena completa del mensaje:**

```
Usuario escribe en Teams
  → Bot Framework
  → POST https://<dev-tunnel>.devtunnels.ms/api/messages
  → dev tunnel
  → localhost:3978/api/messages
  → App() de microsoft-teams-apps  (servidor FastAPI interno)
  → handler @app.on_message
```

**`POST /api/messages`, puerto 3978, es el único punto donde el adaptador de bot tocará el núcleo
de Brújula.** La ruta **no está en el código**: la crea la clase `App` por dentro. El SDK oculta el
servidor HTTP — dato relevante para F2, cuando haya que decidir si el bot y la API viven en el
mismo proceso o en dos.

> **Nota de método:** deducir y verificar son actos distintos. Se hicieron los dos, en ese orden.

---

### Hallazgo 5 — Auditoría del `requirements.txt` generado

El scaffold trae dos defectos, ambos corregidos:

| # | Defecto del scaffold | Corrección | Por qué importa |
|---|---|---|---|
| 1 | `dotenv>=0.9.9` | `python-dotenv==1.0.1` | `dotenv` es un paquete **abandonado desde 2013** cuya propia descripción dice *"THIS LIBRARY IS NO LONGER SUPPORTED, USE python-dotenv INSTEAD"*. No es typosquatting: es **abandonware**. Que un scaffold oficial de Microsoft lo instale por defecto, en 2026, es un defecto de la plantilla. |
| 2 | `microsoft-teams-apps>=2.0.0a8,<3.0.0` | `microsoft-teams-apps==2.0.16` | Un rango abierto sobre un prerelease permite que `pip` instale una versión con cambios rompientes sin aviso. El bot "que funcionaba ayer" deja de arrancar sin que nadie haya tocado el código. |

Se conservaron `requirements.txt.original` y `app.py.original` para que el diff sea auditable.

> **REGLA ADOPTADA:** *todo archivo de dependencias generado por una herramienta se **audita línea
> por línea** antes del primer `pip install`. Nombre canónico del paquete, estado de mantenimiento y
> versión fijada. Confiar en un scaffold es heredar las decisiones de otro sin haberlas revisado.*

**Instalación final:** limpia, sin conflictos, sobre **Python 3.14.3**. Único aviso:
`ExperimentalWarning` de `HtmlWidgetSecurityPolicy`, componente no utilizado por el proyecto.

**Verificación de compatibilidad de API** (`app.py` fue generado contra `2.0.0a8`, se ejecuta con
`2.0.16`): los imports de `microsoft_teams.api` y `microsoft_teams.apps` responden **`IMPORTS OK`**.
La API se mantuvo estable entre la alpha y la GA.

---

### Hallazgo 6 — Qué crea `provision` (dos buenas noticias)

**a) No consume Azure.** Para el entorno `local`, el registro del bot se hace en
`dev.botframework.com` mediante `botFramework/create`, **no** en Azure Bot Service.
El `infra/azure.bicep` existe pero solo aplica al entorno remoto.
**Los créditos de Azure for Students quedan intactos** y reservados para hospedar el backend.

**b) La app de Entra nace multi-inquilino por defecto:**

```yaml
- uses: aadApp/create
  with:
    signInAudience: AzureADMultipleOrgs   # ← multi-tenant
```

Confirma que el radio button que exige la OT-02B (**"Cuentas en cualquier directorio
organizativo"**, ADR-003, modelo ISV) es el correcto. *(La app del spike se descarta con la
carpeta; la permanente se registra a mano en OT-02B.)*

**Manifiesto generado:** `manifestVersion 1.29`, scopes `personal`, `team`, `groupChat`;
permisos `identity` y `messageTeamMembers`.

---

### Hallazgo 7 — Seguridad: protegidos por accidente, no por diseño

`provision` genera un `CLIENT_SECRET` real y lo escribe en `env/.env.local.user`.
Verificación con `git check-ignore -v`:

```
.gitignore:156:ENV/   →   spikes/teams-hello/env/.env.local.user
```

La regla que lo atrapó es **`ENV/` en mayúsculas**, del template de Python de GitHub.
Coincidió con `env/` **únicamente porque el sistema de archivos de Windows no distingue
mayúsculas de minúsculas**. En Linux —es decir, en cualquier CI— esa regla **no habría coincidido**.

Hay protección real: el `.gitignore` propio del scaffold incluye `env/.env.*.user` explícito.
Pero el hallazgo se registra igual.

> **REGLA ADOPTADA:** *estar protegido no es lo mismo que estar protegido **a propósito**. Toda
> regla de `.gitignore` sobre secretos se verifica con `git check-ignore -v` y se lee **cuál** regla
> hizo el match. Una protección que depende de la insensibilidad a mayúsculas de un sistema de
> archivos desaparece al cambiar de máquina.*

Es el mismo problema de fondo que el CRLF detectado en la auditoría del 2-sep: **el repositorio se
comporta distinto según el sistema operativo.** El `.gitattributes` pendiente deja de ser cosmético.

---

### Lo construido: demo de producto sobre el spike

Además de la prueba de plomería, se construyó una **demo honesta** para mostrar avance sin mentir.
Cuatro archivos en `spikes/teams-hello/src/`:

| Archivo | Responsabilidad | Qué demuestra |
|---|---|---|
| `dominio.py` | Entidad `Pendiente` + `FuentePendiente` (ADR-005) | **Cero imports externos.** Regla hexagonal verificable a simple vista |
| `fixtures.py` | Datos de ejemplo, marcados como falsos | Firma `-> list[Pendiente]`, **idéntica a la del futuro `TaskSource`** |
| `tarjetas.py` | `list[Pendiente]` → Adaptive Card | Único módulo que conoce Teams. La frontera hexagonal en 60 líneas |
| `app.py` | 4 handlers | Separa plomería de demo |

**Handlers:** `eco` (plomería pura, devuelve en mayúsculas) · `semana` (la tarjeta) ·
`estado` (lista honesta de lo probado y lo no probado) · `bienvenida`.

**La tarjeta muestra la tesis del proyecto en una pantalla:** cuatro pendientes de cuatro fuentes,
cada uno con `fuente`, `vence` y botón **"Ver origen"** (trazabilidad obligatoria). Los tres
provenientes de sistemas estructurados salen en **verde**, marcados *"Confirmado"*. El cuarto,
inferido de un mensaje de canal, sale en **amarillo**, con **72% de confianza** y la leyenda
*"Brújula no confirma este pendiente. Verifícalo en el origen."*

Ese contraste **es la respuesta visual a la pregunta 2 de sustentación** (*"¿y si el modelo alucina
una fecha de entrega?"*) y al *"¿por qué no Copilot?"*.

> **PRINCIPIO ADOPTADO — honestidad del avance:** *la demo declara explícitamente, en la propia
> tarjeta y en el comando `estado`, que **Graph no está conectado** y que los datos son de ejemplo.
> Demostrar el canal y el modelo de datos es un avance real; presentarlo como integración con Graph
> sería mentir. **Un proyecto que exagera su avance pierde la única moneda que tiene ante un
> evaluador.** Además: nunca poner en una demo algo que no se pueda defender bajo pregunta.*

**Nota:** todo este árbol sigue siendo **desechable**. Estos archivos son un **ensayo** del diseño;
la versión permanente se escribe desde cero en `app/` durante la OT-02B. La regla del ADR-001 no se
relaja porque el spike haya quedado bonito.

---

### Criterio de aceptación de la OT-02A

- [x] Carga de apps personalizadas habilitada en el tenant — *15:24, 2-sep*
- [ ] **Bot echo respondiendo dentro de Teams (con captura)** — *pendiente: propagación de directiva*
- [x] Veredicto documentado sobre el soporte de Python (R4) → **🟢 GA, viable**
- [x] Identificado el punto de entrada → **`POST /api/messages`, puerto 3978** (deducido y verificado)
- [x] `spikes/` marcado como desechable — `spikes/README.md`

**4 de 5.** El único pendiente depende de una espera externa, no de trabajo técnico.

---

### Correcciones del mentor registradas en esta sesión

Se registran con el mismo rigor que los errores del tech lead. **Dos veces en una tarde el mentor
predijo desde documentación y la ejecución lo desmintió.**

| # | Predicción | Realidad | Fuente que corrigió |
|---|---|---|---|
| 1 | *"El SDK usa **aiohttp**; hay tensión con el ADR-001"* | Usa **FastAPI + uvicorn**. Cero tensión. | Árbol de dependencias de `pip install` |
| 2 | *"`dotenv` huele a **typosquatting**"* | Es **abandonware** legítimo de 2013. Diagnóstico equivocado, problema real distinto. | Ficha del paquete en PyPI |

En el caso 1, el error de origen fue leer la documentación del **Agents SDK** (2ª generación) y
asumir que aplicaba al SDK que el Toolkit realmente genera (3ª generación).

> **Confirmación de la regla del 23-ago:** *"la política de una plataforma externa no se deduce de
> la documentación, se verifica ejecutándola."* Esta sesión la extiende: **aplica también al
> ecosistema de dependencias, y aplica también al mentor.** La documentación describe lo que es
> posible; solo la ejecución dice qué es cierto aquí y ahora.

---

### Pregunta de comprensión de la sesión — CERRADA

**Pregunta:** *el SDK parecía exigir un servidor distinto al del ADR-001. ¿Por qué cambiar el
ADR-001 a "lo que traiga el SDK" sería un error de arquitectura, y qué mecanismo del plan libera de
tomar esa decisión hoy?*

**Respuesta registrada:** decidir la arquitectura del núcleo a partir de lo que traiga una
herramienta externa **invierte la relación**: el proyecto pasa a servir a la herramienta.
El mecanismo que protege es la **Capa de Bot Delgada** (ADR-001): el adaptador de bot no contiene
lógica de negocio, así que un SDK hostil cuesta **un módulo**, no el proyecto.

En este caso la tensión desapareció al medirla. **Pero el valor del ADR no dependía del resultado:**
un ADR bien escrito protege igual cuando se acierta que cuando se falla. Esa es la prueba de que
estaba bien escrito.

---

### Pendientes inmediatos para la próxima sesión

1. 🔴 **Cerrar OT-02A:** `F5 → Debug in Teams (Chrome)` → provision → sideload → escribirle al bot →
   **captura**. Requiere que la directiva haya propagado (guardada 15:24 del 2-sep).
2. **Verificación de Graph pendiente** (2 min en Graph Explorer, alto valor):
   `GET /teams/{id}/channels/{id}/messages` → ¿200 o 403? Es la frontera de la fuente `MENSAJE`.
   Si da 403, la vía es **RSC**.
3. **Borrar `spikes/teams-hello/`** una vez capturada la evidencia. Mover capturas a `docs/adr/`.
4. Crear `.gitattributes` con `* text=auto eol=lf`.
5. Arrancar **OT-02B**: estructura hexagonal en `app/`, `mypy` + `ruff` desde el primer commit,
   registro de app en Entra ID multi-inquilino con los 5 permisos delegados.
6. ⚠️ **15-sep:** decidir pago del tenant (16,80 USD/mes) o migración. **Fecha crítica.**


## OT-02B — Esqueleto hexagonal + app de Entra ID

**Se ejecuta después de OT-02A y con lo aprendido en ella.** Esto **sí** es código permanente.

### Parte 1 — Estructura del proyecto
Crear el árbol del ADR-004 con archivos mínimos:

```
brujula-teams/
├── app/
│   ├── domain/pendiente.py        # entidad + enum FuentePendiente
│   ├── ports/                     # llm_provider.py, task_source.py
│   ├── services/                  # (vacío por ahora)
│   ├── adapters/                  # (vacío por ahora)
│   └── api/main.py                # FastAPI + GET /health
├── tests/
├── spikes/
├── .env.example                   # sin un solo valor real
├── requirements.txt
└── pyproject.toml                 # config de mypy y ruff
```

**Disciplina obligatoria (compensa la venida de .NET, ADR-001):** tipado estricto, `mypy` y `ruff`
configurados **desde el primer commit**. Añadirlos después es refactorizar; ponerlos al inicio es
gratis.

**Regla de dependencias, verificable:** `app/domain/` **no puede importar nada** fuera de la
librería estándar. Ni FastAPI, ni Mongo, ni el SDK de Graph. Si un import se cuela ahí, la
arquitectura hexagonal ya se rompió.

### Parte 2 — Registro de app en Entra ID (permanente, no la del Toolkit)
- Portal de Entra → Registros de aplicaciones → Nuevo registro.
- **Tipos de cuenta: "Cuentas en cualquier directorio organizativo (multiinquilino)"**
  ⚠️ Decisión difícil de revertir. Elegir "solo mi organización" ata el `CLIENT_ID` a
  `brujulateams` para siempre y ninguna empresa cliente podría instalar Brújula (ADR-003, modelo ISV).
- Permisos delegados, solo lectura: `User.Read`, `Calendars.Read`, `Tasks.Read`,
  `Team.ReadBasic.All`, `Chat.Read`. **Ni un `ReadWrite`.**
- Generar secreto y guardarlo **solo** en `.env` local. `.env.example` lleva los nombres, nunca los valores.

### Criterio de aceptación
- [ ] `GET /health` responde 200 en local
- [ ] `mypy` y `ruff` corren limpios
- [ ] `Pendiente` definido en `domain/` sin imports externos
- [ ] App multiinquilino registrada, con los 5 permisos delegados
- [ ] `.env` en `.gitignore`; `.env.example` versionado y sin secretos
- [ ] `.gitattributes` con `* text=auto eol=lf`

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

- ⚠️ **15 sep — FECHA CRÍTICA:** vence la prueba de M365 Business Standard. Decidir pago
  (16,80 USD/mes) o migrar de tenant **antes** de esa fecha. Un tenant caído en octubre = sin demo.
- ⚠️ **30 sep — DISPARADOR ADR-009:** si no hay núcleo end-to-end, congelar Teams y priorizar la
  web responsive para asegurar la rúbrica.
- **Preguntar al docente** si un bot de Teams cuenta como *"implementación responsive (Desk y Mobile)"*.
  Un minuto de conversación elimina el riesgo más grande del proyecto.
- Verificar qué se entregó realmente en E2 (OKR/buyer persona), E3 (prototipo) y E4 (User Story
  Mapping + HU). Postergado por decisión del tech lead. **Riesgo R8.**
- Frontend en React (propuesta original) vs Angular (fortaleza de Iker). Decidir en F4.
- ¿Qué métrica exacta se usará para evaluar la calidad de las respuestas? (Definir antes de la demo.)

---

## Riesgos — actualización 2-sep-2026

| # | Riesgo | Estado |
|---|---|---|
| R4 | SDK de bot de Teams para Python inmaduro | 🟢 **CERRADO 2-sep.** `microsoft-teams-apps 2.0.16` es GA y corre sobre FastAPI. Riesgo residual: rotación de SDKs y poca documentación de terceros |
| R8 | **Entregables E2/E3/E4 del curso sin verificar** | 🔴 **Nuevo. Abierto por decisión del tech lead** |
| R9 | **Ventana real de 8 semanas, no 14** | 🔴 **Nuevo. Mitigado con recorte del RAG** |
| R10 | **Rúbrica exige responsive Desk+Mobile; el bot no lo cumple literalmente** | 🟠 **Nuevo. ADR-009, disparador 30-sep** |
| R11 | **Tenant vence el 15-sep** | 🟠 **Nuevo. Requiere decisión de pago** |
