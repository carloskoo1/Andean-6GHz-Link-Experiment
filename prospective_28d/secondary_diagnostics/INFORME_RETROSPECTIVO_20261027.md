# Análisis retrospectivo del segmento 16 y seguimiento prospectivo

Luisita Mendo · 27 de octubre de 2026 · Exploración secundaria motivada por un hallazgo observado.

## Resultado principal

El patrón de pérdida de señal y rendimiento reducido no es exclusivo del segmento 16. En la primera aplicación de 7000/20, el 2 de octubre por la noche, se encontraron horas con TCP DL cercano a 21 Mb/s, RSSI DL de −82 a −83 dBm y UL también reducido. La mediana global alta de esa aplicación ocultaba esos intervalos. El segmento 16 se distingue por la persistencia del deterioro nocturno, además de la inestabilidad documentada durante la mañana del 21.

Este hallazgo corrige el alcance del diagnóstico previo: no corresponde describir el episodio como una anomalía totalmente nueva y exclusiva del 21–22. La recurrencia bajo la misma configuración es compatible con un proceso temporal de desvanecimiento, pero no demuestra su mecanismo ni independencia respecto de la frecuencia o del ancho.

## Comparación de las tres aplicaciones

Cada celda es la mediana de las medianas horarias disponibles. No debe confundirse con la mediana de todas las pruebas TCP del segmento, ni con una estimación confirmatoria. Día y noche son franjas exploratorias fijas 06:00–18:00 y 18:00–06:00, hora peruana.

| Segmento | Franja | TCP DL Mb/s | TCP UL Mb/s | RSSI DL dBm | RSSI UL dBm |
|---|---|---:|---:|---:|---:|
| 6 | Día 06–18 | 61.70 | 32.11 | -74.00 | -81.00 |
| 6 | Noche 18–06 | 64.88 | 32.11 | -73.00 | -80.00 |
| 12 | Día 06–18 | 47.85 | 31.98 | -74.00 | -81.00 |
| 12 | Noche 18–06 | 65.93 | 32.05 | -73.75 | -80.00 |
| 16 | Día 06–18 | 43.41 | 29.46 | -75.00 | -81.00 |
| 16 | Noche 18–06 | 21.15 | 9.57 | -82.00 | -84.00 |

Las franjas del segmento 16 tienen cobertura desigual. Las horas con fallos completos no aportan throughput y no se convierten en ceros. Los resúmenes describen observaciones válidas disponibles, no disponibilidad absoluta del servicio. La noche cruza fechas; cada hora se etiqueta por su hora civil, sin asumir jornadas nocturnas completas.

La figura comparativa está incluida en el expediente de análisis entregado al asesor.

## Un episodio anterior especialmente informativo

| Hora local | Segmento | TCP DL | TCP UL | RSSI DL | RSSI UL | RH San José |
|---|---:|---:|---:|---:|---:|---:|
| 2 oct., 23:00–23:59 | 6 | 21,051 | 8,915 | −82 | −84 | 100 % |
| 21 oct., 22:00–22:59 | 16 | 21,140 | 9,568 | −82 | −84 | 100 % |

Ambos intervalos tienen temperatura local y humedad similares en los dos extremos, sin precipitación móvil de una hora registrada en San José. Esto aporta un antecedente del patrón de degradación. También hay horas bajas al inicio del segmento 12, pero coinciden con el inicio de tratamiento y requieren distinguir transición de comportamiento estable.

## El clima local parecido no produce siempre el mismo resultado

| Hora local | Configuración | TCP DL | RSSI DL | Temperatura SJ | RH SJ | Viento SJ |
|---|---|---:|---:|---:|---:|---:|
| 14 oct., 22:00–22:59 | 7000/20 | 66,109 Mb/s | −74 dBm | 7,94 °C | 100 % | 2,40 m/s |
| 21 oct., 21:00–21:59 | 7000/20 | 21,136 Mb/s | −82 dBm | 7,85 °C | 100 % | 2,65 m/s |

Las variables son medianas horarias. Cuñacales también presenta condiciones locales próximas: temperatura 17,70 frente a 17,89 °C, y humedad 70,065 frente a 71,50 %. No se registró lluvia móvil de una hora en esos dos intervalos.

La humedad alta en un punto no basta para explicar la caída. La igualdad del valor 100 % tampoco implica igualdad física de humedad real cuando el sensor alcanza su límite de reporte. Persisten variables no observadas en la trayectoria y mecanismos alternativos: estructura vertical de refractividad, trayectos múltiples, mojado de equipos, interferencia intermitente o interacción entre condiciones ambientales y configuración.

### Selección reproducible de análogos

