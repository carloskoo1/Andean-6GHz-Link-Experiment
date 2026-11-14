# Luisita · Cierre operativo del segundo ciclo prospectivo

Corte del 14 de noviembre de 2026 a las 10:01 (America/Lima). Intento `LUISITA_PROSPECTIVE_28D_20261107`, plan `field_v4` según la bitácora de vigilancia. Las cifras de este informe proceden de los cortes de vigilancia del Controlador.

## Cobertura para O5

| Ventana o conjunto | Resultado observado |
|---|---|
| Ciclo 1 del intento activo | 5 exposiciones cerradas elegibles. `P01_S04` quedó excluida con cero pruebas. |
| Ciclo 2 | 6 exposiciones cerradas elegibles. Cinco registraron 45 de 45 pares TCP válidos tras la estabilización y `P02_S03` registró 44 de 45. |
| `P02_S06` | Cerró el 14 de noviembre a las 00:00, con 45 de 45 pares TCP válidos y descargas en 12 horas civiles, en 6655 MHz / 40 MHz. |
| Acumulado del intento activo | **11 exposiciones cerradas elegibles para O5**. |
| `P02_RESERVE` | La transición a 7000 MHz / 20 MHz se verificó a las 00:01:19. Al corte había 38 pares válidos. La reserva queda fuera de O5. |

Los umbrales de cobertura reportados son 36 descargas TCP válidas en al menos nueve horas civiles por exposición. La unidad de análisis para O5 es la exposición. Los pares TCP son mediciones dentro de cada exposición. El balance de tres ciclos está previsto para el 19 de noviembre. El tercer ciclo comienza según el calendario operativo el 15 de noviembre a las 00:00.

## Registro de verificación del respaldo

| Campo | Registro |
|---|---|
| Copia local | 14 de noviembre de 2026 a las 07:57 |
| Drive principal | Verificación registrada a las 09:47 |
| Drive UNC | Verificación registrada a las 09:48, tras fallos de carga reportados |
| Inventario efectivo y SHA-256 del paquete | Pendientes de cotejo con el paquete original |
| Calendario congelado y código ejecutado en campo | Pendientes de cotejo y de fijar sus referencias exactas para este intento |

La bitácora de vigilancia sustenta las horas y el resultado operativo de las verificaciones remotas. El inventario esperado para recuperación comprende SQLite, calendario congelado, código del ejecutor, eventos y certificados de recuperación. Para documentar la integridad del contenido se requiere cotejar ese inventario y calcular el SHA-256 del paquete exacto verificado en ambos destinos.

La [auditoría publicada el 6 de noviembre](../20261106_cycle1/REPORT.md) corresponde al intento anterior `LUISITA_PROSPECTIVE_28D_20261102`. Los recuentos de este cierre corresponden exclusivamente al intento iniciado el 7 de noviembre.
