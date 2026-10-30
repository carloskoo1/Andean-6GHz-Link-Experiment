Efectos de la frecuencia y del ancho de canal sobre el rendimiento TCP de un radioenlace altoandino de 6 GHz

Evaluación factorial de campo y protocolo de contraste temporal

Resumen

La configuración espectral de un radioenlace puede modificar su rendimiento, pero una comparación operativa también está expuesta a variación temporal, incidentes y diferencias en la adquisición. Se evaluaron tres frecuencias —6475, 6655 y 7000 MHz— y dos anchos de canal —20 y 40 MHz— en un enlace de aproximadamente 12 km entre Cuñacales y San José, Cajamarca, Perú. La campaña original comprendió 18 exposiciones en tres bloques entre el 15 de septiembre y el 27 de octubre de 2026. La selección técnica retrospectiva identificó 3419 pruebas TCP descendentes comparables, resumidas en 17 medianas por segmento. Un modelo factorial ajustado por bloque estimó un contraste marginal de 40 frente a 20 MHz de +21,097 Mb/s, con intervalo de confianza convencional del 95 % de 8,494 a 33,699 Mb/s. El signo positivo se mantuvo en cuatro especificaciones; sin embargo, la prueba global ajustada por multiplicidad dejó de ser significativa al restringir el análisis a los dos bloques completos. La revisión bidireccional RF/TCP identificó degradaciones recurrentes bajo 7000 MHz y 20 MHz. Los registros meteorológicos locales de ambos extremos mostraron coincidencias y divergencias que no permitieron atribuir una causa ambiental única. Se describe una fase prospectiva de 28 días para contrastar temporalmente los efectos mediante nuevas exposiciones. Los resultados originales respaldan diferencias locales de rendimiento y justifican evaluar su estabilidad, sin establecer una configuración universalmente óptima.

Palabras clave: radioenlace altoandino; 6 GHz; ancho de canal; throughput TCP; diseño factorial; meteorología local.

Abstract

Three operating frequencies and two channel widths were evaluated on a 12 km high Andean point-to-point link in Peru. The original campaign comprised 18 exposures in three temporal blocks. Retrospective technical screening retained 3419 comparable downlink TCP tests and 17 segment-level medians. A block-adjusted factorial model estimated an average 40 versus 20 MHz contrast of +21.097 Mb/s, with a conventional 95% confidence interval of 8.494 to 33.699 Mb/s. Its direction persisted across four specifications, whereas multiplicity-adjusted global significance did not persist when only the two complete blocks were analyzed. Concurrent uplink, downlink and RF observations revealed recurrent degradation under the same configuration. Local weather measurements at both endpoints provided environmental context without identifying a unique physical cause. A 28-day prospective phase is described to assess temporal stability; no prospective outcomes are reported.



1 Introducción

Los radioenlaces punto a punto constituyen una alternativa de transporte en territorios donde la extensión de fibra óptica resulta difícil. La elección de frecuencia y ancho de canal debe considerar tanto los mecanismos de propagación como el rendimiento efectivo del tráfico. Los procedimientos de diseño para sistemas terrestres de línea de vista y los modelos de atenuación por lluvia aportan fundamentos físicos [1], [2], pero no sustituyen una comparación de throughput TCP realizada sobre una instalación operativa.

Una dificultad de esa comparación es que cada configuración ocupa un período distinto. La hora, el ambiente y el estado del enlace pueden cambiar entre exposiciones. Miles de pruebas sucesivas no equivalen a miles de intervenciones independientes: el tratamiento se aplica a un intervalo y las mediciones dentro de él caracterizan su respuesta. La identificación de bloques temporales permite representar parte de esa estructura, aunque no elimina por sí sola la confusión con el calendario ni la dependencia temporal [3], [4].

Este estudio examina un enlace altoandino entre Cuñacales y San José. La pregunta principal es qué diferencias de rendimiento TCP descendente se observan al combinar tres frecuencias y dos anchos de canal, y si esas diferencias se sostienen al reaplicar las configuraciones en otro período. La meteorología local se incorpora para contextualizar variaciones y buscar episodios comparables; no constituye un factor manipulado.

La investigación combina una campaña original cerrada con una segunda fase prospectiva cuyo protocolo y calendario quedaron identificados antes del inicio programado. En este artículo se presentan los resultados originales y los métodos de la segunda fase. La comparación entre fases requiere su cierre y auditoría; no se anticipan resultados de estabilidad temporal.