Se compararon horas con al menos seis registros RF duales, dos pruebas TCP DL 8/1 válidas, 30 observaciones meteorológicas CU01 y 20 SJ01. Los controles debían situarse a ±1 hora civil (distancia circular) y fuera del segmento 16. Se seleccionó el vecino más cercano exclusivamente por ocho covariables: temperatura, humedad, viento y máximo de precipitación móvil de una hora, en ambos extremos. Escalas exploratorias: 3 °C, 10 puntos porcentuales, 2 m/s y 2 mm, respectivamente. La distancia es la raíz de la media de diferencias normalizadas al cuadrado.

Para la misma configuración se obtuvieron 41 pares, con reutilización de controles. En el subconjunto de distancia ≤0,5 quedaron 23 pares y 15 controles distintos: diferencia mediana de RSSI DL de −5 dB y de TCP DL de −17,671 Mb/s (segmento 16 menos control). El umbral y las escalas se eligieron durante la exploración, no son márgenes de equivalencia ni criterios de elegibilidad de la tesis. La reutilización de controles y la autocorrelación impiden tratar esos pares como réplicas independientes. No se calculan p-valores ni se atribuye causalidad.

También se buscaron análogos en configuraciones diferentes y se conservaron sus identificadores. Sus throughput no son comparables directamente como efecto climático porque cambia el tratamiento. Se usan para inspección de recurrencia y para diseñar el seguimiento prospectivo, no para estimar un efecto ambiental común.

## RF, TCP, potencia y reinicios

El deterioro aparece tanto en TCP DL como en UL y coincide con menor señal y SNR de ambas direcciones. Esto contradice una explicación exclusivamente basada en la prueba TCP descendente. Las medianas de potencia permanecen en AP 10 dBm y SM 3 dBm. Los contadores observados en RF dual válida del segmento 16 permanecen en AP 75 reinicios (71 duros y 4 suaves) y SM 13 (8 duros y 5 suaves); WDT=0 en ambos. Ethernet conserva 1000 Mb/s en AP y 100 Mb/s en SM. Los huecos no permiten certificar continuidad absoluta, ni estos valores descartan toda falla instrumental.

Los eventos de cnMaestro previamente conservados documentan 58 STA_DROP con AP KEEP ALIVE RX STUCK el 21, además de pérdidas de gestión del SM. No equivalen a 58 interrupciones independientes ni explican por sí solos la recaída nocturna posterior. Sus SYS_UP no deben traducirse automáticamente en reinicios físicos; sus relojes requieren conciliación formal con el colector.

### Cadenas RF: límite comprobado

En radio_link_local existen columnas rssi_c0p, rssi_c0e, rssi_c1p y rssi_c1e, pero las cuatro están vacías en los 117 694 registros consultados del 15 de septiembre al 26 de octubre, incluidos ambos roles. Los JSON examinados del colector de configuración tampoco aportan las claves de cadena buscadas. Tener columnas definidas no equivale a disponer de mediciones. No se puede ejecutar retrospectivamente una comparación de polarizaciones/cadenas con esta fuente; se documenta el faltante y se propone verificar soporte para medición futura.

## Qué sabemos y qué no

La interpretación de trabajo más coherente es un desvanecimiento RF temporal y recurrente que redujo la capacidad del enlace, con mayor persistencia en el segmento 16. La relación con condiciones ambientales es una hipótesis todavía abierta. Los datos locales no identifican una causa única, ni permiten afirmar que frecuencia/ancho sean ajenos al comportamiento. El seguimiento prospectivo permitirá comprobar recurrencia bajo las seis configuraciones, sin garantizar que se repita el episodio.

## Trazabilidad y fuentes

Consulta SQLite de solo lectura a weather_local.db del Controlador, tablas radio_link_config_telemetry, active_throughput_6g y station_observations; cronograma campaign_schedule.csv. TCP: campaña identificada, estado OK, TCP 8 s/omisión 1 s, un flujo, configuración programada coincidente en ambos radios y telemetría asociada a ≤300 s. RF: estado dual y coincidencia estricta AP/SM; RSSI cero o físicamente sospechoso no se utiliza como potencia. Meteorología: indicadores instrumentales bme_ok, wind_ok y rain_ok. Los pluviometros están calibrados según confirmación del asesor. No se sustituyen registros ni se modifica la base.

Los agregados se generaron con retrospectivo_s16.py; las tablas completas y emparejamientos están en el JSON completo del expediente entregado al asesor (el repositorio conserva RESULTADOS_RESUMIDOS_20261027.json). El archivo contiene agregados descriptivos, no un respaldo forense íntegro. La consulta independiente de radio_link_local confirmó ausencia de cadenas, y la revisión cnMaestro está documentada en el expediente anterior adjunto.

NASA POWER tiene datos locales hasta el 25 de octubre a las 18:00; ERA5-Land consultado llega al 9 de octubre a las 23:00. Por tanto, no se ha utilizado ERA5 para atribuir condiciones al 21–22 ni se ha supuesto cobertura que no existe. No se realizaron cambios RF, reinicios ni nuevas pruebas activas.
