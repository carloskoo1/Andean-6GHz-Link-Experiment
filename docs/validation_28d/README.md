# Validación temporal prospectiva de 28 días — protocolo en revisión

**Estado 18/10/2026: BORRADOR NO HABILITADO.** Este documento NO programa ni ejecuta nuevas transiciones y no modifica el orquestador activo.

## Separación de fases

La fase factorial original de Luisita incluye seis tratamientos (6475/6655/7000 MHz × 20/40 MHz), en 18 segmentos distribuidos en tres bloques de 3, 2 y 2 días por combinación. Su inferencia se basa en unidades de intervención y no trata lecturas consecutivas como réplicas independientes.

La **validación adicional de Luisita** se propone separadamente: 28 días calendario, siete ciclos de cuatro días, seis tratamientos de hasta 12 horas por ciclo (máximo 72 horas) y 24 horas de reserva y contingencias. Máximo **42 nuevas aplicaciones**. No mezclar automáticamente estas observaciones con las de la fase original ni con ASDE o campañas TCP posteriores.

La fecha de comienzo, el orden de tratamientos y la asignación de turnos quedan **pendientes de aprobación prospectiva**.

## Variables y medición

- Factores: frecuencia, ancho de canal y su interacción.
- Respuesta principal: throughput TCP activo DL en ruta y protocolo homogéneos, diferente de la tasa de enlace de Cambium.
- Variables RF secundarias: SNR, RSSI, tasa de enlace y categorías MCS interpretadas conforme al equipo y firmware.
- Contexto: hora, lluvia, interferencias e incidentes; no se presentan como factores manipulados.
- Controles RF: AP 10 dBm, SM 3 dBm, ganancias *configuradas* 26/26 dBi; comprobar física de antenas, geometría, polarización, TDD, firmware y Ethernet.

## Condiciones necesarias antes de activar los 28 días

1. **Conciliar 27/28 octubre** con CSV, eventos y telemetría AP/SM y documentar cierre real de fase original.
2. **Retornar a 7000 MHz/20 MHz**, con al menos 48 horas de estabilidad efectiva.
3. **Inspeccionar físicamente** los extremos Cuñacales y San José: alineación, soportes, herrajes, fijaciones, conectores y polarización; documentar intervenciones y seguridad por vientos.
4. **Prevalidar software y medición**: calendario congelado, dry-run, preflight, simulación, piloto supervisado, idempotencia, rollback, relojes sincronizados y pruebas TCP comparables; no desplegar ejecutor sin habilitación técnica.
5. **Preespecificar el análisis**: pregunta P5, objetivo O5, estimandos por fase, intervalos, heterogeneidad, criterios de elegibilidad, concordancia y sensibilidad; inventariar respaldos verificando restauración y SHA-256.

Si falta cualquiera de las condiciones, **NO iniciar nuevas transiciones**. El 29 de octubre es solo una fecha tentativa dependiente del retorno real, inspecciones y autorizaciones.

## Inferencia prospectiva

Ajustar efectos principales e interacción de la fase original por bloque, usando resúmenes por segmento. Analizar la fase adicional por ciclo/segmento, considerando turnos y dependencia temporal. Evaluar dirección, magnitud, incertidumbre y heterogeneidad. Coincidencia de signo o ausencia de una diferencia significativa **no prueban por sí solas concordancia**. No se anticipan resultados.

## Discrepancia ya verificada (18/10/2026)

El calendario ejecutable `campaign_runtime/campaign_schedule.csv` termina F7000_B40 el **27/10 a las 00:00**, hora de Perú. `README.md` y `README_EXECUTOR.md` consignan **28/10 a las 00:00**. No se debe alterar la historia de ejecución para reconciliar fechas; se requiere acta y verificación de cambios reales.

## Confidencialidad

Repositorio público: solo código, protocolos y registros técnicos depurados. No subir dictámenes íntegros, firmas, credenciales, tokens, respaldos completos ni datos sensibles. El expediente con firmas queda bajo custodia académica restringida.
