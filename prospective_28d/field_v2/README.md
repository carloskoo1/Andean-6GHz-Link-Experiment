# Controlador prospectivo de campo V2

Versión activada el 31/10/2026 tras reconciliar el intento fallido del día 30, que no adquirió TCP prospectivo.

- Calendario: 31/10/2026 12:00 a 28/11/2026 12:00 America/Lima.
- Campaña: LUISITA_PROSPECTIVE_28D_20261031.
- Se mantienen 42 exposiciones factoriales, siete reservas, duración de 12 horas por tratamiento, TCP 8/1 y un flujo, estabilización de 30 minutos y las reglas de cobertura y selección existentes.
- El SM debe conservar las listas 6475 6655 7000 tanto en 20 como en 40 MHz y máscara 3. Se verifican antes de operar.
- El plazo de verificación previo a confirmar es 180 s, coherente con el parámetro de asociación del orquestador original. No se relajan las diez comprobaciones consecutivas, el límite de confirmación de 210 s ni el bloqueo de estados ambiguos. Se registra cada error o cambio de estado relevante.
- HALTED produce error explícito de ejecución y STATUS.json. El motivo original de HALT se conserva.
- La unidad systemd existente sigue apuntando a field_v1/controller.py, convertido en despachador a esta versión. El temporizador y sus protecciones permanecen instalados; no se necesita otro instalador para esta actualización.
- freeze.json incluye el despachador, esta versión y las dependencias externas verificadas.
- activate_recovery.py se ejecutó una sola vez, bajo exclusión mutua, después del piloto completo, respaldo y reconciliación. No debe repetirse sobre un intento ya activado.
- Se conserva evidencia en VALIDATION.json y en ../recovery_20261031/.

El inicio programado y WAITING_START no equivalen a primera exposición adquirida. La comprobación del cambio y del primer par TCP está programada para 31/10 12:50. Los datos del piloto se identifican aparte y no son resultados de la campaña.
