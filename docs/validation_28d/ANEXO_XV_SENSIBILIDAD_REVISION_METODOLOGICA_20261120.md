# Luisita — Anexo XV: revisión metodológica del análisis de sensibilidad (V0.2)

**Fecha del anexo:** 2026-11-20 (America/Lima)  
**Estado:** revisión documental elaborada DURANTE la fase prospectiva. No es un prerregistro anterior al inicio, no sustituye las reglas vigentes, no acredita aprobación de la adenda ni autoriza cambios RF.  
**Fuente académica privada:** `TESIS_LUISITA_MATRICES_PRESENTACION_FINAL_20261103.docx`. El Word académico completo, fichas y firmas permanecen bajo custodia privada.  
**SHA-256 Word fuente:** `5f4d5d62fcc1cafbb7f1e8328c94064d4bfa98cca7bbdadf25b103c7e4d9f265`.  
**SHA-256 tesis de trabajo integrada con Anexo XV:** `c6178a486cdc56bef33dbc4e38c729c907403290a680840177f036c423a40c23`; no se publica el DOCX completo durante adquisición.

## O5, diseño y estimando

El objetivo O5 examina la concordancia temporal de los contrastes de throughput TCP DL entre la campaña original factorial 3×2 y la validación prospectiva en el mismo enlace Cuñacales–San José. Factores: 6475/6655/7000 MHz × 20/40 MHz. Unidad de inferencia: **exposición de tratamiento**, no cada ensayo TCP. La fase original contiene 18 segmentos de 48–72 h; la fase prospectiva contempla como máximo 42 exposiciones de 12 h en siete ciclos. Presentar estimaciones por fase, diferencias de efectos e incertidumbre; no mezclar ingenuamente segmentos entre fases.

La respuesta primaria es la mediana del throughput TCP DL de ensayos elegibles por exposición. UL, disponibilidad, errores ICMP, métricas RF y meteorología se informan como resultados secundarios o contexto sin sustituir el estimando principal.

## Hallazgos de auditoría que obligan a limitar la inferencia

**H1 — Heterogeneidad instrumental (CRÍTICO).** La auditoría técnica del 17/11/2026 acredita registros originales en dos regímenes TCP: 15 s con omisión de 2 s y 8 s con omisión de 1 s. El cambio se asocia documentalmente a un cambio de rama y regresión del módulo de medición del Controlador el 20/09/2026; no se atribuye autoría personal. El perfil original homogéneo 8 s/1 s se analizará separado; los registros 15 s/2 s no son intercambiables. Verificar el protocolo efectivo de la prospectiva antes de declarar comparabilidad. El segmento original S02 conserva subperiodos parciales de ambos regímenes; la auditoría 17/11 informa además sensibilidad al bloque 1 y a S16, que debe retenerse.

**H2 — Cronología (ALTA).** El Word fuente fechado 03/11 todavía menciona la prospectiva field_v3 de 02–30/11; reportes posteriores sitúan la campaña en 07/11–05/12 y la auditoría 17/11 menciona plan field_v4. Conciliar fecha real y plan desplegado contra bitácora, SHA-256, JSON de despliegue y evidencia de campo. No reescribir retrospectivamente el documento histórico.

**H3 — Elegibilidad y preespecificación (ALTA).** La referencia operativa utilizada para R0 es al menos 36 pares DL/UL completos y válidos, con cobertura en nueve horas civiles por ventana, verificación de ruta y RF y estabilización documentada. La documentación revisada NO acredita por sí sola la fecha en que la formulación exacta quedó congelada. R0 se presenta como análisis principal **de referencia**; solo podrá llamarse confirmatorio preespecificado cuando se compruebe expediente fechado anterior a la primera exposición. Este umbral no demuestra potencia por sí solo.

**H4 — Faltantes e incidencia RF (ALTA).** P01_S04 carece de parejas TCP válidas por fallo de asociación; P03_S01 cuenta con 34 pares válidos y nueve horas civiles en el corte operativo revisado. Permanecen excluidas de R0 si se acredita el umbral 36. P03_S01 puede incluirse únicamente en un escenario S2 exploratorio, nunca convertirse retroactivamente en exposición elegible. No imputar ceros por fallos de logging ni tratar un fallo RF como simple ausencia aleatoria.

**H5 — Revisión independiente (ALTA).** La solicitud de revisión estadística del 12/11 acerca de contingencias/ampliación figura pendiente. Este anexo no sustituye ese dictamen ni autoriza nuevas exposiciones, cambios de RF o ampliación. El efecto de frecuencia, ancho e interacción se limita a este único enlace y períodos observados.

