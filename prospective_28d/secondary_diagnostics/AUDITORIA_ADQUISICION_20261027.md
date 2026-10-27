# Auditoría de adquisición para seguimiento secundario

Corte: 27 de octubre de 2026, 14:27:18, Perú. Ventana exacta de 24 horas hasta ese instante, con timestamps UTC y límites explícitos. Consulta pasiva; base activa, no imagen forense congelada.

| Componente | Evidencia observada en la ventana |
|---|---|
| RF AP/SM | 287 registros duales con frecuencia/ancho coincidentes; RSSI/SNR DL y UL y potencias presentes |
| TCP | 190 intentos OK: 95 DL y 95 UL; 8 s/omisión 1 s, un flujo; ruta verificada y RF asociada a ≤300 s |
| Meteorología CU01 | 1380 registros con temperatura, humedad, presión, viento, dirección, ráfaga, precipitación y pulsos presentes; banderas BME/viento/lluvia válidas |
| Meteorología SJ01 | 943 registros con esas variables presentes y banderas válidas |
| Reloj del Controlador | America/Lima; NTPSynchronized=yes observado mediante timedatectl |
| Relojes de radios | Hora AP inconsistente con la del colector; SM próximo a UTC si se interpreta su reloj como UTC; zona del radio no verificada |
| Cadenas RF | Cuatro columnas sin valores en los 2858 registros de radio_link_local de la ventana |

Estos conteos demuestran presencia y estado reportado; no garantizan cobertura completa, precisión instrumental ni continuidad fuera de las observaciones. Los pluviómetros están calibrados según confirmación del asesor. No interpretar automáticamente ceros válidos como avería.

## Diferencia de relojes

En la adquisición RF 19:22:57 UTC del 27 de octubre (14:22:57 Perú), AP reporta cambiumDateTime=10/28/2026:06:22:56 y SM=10/27/2026:19:22:55. Si se interpretaran como UTC, los offsets serían +39599 s y −2 s, respectivamente. La interpretación UTC es diagnóstica, no una verificación de zona horaria: no presentar +11 h como deriva medida del reloj sin comprobar su configuración.

La reconstrucción utiliza timestamp_utc/local del colector, conserva la hora original del radio y marca su incertidumbre. La misma regla debe acompañar el cotejo con cnMaestro: sus horas aún requieren conciliación. No se cambiaron relojes ni se reinició ningún radio.

## Preparación alcanzada y límites

El seguimiento puede apoyarse en RF, TCP y meteorología ya conservados. Se añadió un auditor reproducible de solo lectura y un anexo secundario enlazado a O5, sin cambiar los ejecutores. Las pruebas del auditor usan bases temporales para verificar zonas horarias, límites de ventana, configuraciones incongruentes, RSSI cero, cadenas vacías y ausencia de modificaciones de la fuente.

No se declara completada la adquisición de cadenas ni aprobado el protocolo operativo prospectivo. Antes de congelar se debe conciliar la versión principal de TCP, elegibilidad y reservas, fijar hashes de referencias y registrar cómo se interpretan los relojes. Ninguno de estos pendientes exige borrar o alterar el segmento 16.
