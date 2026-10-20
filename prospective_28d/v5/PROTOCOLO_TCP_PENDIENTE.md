# TCP — configuración preparada, pendiente de aprobación

`tcp_protocol.pending.json` conserva dos perfiles para comparar: 8 s/omit 1 s y
15 s/omit 2 s, un flujo, TCP y DL/UL secuenciales. **Ninguno está seleccionado**;
la cadencia y el minuto de ejecución siguen sin fijarse. Las verificaciones de
reloj/ruta permanecen falsas y no existe llamada a iperf en este ejecutor.

Antes de aprobar un perfil deben definirse y documentarse:

| Elemento | Requisito de congelación |
|---|---|
| Ruta y dirección | Cliente, servidor, extremos y uso de reverse; verificar qué tráfico corresponde a DL y UL |
| Motor de medición | Versión iperf, parámetros efectivos, sistema operativo, control de congestión y unidades |
| Comparabilidad 8/1 frente a 15/2 | Ensayo supervisado después del cierre, orden balanceado, condiciones equivalentes y número de repeticiones predefinido |
| Separación temporal | Espera entre pruebas, cadencia y carga concurrente aceptadas; evitar solapamiento con otros ensayos |
| Estimando | Métrica de throughput, dirección principal, regla de resumen e incertidumbre por segmento/ciclo |
| Fallos y QC | Reglas para retransmisiones, interrupciones, reinicios, rutas distintas, pérdidas y datos faltantes |
| Aprobación | Versión, fecha, evidencia y responsables antes de medir la fase prospectiva |

No sumar mecánicamente duration+omit para deducir el intervalo real de una prueba.
Registrar inicio/fin efectivos del proceso y los intervalos reportados por la
versión iperf validada; excluir una prueba completa si cruza un límite válido.
No mezclar directamente los históricos 8/1 y 15/2 como si fueran el mismo protocolo.

El clasificador V5 puede evaluar la ventana temporal de un intervalo ficticio,
pero siempre devuelve `study_eligible=false`: no ejecuta throughput, no aprueba
TCP y no certifica datos de campo. Su salida `temporal_eligible=true` significa
solo que el ejemplo de laboratorio cumple tiempos, QC indicado y objetivo RF.
Una futura versión debe además contrastar los parámetros TCP reales, la ruta,
la sincronización y el QC sostenido de la medición.
