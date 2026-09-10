# Ejecutor automático de la campaña 3×2

El temporizador consulta el calendario cada minuto. Solo ejecuta una transición cuando entra en una nueva fila experimental y registra el número de secuencia en `campaign_runtime/executor_state.json`; por ello, reinicios y ejecuciones repetidas no duplican cambios.

El 15 de septiembre a las 10:00 se conserva como piloto supervisado separado. El ejecutor de la campaña no actúa antes del 16 de septiembre a las 00:00 (America/Lima).

Si una transición falla, el ejecutor registra el incidente y espera 30 minutos antes de reintentar; así evita actuar sobre el radio cada minuto. Al finalizar el diseño el 28 de octubre a las 00:00, aplica explícitamente la línea base `7000 MHz / 20 MHz`.

Los eventos de cambio y recuperación quedan en `campaign_runtime/campaign_events.jsonl`. Las métricas científicas continúan siendo recopiladas por AtmosLink en sus tablas y exportaciones habituales.
