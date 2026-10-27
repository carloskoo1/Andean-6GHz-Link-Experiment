# Protocolo O5 — estimandos, comparación y reserva (candidato 27/10/2026)

Estado: propuesta para aprobación ANTES de obtener nuevos datos. No constituye autorización RF.

## Objetivo, unidad y estimando
O5: examinar la concordancia temporal de los contrastes de throughput TCP DL entre la campaña original factorial 3x2 y siete nuevos ciclos del mismo radioenlace. Alcance limitado a Cuñacales–San José.

Unidad prospectiva: una exposición de tratamiento de 12 horas, con un resumen primario por exposición; no tratar las pruebas TCP sucesivas como réplicas independientes.

Respuesta principal candidata: mediana del throughput TCP DL medido mediante protocolo homogéneo (duración 8 s, omisión inicial 1 s, ruta verificada y parámetros restantes congelados). Contar intentos, errores y éxitos; documentar cobertura temporal y validez RF. Cada ciclo incluye seis tratamientos distintos y hasta siete ciclos contienen 42 exposiciones.

Estimandos candidatos: efectos de frecuencia, ancho de canal e interacción ajustados por ciclo y franja; reportar las diferencias homólogas respecto de la campaña original con sus intervalos e incertidumbre, sin mezclar ingenuamente ambos conjuntos de mediciones.

## Regla de concordancia — todavía NO congelada
Para cada contraste predefinido informar magnitud en ambas fases, diferencia entre fases e intervalos de confianza, así como dirección y heterogeneidad. Una declaración de equivalencia práctica requiere margen en Mbps justificado y fijado antes de nuevas mediciones y prueba estadística pertinente. Sin margen sustantivo aprobado, limitar las conclusiones a estabilidad descriptiva; el signo común, la superposición de intervalos o p mayor de 0,05 no demuestran equivalencia.

## Elegibilidad — condiciones por definir formalmente
Preespecificar estabilización posterior a cambios, cobertura mínima, AP/SM concordantes, protocolo TCP idéntico, relojes sincronizados y manejo de incidentes. No excluir segmentos únicamente por valores extremos ni cambiar reglas al observar resultados. Ejecutar análisis de sensibilidad para faltantes, franja horaria, día de semana, posición y posible efecto de arrastre.

## Reserva de 24 horas: propuesta operativa conservadora
Las siete reservas son ventanas de monitorización y contingencia, no aplicaciones adicionales del tratamiento ni oportunidad automática de reposición. Propuesta: prohibir nuevas conmutaciones automáticas durante la reserva y mantener la última configuración estable confirmada, salvo condición de seguridad previamente documentada que exija retorno seguro. Etiquetar datos de reserva como RESERVE_MONITORING para no incorporarlos al estimando factorial.

NO_RF_CHANGE describe ausencia de orden de cambio; no es una instrucción de retornar a la línea base. Si la última transición falla o hay pérdida de conectividad, aplicar bloqueo seguro en el ejecutor, registrar la incidencia y exigir recuperación verificada según protocolo de seguridad y piloto. No utilizar el simulador como prueba de recuperación física.

## Requisitos para aprobar
Completar los criterios de elegibilidad y margen o regla de concordancia descriptiva, aprobar el calendario y SHA-256, validar un ejecutor integrado fuera de producción (idempotencia, persistencia y rollback), inspección física, controles de RF, respaldos restaurables y 48 horas efectivas de estabilidad. Registrar aprobación de tesista y asesor. Evitar pedir dictámenes adicionales a los expertos salvo nueva necesidad sustantiva.

Estado final: BORRADOR NO HABILITADO.
