# Condiciones y levantamiento de observaciones (corte: 18/10/2026)

Esta matriz resume condiciones de tres áreas (radiofrecuencia, automatización y metodología), sin reproducir ni autenticar firmas de expertos. **VERIFICADO** se refiere exclusivamente a la evidencia descrita, no a la habilitación de la fase.

| ID | Área | Condición | Evidencia requerida | Estado |
|---|---|---|---|---|
| C01 | Cierre | Conciliar 27/28 octubre | CSV, eventos reales, RF AP/SM y acta | **PENDIENTE**: discrepancia acreditada |
| C02 | Cierre | Retorno 7000/20 y 48 h estables | Eventos, asociación, RF y alarmas | **PENDIENTE**: fase activa |
| RF01 | Campo | Inspección segura de antenas y soportes por viento | Visita CU/SJ, fotos y acta | **PENDIENTE** |
| RF02 | Control RF | Confirmar 10/3 dBm y 26/26 dBi configurados, contrastar ganancia física | Telemetría, fichas, inspección | **PARCIAL**, falta corroboración física |
| RF03 | Control RF | Acreditar polarización, TDD, firmware, orientación y cambios | Inventario y acta pre/post | **PENDIENTE** |
| SI01 | Orquestador | Aprobar calendario 7 ciclos × 6 tratamientos | Versión y dry-run firmados | **PENDIENTE**, no desplegado |
| SI02 | Orquestador | Verificar preflight, idempotencia, rollback y piloto | Pruebas y bitácoras | **PENDIENTE** para extensión |
| SI03 | TCP | Resolver identificadores/cadencias, ruta, omit, flujos y Ethernet | Protocolo y series homogéneas | **PENDIENTE** |
| SI04 | Custodia | Sincronización de relojes, SHA-256 y respaldo restaurable | Reporte de restore y hashes | **PENDIENTE**, existen respaldos |
| ME01 | Estadística | Incorporar P5/O5 y comparación prospectiva | Tesis y matrices | **DOCUMENTADO**; aprobar versión final |
| ME02 | Estadística | Preespecificar estimandos, incertidumbre y regla de concordancia | Plan congelado antes de medir | **PENDIENTE** |
| ME03 | Estadística | Analizar fases separadas, por segmento/ciclo, sin pseudorreplicación | Scripts y resultados auditados | **PENDIENTE** |
| CU01 | Integridad | Separar originales, validación, ASDE y otros ensayos | Manifiestos y hashes por fase | **PENDIENTE** |

### Para cambiar un estado a CUMPLIDA
Vincular evidencia fechada, sistema fuente, hash (cuando proceda), responsable de comprobación y acta o informe de cierre. Dictamen favorable con condiciones **no** certifica ejecución ni resultados futuros.

Responsables funcionales: especialista RF para inspección; especialista de sistemas para software y datos; especialista en métodos cuantitativos para protocolo inferencial; asesoría/tesista para expediente y autorización. Las firmas y pronunciamientos personales no deben publicarse aquí.