1.1 Aporte y preguntas de análisis

El aporte empírico consiste en una comparación factorial de seis configuraciones en una instalación real, con una respuesta por exposición, análisis de sensibilidad y conservación de episodios de bajo rendimiento. Su extensión temporal permitirá examinar si las diferencias originales persisten al cambiar el período de observación. La interpretación integra TCP descendente y ascendente, telemetría RF, incidencias y mediciones meteorológicas en ambos extremos.

Se abordan tres preguntas conectadas. Primero, ¿cuáles son la magnitud y la incertidumbre de los contrastes marginales de frecuencia, ancho e interacción? Segundo, ¿hasta qué punto cambian las conclusiones al considerar cobertura, bloques y agregación? Tercero, ¿qué muestran los perfiles horarios y las condiciones meteorológicas concurrentes sobre la recurrencia de una degradación bajo la misma configuración? La comparación prospectiva añadirá la evaluación de estabilidad y heterogeneidad de esos contrastes.

El alcance es un estudio de campo de un solo trayecto. La repetición temporal mejora la caracterización de esa instalación, pero no constituye replicación espacial. Tampoco se interpreta una ausencia de significación como demostración de igualdad o equivalencia.



2 Materiales y métodos

2.1 Enlace y diseño original

El escenario es una pareja de radios Cambium Force 4600C en un enlace de aproximadamente 12 km entre Cuñacales y San José, Cajamarca. Se aplicaron seis tratamientos: 6475/20, 6475/40, 6655/20, 6655/40, 7000/20 y 7000/40, expresados como frecuencia y ancho en MHz. Las potencias configuradas fueron 10 dBm en el AP y 3 dBm en el SM, con ganancia configurada de 26 dBi en ambos extremos. La ganancia declarada en el equipo no se interpreta como una medición física independiente de la antena.

La campaña original se extendió nominalmente desde el 15 de septiembre hasta el 27 de octubre de 2026. Comprendió tres bloques con seis exposiciones cada uno: tres días por configuración en el primero y dos días en el segundo y tercero. La secuencia temporal registrada se conserva en el repositorio [5]. No se presenta el orden observado como una asignación aleatoria estricta. La unidad de intervención es cada segmento de exposición; los registros RF y TCP son observaciones repetidas dentro de esa unidad.

2.2 Variables y fuentes instrumentales

Tabla 1 Variables y procedencia

Componente | Variables o indicadores | Fuente

Configuración manipulada | Frecuencia y ancho de canal | Confirmación y telemetría AP y SM

Respuesta primaria | Mediana TCP DL por segmento en Mb/s | Pruebas activas de protocolo homogéneo

Caracterización complementaria | TCP UL RSSI SNR tasas y MCS disponibles | Pruebas y telemetría con dirección identificada

Contexto meteorológico observado | Precipitación humedad temperatura viento y ráfagas disponibles | Estaciones locales CU01 y SJ01 por separado

Control de adquisición | Cobertura transiciones fallos y eventos | Bitácoras y registros del colector



Las pruebas activas se ejecutaron con iperf3 [6]. La respuesta principal utiliza un flujo TCP y el perfil identificado como 8/1: duración configurada de 8 s y omisión inicial configurada de 1 s. El régimen 15/2 existente en otra serie se conserva separado. Se distingue el throughput TCP de la tasa de enlace informada por el radio. El estado Ethernet observado del SM a 100 Mb/s también condiciona la interpretación de los valores elevados; no se infiere capacidad PHY a partir de ellos.

La telemetría RF tiene cadencia nominal aproximada de cinco minutos. Los campos de cadenas RF presentes en el esquema no contienen observaciones en los 117 694 registros revisados de la campaña. No se construyen comparaciones por polarización a partir de esas columnas vacías. Los códigos MCS se conservan como categorías nominales.



2.3 Elegibilidad y respuesta por exposición

La selección original se formalizó retrospectivamente el 27 de octubre. Por ello, sus contrastes se interpretan como exploratorios. Se exigieron identificador de campaña, perfil TCP homogéneo, un flujo, estado satisfactorio y ruta verificada. La prueba debía comenzar después de la confirmación efectiva del tratamiento y finalizar dentro del segmento. Se cotejó una lectura RF dual con frecuencia y ancho coincidentes en AP y SM y separación temporal absoluta no mayor de 300 s. Los registros originales, errores y exclusiones se preservaron con sus causas [5].

