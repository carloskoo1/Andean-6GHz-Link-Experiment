# Plan de análisis de O5: concordancia entre fases

**Tesis:** Evaluación experimental de la influencia de la configuración espectral en el desempeño técnico de un radioenlace punto a punto (UNC).
**Autora:** Bach. Luisita Adalid Mendo Urbina. **Asesor:** Ing. Carlos Jesús Koo Labrín.
**Versión:** 1.0, 22/11/2026 (America/Lima).
**Estado:** plan fijado durante la adquisición prospectiva y antes de su cierre programado (05/12/2026 00:00). Complementa el plan field_v4 y el Anexo XV de la tesis; no modifica la adquisición, los tratamientos ni la regla de cobertura.

---

## 1. Declaración de lo conocido al fijar este plan

Al redactar este plan se conocían:

- los resultados de la fase original (exploratorios, 17 exposiciones con perfil 8 s/1 s), descritos en la tesis (4.1);
- los reportes operativos de cobertura de la fase prospectiva (exposiciones elegibles y no elegibles, incidentes D2 a D6 del Anexo XVI).

**Declaración de la autora:** no se han inspeccionado los valores de throughput de la fase prospectiva por configuración.

## 2. Datos y unidad de análisis

- **Fase original (referencia):** 17 exposiciones con perfil TCP de 8 s y omisión de 1 s (S02 a S18), con la mediana del throughput TCP DL por exposición como respuesta. La serie de 15 s/2 s no interviene en O5.
- **Fase prospectiva:** exposiciones del segundo intento (plan field_v4, 07/11/2026 a 05/12/2026) que cumplan la regla R0: al menos 36 descargas válidas en al menos nueve horas civiles distintas. Las reservas a 7000/20 no son réplicas factoriales.
- **Verificación de perfil:** antes del análisis se comprobará, fila por fila, que las pruebas prospectivas tienen duración de 8 s y omisión de 1 s. Las filas con otro perfil se excluyen y se informan.
- **Unidad:** la exposición de 12 h. Las pruebas TCP dentro de una exposición no son réplicas.
- **Sin imputación:** las exposiciones no elegibles (por ejemplo, P01_S04, P03_S01 y la afectada por D6, si no cumple R0) quedan fuera del análisis principal.

## 3. Hipótesis de O5

La fase original generó una hipótesis direccional sobre la frecuencia, que la fase prospectiva somete a prueba:

| Código | Hipótesis | Tipo |
| --- | --- | --- |
| H5a | En la fase prospectiva, el throughput a 6655 MHz es mayor que a 6475 MHz (μ6655 − μ6475 > 0), promediando sobre el ancho de canal | Confirmatoria, unilateral |
| H5b | En la fase prospectiva, el throughput a 7000 MHz es mayor que a 6475 MHz (μ7000 − μ6475 > 0), promediando sobre el ancho de canal | Confirmatoria, unilateral |
| H5c | Efecto del ancho de canal (40 − 20 MHz) | Bilateral, secundaria |
| H5d | Interacción frecuencia × ancho | Bilateral, secundaria |

No se formula una hipótesis direccional para el ancho de canal ni para la interacción porque la fase original no los estableció.

## 4. Modelo y estimación

**Fase prospectiva:** sobre las medianas por exposición elegibles,

Y = μ + Ciclo + Franja + F + W + F×W + ε,

con Ciclo como efecto fijo (hasta siete niveles) y Franja (00:00–12:00 frente a 12:00–00:00). Si la matriz no tiene rango completo, se eliminará primero Franja y luego la interacción, y se informará.

**Fase original:** Y = μ + Bloque + F + W + F×W + ε, sobre las 17 exposiciones.

Los contrastes de frecuencia se estiman como medias marginales promediadas sobre ancho de canal, con IC en Mb/s.

## 5. Inferencia

**Pruebas de H5a y H5b.** La prueba principal depende de un hecho de diseño ya fijado, que se verificará en el `plan.json` de field_v4 (SHA-256 cf870aeee1718d673fed20b38e7014b9d551bb70fb472bd910f24d0cbcb7c740) antes de ver los resultados:

- **Si el orden de tratamientos de field_v4 fue aleatorizado:** prueba de permutación unilateral restringida por ciclo, con al menos 10 000 permutaciones y semilla 20261205.
- **Si el orden fue fijo y balanceado:** prueba t unilateral sobre el contraste del modelo lineal; la permutación se informa solo como sensibilidad.

