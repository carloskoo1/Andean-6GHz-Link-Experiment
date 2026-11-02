# Control operativo: 2 de noviembre de 2026, 13:37 America/Lima

La campaña está en MONITORING, P01_S02, 7000/20. Transición de mediodía
verificada a las 12:01:21; primera pareja del segmento a las 12:45.
Hasta 13:30 hay 48 DL y 48 UL, todos OK, y 96 verificaciones RF asociadas.
No hay HALT ni PENDING; hashes congelados intactos, reloj sincronizado,
365 GB libres y 6.5 GiB de memoria disponible. Sin reinicio del controlador
desde el 20 de septiembre. Ambas estaciones siguen enviando datos válidos.

Incidencia de adquisición a las 10:00: una consulta no devolvió variables
obligatorias. Se perdió la pareja programada y no se reintentó fuera de turno,
conforme al protocolo. La siguiente pareja terminó correctamente a las
10:15. Primer segmento: 44 DL OK de 48 oportunidades nominales, en 12 horas
civiles; 44 de las 45 oportunidades posteriores a estabilización. Supera
los criterios de cobertura 36 DL y 9 horas. No se alteraron las mediciones.

El respaldo nocturno había fallado por rateLimitExceeded. La recuperación
posterior terminó correctamente: copia backup_CU01_20261102_125024.zip,
255313169 bytes, verificada en ambos destinos Google Drive (primary y UNC),
con finalización a las 13:35:57. El estado failed del servicio nocturno es
histórico y no implica que siga faltando la copia dual.

Se conserva el emparejamiento climático retrospectivo separado; los deltas
disponibles al adquirir no deben confundirse con el emparejamiento final.
Esta inspección no cambia RF, servicios, temporizadores ni bases de datos.