La respuesta primaria fue la mediana de las pruebas individuales elegibles de cada segmento. El modelo asignó una respuesta y el mismo peso a cada segmento, sin ponderarlo por el número de pruebas. No se impuso retrospectivamente un umbral de cobertura que retirara el segmento 2; su baja cobertura se examinó en sensibilidad. El segmento 16 se conservó en todos los ajustes presentados.

2.4 Modelo y contrastes originales

Se ajustó por mínimos cuadrados un modelo con intercepto, bloque temporal, frecuencia categórica, ancho categórico e interacción frecuencia por ancho. Con 17 respuestas, la matriz de diseño tuvo rango 8 y nueve grados de libertad residuales. Se estimaron cuatro contrastes conjuntos: igualdad de las seis respuestas de tratamiento, frecuencia marginal promediada por igual entre anchos, ancho marginal promediado por igual entre frecuencias e interacción.

La familia de cuatro pruebas F se ajustó mediante el procedimiento de Holm, con α = 0,05 [7]. Los intervalos del 95 % de los contrastes son convencionales y dependen del modelo; no son intervalos simultáneos ni resultados de inferencia por aleatorización. El ajuste por bloque no garantiza independencia residual. Se revisaron normalidad e influencia como diagnósticos descriptivos, sin interpretar una prueba de normalidad no significativa como validación integral del análisis.

Las sensibilidades utilizaron: las 17 medianas; 16 medianas excluyendo únicamente el segmento 2 por cobertura; los 12 segmentos de los bloques completos 2 y 3; y las medias de los 17 segmentos en lugar de medianas. Estas especificaciones permiten distinguir estabilidad de dirección, amplitud de incertidumbre y estabilidad de las decisiones estadísticas.

2.5 Meteorología y perfiles horarios

Las observaciones meteorológicas proceden de las estaciones locales CU01 y SJ01. Se preservan estación, unidad, intervalo, calidad y separación temporal de cada emparejamiento; los registros no se sustituyen por un promedio entre extremos. Los pluviómetros están calibrados según confirmación del responsable de la investigación. Esa condición no demuestra cobertura espacial del trayecto ni elimina la necesidad de auditar contador y faltantes.

Los acumulados diarios de precipitación se reconstruyeron mediante incrementos del contador, sin sumar ventanas móviles superpuestas. Para los perfiles se distinguieron las franjas exploratorias 06:00–18:00 y 18:00–06:00, hora de Perú. Sus valores son medianas de medianas horarias disponibles y no se confunden con la respuesta primaria. La búsqueda retrospectiva de análogos utilizó meteorología en ambos extremos y proximidad horaria de ±1 hora, sin seleccionar los candidatos por su RF o TCP. Sus resultados constituyen exploración, no una prueba causal ambiental.



2.6 Fase prospectiva y comparación temporal

El calendario prospectivo comprende 28 días, desde el 30 de octubre de 2026 a las 12:00 hasta el 27 de noviembre a las 12:00, hora de Perú. Incluye siete ciclos de cuatro días: seis exposiciones nominales de 12 horas y una reserva de 24 horas por ciclo. Cada configuración aparece siete veces, con distribución entre 00:00–12:00 y 12:00–00:00 de tres y cuatro aplicaciones, o viceversa. Este balance parcial no equivale a aleatorización estricta ni controla automáticamente día de semana, arrastre o ambiente [8].

El controlador de campo quedó instalado y habilitado el 30 de octubre a la 01:59. La verificación de instalación registró espera del inicio, sin exposiciones adelantadas. El calendario prevé 42 exposiciones factoriales y siete reservas. La configuración de referencia durante reservas y al cierre es 7000/20; las reservas no se contabilizan como exposiciones factoriales. El registro de instalación no se utiliza como evidencia de ejecución posterior ni de adquisición completa.

El protocolo identifica las confirmaciones de configuración en ambos extremos, los períodos de transición y 30 minutos de estabilización posteriores a la verificación efectiva. El controlador serial programa oportunidades nominales cada 15 minutos y un intento TCP por dirección. Los fallos y las oportunidades no adquiridas se conservan; no se reescriben como resultados favorables ni se compensan silenciosamente. La identidad de la fase separa sus registros del conjunto original [8].

