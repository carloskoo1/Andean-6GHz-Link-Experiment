# Seguimiento secundario de degradación RF

Complemento de O5 motivado por el segmento 16, con antecedente similar el 2 de octubre. La conservación del segmento 16 está acordada. No modifica calendario, tratamientos, reservas ni ejecutor RF. No es autorización de campo.

## Documentos integrados

- [Anexo prospectivo](ANEXO_SECUNDARIO_V1_20261027.md): preguntas, variables, referencias y análisis antes de la adquisición prospectiva.
- [Informe retrospectivo](INFORME_RETROSPECTIVO_20261027.md): comparación S6/S12/S16, análogos meteorológicos y límites de inferencia.
- [Auditoría de adquisición](AUDITORIA_ADQUISICION_20261027.md) y [resultado JSON](AUDITORIA_ADQUISICION_20261027.json).
- `retrospectivo_s16.py`: consulta reproducible de solo lectura del análisis original. Requiere la base y el cronograma originales; la ruta predeterminada corresponde al Controlador.
- `RESULTADOS_RESUMIDOS_20261027.json`: agregados por segmento, perfiles horarios y ejemplos de análogos; no son una base cruda ni un respaldo completo.

## Herramienta pasiva

`python3 prospective_28d/secondary_diagnostics/audit_acquisition.py --database /ruta/weather_local.db`

Solo consulta SQLite mediante mode=ro. Imprime JSON y no accede a radios, no lanza iperf, no instala timers ni modifica la base. No se ha instalado como servicio; puede ejecutarse manualmente para acompañar la revisión de episodios. Acepta --as-of con zona horaria y --hours. El resultado no certifica habilitación ni exactitud de los sensores.

Pruebas aisladas: `python3 -m unittest discover -s prospective_28d/secondary_diagnostics -v`.

## Conciliación con protocolo principal

8/1 es el perfil candidato del seguimiento y el protocolo histórico principal; no se cambia ni se declara aprobado `v5/tcp_protocol.pending.json`. La selección definitiva del perfil, cadencia, elegibilidad, reservas y ejecutor corresponde al cierre principal O5. El anexo define reglas analíticas secundarias y debe incorporarse a ese cierre sin sustituirlo.

Los contadores/uptime y cambiumDateTime ya se conservan en JSON originales. El Controlador sincronizado aporta el tiempo de adquisición. No usar los relojes internos de radio como tiempo científico hasta reconciliar zona horaria y offset. No corregir automáticamente los equipos para investigar un incidente histórico.

Las cuatro columnas de cadena existen pero no contienen mediciones. No se afirma que el firmware carezca de soporte: la ruta de adquisición actual no las aporta. La capacidad física de obtenerlas y cualquier ampliación del colector permanecen sin verificar; no se han ensayado comandos nuevos contra los radios.
