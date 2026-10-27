# Anexo secundario prospectivo: recurrencia de episodios de degradación RF

Versión documental 1 · 27 de octubre de 2026 · Preparada antes de adquirir datos prospectivos. Motivación explícita: episodio observado en segmento 16 y hallazgos retrospectivos, incluidos intervalos similares del segmento 6.

## Alcance y relación con O5

O5 conserva la evaluación de estabilidad temporal de efectos factoriales. Este anexo define un seguimiento secundario de mecanismos candidatos. No modifica las 42 exposiciones, siete ciclos ni el calendario, no añade tratamientos y no autoriza ejecución RF. Los criterios generales de elegibilidad y reservas del protocolo principal prevalecen; deben conciliarse con esta versión antes de la congelación general. El anexo está preparado, no se declara un protocolo operativo definitivamente aprobado.

## Preguntas y predicciones

| Pregunta | Predicción observable | Evidencia que la debilitaría |
|---|---|---|
| ¿Reaparece pérdida RF temporal? | Disminuyen RSSI y SNR junto con tasa reportada y TCP; luego se recuperan sin conmutación | TCP cae con RF y tasas estables |
| ¿Es sensible a configuración? | Deterioro reproducible de una configuración respecto de su referencia horaria y en varios ciclos | Episodios distribuidos sin patrón consistente por configuración |
| ¿Concurre con condiciones meteorológicas? | Recurrencia temporal con condiciones semejantes, considerando ciclo y hora | Climas semejantes con comportamiento RF opuesto de forma frecuente |
| ¿Hay contribución mecánica de viento? | Coincidencia con ráfagas/dirección y recuperación, repetida en exposiciones | Caídas persistentes en calma y recuperaciones con viento mayor |
| ¿Es un problema TCP? | TCP bajo sin deterioro RF, con evidencia de errores de ruta/servidor o carga local | DL y UL RF se degradan junto con sus throughput |

Las predicciones no identifican por sí mismas causas físicas. Sin inclinómetro, inspección o perfiles atmosféricos no se demostrará movimiento angular, mojado o multitrayectoria directamente.

## Variables y conservación

Conservar por extremo: temperatura, humedad, presión, precipitación acumulada/pulsos, acumulado móvil de una hora, viento, ráfaga y dirección, indicadores de calidad y tiempos de origen y recepción. Conservar RF: configuración efectiva AP/SM, potencia, RSSI/SNR DL y UL, MCS y tasas reportadas, contadores de reinicio, uptime, Ethernet, estado de asociación y errores. Conservar TCP 8/1 de un flujo y todos sus errores. Las columnas de cadena se clasificarán como no disponibles hasta comprobar soporte real; nunca se rellenarán con ceros.

Antes de iniciar, comprobar mediante lectura pasiva del colector y pruebas aisladas si el firmware permite obtener las cadenas sin cambios RF. Cualquier ampliación de adquisición se versionará y validará aparte; este anexo no afirma que ya esté implementada. No cambiar el calendario a partir del tiempo meteorológico esperado.

## Análisis definido para el seguimiento

1. Analizar todas las exposiciones elegibles del protocolo principal, conservando errores y faltantes. No abrir/cerrar ventanas según favorabilidad de resultados. Mantener separados transición, reserva y exposición confirmada.
2. Construir resúmenes por hora civil de Perú para visualización. Conservar número de observaciones y cobertura. Los ceros de RSSI no se aceptan como potencia; los ceros de lluvia/viento se conservan conforme a sus banderas instrumentales. No imputar throughput cero a pruebas fallidas.
3. Emparejar RF–TCP a una distancia absoluta máxima de 300 s, reportando la separación; evaluar sensibilidad ≤120 s. Para el seguimiento meteorológico secundario usar el registro más cercano de cada extremo a ≤120 s, con bandera válida; reportar faltantes sin alterar la elegibilidad principal O5.
4. Usar como resultados continuos secundarios RSSI/SNR DL y UL y throughput TCP DL/UL. Para inspección temporal calcular desviaciones respecto de la mediana horaria de la campaña original para la misma configuración. Esa referencia incluye las exposiciones elegibles originales, incluido el segmento 16; congelar su tabla y hash una vez finalizada la elegibilidad principal. No sustituirla después de observar resultados prospectivos.
5. Comparar patrones por configuración, ciclo y hora. Si se realiza inferencia, el nivel de repetición es la exposición de 12 horas y el ciclo, no cada medición. El análisis secundario no sumará observaciones como réplicas independientes. La incertidumbre deberá respetar dependencia temporal; con pocos episodios la conclusión será descriptiva.
6. Aplicar la búsqueda secundaria de análogos con las ocho covariables y escalas documentadas en el informe retrospectivo, ±1 hora civil y sin seleccionar por resultados RF/TCP. Conservar todos los vecinos y sus distancias; distinguir misma configuración de configuraciones distintas. Usar distancia ≤0,5 solo como sensibilidad exploratoria, sin interpretarla como equivalencia meteorológica. La escasez de análogos también se reportará.
7. Presentar perfiles día 06–18/noche 18–06 y series completas, sin limitarse a estas franjas. Marcar recuperaciones observadas sin afirmar continuidad en los huecos. Los episodios identificados visualmente serán exploratorios; no se introducen umbrales confirmatorios de evento después de ver los nuevos datos.
8. Mantener separados resultados de O5 y hallazgos secundarios. No afirmar equivalencia entre campañas sin margen justificado. Si no reaparece el patrón, concluir ausencia de reproducción durante las exposiciones observadas, no inexistencia del fenómeno.

## Cierre documental antes de la adquisición

Integrar este anexo con la versión final O5; registrar fecha, versión, hash, referencia horaria y configuración del colector. Documentar cualquier desviación posterior con motivo y fecha. No reabrir la conservación del segmento 16 ni modificar el calendario para favorecer una explicación.
