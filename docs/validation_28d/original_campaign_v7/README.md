# Cierre original 3×2 y propuesta prospectiva V7

Corte: 27/10/2026. La adquisición original de los 18 segmentos terminó. No hay que esperar 28 días para informar esta fase. El cierre del manuscrito integra O1–O4; O5 espera datos prospectivos.

- `RESULTADOS_ORIGINALES_V7.md`: resumen de las 18 ventanas y limitaciones.
- `cierre_original_v7.py`: consulta SQLite de solo lectura, calendario y eventos reales del Controlador. Imprime `CLOSURE_JSON=...`; no modifica base ni radios. Requiere las rutas explícitas del proyecto y la base meteorológica en el Controlador.
- `Cierre_original_V7.json`: extracción al corte con conteos, exclusiones, RF y TCP. Sus 17 respuestas 8/1 no significan que falte adquirir S1: este contiene otro perfil TCP.
- `modelo_exploratorio_v7.py`: una respuesta por segmento; factorial frecuencia×ancho y bloque; contrastes marginales, ajuste Holm y sensibilidades. Requiere Python, NumPy y SciPy. Ejecutar desde esta carpeta: `python3 modelo_exploratorio_v7.py`. Escribe `Modelo_exploratorio_V7.json`.
- `Modelo_exploratorio_V7.json`: cuatro ajustes, todos con S16. Inferencia convencional y exploratoria, sin tratar pruebas TCP individuales como réplicas independientes.
- `VALIDACION_V7.json`: comprobaciones de estructura y contraste independiente por diferencias de RSS.
- `PROTOCOLO_PROSPECTIVO_PROPUESTA_V1_20261027.md`: propuesta documental de reglas antes de nuevos datos. Pendiente de cotejo con ejecutor y aceptación operativa; no activa la campaña.

Las reglas originales se formalizaron retrospectivamente. No son prerregistro. S2 se conserva con cobertura reducida y su exclusión se muestra como sensibilidad. Se transparentan las diferencias de conteos respecto de cortes históricos. El hash de proyección seleccionada no sustituye la custodia íntegra de la base.

El análisis secundario meteorológico y de eventos está en `prospective_28d/secondary_diagnostics/` (commit e98f9967d598f58d57171f71a253fc9f32be7289). No se atribuye una causa física única al S16; la fase prospectiva podrá contrastar las explicaciones posibles si aparecen nuevas observaciones útiles.

La versión académica del manuscrito se conserva por separado; este directorio contiene código, resultados derivados y protocolo, sin los dictámenes firmados.
