# Luisita Mendo · Auditoría del primer ciclo prospectivo

Corte científico del 6 de noviembre de 2026 a las 08:16, hora peruana. Campaña LUISITA_PROSPECTIVE_28D_20261102. Calendario field_v3/plan.json verificado del 2 al 30 de noviembre de 2026 a las 00:00, 42 exposiciones de 12 horas y siete reservas de 24 horas. La reserva 7000/20 es de referencia y queda fuera de las réplicas factoriales.

## Cobertura y estado del hito

El primer ciclo terminó en el calendario el 6 de noviembre a las 00:00. Sólo dos de seis configuraciones tuvieron TCP y una cumplió la cobertura predefinida de al menos 36 DL válidos y nueve horas con DL. La revisión de tres exposiciones y la comparación del primer ciclo completo quedan pendientes de evidencia. P02_S01 ya había empezado según el calendario al momento del corte, con cero TCP.

| Ventana | MHz / MHz | DL válido / 48 | UL válido | Horas con DL | Cobertura |
|---|---:|---:|---:|---:|---|
| P01_S01 | 6655 / 40 | 44 | 44 | 12 | Cumple, 44 de 45 oportunidades tras estabilización |
| P01_S02 | 7000 / 20 | 28 | 27 | 8 | Insuficiente, 28 de 45 oportunidades, un UL ERROR |
| P01_S03 | 7000 / 40 | 0 | 0 | 0 | Sin adquisición |
| P01_S04 | 6655 / 20 | 0 | 0 | 0 | Sin adquisición |
| P01_S05 | 6475 / 40 | 0 | 0 | 0 | Sin adquisición |
| P01_S06 | 6475 / 20 | 0 | 0 | 0 | Sin adquisición |
| P01_RESERVE | 7000 / 20 | 0 | 0 | 0 | Sin adquisición |

La base contiene 144 registros TCP de la campaña exacta, 143 válidos. Se excluyeron los pilotos y los intentos previos sin TCP. Se registraron 90 oportunidades y 72 eventos de fin de medición, que incluyen el par con UL fallido. No se imputaron ceros. Sobre las 48 oportunidades nominales por exposición, S01 supera 50 %, 75 % y 90 %. S02 supera sólo 50 %. S01 perdió la oportunidad de las 10:00 por ausencia de variables obligatorias.

## Estado operativo

El último TCP se registró el 2 de noviembre a las 19:30. A partir de las 19:45 se registraron fallos SSH, alertas de potencia/ganancia y discrepancias de identidad RF. Al inicio de P01_S03 hubo diez errores de inaccesibilidad del extremo remoto, desde las 00:00 hasta las 00:09 del 3 de noviembre. A las 00:10 se produjo MISSED_WINDOW_HALT. HALT identifica P01_S03 y el inicio perdido por más de 600 s. STATUS continúa en HALTED, state conserva P01_S02 con última oportunidad a las 23:45 y PENDING está ausente. Los registros no aíslan la causa de la pérdida de acceso.

El arranque que devuelve uptime -s es del 20 de septiembre de 2026. En la telemetría asociada a TCP elegible los contadores AP permanecieron en 76 reinicios (72 duros, cuatro suaves) y los del SM en 13 (ocho duros, cinco suaves), con WDT en cero en ambos. Esto cubre las muestras observadas. Durante los huecos no se puede verificar la continuidad de los radios. Una alerta de potencia o identidad no prueba un reinicio.

## Comparación descriptiva de las dos exposiciones

Medianas por exposición de TCP válido y de la RF direccional asociada (ventana de hasta 300 s). La elegibilidad exige una verificación viva única por test_id y direction, coincidencia del AP y SM con el objetivo y estado asociado del SM. Los 144 registros TCP tuvieron verificación viva coincidente, incluido el UL fallido. En estas filas el dashboard bruto del SM coincidió con la verificación viva. Las cadenas rssi_c0p, rssi_c0e, rssi_c1p y rssi_c1e están vacías en los 2 840 registros de radio_link_local del 2 de noviembre, por lo que sólo se comparan métricas agregadas por dirección.

| Ventana y franja observada | TCP DL / UL (Mb/s) | RSSI DL / UL (dBm) | SNR DL / UL (dB) | Potencia AP / SM (dBm) |
|---|---:|---:|---:|---:|
| S01, 00:45–11:45 | 64,51 / 21,63 | −78 / −82 | 21 / 19 | 10 / 3 |
| S02, 12:45–19:30 | 44,14 / 31,85 | −74 / −81 | 23 / 18 | 10 / 3 |

