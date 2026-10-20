# Luisita — V3: integración de laboratorio con el orquestador existente

**Estado: ADAPTADOR CANDIDATO. LIVE DESHABILITADO. NO INSTALAR EN CU01.**

La V2 modelaba radios ficticias con un controlador independiente. La V3 adapta
cada fila del calendario al contrato real de `Orchestrator.switch()` del
repositorio, ejecutando su implementación de trial/confirm y rollback con una API
ficticia y sondeos ficticios. No usa el `dry-run` simplificado del orquestador.
No construye CambiumAPI, no autentica, no envía HTTP y no habilita temporizadores.

## Resultado verificado

- 27 pruebas nuevas de integración: PASS, también con Python `-O`.
- 35 pruebas V2: PASS.
- 76 pruebas existentes de orquestador, ejecutor, etiquetado y recuperación: PASS.
- Ensayo de 49 transiciones: 42 tratamientos y 7 reservas; 49 confirmaciones
  ficticias y referencia final simulada 7000 MHz/20 MHz.
- Cero cambios RF reales. Ninguna medición simulada es elegible para la tesis.

Los 138 casos de las tres suites son verificaciones de software; no son ensayos
con 138 radios ni aplicaciones experimentales. No se ejecutaron pruebas en CU01.

## Contrato implementado

`adapter.py` convierte TREATMENT a PROSPECTIVE_TREATMENT y RESERVE a
PROSPECTIVE_RESERVE, conservando secuencia, ciclo, frecuencia y ancho. La reserva
se dirige a F7000_B20 y queda fuera de tratamientos. No llama al calendario
original ni a `campaign_executor.run_once()`.

La integración conserva la arquitectura AP-only: el orquestador aplica cambios
solo al AP; el SM se reasocia usando su configuración de exploración existente.
El contrato exige configuración confirmada persistida, readback RF del AP y
conectividad AP/SM/RPi. **No acredita lectura RF del SM**, identidad física,
SNR/RSSI, potencias, ganancias, TDD ni estabilidad real sostenida.

SQLite registra INTENT antes de invocar switch; el bloqueo exclusivo abarca la
transacción completa. Una intención interrumpida o cualquier HALTED impide
continuar automáticamente. La huella del plan, configuración del orquestador,
código fuente y tiempos detecta cambios entre ejecuciones. Las llamadas duplicadas
se reconocen por el registro; no certifican que la RF siga intacta.

Las ventanas son [inicio, fin). Un salto de secuencia o demora superior a 60 s
bloquea la campaña de laboratorio. Los 300 s de estabilización y 60 s de tolerancia
son parámetros de prueba, pendientes de aprobación. `lab_eligible_after` es una
marca calculada desde la solicitud, NO una fecha real de elegibilidad tras
confirmación. Las transiciones reales deberán usar tiempos efectivos de confirmación
y QC antes de habilitar mediciones. No se ejecuta iperf ni se mide throughput.

## Hallazgos que requieren resolución antes de campo

1. **Respuesta perdida durante trial:** el orquestador marca `trial_started` solo
   al recibir retorno de la API. Si el radio aceptó el cambio y la respuesta se
   pierde, el estado es incierto. La prueba nueva lo reproduce; la V3 queda HALTED.
   La simulación no demuestra reversión del equipo por vencimiento de 300 s.
2. **Respuesta perdida durante confirmación:** no puede inferirse si el radio
   confirmó o no. La V3 conserva el fallo y bloquea nuevos cambios aun cuando el
   orquestador intente cancelar. No borrar el registro para reintentar.
3. El rollback real del orquestador no se valida por estos mocks. Tampoco se
   validan latencias, duración de sondeos, comunicación Cambium ni cortes eléctricos.
4. El bloqueo prospectivo es independiente del ejecutor original. Aún falta un
   precheck real de exclusión de servicios, cierre original, reloj sincronizado,
   restauración de respaldos, conformidades RF y metodología y 48 h de estabilidad.
5. Antes de campo se necesita conciliación documentada: AP/SM reales, trial y
   configuración efectiva, decisión de retorno y autorización. No se ofrece una
   orden para borrar incidencias ni un comando de activación.

No se modificó el orquestador de la campaña original para corregir estos puntos.
El propósito es ensayarlos y resolverlos en la extensión antes de habilitarla.

## Reproducir desde la raíz del repositorio

Linux, Python 3.10 o superior, zona America/Lima disponible, sin dependencias extra:

```bash
python3 -m unittest discover -s prospective_28d/v3 -v
python3 -O -m unittest discover -s prospective_28d/v3 -v
python3 -m prospective_28d.v3.rehearse
python3 -m unittest discover -s prospective_28d/v2 -v
python3 -m unittest -v test_campaign_orchestrator test_campaign_executor test_campaign_labeler test_campaign_recovery
```

El comando rehearse crea y destruye su directorio temporal. Mantiene fuera de los
archivos originales los logs, SAFE_ABORT y SQLite de laboratorio. Los sondeos y la
API se sustituyen; los ensayos de estabilidad no esperan tiempos reales.

La V3 importa el planificador V2; descargar el repositorio completo para reproducir.
La fecha 1–29 de noviembre sigue siendo provisional. Ver las
[condiciones del protocolo](../../docs/validation_28d/README.md) y la
[revisión metodológica V2](../v2/REVISION_V2.md).
