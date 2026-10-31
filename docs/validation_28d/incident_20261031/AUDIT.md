# Auditoría del controlador prospectivo de Luisita

Fecha de revisión: 31 de octubre de 2026, hora de Perú. Evidencia detallada en EVIDENCE.json.

## Resultado

La campaña prospectiva no está adquiriendo TCP. El temporizador está habilitado y ejecuta comprobaciones, pero el controlador permanece en HALTED. El éxito de las comprobaciones posteriores de systemd no significa que se hayan realizado exposiciones.

## Secuencia acreditada

- 30/10 12:00:01: intención de primera exposición P01_S01, 6655 MHz / 40 MHz.
- 30/10 12:00:02: TRIAL_ACK. Ese acuse no acredita asociación del SM ni confirmación definitiva del tratamiento.
- 30/10 12:02:33: Dual target/connectivity not stable before deadline. Se conservaron HALT.json y PENDING.json; no existe WINDOW_COMMITTED de esa exposición en el registro revisado.
- El colector independiente registró errores de acceso SSH al SM a las 12:01 y 12:06, con No route to host. Ese error no distingue por sí solo asociación RF, transporte o gestión.
- A las 12:11 el colector volvió a observar ambos extremos en 7000/20. La secuencia es compatible con reversión del modo trial; no se atribuye una causa física definitiva.
- No existen pruebas con campaign_id LUISITA_PROSPECTIVE_28D_20261030 al corte.

## Estado del equipo y de la adquisición auxiliar

Controlador encendido, reloj NTP sincronizado y espacio libre suficiente. Los doce archivos del manifiesto congelado mantienen sus hashes. Los tres temporizadores TCP/orquestador anteriores continúan deshabilitados e inactivos. Colector RF, meteorología local, sincronización de SJ01 e inhibidor de suspensión operativos. Los últimos servicios de respaldo finalizaron con código cero; esta revisión no es una nueva prueba de restauración integral.

La lectura directa de ambos radios durante la revisión indicó 7000/20 y la ruta al extremo remoto respondió. CU01 se almacena en weather_local; SJ01 se sincroniza en station_observations. No se debe interpretar la ausencia de SJ01 en la primera tabla como ausencia de adquisición remota.

## Alcance de la conclusión y recuperación

La protección evitó continuar ante un cambio no verificado, pero el inicio operativo no quedó completado. La verificación del 30/10 a la 01:59 acreditó instalación y espera antes de D0; no acreditó la ejecución posterior del primer cambio.

Antes de reanudar se requiere identificar la causa del fallo de asociación o de verificación, conservar el incidente y validar una transición controlada. wait_target actualmente oculta las excepciones de cada intento; una revisión del controlador debería conservar diagnóstico por intento sin relajar la verificación dual ni confirmar estados ambiguos.

No se deben borrar HALT/PENDING para forzar continuidad ni lanzar cambios RF sin reconciliar el estado. Esta auditoría no modifica el calendario, no reinicia servicios y no lanza pruebas TCP ni cambios RF. Las ventanas transcurridas quedan sin adquisición prospectiva; no se retrodata su ejecución. Si se pretende completar 28 días nuevos íntegros, será necesario versionar un nuevo D0 y su cierre a D0 más 28 días. El 27 de noviembre al mediodía no puede darse por cierre de 28 días efectivamente ejecutados.