Las franjas, frecuencias y anchos difieren dentro del mismo ciclo. El resumen mezcla horas de comportamiento distinto y S02 perdió el resto de la noche. Por ejemplo, entre las 13:00 y las 16:59 sus medianas horarias DL variaron entre 43,75 y 65,31 Mb/s. Entre las 17:00 y las 19:30 quedaron en 14,51–14,72 Mb/s y las UL en 7,14–9,43 Mb/s, con RSSI DL de −82,5 a −82 dBm. Hay menos observaciones en la última hora.

## Emparejamiento meteorológico retrospectivo

| Estación | Original ≤120 s | Retrospectivo ≤120 s | Recuperadas | Posteriores al inicio TCP |
|---|---:|---:|---:|---:|
| CU01 | 142/144 | 142/144 | 0 | 53 |
| SJ01 | 80/144 | 144/144 | 64 | 34 |

Todas las parejas dentro del umbral tienen bme_ok, rain_ok y wind_ok en 1. CU01 queda sin pareja válida para el DL y el UL de las 13:45 de S02 (197 y 181 s). En los 143 TCP elegibles, CU01 emparejó 141 y SJ01 los 143. Las marcas de tiempo, diferencias con signo, identificadores de origen, calidad y valores se conservan en weather/pairing.json y weather/snapshot.json. Las observaciones posteriores se usan sólo en este análisis retrospectivo.

| Ventana | CU01, mediana T / HR / viento | SJ01, mediana T / HR / viento | Máx. lluvia móvil 1 h CU01 / SJ01 |
|---|---|---|---|
| S01 | 17,06 °C / 72,78 % / 0,00 m/s | 7,72 °C / 100 % / 0,90 m/s | 0,00 / 0,56 mm |
| S02 | 22,57 °C / 59,40 % / 0,50 m/s | 8,93 °C / 100 % / 2,75 m/s | 0,00 / 4,19 mm |

Resúmenes sobre observaciones meteorológicas únicas emparejadas a pruebas válidas. En S02 hubo dos muestras únicas de SJ01 con acumulación positiva en el intervalo de origen de rain_1min_mm, máximo 0,28 mm. Entre las 17:00 y las 19:30, SJ01 reportó 100 % de humedad relativa en las parejas, lluvia móvil de una hora de 0 a 3,07 mm y acumulación de un minuto igual a cero. La acumulación del intervalo de origen no mide intensidad instantánea ni la precipitación en toda la trayectoria.

## Contraste exploratorio con la campaña original

En 7000/20, el descenso conjunto de TCP y RSSI DL recuerda las horas de los segmentos originales 6 (2 de octubre, 23:00) y 16 (21 de octubre, 22:00), que registraron aproximadamente 21 Mb/s DL, 9–10 Mb/s UL y RSSI DL de −82 dBm. Coinciden la configuración y el patrón descriptivo, con horas distintas, cobertura desigual y condiciones de lluvia móvil que pueden diferir. El episodio del 2 de noviembre se observó dentro de un único ciclo incompleto. La evidencia no estima efectos de frecuencia/ancho, no establece una asociación meteorológica repetida y no identifica una causa. Se conserva el segmento 16 en la tesis y el contraste queda como exploratorio, con O5 pendiente.

Fuente histórica: [análisis retrospectivo del segmento 16](../../secondary_diagnostics/INFORME_RETROSPECTIVO_20261027.md).

## Reproducción

Desde la raíz, con Python 3.12 en el Controlador:

```bash
D=prospective_28d/operational_audits/20261106_cycle1
PYTHONDONTWRITEBYTECODE=1 python3 prospective_28d/analysis_retrospective/reconcile_weather.py \
  --snapshot "$D/weather/snapshot.json" --output /tmp/luisita_replay_UNICO
cmp "$D/weather/pairing.json" /tmp/luisita_replay_UNICO/pairing.json
PYTHONDONTWRITEBYTECODE=1 python3 "$D/compare.py" "$D/weather" > /tmp/luisita_evidence.json
```

El emparejamiento se reproduce desde su snapshot; compare.py consulta SQLite en modo sólo lectura y vuelve a leer el estado operativo, por lo que STATUS y el arranque del host pueden cambiar. Los eventos se limitan al corte del snapshot. Para un nuevo emparejamiento se omite --snapshot y se elige una carpeta nueva. Los archivos publicables contienen observaciones científicas y campos operativos seleccionados, sin JSON bruto de equipos ni mensajes con direcciones de gestión. Se conservaron los originales.
