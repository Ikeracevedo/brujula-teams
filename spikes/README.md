# spikes/ — CODIGO DESECHABLE

> **Nada de lo que vive en esta carpeta forma parte de Brujula.**
> Se borra al cerrar la Orden de Trabajo que lo creo.

Un **spike** es un experimento acotado y desechable cuyo producto **no es codigo,
sino conocimiento**. Se mide por lo que ensena, no por lo que queda.

## Regla no negociable (ADR-001, ADR-004)

El scaffold generado por una herramienta externa (Microsoft 365 Agents Toolkit,
en este caso) **jamas** se convierte en la base del proyecto. Si se queda, impone
su forma al sistema y destruye la arquitectura hexagonal antes de que exista.

El codigo permanente vive en `app/`. Este arbol es un laboratorio.

## Contenido actual

| Carpeta | OT | Pregunta que responde | Estado |
|---|---|---|---|
| `teams-hello/` | OT-02A | Puede un bot responder dentro de Teams en el tenant `brujulateams`? | En curso |

## Al cerrar la OT-02A

1. Los hallazgos se escriben en `docs/BITACORA.md`.
2. Las capturas de evidencia se mueven a `docs/adr/`.
3. **`teams-hello/` se elimina del repositorio.**

Si al terminar la OT esta carpeta sigue existiendo, el spike fallo en lo unico
que importaba: convertirse en conocimiento en vez de en deuda.
