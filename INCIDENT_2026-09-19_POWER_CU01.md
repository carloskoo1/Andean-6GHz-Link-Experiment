# Incidente de energía/adquisición CU01 — 19–20 de septiembre de 2026

## Contexto

Durante la campaña experimental 3×2 del radioenlace rural altoandino CU01–SJ01 se produjo una interrupción de energía que afectó al nodo de cómputo Controlador ubicado en CU01.

- Escenario activo: F7000_B40
- Configuración RF: 7000 MHz / 40 MHz
- Inicio aproximado de pérdida del Controlador: 2026-09-19 13:34 (-05:00)
- Recuperación de adquisición/control: 2026-09-20 ~09:19 (-05:00)
- Clasificación: POWER_OUTAGE_CU01 / CONTROL_NODE_OUTAGE

## Naturaleza del incidente

El evento no se clasifica como una caída del radioenlace de 6 GHz. La infraestructura RF permaneció operativa mientras la laptop Controlador quedó apagada.

La laptop puede permanecer temporalmente activa con su batería ante una interrupción eléctrica, pero si se apaga completamente no vuelve a encender automáticamente al retornar la energía. La recuperación requiere intervención humana presencial en CU01.

SJ01 utiliza una Raspberry Pi y mantuvo su adquisición local. Su arquitectura permite además reinicio automático cuando retorna la alimentación después de una pérdida total de energía.

## Evidencia de continuidad y discontinuidad

La inspección posterior a la recuperación mostró una discontinuidad prolongada en los registros centralizados de CU01, consistente con el apagado del Controlador.

Después del retorno:
- weather_local CU01 volvió a registrar observaciones.
- radio_link_local volvió a registrar telemetría RF.
- active_throughput_6g reanudó las pruebas programadas.
- master_observations_multistation volvió a reconstruirse.
- SJ01 aportó observaciones correspondientes al intervalo en el que Controlador estuvo fuera de servicio, evidenciando continuidad de su adquisición local y posterior sincronización.

Por tanto, la ausencia temporal de registros CU01 no debe interpretarse como evidencia de LINK_DOWN.

## Impacto científico

El intervalo afectado debe tratarse como una interrupción de infraestructura de adquisición/control y no como comportamiento RF anómalo.

Los datos válidos obtenidos autónomamente por SJ01 durante el intervalo deben conservarse. Las variables no observables desde CU01 durante el apagado deben permanecer como datos ausentes y no deben interpolarse ni reinterpretarse como fallos del enlace.

El evento forma parte de la trazabilidad experimental del escenario F7000_B40.

## Decisión durante la campaña 3×2

No se realizarán cambios de arquitectura, failover, RF, timers ni orquestación durante la campaña actual como respuesta a este incidente.

Se prioriza mantener constante la plataforma experimental y evitar introducir una nueva variable instrumental durante la campaña.

## Mejora posterior a campaña

Después de finalizar la campaña 3×2 se evaluará reemplazar la laptop Controlador de CU01 por una Raspberry Pi u otro SBC apto para operación autónoma 24/7.

Requisito de diseño propuesto: ante pérdida total y posterior recuperación de energía, cada nodo de campo debe recuperar automáticamente adquisición, almacenamiento local, sincronización y supervisión sin intervención humana.

También se evaluará una arquitectura de redundancia/store-and-forward entre CU01 y SJ01, manteniendo procedencia explícita de cada observación y evitando que dos nodos puedan ejecutar simultáneamente cambios RF.

## Estado posterior

Tras el encendido de Controlador el 20 de septiembre, los servicios de adquisición y campaña reanudaron su operación, la telemetría RF volvió a registrarse y el escenario F7000_B40 permaneció aplicado.

Este documento registra el incidente sin modificar datos experimentales ni la configuración operacional de la campaña.
