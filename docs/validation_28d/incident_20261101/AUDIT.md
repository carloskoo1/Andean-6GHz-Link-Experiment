# Estado prospectivo al 1 de noviembre de 2026

La campaña LUISITA_PROSPECTIVE_28D_20261031 no adquirió pruebas TCP. El temporizador está activo, pero el controlador está HALTED y carece de state.json de exposición verificada.

El 31/10 a las 12:00 el AP rechazó la autenticación con max_user_number_reached. El error se repitió hasta las 12:09; a las 12:10 se bloqueó por exceder el margen de inicio. Por tanto, esta segunda detención ocurrió antes de aplicar un nuevo tratamiento y es distinta de la transición RF fallida del 30/10. El piloto del 31/10 sí había completado sus seis configuraciones, pero no acreditaba que la autenticación estuviera disponible en D0.

RF y meteorología CU01/SJ01 continúan adquiriéndose. Los 19 hashes de la versión activa coincidieron en la revisión. No se contabiliza este período como campaña prospectiva válida.

El respaldo remoto del 1/11 registró una copia local consistente, pero ambas cargas a Drive fallaron por cuota de peticiones API. No corresponde describir esa ejecución como respaldo remoto verificado. El estado del recuperador posterior se conserva en EVIDENCE.json.

Antes de otro inicio deben resolverse la disponibilidad y gestión de sesiones del AP y verificarse el arranque en el contexto real de systemd, junto con las primeras mediciones. No basta con otro WAITING_START ni con aprobar el piloto. La fecha 28/11 no acredita 28 días ejecutados. Esta revisión no borra bloqueos ni modifica RF, servicios o calendario.
