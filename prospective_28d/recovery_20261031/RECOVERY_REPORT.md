# Recuperación operativa de la prospectiva de Luisita

31 de octubre de 2026, hora de Perú.

## Hallazgo y corrección

El SM habilitaba 20 y 40 MHz mediante máscara 3, pero su lista de búsqueda de 40 MHz estaba vacía y la de 20 MHz contenía 275 frecuencias. Se acotaron ambas listas a 6475, 6655 y 7000 MHz mediante trial, con verificación dual, confirmación y comprobación posterior de persistencia. Se conservaron país, potencia, ganancia y demás controles examinados.

La corrección conjunta eliminó el fallo en las pruebas posteriores. No permite aislar cuánto correspondía a la lista vacía y cuánto al tiempo de búsqueda; no se atribuye al clima el fallo de arranque.

## Validación real y aislada

Se confirmaron sucesivamente 6655/40, 7000/40, 6655/20, 6475/40, 6475/20 y 7000/20, con diez verificaciones duales y de conectividad consecutivas antes y después de cada confirmación. El piloto terminó a las 11:24:02 en la referencia 7000/20. Durante transiciones se observaron estados temporales discordantes, que no se trataron como confirmaciones válidas.

En 6655/40 se adquirió un par TCP de diagnóstico: DL 88,4107 Mb/s y UL 44,0401 Mb/s, perfil 8/1, un flujo y ruta verificada. Los registros llevan LUISITA_RECOVERY_PILOT_20261031 y se excluyen del factorial. El emparejamiento meteorológico SJ01 de ese par tuvo desfases de 136 y 151 s, superiores al límite secundario de 120 s; no se presenta como par ambiental elegible. No se cambió ese umbral. La serie meteorológica local sigue conservándose para su análisis con trazabilidad.

La versión V2 pasó 21 pruebas aisladas tanto en Python normal como optimizado. Cubre todos los intervalos y la referencia final, pérdidas de acuse, reinicio, duplicados, ventanas vencidas, listas SM incompletas, errores de acceso y ruta, y margen de confirmación. No se generaron mediciones reales con las pruebas aisladas.

Se agregó comprobación de las listas SM, diagnóstico por intento relevante y señalización explícita de HALTED. Se usan 180 s de asociación antes de confirmar, sin eliminar verificación dual ni aumentar el límite de confirmación de 210 s. El piloto completo pasó incluso con 150 s. Se preserva el bloqueo ante escrituras ambiguas.

## Calendario y conciliación

El intento del 30/10 conserva cero pruebas TCP prospectivas y se archivó íntegro antes de reconciliar HALT y PENDING. No se contabiliza como un día de campaña. La habilitación que bloquea controladores anteriores se mantuvo de forma continua. Se guardó una copia SQLite consistente antes del relevo, con quick_check satisfactorio y SHA256.

La nueva campaña LUISITA_PROSPECTIVE_28D_20261031 está programada desde el 31/10/2026 a las 12:00 hasta el 28/11/2026 a las 12:00. Se mantiene la secuencia y distribución de franjas, desplazando exactamente un día las 49 ventanas; no se altera la respuesta estadística ni las reglas de elegibilidad. La estabilización de referencia auditada antes del intento original y el piloto de recuperación se identifican como etapas distintas; cada nueva exposición conserva su estabilización analítica de 30 minutos después de la verificación efectiva.

El relevo se realizó a las 11:24:54. El primer tick y el temporizador real a las 11:25 registraron WAITING_START con la campaña nueva. Al corte se verificaron los 19 hashes del manifiesto, sin HALT/PENDING. Esto acredita activación antes de D0; no anticipa el resultado del cambio de mediodía ni las primeras pruebas, previstas alrededor de las 12:45. Se programó una revisión de solo lectura a las 12:50 para comprobarlos e informar al asesor.

## Trazabilidad

SM_SCAN_BEFORE/INTENT/VERIFIED identifican la modificación; PILOT_STARTED/PASSED y events.jsonl conservan la ejecución; failed_runtime_20261030 y original_field_v1 preservan el intento anterior y los archivos previos. La unidad instalada conserva su punto de entrada mediante un despachador hacia field_v2. VALIDATION.json de esa versión reúne los estados al corte y la identidad del respaldo.

Documentación del fabricante consultada: https://www.cambiumnetworks.com/wp-content/uploads/2021/07/ePMP-CLI-User-Guide-v3.4.1.pdf y https://community.cambiumnetworks.com/t/adding-160-mhz-channels-to-existing-4625-subscribers/108286 . Las capacidades concretas y la persistencia se verificaron en el SM con firmware 5.4.
