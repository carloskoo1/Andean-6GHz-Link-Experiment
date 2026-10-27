# Justificación metodológica del orden prospectivo — propuesta no autorizada

**Fecha de diseño:** 27/10/2026, antes de obtener datos de la fase prospectiva. **Propósito:** minimizar el sesgo de horario y asegurar réplica temporal interna; no seleccionar una secuencia según resultados esperados.

- El diseño contiene seis combinaciones de 3 frecuencias × 2 anchos; siete ciclos de cuatro días; seis exposiciones de 12 h y 24 h de reserva por ciclo (42 exposiciones, 28 días).
- Cada combinación aparece exactamente una vez por ciclo (7 aplicaciones por combinación).
- Cada combinación aparece 3 o 4 veces en las ventanas 00–12 y 3 o 4 veces en las ventanas 12–00. El equilibrio perfecto 3,5/3,5 es imposible con siete réplicas.
- Orden candidato generado mediante búsqueda pseudoaleatoria reproducible con semilla 20261027, sujeto a equilibrio 3/4 y penalización de acumulación por posición. No implica que el experimento esté todavía aleatorizado en sentido estricto ni validado contra todas las condiciones operativas.
- Las exposiciones se distribuyen en diferentes días y horarios; el modelo incluirá ciclo y franja horaria como fuentes de variación, con evaluación de dependencia temporal.
- El análisis estará centrado en diferencias y patrones de estabilidad de los efectos entre campaña original y fase prospectiva. Se definirán antes de medir reglas de eligibilidad, intervalos, umbral sustantivo para concordancia y análisis de sensibilidad. Los 42 segmentos no se agregan ingenuamente a los 18 iniciales.
- Fecha real de inicio pendiente de seguridad, 48 horas de estabilidad, inspección física y pruebas de control. Horarios sujetos a aprobación y congelación con hash; modificar el plan después exige enmienda fechada y conservar ambas versiones.

**Respuesta ante jurado:** «El orden fue definido antes de la recolección de la segunda fase mediante una búsqueda reproducible y restricciones de equilibrio. Aseguramos siete reaplicaciones por configuración y aproximamos el equilibrio entre franjas horarias (3/4), conservando reserva para contingencias. No fue elegido para obtener un valor p favorable. Documentamos el algoritmo, la semilla, la matriz calendario, las limitaciones temporales y las enmiendas». 

**Advertencia:** Aún debe verificarse balance por día de semana, dependencia de transiciones, interferencias y capacidad operativa de sostener cambios cada 12 horas. Este texto no demuestra esas condiciones ni constituye autorización.
