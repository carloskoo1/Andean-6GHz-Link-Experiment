# Emparejamiento climático retrospectivo: primer tramo prospectivo

Corte de datos: 2 de noviembre de 2026, 08:41:25, America/Lima.
Incluye 64 pruebas TCP (32 DL y 32 UL), de 00:45 a 08:30, del primer
segmento 6655/40. No representa la cobertura final de toda la campaña.

| Estación | Original a ≤120 s | Retrospectivo a ≤120 s | Recuperados | Separación máxima final |
| --- | ---: | ---: | ---: | ---: |
| CU01 | 64/64 | 64/64 | 0 | 42 s |
| SJ01 | 36/64 | 64/64 | 28 | 47 s |

Las 64 observaciones seleccionadas de cada estación tienen bme_ok=1,
rain_ok=1 y wind_ok=1. Son indicadores de adquisición; no constituyen
una nueva validación de la calibración. No quedaron emparejamientos sin
resolver en este corte. Ambas series se extendían al menos 120 segundos
más allá de cada prueba, evitando declarar definitivos los casos del borde
más reciente.

## Procedimiento reproducible
Consulta SQLite de sólo lectura, dentro de una transacción consistente,
limitada a la campaña LUISITA_PROSPECTIVE_28D_20261102 y los registros
meteorológicos locales CU01 y SJ01. Se usa el inicio UTC de cada dirección
TCP, no el momento de recepción/sincronización. Se selecciona la observación
de menor distancia absoluta; empate: observación anterior, luego menor ID.
Se conserva el umbral de 120 segundos, sin interpolar ni imputar valores.
Los identificadores de origen, timestamps, indicadores de calidad y valores
meteorológicos quedan en snapshot.json. pairing.json conserva lado a lado
el emparejamiento original y el retrospectivo, incluida la diferencia con
signo (positiva = observación posterior a la prueba).

Se conservaron sin modificación la base de datos, las pruebas TCP, las
lecturas originales, los programas de adquisición y sus hashes congelados.
Este procedimiento es análisis posterior y no cambia la ejecución en campo.

## Interpretación y límites
Se recuperan 28 emparejamientos de SJ01. En 25 de ellos la
observación escogida ya había sido generada antes de iniciar TCP. Ejemplo:
DL 00:45:08, dato original SJ01 00:42:53 (135 s); dato retrospectivo
SJ01 00:44:53 (15 s). Esto es compatible con disponibilidad tardía por
sincronización en el controlador, no con ausencia de registro climático.
No se dispone aquí de un timestamp individual de inserción para cuantificar
el retraso de sincronización de cada observación.

El emparejamiento simétrico seleccionó observaciones posteriores al inicio
TCP en 32 casos de CU01 y 16 de SJ01. Es apropiado para el análisis
retrospectivo exploratorio; no debe presentarse como información disponible
en tiempo real ni usarse así para evaluar predicciones. Una evaluación
predictiva requiere un emparejamiento causal separado.

La precipitación rain_1min_mm representa acumulación del intervalo de origen;
la cercanía temporal no transforma ese valor en intensidad instantánea ni
en lluvia medida a lo largo de todo el trayecto. Para contrastar episodios
deben respetarse el soporte temporal y los indicadores de cada variable.
Esta revisión no demuestra una causa meteorológica de las variaciones RF.

## Validación
Cinco pruebas de regresión, normales y optimizadas: OK. Cubren coincidencia
exacta, empate, zona horaria, rechazo de timestamp sin zona, ausencia de
muestras y frontera 120/121 segundos. Reanálisis desde el snapshot produjo
pairing.json idéntico byte por byte. SHA-256 del snapshot:
b31519366e903132e00d186363cb071a0f9609e5196a62438e59fcba1dd796f2.

Reproducción desde la raíz del repositorio:
python3 prospective_28d/analysis_retrospective/reconcile_weather.py --snapshot prospective_28d/analysis_retrospective/audit_20261102_0842/snapshot.json --output /tmp/luisita_weather_replay_UNIQUE

Para un nuevo corte, omitir --snapshot y elegir una carpeta de salida nueva.
No se amplía automáticamente el umbral ni se reescriben resultados previos.
