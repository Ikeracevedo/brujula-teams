# Brújula — Guía de instalación para el administrador de TI

> **⚠️ BORRADOR — versión 0.1, 8 de septiembre de 2026.**
> Los campos marcados «así» están pendientes y **no se puede enviar a nadie hasta rellenarlos**.
> Las secciones marcadas 🔴 dependen de decisiones que el proyecto aún no ha tomado.
>
> *Nota interna, borrar antes de publicar: este documento es para un cliente. El procedimiento de
> montaje del entorno de desarrollo está en `RUNBOOK-TENANT.md` y no se comparte.*

---

## En 30 segundos

Brújula es un asistente dentro de Microsoft Teams que responde *"¿qué tengo esta semana?"*
reuniendo los pendientes que su gente ya tiene dispersos en Planner, To Do, Calendario y
conversaciones, y devolviéndolos en una sola lista **con enlace a su origen**.

| | |
|---|---|
| **Qué necesita de usted** | Una aprobación de consentimiento y una instalación en Teams. Nada más |
| **Qué instala en su infraestructura** | Nada. Brújula se ejecuta en «‹hosting›», fuera de su tenant |
| **Qué permisos pide** | Cinco, **todos de solo lectura**. Ninguno de escritura |
| **Qué datos ve** | Únicamente los del usuario que inició sesión, y solo lo que ese usuario ya puede ver |
| **Tiempo de instalación** | ~10 minutos |
| **Cómo se revoca** | Un clic, desde su propio portal. Sección 5 |

---

## 1. Qué hace y qué no hace

**Sí:**
- Reúne pendientes de Planner, To Do y Calendario del usuario autenticado.
- Detecta compromisos mencionados en conversaciones y los marca **como inferencias**, con su nivel
  de confianza y un aviso explícito de que deben verificarse.
- Enlaza cada elemento a su origen dentro de Teams.

**No:**
- ❌ No es un asistente de propósito general. Fuera de sus pendientes, declina responder.
- ❌ No lee la organización. Solo lo que el usuario autenticado ya tiene permiso de ver.
- ❌ **No escribe nada.** No crea, no modifica y no borra tareas, eventos ni mensajes.
- ❌ No reemplaza a Planner. Lo unifica con lo que Planner no ve.

---

## 2. Permisos solicitados

Los cinco son **permisos delegados de Microsoft Graph**: Brújula actúa *como el usuario* y con los
permisos del usuario. Nunca por sí misma sobre la organización.

| Permiso | Qué dato lee | Para qué |
|---|---|---|
| `User.Read` | Nombre y correo del usuario que inició sesión | Identificar a quién se responde |
| `Calendars.Read` | Eventos del calendario **del propio usuario** | Mostrar compromisos de la semana |
| `Tasks.Read` | Tareas de To Do y Planner del usuario | Fuente principal de pendientes |
| `Team.ReadBasic.All` | **Solo nombres y descripciones** de los equipos a los que el usuario ya pertenece | Ubicar el origen de un pendiente. No da acceso al contenido |
| `Chat.Read` | Mensajes de los chats del usuario | Detectar compromisos mencionados en conversación |

### Lo que NO se pide, y es lo importante

**Ningún permiso termina en `ReadWrite`. Ninguno.** Brújula no puede modificar nada en su tenant,
ni aunque quisiera: los permisos que se lo permitirían no están en la solicitud, y añadirlos
requeriría una nueva aprobación suya.

Tampoco se solicita `ChannelMessage.Read.All` — el permiso que daría acceso a los mensajes de los
canales de la organización. 🔴 *Pendiente: si en el futuro se necesitara, la vía prevista es RSC
(Resource-Specific Consent), donde el propietario de un equipo concreto autoriza la app solo sobre
ese equipo. Se documentará como una decisión suya, equipo por equipo.*

> Sobre `Team.ReadBasic.All`: el sufijo `.All` suele encender alarmas y es correcto que así sea.
> En este caso cubre **únicamente nombres y descripciones** de los equipos a los que el usuario ya
> pertenece — el equivalente a la lista que ya ve en su barra lateral de Teams. No otorga acceso a
> mensajes, archivos ni miembros.

---

## 3. Requisitos previos

- Un tenant de Microsoft 365 con Teams (cualquier plan de empresa o educación).
- Un usuario con rol **Administrador global** o **Administrador de aplicaciones en la nube**.
- Permitir la carga de aplicaciones personalizadas, **o** publicar Brújula en su catálogo interno.
  Sección 4.2.

---

## 4. Instalación

### 4.1 — Aprobar el consentimiento (una vez, para toda la organización)

Abra esta dirección con su cuenta de administrador, reemplazando `{su-tenant}` por el dominio o el
identificador de su organización:

```
https://login.microsoftonline.com/{su-tenant}/adminconsent?client_id=«CLIENT_ID_DE_PRODUCCION»
```

Verá la lista exacta de permisos de la sección 2. Revísela antes de aprobar: **lo que aparece en
esa pantalla es todo lo que Brújula puede hacer.** Si aparece algo distinto de esos cinco permisos
de lectura, **no apruebe y avísenos** — significaría que está usando un enlace que no es el nuestro.

> 🔴 **Pendiente del proveedor:** el `CLIENT_ID` de la aplicación de producción. El actual pertenece
> al entorno de desarrollo y **no debe distribuirse**.

### 4.2 — Instalar la aplicación en Teams

**Opción A — catálogo de la organización (recomendada).**
Centro de administración de Teams → *Aplicaciones de Teams* → **Administrar aplicaciones** →
*Cargar nueva aplicación* → seleccione el paquete `«brujula-vX.Y.Z.zip»` que le entregamos.
Desde ahí puede asignar quién ve la app mediante directivas de permisos.