La respuesta primaria prospectiva requiere al menos 36 pruebas DL técnicamente válidas de 48 oportunidades nominales y presencia en nueve horas civiles de la exposición. La cobertura se refiere al calendario nominal e incluye el efecto de las exclusiones de transición y estabilización. Se informarán sensibilidades de 50 %, 75 % y 90 % conforme al protocolo identificado, sin trasladarlas retrospectivamente a la fase original. El emparejamiento secundario conserva los límites de 300 s para RF y 120 s para meteorología.

Cada fase tendrá estimaciones separadas de los mismos contrastes marginales. La comparación examinará signo, magnitud, incertidumbre y heterogeneidad. Las exposiciones originales de dos o tres días y las prospectivas de 12 horas no son ventanas intercambiables: la duración, composición horaria y cobertura deben acompañar cualquier diferencia entre fases. La coincidencia de signos o el solapamiento de intervalos no demostrarán equivalencia.

Antes de calcular intervalos de diferencias entre fases deberá verificarse la correspondencia exacta con el plan analítico versionado y declararse cómo se maneja la covarianza. Dos períodos del mismo enlace no son automáticamente independientes. Cualquier precisión adicional no contemplada en el plan se fechará y diferenciará de las decisiones definidas antes de observar los resultados correspondientes. El estudio no fija retrospectivamente un margen de equivalencia ni modifica el calendario para favorecer una conclusión.

El seguimiento ambiental buscará recurrencias y condiciones discordantes antes, durante y después de las degradaciones, conservando los períodos sin deterioro. NASA POWER y ERA5-Land se identificarán separadamente como fuentes complementarias si se incorporan; no reemplazan la meteorología local ni aportan por sí solas una medición del trayecto. En los resultados originales aquí presentados no se utiliza ERA5-Land para explicar los días 21 y 22 de octubre.



3 Resultados de la campaña original

3.1 Cobertura y rendimiento por segmento

La selección reunió 3419 pruebas DL comparables en 17 segmentos. S1 no aportó respuesta del régimen principal, aunque conserva RF y 48 pruebas DL y 48 UL del perfil 15/2 en otra serie. S2 aportó 32 pruebas distribuidas en nueve horas civiles de 72 nominales. La tabla 2 conserva todas las exposiciones y hace visibles esas diferencias.

Tabla 2 Exposiciones y respuesta principal

Seg. | Bloque | F y ancho MHz | n DL | Mediana Mb/s | Horas con DL

1 | 1 | 6655/20 | 0 | — | 0/72

2 | 1 | 7000/40 | 32 | 89,842 | 9/72

3 | 1 | 6475/20 | 284 | 31,748 | 72/72

4 | 1 | 6655/40 | 287 | 88,987 | 72/72

5 | 1 | 6475/40 | 283 | 43,173 | 72/72

6 | 1 | 7000/20 | 286 | 63,876 | 72/72

7 | 2 | 7000/40 | 191 | 81,467 | 48/48

8 | 2 | 6655/40 | 187 | 89,245 | 48/48

9 | 2 | 6655/20 | 191 | 66,186 | 48/48

10 | 2 | 6475/40 | 189 | 43,280 | 48/48

11 | 2 | 6475/20 | 189 | 31,781 | 48/48

12 | 2 | 7000/20 | 187 | 62,788 | 48/48

13 | 3 | 6475/40 | 191 | 49,339 | 48/48

14 | 3 | 6655/20 | 191 | 66,307 | 48/48

15 | 3 | 6655/40 | 191 | 89,225 | 48/48

16 | 3 | 7000/20 | 161 | 21,426 | 43/48

17 | 3 | 6475/20 | 191 | 33,668 | 48/48

18 | 3 | 7000/40 | 188 | 66,039 | 48/48



Las horas con alguna prueba no equivalen a servicio continuo ni a disponibilidad RF. S16 registró 161 pruebas DL y una mediana de 21,426 Mb/s. La aplicación más estricta de confirmación y emparejamiento dejó 188 pruebas en S18, con mediana 66,039 Mb/s. Los cambios frente a cortes históricos se deben a reglas explícitas de selección y no a modificación de los datos originales [5].

3.2 Caracterización bidireccional

En S16 las medianas fueron TCP UL de 9,572 Mb/s, RSSI DL/UL de −80/−83 dBm y SNR DL/UL de 17/15 dB. La tasa DL reportada asociada a sus pruebas fue de 51 Mb/s, frente a 103 Mb/s en S6 y S12. La coincidencia de deterioro en RF y ambas direcciones TCP respalda examinar el estado del enlace; no identifica una causa física única.



