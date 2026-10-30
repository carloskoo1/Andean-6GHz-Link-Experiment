# Revisión de correspondencia metodológica V8

Corte: 30 de octubre de 2026. Primera actividad prevista para el 30–31 de octubre. Se revisó el manuscrito V7 y se generó una V8 con la misma identidad documental. Esta revisión no modifica datos ni recalcula resultados.

La configuración espectral es la variable independiente conceptual: frecuencia de operación y ancho de canal son los factores manipulados. El desempeño técnico es la variable dependiente conceptual: la respuesta primaria es la mediana TCP DL elegible por segmento. TCP UL y métricas RF disponibles son complementarios. Precipitación, humedad, temperatura y viento son contexto observado para P4/O4, no tratamientos experimentales.

| Correspondencia | Indicador o estimando | Instrumentos | Ubicación de la respuesta |
|---|---|---|---|
| P1–O1 | Contrastes marginales de frecuencia y ancho, e interacción sobre mediana TCP DL | I1–I4 e I7; I6 transversal | 4.1 y sensibilidad en 4.3 |
| P2–O2 | TCP UL; RSSI y SNR DL/UL; tasas disponibles y MCS nominal | I1–I4 e I7; I6 transversal | 4.2 |
| P3–O3 | Cobertura con denominadores, incidentes y sensibilidad | I1–I4 e I7; I6 transversal | 4.3 |
| P4–O4 | Perfiles horarios y coincidencias o divergencias con meteorología local | I2–I5 e I7; I6 transversal | 4.4, exploratorio |
| P5–O5 | Estimaciones por fase, diferencias de contrastes e incertidumbre | I1–I4, I7 e I8; I6 transversal | 3.8.3 y protocolo; resultados pendientes |

## Correcciones aplicadas

1. Se corrigió la contradicción entre el rótulo confirmatorio del análisis original y la selección retrospectiva de registros. El alcance original es exploratorio y se identifica como tal en hipótesis, metodología y matriz de consistencia.
2. H0F y H0B se formularon como hipótesis marginales, promediando con igual peso los niveles del otro factor. No se confunden con coeficientes condicionales de referencia cuando existe interacción. H0G conserva la prueba conjunta de cinco grados de libertad y H0AB, la de dos.
3. Se explicitó la decisión estadística del modelo original con Holm y α=0,05, distinguiéndola de una afirmación causal definitiva. Se conserva la discrepancia de significación con bloques completos.
4. Se mantuvo una sola respuesta principal por segmento. La media es sensibilidad y no una alternativa elegida según su significación. S1 conserva su cohorte 15/2; S2 conserva su cobertura reducida; S16 permanece en todos los modelos existentes.
5. P2/O2 y las matrices identifican TCP UL junto con las métricas RF disponibles, sin prometer estimaciones de campos no adquiridos. MCS permanece nominal; tasa de enlace y throughput son indicadores distintos.
6. P4/O4 e I5 explicitan humedad, temperatura y viento junto con precipitación, como extensión contextual transparente de la exploración ya realizada. Se conservan fuente, estación, unidad, duración de intervalo, calidad y separación temporal. No se añade una hipótesis meteorológica confirmatoria.
7. Se retiró disponibilidad RF como indicador prometido sin medición sustentada. La cobertura de adquisición conserva su denominador y no se equipara a disponibilidad del enlace.
8. P5/O5 e I8 admiten estabilidad, heterogeneidad o inconclusión. No se formula equivalencia sin margen técnico previo. La incertidumbre de la diferencia debe declarar el tratamiento de la covarianza: separar fases no acredita independencia estadística.
9. Se actualizaron las referencias activas a una fase adicional no autorizada. La evidencia de instalación confirma habilitación y WAITING_START; no acredita el inicio de exposiciones ni mediciones futuras. El calendario programado es 30/10/2026 12:00–27/11/2026 12:00, hora de Perú.
10. Se identificaron como históricos los anexos fechados y se preservaron sus originales, dictámenes y formularios sin crear conformidades. La verificación digital y el respaldo no se presentan como inspección física o cierre general de condiciones de expertos.

## Elementos conservados y pendientes

Se preservaron las tablas numéricas originales de selección, contrastes, RF/UL, sensibilidad y perfiles horarios, así como las 16 imágenes incorporadas, incluidas las reproducciones de dictámenes. El Anexo XV registra el alcance y los cambios de esta revisión. Se actualiza la paginación afectada; la auditoría bibliográfica completa permanece como actividad posterior.

La revisión de correspondencia no altera el calendario, el perfil TCP ni las reglas operativas congeladas del controlador. No se incorporan nuevas exposiciones o resultados prospectivos al manuscrito. O5 requiere adquisición y auditoría de la segunda fase.

Evidencia de instalación: commit da94f8a08490380fae703aacea81676441137992, `prospective_28d/field_v1/DEPLOYMENT_20261030.json`. La versión académica con dictámenes se conserva separadamente del repositorio técnico.
