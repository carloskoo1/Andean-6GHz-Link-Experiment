# Recuperación prospectiva del 1 de noviembre de 2026

## Incidentes y correcciones
Los intentos del 30 y 31 de octubre no produjeron pruebas TCP prospectivas.
Se conservan sus calendarios, incidentes y registros; no se retrodata exposición.

La API de cierre de sesión devolvía success=0 y mantenía válido el token.
El cliente incorpora las cookies de rol y token que utiliza la GUI del propio
equipo. Exige success=1 y verifica que el token anterior, con sus cookies
originales, quede invalidado. Doce ciclos reales de acceso/lectura/cierre
pasaron. El estado privado permite reutilizar únicamente la sesión del
controlador, sin cerrar sesiones ajenas ni almacenar secretos en Git.

El dashboard del SM puede conservar una frecuencia anterior incluso con
asociación y tráfico en la nueva frecuencia. La verificación prospectiva usa
la tabla de AP asociados del SM, identificada por BSSID, y la tabla de clientes
del AP, identificada por MAC e IP. Ambas deben coincidir con el dashboard
del AP y el objetivo. El SM debe estar asociado al AP esperado. Las lecturas
brutas del dashboard se conservan sin modificación. Cada dirección TCP tiene
evidencia adicional en prospective_rf_verification, unida por test_id y
direction; no debe inferirse elegibilidad sólo del campo bruto del SM.

## Validación y calendario
El piloto se ejecuta mediante la unidad systemd instalada, en seis pasos
persistentes, uno por invocación. Verifica diez lecturas consecutivas y
conectividad antes y después de confirmar cada cambio. Un intento
interrumpido o fallido bloquea la repetición automática. Se adquieren pares
TCP DL/UL en el primer y último paso. El identificador
LUISITA_SERVICE_PILOT_20261101_LIVE queda excluido del factorial.
La evidencia FAILED del primer piloto se conserva separadamente.

La activación exige seis configuraciones verificadas, cuatro pruebas TCP OK,
cuatro verificaciones RF asociadas, retorno a 7000/20 sin trial activo, copia
SQLite íntegra y cero pruebas en los dos intentos previos. Sólo entonces se
archiva el bloqueo anterior y se habilita el calendario:
2 de noviembre, 00:00 a 30 de noviembre, 00:00, America/Lima.
La secuencia original se conserva desplazada; 42 exposiciones de 12 horas
y siete reservas de 24 horas. La adquisición científica comienza después
de la estabilización de 30 minutos y en el siguiente cuarto de hora civil.
Antes de D0 el estado WAITING_START no demuestra adquisición científica.

Los registros locales CU01 y SJ01 continúan siendo las fuentes climáticas;
las asociaciones con episodios de degradación siguen siendo exploratorias.