3.3 Contrastes factoriales e incertidumbre

Tabla 3 Pruebas factoriales del ajuste principal

Contraste | gl num./den. | F | p nominal | p Holm

Global tratamientos | 5/9 | 11,116 | 0,00122 | 0,00365

Frecuencia marginal | 2/9 | 17,396 | 0,00081 | 0,00324

Ancho marginal | 1/9 | 14,340 | 0,00430 | 0,00861

Frecuencia × ancho | 2/9 | 0,844 | 0,46153 | 0,46153



El contraste marginal de 40 frente a 20 MHz fue +21,097 Mb/s, con IC del 95 % de 8,494 a 33,699 Mb/s. Los contrastes marginales de frecuencia fueron +39,984 Mb/s para 6655 frente a 6475 MHz y +25,408 Mb/s para 7000 frente a 6475 MHz, con intervalos respectivos de 24,203 a 55,766 y 10,692 a 40,125 Mb/s. Estos promedios asignan el mismo peso a los niveles del otro factor.

El modelo principal presentó diferencias globales, de frecuencia y de ancho con p ajustadas inferiores a 0,05. La interacción tuvo p ajustada de 0,46153. Esa ausencia de rechazo no demuestra que la interacción sea nula; el número de exposiciones y la variabilidad limitan la precisión. Los intervalos individuales informados no están ajustados simultáneamente.

3.4 Sensibilidad e influencia

Tabla 4 Sensibilidad del contraste marginal de ancho

Especificación | n | 40−20 Mb/s | IC 95 % convencional | p Holm global

17 segmentos con mediana | 17 | 21,097 | 8,494 a 33,699 | 0,00365

16 segmentos sin S2 | 16 | 20,054 | 6,479 a 33,628 | 0,01016

12 segmentos B2 y B3 | 12 | 22,740 | 4,007 a 41,473 | 0,08488

17 segmentos con media | 17 | 19,777 | 10,809 a 28,744 | 0,00169



El contraste de ancho mantuvo signo positivo en las cuatro especificaciones, entre +19,777 y +22,740 Mb/s. Sin embargo, en los bloques completos 2 y 3 la prueba global pasó de p nominal 0,03787 a p ajustada 0,08488; frecuencia y ancho también tuvieron p ajustada de 0,08488. La estabilidad de dirección y la estabilidad de significación son, por tanto, resultados diferentes. La reducción a 12 exposiciones también amplió la incertidumbre.

En el ajuste principal se obtuvo Shapiro–Wilk W = 0,917 y p = 0,132, distancia de Cook máxima de 0,686 en S16 y apalancamiento máximo de 0,583. Con pocas respuestas, esos diagnósticos no certifican normalidad o independencia. S16 permanece en todos los modelos de la tabla 4: su influencia se informa como parte del comportamiento de campo, sin retirarlo para mejorar el resultado.



3.5 Recurrencia horaria y meteorología local

Tabla 5 Perfiles de las tres aplicaciones de 7000 MHz y 20 MHz

Seg. | Franja Perú | TCP DL Mb/s | TCP UL Mb/s | RSSI DL dBm

6 | 06–18 | 61,701 | 32,113 | -74,0

6 | 18–06 | 64,877 | 32,112 | -73,0

12 | 06–18 | 47,849 | 31,985 | -74,0

12 | 18–06 | 65,926 | 32,046 | -73,8

16 | 06–18 | 43,409 | 29,458 | -75,0

16 | 18–06 | 21,152 | 9,569 | -82,0



Las medianas horarias muestran una degradación nocturna más persistente en S16, pero no exclusiva de él. El 2 de octubre entre las 23:00 y las 23:59, durante S6, se registraron DL de 21,051 Mb/s, UL de 8,915 Mb/s y RSSI DL/UL de −82/−84 dBm. El 21 de octubre entre las 22:00 y las 22:59 se observaron valores próximos: 21,140 y 9,568 Mb/s, con iguales medianas RSSI. Una respuesta global elevada por segmento puede ocultar horas de degradación.

