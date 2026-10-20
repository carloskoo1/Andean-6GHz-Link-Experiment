# Luisita — V5: ejecutor candidato integrado, solo simulación

**NO ACCEDE A CU01. NO HABILITA RF NI TCP. NO ES UNA VERSIÓN DE CAMPO.**

Un único punto de ensayo conecta calendario, cambio, verificación, incidencia,
recuperación y clasificación temporal de mediciones. Reutiliza el contrato de
órdenes AP-only ensayado en V3 y la máquina de recuperación y guardia V4. El
código original `CambiumAPI` construye y procesa las órdenes contra un servidor
ficticio en memoria; NO existe un socket, autenticación real o dirección de radio.

La rutina anterior de `Orchestrator.switch()` no se ejecuta en V5: la transacción
conservadora heredada de Candidate V4 es la única responsable del cambio y la
recuperación. Así se evita que dos rutinas de rollback actúen sobre la misma
incidencia. V3 y V4 permanecen como versiones de referencia, sin modificarlas.

## Reproducir desde la raíz del repositorio

Linux, Python 3.10 o superior y zona America/Lima disponible:

```bash
python3 -m prospective_28d.v5.rehearse
python3 -m unittest discover -s prospective_28d/v5 -v
python3 -O -m unittest discover -s prospective_28d/v5 -v
```

El ensayo crea y elimina sus directorios temporales. Solo imprime JSON; no hay
comando live ni instalación. Los tests bloquean sockets y subprocess. Descargar
el repositorio completo, ya que V5 importa las piezas V2/V4 y la API original.

## Qué queda integrado

- Plan reproducible V2: 42 tratamientos y 7 reservas, 49 ventanas en total.
- Guardia única por enlace: exclusión y titularidad persistente de fase V4.
- Adaptación a get_param, set_param y set_trial_param con config_id dinámico,
  centerFrequency y códigos de ancho 1/2; centerFrequency2 no se modifica.
- Registro durable de intención antes de cambiar o confirmar. Respuestas perdidas
  conservan la incidencia y bloquean la continuación.
- Recuperación con plazo y lectura posterior, restauración única cuando procede,
  revisión obligatoria y calendario detenido tras una ventana fallida.
- Contrato congelado de calendario, TCP, estabilización y hashes del código;
  modificaciones se rechazan antes del cambio o la recuperación.

El simulador incluye retardo de lectura, trial y confirmación, más vencimiento
ficticio del trial. Estos retardos no miden latencias ni estabilidad del equipo.
Los plazos y controles siguen sujetos a aceptación y verificación de campo.

## Tiempos y exclusión

Cada ventana guarda solicitud, solicitud de trial, solicitud de confirmación,
recepción del ACK, verificación final y comienzo calculado de análisis. Los tiempos
son **efectivos dentro del reloj simulado**, nunca evidencia de una ejecución real.

`analysis_start = verified_at + settle_seconds`, con 300 s solo para laboratorio.
No se calcula desde el inicio programado ni desde el envío de la orden.
Si la configuración ya coincide con el objetivo, se registra LAB_NO_CHANGE:
no hay trial/ACK inventados, pero sí lectura y verificación antes de estabilizar.

| Condición del intervalo completo de medición | Clasificación |
|---|---|
| Inicio anterior a verificación + estabilización | TRANSITION_OR_SETTLING |
| Fin posterior al término programado | CROSSES_WINDOW_END |
| Reserva | RESERVE |
| Ventana con incidente o sin verificación | UNVERIFIED_OR_INCIDENT |
| QC no acreditado | QC_PENDING |
| Objetivo RF no confirmado para ese intervalo | RF_NOT_CONFIRMED |
| Intervalo ficticio que supera lo anterior | temporal_eligible=true, study_eligible=false |

Se usan ventanas [inicio, fin): un intervalo puede terminar exactamente en el
límite; no puede comenzar en él como parte del tratamiento anterior. Se exige QC
explícito y objetivo RF declarado, sin confundirlos con una lectura real del SM.
La función no lee RF en la fecha histórica del intervalo: su QC y objetivo son
entradas de laboratorio; un integrador de campo deberá aportar evidencia real.

Una incidencia posterior no invalida automáticamente ventanas anteriores ya
verificadas. La recuperación NO vuelve elegible la ventana fallida y reconocer
la incidencia NO reanuda el calendario. La decisión metodológica queda pendiente.

## TCP y procedimiento de campo

- [Configuración TCP pendiente](tcp_protocol.pending.json): 8/1 y 15/2, sin perfil
  activo, cadencia sin fijar, ejecución deshabilitada y verificaciones falsas.
- [Protocolo TCP para revisión](PROTOCOLO_TCP_PENDIENTE.md): decisiones necesarias
  para comparar y congelar medición y análisis.
- [Cierre, instalación y prueba supervisada](PROCEDIMIENTO_CAMPO_PENDIENTE.md):
  secuencia propuesta posterior al cierre y las conformidades. No autoriza acción.

El clasificador no ejecuta throughput ni aprueba el protocolo. `request_tcp_measurement`
se rechaza incluso si alguien cambia flags manualmente. No hay llamadas a iperf.

## Evidencia y límites

44 pruebas nuevas pasan en modo normal y optimizado. Incluyen 49 ventanas completas,
los cuatro casos de ACK perdido antes/después de trial y confirmación, recuperación
tras reinicio, restauración ambigua, registro fallido después de confirmar,
exclusión por intervalos completos y conservación del histórico válido.

`REHEARSAL.json` contiene la cronología completa, siete ejemplos de exclusión y
cuatro incidentes con recuperación. `TIMELINE.csv` y `EXCLUSION_EXAMPLES.csv`
facilitan su revisión. Todos los registros están marcados LAB_ONLY y ninguno
constituye una observación científica de la campaña.

El servicio original instalado NO usa aún la guardia común. La V5 no puede
protegerlo sin integrar todos los puntos de entrada en un despliegue futuro.
También faltan identidad AP/SM, RF del SM, controles físicos/RF, reloj real, QC
sostenido, respaldo restaurable, piloto y aprobaciones. El calendario 1–29 de
noviembre sigue siendo provisional. No se modificaron ejecutores, servicios,
calendario histórico ni radios de CU01.
