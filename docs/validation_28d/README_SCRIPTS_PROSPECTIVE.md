# Preparación prospectiva de Luisita — solo simulación

**Estado: NO DESPLEGADO / NO HABILITADO.** Scripts offline separados del
`campaign_executor.py`, `campaign_orchestrator.py`, services y timers activos.

Archivos:
- `prospective_plan.py`: genera CSV con 7 ciclos × 6 tratamientos de 12 h,
  más siete reservas de 24 h; total 28 días, 42 tratamientos previstos.
- `test_prospective_plan.py`: prueba duraciones, secuencia, combinaciones,
  continuidad y bloqueo de autorización.
- `preflight_offline.py`: chequea expediente y evidencia documental, sin
  interactuar con radioenlaces. Siempre devuelve autorización RF falsa.

Ejemplo de simulación con fecha **hipotética** (NO INICIO AUTORIZADO):

```sh
python3 -m unittest test_prospective_plan.py -v
python3 prospective_plan.py --start 2026-11-01T00:00:00-05:00 --out /tmp/luisita_prospectiva_SIMULACION.csv
python3 preflight_offline.py --manifest evidence_manifest_template.csv
```

Antes de aprobar un calendario real: fecha de inicio, orden y turnos aprobados,
contrabalanceo argumentado, análisis P5/O5 preespecificado, integridad y hashes,
48 h efectivas sin incidentes después del retorno 7000/20, inspección física,
piloto supervisado, pruebas con radio simulado del ejecutor definitivo, rollback,
idempotencia, separación de campañas, sincronización horaria y protocolo TCP.

La asignación determinista de tratamientos propuesta es un **borrador técnico**,
no una aleatorización validada. Debe revisarse por balance horario, condiciones
operativas, ausencia de interferencia con ASDE y reglas de exclusión.
Las reservas NO asignan automáticamente tratamiento ni ejecutan cambios.
El software preparado aquí no implementa actuadores, red ni programación de servicios.

## Simulador aislado (27/10/2026)

- `prospective_simulator.py`: motor de simulación en memoria mediante `FakeRadio`, sin llamadas a Cambium, red, temporizadores ni servicios.
- `test_prospective_simulator.py`: cinco pruebas nuevas de idempotencia, fallo/bloqueo, reserva, recorrido y fuera de ventana.
- Comando: `python3 -m unittest test_prospective_plan.py test_prospective_simulator.py -v` (9/9 OK el 27/10/2026).
- El `SAFE_ABORT` y retorno al estado previo se **simulan solamente en memoria**. No se ha validado recuperación física, reconexión, autorización, persistencia ante reinicio, reloj de campo ni despliegue real.
- Este paquete es una prueba conceptual, **no un ejecutor prospectivo integrado listo para RF**. Queda sin despliegue y sin inicio automático.