La humedad local elevada no fue una condición suficiente para ese deterioro. El 14 de octubre a las 22:00, con 7000/20 y humedad SJ01 del 100 %, el DL fue de 66,109 Mb/s y el RSSI DL de −74 dBm. El 21 a las 21:00, con humedad igualmente del 100 %, los valores fueron 21,136 Mb/s y −82 dBm. La coincidencia de una variable superficial no identifica el mismo estado de propagación.

El 21 de octubre fue el día de mayor humedad media observada en ambos extremos durante el período revisado, pero no de viento extraordinario. En SJ01 el viento medio fue 1,67 m/s y la ráfaga máxima 7,97 m/s; esta última fue la menor máxima diaria del período. El 22 a la 01:00 ambos sensores registraron viento cero y el DL permaneció alrededor de 21,23 Mb/s. Estos registros debilitan la flexión reversible por viento como explicación completa, sin excluir contribuciones puntuales no capturadas.

En SJ01 los incrementos de precipitación sumaron 11,18 mm el 21, 3,91 mm el 22 y 4,19 mm el 23. Hubo coincidencia entre lluvia y una recaída alrededor de las 18:00 del día 22, pero también bajo rendimiento sin nuevos pulsos y recuperación durante lluvia. CU01 no registró nuevos pulsos durante el intervalo revisado. Los dos puntos distan aproximadamente 12 km: sus diferencias se conservan y no se interpretan como lluvia uniforme sobre el trayecto.

La revisión de cnMaestro identificó 58 registros STA_DROP con motivo AP KEEP ALIVE RX STUCK entre las 01:28 y las 12:18 del 21, además de 16 eventos STATUS_DOWN del SM. Esos registros no equivalen a 74 fallas independientes ni permiten sumar una duración de indisponibilidad RF. Los contadores de reinicio disponibles permanecieron constantes. Se documenta una degradación temporal recurrente cuya causa física no quedó identificada [9].



4 Discusión

4.1 Alcance de la comparación espectral

La campaña original mostró un contraste medio favorable a 40 MHz y diferencias entre frecuencias dentro del enlace estudiado. La consistencia del signo en sensibilidad aporta una observación operativa útil. No obstante, la pérdida de significación ajustada al analizar solo bloques completos obliga a moderar la precisión atribuida al ajuste principal. No puede afirmarse que las seis configuraciones tengan un orden universal ni que el contraste estimado se mantenga fuera del período y la instalación observados.

La selección homogénea evita mezclar protocolos TCP distintos y la agregación por exposición evita contar pruebas sucesivas como réplicas de intervención. Ambas decisiones mejoran la comparabilidad, pero no recuperan una asignación aleatoria no acreditada. La formalización retrospectiva de elegibilidad, el desbalance de cobertura, las pocas exposiciones y la posible confusión temporal permanecen como límites del análisis exploratorio.

4.2 Interpretación del episodio de degradación

La afectación concurrente de RSSI, SNR, tasa reportada y TCP en ambas direcciones orienta la explicación hacia un deterioro del enlace y hace insuficiente una hipótesis restringida al ensayo TCP DL. Aun así, los datos no distinguen de manera concluyente interferencia, multitrayectoria, refractividad, mojado de componentes o efectos mecánicos. La falta de cadenas RF observadas limita una parte de esa discriminación.

Los registros meteorológicos locales permiten evaluar si una explicación concuerda con la secuencia observada y buscar contraejemplos. En esta campaña, humedad del 100 % con buen rendimiento y bajo rendimiento con viento registrado cero impiden usar esas variables, por separado, como explicaciones suficientes. La lluvia tampoco acompañó todas las fases de deterioro y recuperación. Los modelos físicos de propagación requieren variables y resolución adecuadas [1], [2]; un acumulado diario en un extremo no representa directamente la atenuación instantánea integrada sobre el trayecto.

4.3 Valor de la comparación prospectiva

La nueva fase puede aportar evidencia sobre estabilidad temporal aun cuando el episodio no reaparezca. Si los contrastes mantienen magnitud y dirección con incertidumbre compatible, se reforzará su consistencia en esta instalación. Si cambian, la heterogeneidad será un resultado que debe relacionarse con duración de exposición, horario, adquisición y contexto ambiental. La ausencia de nuevas degradaciones no refutará por sí sola una causa propuesta para octubre.

La comparación deberá preservar las diferencias entre fases y evitar una lectura binaria basada solo en valores p. Las reservas a 7000/20 ofrecen observación contextual, pero no añaden réplicas factoriales intercambiables. La repetición sobre el mismo trayecto no permite generalizar a otros radioenlaces ni separar todos los mecanismos físicos. Su utilidad está en precisar bajo qué condiciones se sostienen las diferencias registradas.