## Modelización por fase

Se usará la mediana DL por exposición y el modelo de referencia `Y_e = β0 + F_e + W_e + (F×W)_e + C_e + H_e + ε_e`, condicionado a rango completo e identificabilidad: F = frecuencia categórica, W = ancho categórico, C = ciclo/bloque y H = franja. El modelo puede ser inestable con pocas exposiciones; reportar IC95%, n de exposiciones/ciclos, grados de libertad, diagnósticos de residuos y limitaciones de dependencia temporal. HC3 será solo diagnóstico exploratorio de heterocedasticidad, no solución a autocorrelación. El análisis original y el prospectivo se ajustan por separado.

En ausencia de margen de equivalencia práctica justificado y aprobado antes de observar datos pertinentes, informar **concordancia descriptiva/heterogeneidad**, no equivalencia estadística. Signos compartidos, intervalos superpuestos o p>0,05 no prueban equivalencia.

## Escenarios reproducibles

| Código | Cambio frente a R0 | Etiqueta |
|---|---|---|
| R0 | Exposiciones ≥36 pares y ≥9 h, además de controles RF/ruta; verificar versión original | Principal de referencia; confirmatorio solo con prueba documental |
| S1 | Relajar a ≥35 pares, conservando los demás controles | Exploratorio |
| S2 | Relajar a ≥34 pares; evaluar P03_S01 si pasa los demás filtros | Exploratorio |
| S3 | Leave-one-cycle-out, con diagnóstico de identificabilidad | Temporal |
| S4 | Franjas, día de semana y posición cuando exista soporte suficiente | Temporal |
| S5 | Incorporar covariables meteorológicas temporalmente alineadas | Condicionado, no causal |
| S6 | Diagnósticos de influencia y media recortada 10% como resumen alternativo | Robustez |
| S7 | Acotar efectos de P01_S04 ausente mediante escenarios explícitos; sin imputación en R0 | Hipotético |
| S8 | Separar fallos instrumentales, interrupciones RF y tasa de éxito | Descriptivo operacional |
| S9 | Restringir comparaciones al régimen TCP realmente homogéneo; sensibilidad a S02, B1 y S16 originales | Validez instrumental |

Reportar para cada contraste y escenario: n, efectos en Mbps, IC95%, cambio absoluto respecto de R0, cambios de signo, errores, causa de exclusión y hash de insumos. No seleccionar escenarios por obtener la conclusión deseada.

## Cronograma operativo propuesto

- 20–28/11: cotejo de reglas, diccionario de datos, versiones de TCP y calendario; sin intervención en adquisición.
- 29/11: corte analítico interno y descriptivo, no para reprogramar tratamientos.
- 05/12: cierre operativo previsto, **sujeto a verificación**.
- 06–08/12: conciliación de fuentes y congelamiento con SHA-256.
- 08–10/12: análisis final por fase, S1–S9, sensibilidad al faltante y auditoría de O5.

Preservar crudos inmutables y registrar versión de ejecutor, timestamp local/UTC, identificación del ensayo y vínculo prueba-RF. Separar resultados confirmatorios históricos, análisis de referencia y exploratorios posteriores.

## Procedencia

- [Protocolo O5 candidato del 27/10](PROTOCOLO_O5_Y_RESERVAS_CANDIDATO_20261027.md) — documento histórico **no habilitado** en esa fecha.
- [Anexo cronograma candidato 27/10](ANEXO_METODOLOGICO_CRONOGRAMA_O5_20261027.md) — histórico, no prueba despliegue.
- Auditoría técnica del cambio de protocolo TCP (17/11/2026) — expediente académico privado, no publicado.
- Solicitud de revisión estadística independiente (12/11/2026) — pendiente, custodia privada.
- R. Jain, *The Art of Computer Systems Performance Analysis*, Wiley, 1991.
- R. Jacob et al., “Designing Replicable Networking Experiments With TriScale”, *Journal of Systems Research*, 2021.

**Confidencialidad:** no incorporar a GitHub ni a una versión pública de Zenodo tesis integral, informes privados, fichas de expertos, firmas, datos crudos, credenciales o documentos que no cuenten con autorización académica. La presente nota de método no es una validación de resultados definitivos.
**Estado Zenodo al 20/11/2026:** no se identificó un depósito/DOI verificable de Luisita con permisos de edición; **no** se creó ni actualizó registro Zenodo. Se preparó un paquete de borrador privado para revisión académica y depósito manual ulterior.
