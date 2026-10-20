# Procedimiento propuesto de cierre, instalación y prueba supervisada

**Preparado para revisión. NO es autorización de instalación ni ejecución.**
La V5 entregada contiene solo simulación. Este procedimiento describe un futuro
paquete de campo; no existen en esta entrega un comando de activación ni un
servicio operativo nuevo. No ejecutar modificaciones en CU01 durante la fase 3×2.

## 1. Cierre y custodia de la campaña original

- Conciliar el 27/28 de octubre con el CSV ejecutado, eventos y telemetría. El paso
  de una fecha no certifica cierre; conservar el calendario y la historia reales.
- Registrar último tratamiento, hora efectiva de término y configuración final
  AP/SM. Respaldar código, configuración sin secretos y datos brutos por fase;
  calcular SHA-256 y verificar restauración en una copia aislada.
- Tras acreditar cierre y autorizar la intervención, detener/deshabilitar el timer
  original de transiciones y comprobar que el servicio terminó, sin procesos
  huérfanos ni cambios RF manuales concurrentes. Inventariar por separado los
  temporizadores de throughput; evitar ensayos TCP superpuestos.
- Conservar los servicios meteorológicos y de custodia que corresponda mantener.
  No detener indiscriminadamente AtmosLink. No modificar fechas o datos históricos
  para hacer coincidir los documentos.

**Evidencia de salida:** acta de cierre con registros fuente y horas Perú/UTC,
respaldo restaurable, inventario de procesos/timers y responsable de verificación.
Todos estos elementos permanecen pendientes; no fueron verificados desde aquí.

## 2. Condiciones antes de RF prospectiva

- Inspección y conformidad RF de ambos extremos: alineación, soportes, conectores,
  antenas, polarización, ganancias físicas/configuradas, potencias, TDD y firmware.
- Confirmar configuración de referencia 7000/20 y comprobar mediante registros
  las 48 h de estabilidad previstas en la preparación; ratificar en el protocolo
  aprobado la duración y los criterios finales. No convertir horas transcurridas
  en evidencia automática de estabilidad.
- Aceptación del calendario, unidad experimental, franjas, dependencia temporal,
  estabilización, tolerancia, manejo de ventanas perdidas y QC por el Experto 3.
- Congelar el protocolo TCP después del ensayo de comparabilidad y aceptación;
  aprobar ruta, duración, omit, flujos, cadencia, dirección y carga concurrente.
- Revisión técnica del Experto 2 y autorización de la fase adicional. Las pruebas
  de software no sustituyen conformidades, firmas ni verificación física.

## 3. Instalación futura, aislada y reversible

1. Seleccionar una versión de campo revisada que implemente el transporte real.
   La V5 actual usa un servidor ficticio y **no es instalable para controlar RF**.
2. Preparar un directorio de versión separado del ejecutor original; verificar
   hashes y dependencias contra el manifiesto. No sobrescribir archivos activos.
3. Definir un directorio de estado local común para el enlace y permisos del
   usuario de ejecución. Original, prospectivo y operaciones RF autorizadas deben
   usar la MISMA guardia; no basta con que cada uno tenga su propio lock.
4. Integrar esa guardia en todos los puntos de entrada. Revisar especialmente la
   transición final a referencia y los comandos manuales/piloto del orquestador.
   Los servicios originales de CU01 todavía no la usan.
5. Mantener credenciales existentes fuera de Git, con permisos controlados.
   Verificar identidad AP/SM, reloj y ruta de administración mediante precheck de
   solo lectura del paquete de campo. No inventar evidencia de readback RF del SM.
6. Iniciar con titularidad original y ninguna transición automática prospectiva.
   Ensayar rechazo de acceso concurrente sin cambios RF. Documentar el relevo
   únicamente después del cierre y de cumplir las condiciones.

**Reversión de software:** retirar la versión candidata preservando logs y estado.
No reactivar automáticamente el ejecutor anterior: podría aplicar referencia o
reproducir acciones incompatibles con el cierre ya registrado.

## 4. Prueba RF supervisada posterior a la habilitación

- Reservar una ventana explícita con operador, acceso alternativo y procedimiento
  de recuperación. Verificar los criterios de interrupción antes de cambiar RF.
- Registrar solicitud, trial, confirmación, verificación y estabilización con
  tiempos efectivos. Confirmar qué mide cada variable del AP y del SM.
- Validar retorno al estado anterior conocido y plazos reales del firmware.
  La simulación de vencimiento de trial no prueba que el equipo real revierta.
- No provocar deliberadamente pérdida de acceso al único canal de administración.
  Verificar primero la recuperación en equipo de banco o con acceso alternativo.
- Ante respuesta perdida, conservar intención y bloquear nuevas transiciones.
  Conciliar mediante lecturas verificadas y tiempo confiable; no cancelar ni
  repetir a ciegas. Una restauración incierta exige revisión, sin bucles RF.
- Ante fallo, diario ilegible, reloj no confiable, asociación inestable o estado RF
  inesperado: detener la prueba y excluir su ventana; conservar evidencia.

## 5. Decisión de habilitación

Registrar conformidad del piloto, revisión de incidentes, controles RF, respaldo,
protocolo TCP, calendario y exclusión entre ejecutores. Solo entonces programar
el inicio aceptado. El 1 de noviembre es provisional y se desplaza si falta una
condición. Conservar las fases original y prospectiva separadas para el análisis.

Una recuperación técnica exitosa no autoriza reanudar una ventana fallida ni
contar sus datos como tratamiento válido. La decisión metodológica debe quedar
fechada y trazable, sin rellenar retrospectivamente intervalos excluidos.
