# Auditoría inicial del contrabalanceo prospectivo — 27/10/2026

Origen: `prospective_plan.py`, variable `PERMUTATIONS`. Auditoría offline de las 42 exposiciones propuestas; NO es autorización de ejecución.

Cada tratamiento aparece una vez por ciclo y siete veces en total. Cada ciclo reserva 24 horas. El plan de 12 horas por tratamiento genera franjas alternadas 00:00–12:00 (slots 1,3,5) y 12:00–00:00 (slots 2,4,6) cuando el ciclo empieza a medianoche.

| Código | Frecuencia/ancho | 00–12 | 12–00 |
|---|---|---:|---:|
| 0 | 6475/20 | 5 | 2 |
| 1 | 6475/40 | 3 | 4 |
| 2 | 6655/20 | 2 | 5 |
| 3 | 6655/40 | 4 | 3 |
| 4 | 7000/20 | 4 | 3 |
| 5 | 7000/40 | 3 | 4 |

**Dictamen:** hay equilibrio de exposición por tratamiento (7) pero NO equilibrio horario suficiente: dos tratamientos tienen proporción 5/2. Se requiere revisar y mejorar las permutaciones y evaluar balance respecto al día de la semana, transición anterior y variables meteorológicas. Con siete aplicaciones por tratamiento, un balance 3/4 o 4/3 por franja es el más próximo al perfecto. La asignación actual es determinista y aún no aprobada.

No editar el calendario ni el ejecutor activo. No habilitar RF hasta nuevo protocolo, seguridad y pruebas.