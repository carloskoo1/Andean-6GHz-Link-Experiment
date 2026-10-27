# ANEXO METODOLÓGICO PROPUESTO — FASE PROSPECTIVA O5
Fecha de auditoría: 27/10/2026. Estado: diseño candidato, SIN AUTORIZACIÓN PARA RF.

## Incorporación al capítulo III de la tesis UNC

La fase prospectiva se ha previsto como verificación temporal independiente de la campaña factorial 3×2, para examinar la concordancia de las diferencias de throughput TCP descendente entre combinaciones de frecuencia y ancho de canal. El plan comprende siete ciclos de cuatro días: tres días con seis ventanas sucesivas de doce horas cada una y un día reservado para contingencias y estabilización. Cada una de las seis configuraciones aparece una vez por ciclo, hasta completar 42 exposiciones.

La distribución se elaboró *antes* de recopilar datos prospectivos, utilizando una búsqueda pseudoaleatoria con semilla documentada (20261027) y restricciones de equilibrio entre franjas 00:00–12:00 y 12:00–00:00. Debido a que existen siete aplicaciones por tratamiento, el equilibrio factible es 3/4 o 4/3, verificado para todas las configuraciones. La selección constituye un cronograma con restricciones y NO demuestra aleatorización completa ni elimina la confusión temporal.

## Auditoría complementaria del candidato (inicio hipotético: 01/11/2026)

- Seis tratamientos, siete aplicaciones cada uno; distribución total 21 aplicaciones en cada franja de 12 horas.
- La distribución por día de semana no es homogénea: algunas configuraciones tienen tres apariciones el miércoles; otras no aparecen ese día.
- Entre las aplicaciones consecutivas, algunos pares ordenados de configuraciones ocurren cuatro veces. Se observaron dos casos de repetición del mismo tratamiento al pasar entre ciclos (excluyendo en este recuento la separación temporal real de 24 h de reserva).
- Las cifras por día de semana son únicamente para el **inicio hipotético** utilizado; deben recalcularse cuando se apruebe la fecha real.
- La reserva no equivale automáticamente a apagado, permanencia en la configuración previa o retorno a línea base. El comportamiento RF durante la reserva debe especificarse y aprobarse por separado.

## Plan de control y análisis que debe quedar congelado

1. Definir una fecha real de inicio únicamente cuando se acrediten condiciones RF, integridad y seguridad.
2. Justificar el criterio de elegibilidad por segmento (ventana de estabilización, cobertura efectiva, incidencias, protocolo TCP homogéneo y tratamiento de datos faltantes).
3. Definir y versionar de forma explícita el estimando principal prospectivo, sus contrastes y límites de diferencia con la fase original. Concordancia de signos y superposición de intervalos NO equivalen por sí solas a equivalencia.
4. Evaluar ciclo y franja horaria como componentes del diseño; hacer sensibilidad por día de semana y posición de tratamiento. Evaluar precedencia de tratamiento/efectos de arrastre.
5. No utilizar el resultado de la primera campaña para seleccionar una secuencia de tratamientos con diferencias anticipadamente favorables; tampoco elegir criterios de concordancia mirando la segunda fase.
6. Registrar con hashes el calendario y el protocolo definitivos antes del primer tratamiento, y toda enmienda mediante control de versiones.
7. No tratar múltiples lecturas de 5 o 15 minutos como réplicas experimentales independientes.

## Respuesta sugerida para el jurado

«El cronograma responde a la necesidad de observar seis configuraciones de forma repetida durante siete ciclos, con una exposición uniforme por ciclo y equilibrio horario cercano al óptimo matemático. La secuencia se generó antes de recolectar datos prospectivos mediante reglas reproducibles, no para favorecer resultados. Reconocemos que no asegura igualdad perfecta por día de semana ni neutraliza la dependencia entre transiciones; por eso preespecificamos ajustes por ciclo/franja, análisis de sensibilidad y trazabilidad de enmiendas».

## Estado de seguridad

El calendario candidato NO está aprobado para desplegarse. Los scripts actuales solo generan cronogramas y simulan un radio ficticio. La validación de un actuador real, las pruebas de rollback físico, la inspección de ambos extremos, la evidencia de estabilidad y la aprobación técnica siguen pendientes.