Nivel de significación: α = 0,05, con ajuste de Holm sobre la familia {H5a, H5b}. H5c y H5d se informan con su IC del 95 % y su valor p bilateral, sin decisión confirmatoria.

## 6. Margen de concordancia y clasificación

**Margen: δ = 11 Mb/s**, fijado con una regla definida antes de conocer los resultados prospectivos y con datos ajenos a ambas fases. Su fuente es la línea base del 01 al 14/09/2026, con configuración fija 7000/20 y el mismo perfil de 8 s/1 s. Las 22 ventanas de 12 h con al menos 36 pruebas tuvieron medianas entre 31,0 y 65,6 Mb/s, con desviación estándar de 11,2 Mb/s. Una diferencia menor que esa variabilidad espontánea entre ventanas de 12 h, sin cambio de configuración, no es distinguible en la práctica en este enlace. El margen se redondea a 11 Mb/s.

**Diferencia entre fases:** para cada contraste θ, Δ = θ̂_prospectiva − θ̂_original, con error estándar √(EE²_original + EE²_prospectiva) y grados de libertad de Welch–Satterthwaite.

**Clasificación** de cada contraste:

| Resultado | Criterio |
| --- | --- |
| Concordante | Mismo signo en ambas fases y el IC del 90 % de Δ está completamente dentro de ±11 Mb/s (equivalencia por dos pruebas unilaterales, α = 0,05) |
| Discordante | El IC del 90 % de Δ está completamente fuera de ±11 Mb/s, o los signos difieren y el IC del 95 % del contraste prospectivo excluye cero |
| Inconcluso | Cualquier otro caso |

**Conclusión de O5:**

- **Se confirma el efecto de la frecuencia** si se rechazan H5a y H5b tras el ajuste de Holm.
- **Las magnitudes son concordantes** si, además, los contrastes de H5a y H5b se clasifican como concordantes.
- Si se rechazan H5a y H5b pero la clasificación es inconclusa, se informará como **dirección confirmada con magnitud no establecida**.
- Coincidencia de signos, intervalos superpuestos o p > 0,05 no se presentarán como equivalencia.

## 7. Sensibilidad

Se informarán todas, sin elegir la favorable:

1. Umbral R0 alternativo de 35 y 34 descargas (incluye P03_S01 si cumple el resto).
2. Exclusión de un ciclo por vez.
3. Fase original sin S16.
4. Mediana frente a media recortada al 10 % por exposición.
5. Exclusión de la exposición afectada por el corte del 22/11/2026, si cumple R0.

## 8. Congelamiento y desviaciones

- Este archivo se publica en el repositorio del proyecto antes del 05/12/2026, en un commit cuyo identificador y SHA-256 se registrarán en la tesis (Anexo XV y Anexo XVI).
- Cualquier cambio posterior a la publicación se registrará como desviación, con fecha y motivo, y el análisis según esta versión se informará siempre.
- El análisis se ejecutará sobre una copia congelada de los datos (6 a 8/12/2026), con manifiesto SHA-256 de entradas, scripts y salidas.

## Referencias

- S. Holm, "A simple sequentially rejective multiple test procedure," *Scandinavian Journal of Statistics*, vol. 6, no. 2, pp. 65–70, 1979.
- M. D. Ernst, "Permutation methods: A basis for exact inference," *Statistical Science*, vol. 19, no. 4, pp. 676–685, 2004, doi: 10.1214/088342304000000396.
- B. A. Nosek, C. R. Ebersole, A. C. DeHaven y D. T. Mellor, "The preregistration revolution," *PNAS*, vol. 115, no. 11, pp. 2600–2606, 2018, doi: 10.1073/pnas.1708274114.
- D. J. Schuirmann, "A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability," *Journal of Pharmacokinetics and Biopharmaceutics*, vol. 15, no. 6, pp. 657–680, 1987, doi: 10.1007/BF01068419.
- R. L. Wasserstein y N. A. Lazar, "The ASA's statement on p-values: Context, process, and purpose," *The American Statistician*, vol. 70, no. 2, pp. 129–133, 2016, doi: 10.1080/00031305.2016.1154108.