**Opción B — carga individual.** Si su organización permite cargar apps personalizadas, cada
usuario puede instalarla desde *Aplicaciones → Administrar tus aplicaciones → Cargar una aplicación
personalizada*.

### 4.3 — Comprobar que funciona

Abra un chat con **Brújula** y escriba `ayuda`. Debe responder con la lista de comandos
disponibles. Después, `semana`.

**En el primer uso, cada usuario verá una pantalla de inicio de sesión de Microsoft.** Es esperado:
el consentimiento de administrador autoriza a la aplicación, pero cada usuario sigue autenticándose
con su propia cuenta. Brújula nunca ve ni almacena contraseñas.

---

## 5. Cómo revocar el acceso

En cualquier momento y sin avisarnos:

**Portal de Microsoft Entra** → *Aplicaciones empresariales* → buscar **Brújula** →
**Propiedades** → *Eliminar*.

El acceso se corta de inmediato. Los tokens emitidos dejan de renovarse y los existentes caducan en
menos de una hora.

Para desactivarla sin eliminarla: en la misma pantalla, *Propiedades* → **¿Habilitado para que los
usuarios inicien sesión?** → **No**.

> Incluimos esto en la portada de la guía y no en un anexo a propósito. **Un administrador confía en
> lo que puede desinstalar**, y una app que esconde cómo se quita da exactamente la señal contraria.

---

## 6. Tratamiento de datos 🔴

> 🔴 **Sección pendiente. No enviar esta guía a ningún cliente sin completarla** — es la primera
> que lee un administrador con criterio, y dejarla en blanco es peor que no tener guía.

| Pregunta | Respuesta |
|---|---|
| ¿Dónde se ejecuta Brújula? | «región / proveedor de hosting» |
| ¿Qué se almacena? | «historial de conversación / caché de pendientes / nada» |
| ¿Durante cuánto tiempo? | «política de retención» |
| ¿Se almacenan credenciales? | **No.** Nunca se almacenan contraseñas de usuario |
| ¿Cómo se guardan los tokens? | «tokens de corta vida; refresh tokens cifrados en reposo» |
| ¿Se usan los datos para entrenar modelos? | «respuesta explícita» |
| ¿Qué proveedor de IA procesa el texto? | «proveedor, región, política de retención de su parte» |
| ¿Hay subencargados de tratamiento? | «lista» |

*Depende de decisiones de OT-03B (proveedor de LLM) y OT-04 (persistencia). Se completa entonces.*

---

## 7. Estado de verificación del editor 🔴

**Brújula no cuenta todavía con el distintivo *Verified Publisher* de Microsoft.**

Consecuencias concretas para usted:

1. En la pantalla de consentimiento aparecerá un aviso de que el editor no está verificado.
2. Si su tenant tiene deshabilitado el consentimiento de usuario —una configuración común y
   recomendable—, **solo un administrador podrá autorizar la aplicación**. Los usuarios no podrán
   hacerlo por su cuenta.

Lo decimos en la guía en lugar de dejar que lo descubra en la pantalla de aprobación. *Pendiente
del proveedor: alta en el Microsoft Partner Network y solicitud de verificación.*

---

## 8. Preguntas frecuentes

**¿Puede un usuario ver los pendientes de otro?**
No. Cada respuesta se construye con el token del usuario que pregunta, y ese token solo abre lo que
ese usuario ya puede abrir. No existe ninguna ruta en la que Brújula consulte datos de un usuario
distinto del que hizo la petición.

**¿Y si el modelo se inventa una fecha de entrega?**
Brújula distingue explícitamente un **hecho** de una **inferencia**. Lo que viene de Planner, To Do
o Calendario se muestra como confirmado. Lo que se deduce de una conversación se muestra en otro
color, con su porcentaje de confianza y el aviso *"Brújula no confirma este pendiente. Verifícalo
en el origen."* Todo elemento, sin excepción, enlaza a su fuente.

**¿Qué pasa si Brújula no puede consultar una de las fuentes?**
Lo dice. Si Planner no responde, la respuesta incluye *"No pude consultar: Planner — esta lista
está incompleta."* **Nunca presenta un fallo como ausencia de pendientes**, porque un usuario que
confía en un "no tienes nada" equivocado pierde una entrega.

**¿Qué diferencia hay con Microsoft Copilot?**
Copilot requiere licencia adicional y es un asistente de propósito general. Brújula hace una sola
cosa —unificar pendientes dispersos con trazabilidad obligatoria— y funciona sin licencias de
Copilot.

**¿Podemos probarla en un grupo reducido antes de desplegarla?**
Sí. En el paso 4.2, opción A, use las directivas de permisos de aplicaciones de Teams para
asignarla solo a un grupo piloto.

**¿Qué pasa si dejamos de usarla?**
Sección 5. La eliminación es inmediata y no requiere contactarnos.

---

## 9. Contacto

| | |
|---|---|
| Responsable | «nombre» |
| Correo de soporte | «correo» |
| Repositorio del proyecto | «URL» |
| Aviso de privacidad | «URL» — 🔴 obligatoria para publicar en Teams |
| Términos de uso | «URL» — 🔴 obligatoria para publicar en Teams |

---

### Anexo — Lista de comprobación del administrador

- [ ] Revisé los cinco permisos y confirmé que ninguno es de escritura
- [ ] Aprobé el consentimiento de administrador
- [ ] Cargué el paquete en el catálogo de la organización
- [ ] Asigné la app al grupo piloto
- [ ] Probé `ayuda` y `semana` con una cuenta real
- [ ] Verifiqué que el procedimiento de revocación funciona **antes** del despliegue general
