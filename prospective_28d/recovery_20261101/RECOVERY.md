# Reparación verificada del 1 de noviembre de 2026

Se recuperó el controlador prospectivo con field_v3. Los intentos del 30 y
31 de octubre produjeron cero pruebas TCP prospectivas: no constituyen
exposición científica. Se conservaron sus registros y el piloto fallido
que permitió detectar el dashboard atrasado del SM.

## Evidencia
- 32 pruebas unitarias normales y 32 con Python optimizado: OK.
- Dos comprobaciones adicionales de prearranque: referencia válida aceptada,
  referencia incorrecta rechazada; cero cambios RF y cero pruebas TCP.
- Doce ciclos reales de autenticación, lectura y cierre de sesión verificado:
  token anterior rechazado y archivo privado retirado.
- Piloto por la unidad systemd instalada: seis configuraciones verificadas,
  diez comprobaciones consecutivas antes y después de cada confirmación.
- Cuatro registros TCP OK, dos DL y dos UL, con ruta verificada, 8 segundos,
  omisión de 1 segundo y un flujo. Cada dirección tiene evidencia RF viva.
- Retorno a 7000/20, sin trial activo antes de habilitar el calendario.
- CU01 y SJ01 suministran observaciones recientes y sincronización correcta.
- Copia SQLite local verificada mediante quick_check y SHA-256.
- Temporizadores anteriores deshabilitados. Incidentes archivados antes de
  retirar el bloqueo. El piloto queda excluido del factorial.

Los detalles, marcas de tiempo y valores exactos están en HEALTH.json,
SESSION_CYCLES.json, LOGOUT_PROOF.json, PRESTART_TESTS.json,
BACKUP.json, service_pilot/PASSED.json y field_v3/DEPLOYMENT.json.

## Calendario y límite de la comprobación
Inicio habilitado: 2 de noviembre de 2026 a las 00:00, America/Lima.
Fin: 30 de noviembre a las 00:00. Se conserva la secuencia y el diseño de
42 exposiciones de 12 horas y siete reservas de 24 horas.
El primer cuarto de hora previsto para TCP científico es 00:45, tras
verificación y estabilización de 30 minutos. WAITING_START sólo acredita
programación operativa; el primer registro científico debe verificarse
después de D0.

## Medición y trazabilidad
Se corrigió el cierre de sesión utilizando las cookies que exige la GUI
del equipo. Nunca se eliminan sesiones de otros usuarios. Las cookies y
credenciales no forman parte del repositorio.
La frecuencia viva se verifica en ambos extremos con sus MAC/BSSID y
tablas de asociación, conservando la lectura bruta del SM que puede estar
atrasada. La tabla prospective_rf_verification registra esta procedencia
por test_id y direction; debe utilizarse al auditar los nuevos datos.
No se reescribieron observaciones históricas. Véase field_v3/README.md.
