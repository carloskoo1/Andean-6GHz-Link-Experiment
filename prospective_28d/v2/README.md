# Versión V2: leer primero REVISION_V2.md

Incluye controlador simulado y 35 pruebas. El texto siguiente conserva la planificación original; sus afirmaciones históricas sobre CU01 no fueron verificadas en esta revisión.

# Luisita — preparación offline de la fase prospectiva 3×2 (28 días)

**ESTADO: BORRADOR. NO AUTORIZADO PARA CONMUTACIONES RF.**

El paquete se mantiene aislado del ejecutor activo de CU01. No contiene direcciones IP de las radios, credenciales, servicios systemd ni funciones para aplicar parámetros. Los comandos disponibles son **solo** `build` y `validate` y se limitan a archivos propios.

## Diseño provisional

- Inicio propuesto: **2026-11-01 00:00 (Perú)**; finalización proyectada: **2026-11-29 00:00 (Perú)**.
- **Siete ciclos de cuatro días**. En cada ciclo: seis escenarios factoriales **12 horas** cada uno (72 h), seguidos de 24 horas de reserva y referencia planeada 7000 MHz/20 MHz.
- Seis tratamientos de 6475/6655/7000 MHz × 20/40 MHz; cada combinación figura **7 veces**, 84 horas propuestas por configuración. Total: 42 aplicaciones de tratamiento (504 h) y 7 reservas (168 h).
- En los primeros seis ciclos la permutación rotativa proporciona un turno en cada posición por escenario, con tres exposiciones diurnas y tres nocturnas. El séptimo ciclo es un refuerzo desbalanceado de una exposición por escenario que debe contemplarse al analizar.
- La asignación y fecha siguen **sujetas a revisión/aceptación del Experto 3** y autorización institucional.

## Ejecución segura de pruebas

```bash
python3 -m unittest -v test_prospective_plan.py
python3 prospective_plan.py build
python3 prospective_plan.py validate
```

Solo escribe `salidas_offline/calendario_28d_BORRADOR.csv` y `salidas_offline/informe_simulacion_offline.json` en su propio directorio. **No use este código para controlar radios.**

## Condiciones previas a programar la ejecución real

1. Acreditar cierre completo de la fase original; último segmento del calendario activo acaba el 27/10/2026 00:00 hora Perú. Conciliar los documentos que indican 28/10.
2. Desactivar **después del cierre** el ejecutor de fase original de forma autorizada; verificar no duplicidad de timers y que no queda tarea operando en el enlace.
3. Aplicar/confirmar **7000 MHz/20 MHz**, medir al menos 48 h de estabilidad y registrar prueba de retorno. Las 48 horas no se presumen solo por tiempo de calendario.
4. Inspección in situ de alineación, herrajes, conectores, ganancias, potencias y estado de antenas; conformidad técnica del Experto 1.
5. Congelar el protocolo estadístico y el orden/horario de los seis tratamientos por ciclo; conformidad metodológica del Experto 3.
6. Validar los scripts y las pruebas supervisadas del futuro ejecutor sin generar cambios no autorizados, incluidas transiciones, bloqueos, reinicios, rollback e idempotencia; revisión del Experto 2.
7. Acreditar sincronización de relojes, rutas TCP, configuración de iperf, prueba/recuperación de respaldos y custodia de archivos sin credenciales.
8. Aprobación formal del protocolo adicional y autorización expresa de habilitación. Todos los campos `preconditions` se mantienen **false** hasta documentación verificable.

## Alertas técnicas identificadas

- El README del ejecutor antiguo consigna 28/10, pero su `campaign_schedule.csv` operativo finaliza **27/10 00:00**. No modificar el calendario histórico para corregir el texto.
- Existen mediciones TCP antiguas con duración **15 s, omit 2 s** y otras **8 s, omit 1 s**. No mezclarlas directamente ni congelar arbitrariamente el protocolo sin ensayo y justificación. El plan marca 8/1 como **propuesta**, no conformidad.
- Las 24 h de reserva **no equivalen automáticamente a un cambio real de radio a referencia 7000/20**. Hará falta un adaptador operativamente verificado y autorizado. Este paquete solo lo declara como intención.
- El impacto de la prueba de throughput sobre otras cargas debe ser revisado antes del inicio.

## Alcance

No implica ejecución de campañas, ni aprobación de expertos, ni habilitación de servicios. Toda operación RF futura deberá diseñarse como fase distinta, contar con pruebas controladas, go/no-go documental y activación manual explícita.
