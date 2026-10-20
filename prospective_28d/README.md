# Luisita: fase prospectiva de 28 días

BORRADOR OFFLINE. SIN HABILITACIÓN RF.

Consultar [revisión V2](v2/REVISION_V2.md): scripts, calendario, controlador simulado y 35 pruebas.

Preparación para revisión de expertos y desarrollo posterior del adaptador real. No instala servicios ni modifica el ejecutor original. Las fechas 1–29 de noviembre de 2026 son provisionales.

Ver [condiciones pendientes](../docs/validation_28d/README.md).

Pruebas desde v2/: `python3 -m unittest discover -v`.

## Integración V3

La [V3](v3/README.md) ensaya el adaptador con la implementación existente de trial/confirm y rollback, usando dispositivos ficticios: 27 pruebas adicionales. El modo real permanece deshabilitado.

## Recuperación y exclusión V4

La [V4](v4/README.md) ensaya la conciliación de respuestas perdidas y una guardia compartida entre fases, con 37 pruebas nuevas y procesos independientes. Es exclusivamente de laboratorio y no cambia los ejecutores instalados.