5 Conclusiones

En un radioenlace altoandino de aproximadamente 12 km, la campaña original produjo 17 respuestas TCP DL comparables a partir de 3419 pruebas. El modelo exploratorio ajustado por bloque estimó un contraste medio de 40 frente a 20 MHz de +21,097 Mb/s, con IC convencional del 95 % de 8,494 a 33,699 Mb/s. Las sensibilidades conservaron el signo positivo, aunque la significación ajustada no persistió en los bloques completos. El resultado constituye evidencia local condicionada al diseño y al modelo.

La configuración 7000/20 presentó episodios recurrentes de bajo rendimiento acompañados de deterioro RF y TCP bidireccional. S16 concentró una degradación más persistente, pero el episodio no fue exclusivo de ese segmento. Su conservación permite describir variación relevante que un resumen global o una exclusión del período ocultaría.

Las estaciones meteorológicas locales de ambos extremos proporcionaron contexto y contraejemplos, sin demostrar una causa física única. La humedad, la precipitación y el viento no explicaron individualmente toda la secuencia. La fase prospectiva de 28 días permitirá evaluar nuevos contrastes y episodios tras su cierre y auditoría; la estabilidad temporal entre fases permanece pendiente.

Disponibilidad de datos y reproducibilidad

El repositorio Andean 6GHz Link Experiment contiene scripts, resultados derivados y documentación versionada de la campaña original [5], el protocolo de campo [8], el diagnóstico secundario [9] y la revisión metodológica [10]. La huella SHA256 de la proyección analítica original es 6a299d1d05639a81135c3a790d64e5a6620149a7d28730b8eae9787cd7975faa. Esta huella identifica el conjunto derivado documentado, no una copia forense completa de toda la base. La reproducción debe utilizar el corte y las reglas indicados, conservando las diferencias respecto de resúmenes anteriores.

Referencias

[1] ITU-R, “Propagation data and prediction methods required for the design of terrestrial line-of-sight systems,” Recommendation ITU-R P.530-19, Sep. 2025. https://www.itu.int/rec/R-REC-P.530-19-202509-I/en

[2] ITU-R, “Specific attenuation model for rain for use in prediction methods,” Recommendation ITU-R P.838-3, Mar. 2005. https://www.itu.int/rec/R-REC-P.838-3-200503-I/en

[3] NIST/SEMATECH, “Randomized block designs,” e-Handbook of Statistical Methods, sec. 5.3.3.2. https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm

[4] S. H. Hurlbert, “Pseudoreplication and the design of ecological field experiments,” Ecological Monographs, vol. 54, no. 2, pp. 187–211, 1984, doi: 10.2307/1942661.

[5] Andean 6GHz Link Experiment, “Original campaign V7,” código y resultados, 2026, commit 63afe754004b8b30fcde918a70f59ba73c9f505d. https://github.com/carloskoo1/Andean-6GHz-Link-Experiment/tree/63afe754004b8b30fcde918a70f59ba73c9f505d/docs/validation_28d/original_campaign_v7

[6] ESnet, “Invoking iperf3,” iperf3 documentation. https://software.es.net/iperf/invoking.html

[7] R Core Team, “Adjust P-values for Multiple Comparisons,” stats documentation. https://search.r-project.org/R/refmans/stats/html/p.adjust.html

[8] Andean 6GHz Link Experiment, “Prospective field controller and deployment,” 2026, corte da94f8a08490380fae703aacea81676441137992. https://github.com/carloskoo1/Andean-6GHz-Link-Experiment/tree/da94f8a08490380fae703aacea81676441137992/prospective_28d/field_v1

[9] Andean 6GHz Link Experiment, “Secondary diagnostics,” 2026, commit e98f9967d598f58d57171f71a253fc9f32be7289. https://github.com/carloskoo1/Andean-6GHz-Link-Experiment/tree/e98f9967d598f58d57171f71a253fc9f32be7289/prospective_28d/secondary_diagnostics

[10] Andean 6GHz Link Experiment, “Revisión de correspondencia metodológica V8,” Oct. 30, 2026, commit 6f481e3. https://github.com/carloskoo1/Andean-6GHz-Link-Experiment/tree/6f481e3/docs/validation_28d/alineacion_metodologica_v8