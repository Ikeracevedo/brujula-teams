# Política de Privacidad — Brújula

**Última actualización:** 13 de septiembre de 2026

Brújula es una aplicación desarrollada como proyecto académico (Proyecto en TIC 1, Universidad
Pontificia Bolivariana) que se integra con Microsoft Teams para ayudar a estudiantes a consolidar,
en un solo lugar, sus pendientes académicos: eventos de calendario, tareas y compromisos de equipo.

Esta política explica, en lenguaje llano, qué datos lee Brújula, para qué los usa, dónde viven y
qué control tiene el usuario sobre ellos.

---

## 1. Qué datos lee Brújula, y por qué

Brújula solicita acceso a tu cuenta de Microsoft mediante los siguientes permisos, **todos de solo
lectura**:

| Permiso técnico (Microsoft Graph) | Qué significa en la práctica | Para qué lo usa Brújula |
|---|---|---|
| `User.Read` | Leer tu nombre y datos básicos de perfil | Saludarte y confirmar que la sesión es tuya |
| `Calendars.Read` | Leer tus eventos de calendario | Mostrarte tus compromisos de la semana |
| `Tasks.Read` | Leer tus tareas (Microsoft To Do / Planner) | Mostrarte tus pendientes junto al calendario |
| `Team.ReadBasic.All` | Ver de qué equipos de Teams eres miembro | Identificar el contexto de tus entregas de equipo |
| `Chat.Read` | Leer tus chats de Teams | Detectar compromisos mencionados en conversaciones |

**No existe ningún permiso de escritura.** Brújula no puede crear, modificar ni borrar nada en tu
calendario, tus tareas, tus equipos ni tus chats — solo puede leerlos. Tampoco puede ver datos de
otros usuarios de tu organización: solo ve lo que tú, con tu propia cuenta, puedes ver.

## 2. Cómo se obtiene el acceso

Brújula usa el flujo de **autorización delegada** de Microsoft (OAuth 2.0). Esto quiere decir:

- Tú das tu consentimiento explícito, una sola vez, a través de la pantalla oficial de Microsoft —
  nunca a través de un formulario propio de Brújula.
- Brújula actúa **como tú y con tus permisos**, nunca con permisos elevados sobre tu organización.
- Puedes revocar el acceso en cualquier momento escribiendo `desconectar` en el chat, o desde
  [myaccount.microsoft.com](https://myaccount.microsoft.com) → Aplicaciones conectadas.

## 3. Dónde viven tus credenciales y tokens

**Brújula nunca ve ni almacena tu contraseña.** El inicio de sesión ocurre por completo dentro de
la pantalla de Microsoft; Brújula nunca la observa.

Los tokens de acceso y de renovación (*refresh tokens*) son gestionados por el **Bot Framework
Token Service** de Microsoft, no por la infraestructura de Brújula. En la práctica:

- Brújula pide un token vigente al servicio de Microsoft en cada operación que necesita hacer.
- Brújula no guarda esos tokens en ninguna base de datos propia.
- Si revocas el acceso, el siguiente intento de lectura falla de inmediato y Brújula te lo informa
  con claridad, sin fingir que no tienes pendientes.

## 4. Qué pasa si algo falla

Si una fuente de datos (por ejemplo, tu calendario) no puede consultarse — porque el permiso fue
revocado, porque hubo un error de conexión, o porque el servicio de Microsoft no respondió — Brújula
**nunca lo interpreta como "no tienes pendientes"**. Te informa explícitamente cuál fuente falló,
y te muestra igualmente los datos de las fuentes que sí respondieron.

## 5. Qué no hace Brújula

- No vende, comparte ni transfiere tus datos a terceros.
- No usa tus datos para entrenar modelos de lenguaje ni para ningún fin publicitario.
- No mantiene un historial permanente de tus eventos o tareas: los consulta en el momento en que
  se lo pides y no los conserva más allá de lo necesario para responderte.
- No registra el contenido de tus eventos, tareas o chats en archivos de registro (*logs*). Los
  logs técnicos solo contienen información operativa (por ejemplo, que una consulta a Graph
  devolvió un error 403), nunca el contenido de tus datos ni tus credenciales.

## 6. Tus derechos

Como usuario, en cualquier momento puedes:

- Revocar el acceso de Brújula a tu cuenta (comando `desconectar`, o desde tu cuenta de Microsoft).
- Preguntar qué fuentes están conectadas realmente (comando `estado`).
- Solicitar información sobre qué datos ha leído Brújula, escribiendo al contacto indicado abajo.

## 7. Naturaleza académica del proyecto

Brújula es un proyecto desarrollado en el marco de una asignatura universitaria (Proyecto en TIC 1,
UPB). No es un producto comercial en operación permanente. Esta política se mantiene vigente
mientras el proyecto esté activo y se actualizará si su alcance cambia.

## 8. Contacto

Para preguntas sobre esta política o sobre tus datos, contacta al desarrollador:

**Iker Acevedo** — [ikeracevedowrk@gmail.com](mailto:ikeracevedowrk@gmail.com)
Repositorio del proyecto: [github.com/Ikeracevedo/brujula-teams](https://github.com/Ikeracevedo/brujula-teams)
