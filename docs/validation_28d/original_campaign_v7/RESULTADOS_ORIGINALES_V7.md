# Campaña original 3×2: cierre analítico V7

La adquisición de los 18 segmentos terminó el 27/10/2026 a las 00:00, hora de Perú. El retorno a referencia quedó registrado a las 00:02:58. No es necesario esperar la campaña prospectiva para informar esta fase. O5 permanece pendiente de adquisición prospectiva.

La selección retrospectiva produce 3419 pruebas DL 8/1 y 17 respuestas de segmento. S1 contiene mediciones RF y otro perfil TCP 15/2; su ausencia en el modelo homogéneo no significa que falte adquirir ese segmento. S16 se conserva en todos los modelos.

| Segmento | Bloque | MHz / MHz | n DL | Mediana DL Mb/s | Horas con DL / nominales |
|---|---|---|---|---|---|
| 1 | 1 | 6655/20 | 0 | — | 0/72 |
| 2 | 1 | 7000/40 | 32 | 89.842 | 9/72 |
| 3 | 1 | 6475/20 | 284 | 31.748 | 72/72 |
| 4 | 1 | 6655/40 | 287 | 88.987 | 72/72 |
| 5 | 1 | 6475/40 | 283 | 43.173 | 72/72 |
| 6 | 1 | 7000/20 | 286 | 63.876 | 72/72 |
| 7 | 2 | 7000/40 | 191 | 81.467 | 48/48 |
| 8 | 2 | 6655/40 | 187 | 89.245 | 48/48 |
| 9 | 2 | 6655/20 | 191 | 66.186 | 48/48 |
| 10 | 2 | 6475/40 | 189 | 43.280 | 48/48 |
| 11 | 2 | 6475/20 | 189 | 31.781 | 48/48 |
| 12 | 2 | 7000/20 | 187 | 62.788 | 48/48 |
| 13 | 3 | 6475/40 | 191 | 49.339 | 48/48 |
| 14 | 3 | 6655/20 | 191 | 66.307 | 48/48 |
| 15 | 3 | 6655/40 | 191 | 89.225 | 48/48 |
| 16 | 3 | 7000/20 | 161 | 21.426 | 43/48 |
| 17 | 3 | 6475/20 | 191 | 33.668 | 48/48 |
| 18 | 3 | 7000/40 | 188 | 66.039 | 48/48 |

Modelo exploratorio: una respuesta por segmento, factorial frecuencia×ancho y bloque. Efecto marginal igual ponderado 40−20 MHz: +21,097 Mb/s (IC convencional 95 %: 8,494 a 33,699). Pruebas global/frecuencia/ancho/interacción con ajuste Holm; el detalle reproducible está en Modelo_exploratorio_V7.json. No hay inferencia causal definitiva.

El signo del efecto de ancho persiste al excluir S2, limitarse a bloques completos y utilizar medias. En los bloques completos, la prueba global tiene p nominal 0,03787 y p Holm 0,08488: la significación no se mantiene bajo todas las especificaciones. S16 permanece incluido.

Las reglas se formalizaron después de observar la campaña, sin umbral mínimo de cobertura retrospectivo. Se conserva S2 (32 pruebas en nueve horas civiles de 72 nominales); su exclusión se informa solo como sensibilidad. Una hora con prueba no equivale a una hora de disponibilidad. El hash identifica la proyección seleccionada, no certifica custodia íntegra de la base.

El protocolo prospectivo adjunto es una propuesta documental pendiente de cotejo operativo, sin activar radios o ejecutores.
