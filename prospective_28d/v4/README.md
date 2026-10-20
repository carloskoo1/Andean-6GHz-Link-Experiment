# Luisita — V4: recuperación y exclusión entre fases, en laboratorio

**LAB_ONLY. MODO REAL DESHABILITADO. NO DESPLEGADO EN CU01.**

V4 desarrolla la solución candidata para los dos pendientes de V3. Se conserva
V3 como evidencia del ensayo con el orquestador existente. V4 ensaya una política
nueva de trial/confirm y conciliación, con radio y reloj ficticios. No reemplaza
`Orchestrator.switch()` ni cambia el ejecutor original. Su conexión al transporte
Cambium real y a los puntos de entrada de campo es un trabajo posterior.

## Recuperación ante una respuesta perdida

Una excepción de comunicación no demuestra si el equipo aceptó la solicitud.
La intención se guarda en SQLite ANTES del trial y ANTES de confirmar. Ante
incertidumbre, se bloquean nuevas operaciones, no se cancela a ciegas y no se
repite el cambio. Se espera un plazo de laboratorio de 360 s (trial 300 + margen
60), contado conservadoramente desde la excepción si esta llega más tarde.
El ensayo avanza un reloj ficticio: NO espera seis minutos reales.

| Estado observado después del plazo | Acción de laboratorio |
|---|---|
| Configuración anterior en tres lecturas y conectividad | Recuperación al estado previo comprobada; revisión obligatoria |
| Configuración solicitada aún persiste | Una única restauración trial/confirm al estado previo conocido |
| Otra configuración, lecturas inestables o equipo inaccesible | Ninguna escritura adicional; intervención manual |
| Restauración enviada, incluso con respuesta perdida | Esperar su propio plazo y volver a leer |
| Restauración no resuelta tras ese plazo | Intervención manual; sin bucle de reintentos |

Incluso después de recuperar, queda `review_required`. Reconocer el incidente
requiere su identificador y conserva el historial. No acredita conformidad de
experto. Si la incidencia ocurrió en el calendario, `schedule_halted` permanece
activo después de ese reconocimiento: no se repite el tratamiento ni se retoma
la campaña sin una decisión metodológica explícita sobre el periodo perdido.
No se mezclan incidencias con exposiciones válidas ni se declara elegibilidad.

La prueba no demuestra el comportamiento de vencimiento de firmware Cambium.
Los plazos, lecturas, tratamiento de solicitudes tardías y prueba sostenida de
estabilidad deben validarse en campo. Las tres lecturas del simulador son
inmediatas; no equivalen a tres minutos de estabilidad. El estado RF del SM,
controles de potencia/ganancia/TDD y autenticación no están certificados.
La conciliación exige indicar explícitamente que el tiempo es confiable.

## Exclusión entre los dos ejecutores

`Guard` usa un ÚNICO directorio común por enlace y `flock` durante cada operación.
SQLite guarda la fase titular: inicialmente `original`. La fase prospectiva no
puede operar antes del relevo; después de este, la original queda bloqueada aun
cuando ya no exista un proceso ejecutándose. Un proceso muerto libera flock,
pero NO elimina la intención pendiente. El registro impide que otro ejecute
cambios mientras se concilia el incidente.

- `run_original_lab()` envuelve `campaign_executor.run_once()` existente con la
  guardia compartida y un runner ficticio que nunca ejecuta comandos ni radios.
- `ScheduledProspective` combina el calendario V2 con la transacción candidata
  V4 bajo la misma guardia. Mantiene orden, ventanas y detención ante atrasos.
- `handover_lab()` ensaya requisitos de cierre, timer original deshabilitado,
  estabilidad de 48 h y condiciones de expertos. Sus valores son FICTICIOS en
  pruebas; no son evidencia de cumplimiento real.
- Los ensayos con procesos independientes acreditan contención en ambos sentidos
  y supervivencia de la incidencia después de una terminación abrupta.

**La exclusión solo protege puntos de entrada que usan la misma guardia.** El
servicio original instalado hoy NO la utiliza y no fue cambiado. Antes del
futuro despliegue, ambos ejecutores y cualquier cambio manual autorizado deben
pasar por la misma protección, con ruta común estable, permisos controlados,
identidad del enlace y almacenamiento local. Dos directorios distintos o un
comando RF que la omita evaden esta garantía. No borrar ni reemplazar `link.lock`
para recuperar un bloqueo. No se ofrece protección distribuida entre hosts.

## Evidencia

37 pruebas V4 pasan en modo normal y optimizado. Incluyen respuestas perdidas
antes/después de aceptación, confirmación ambigua, restauración ambigua, estado
RF desconocido, reloj no confiable, retraso de trial, diario corrupto, reinicio,
colisión de procesos, relevo y el calendario completo.

El ensayo calendario contiene 49 ventanas: 42 tratamientos y 7 reservas.
Hay 46 cambios ficticios y 3 ventanas donde la configuración ya coincide con el
objetivo. Una ventana programada no implica necesariamente una conmutación RF.
El estado ficticio final es 7000/20. Cero cambios RF reales y cero datos científicos.

Las suites previas tienen 35 casos V2, 27 V3 y 76 originales. La V4 añade 37;
los conteos no constituyen réplicas experimentales ni aprobación del Experto 2.

## Reproducir desde la raíz del repositorio

Linux, Python 3.10 o superior, zona America/Lima disponible:

```bash
python3 -m unittest discover -s prospective_28d/v4 -v
python3 -O -m unittest discover -s prospective_28d/v4 -v
python3 -m prospective_28d.v4.rehearse
```

Todo ensayo usa directorios temporales. No hay CLI de activación, credenciales,
servicios nuevos ni comandos de instalación. `live=True` se rechaza. No se llamó
a CU01 y no se modificaron radios ni archivos operativos originales.

## Paso posterior

Revisar esta solución con el Experto 2. Tras cierre original y habilitación,
integrar la política candidata con las respuestas reales de la API y comprobar
plazos, readback, exclusión en todos los puntos de entrada y acceso de recuperación.
La prueba física requiere ventana supervisada; el calendario y el protocolo TCP
siguen sujetos a aprobación. Este informe cierra el desarrollo de esos dos
mecanismos en laboratorio, no su aceptación operativa.
