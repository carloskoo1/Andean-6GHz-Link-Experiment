# Luisita — sustento bibliográfico del Anexo XV (20/11/2026)

Complemento documental de la tesis de Luisita Mendo Urbina. **Se preparó durante la adquisición prospectiva**. No constituye prerregistro ni sustituye el protocolo original, datos crudos o aprobación estadística independiente.

## Correspondencia entre decisión y referencia

| Decisión | Referencia que proporciona fundamento | Alcance / condición |
|---|---|---|
| Diseño factorial 3×2, evaluación del desempeño y unidad experimental | [1] Jain; [2] Jacob et al. | No establecen ni validan el umbral local de 36 pares/9 horas |
| Variabilidad temporal, ciclos y replicabilidad de redes | [2] TriScale | No exige específicamente 7 ciclos de 4 días o ventanas de 12 horas |
| Separación de perfiles TCP 15 s/2 s y 8 s/1 s; repetibilidad | [3] RFC 6349; [1] Jain | Las diferencias efectivas y su origen se documentan mediante logs de Luisita; la RFC no valida su equivalencia |
| Ausencias y exposición afectada por falla RF | [4] Rubin | Una ausencia de asociación puede no ser aleatoria; no imputar automáticamente |
| Escenarios de sensibilidad y decisiones analíticas alternativas | [5] Steegen et al. | Reportar todos los escenarios, sin escoger según resultado favorable |
| Enmienda fechada y clasificación confirmatorio/exploratorio | [6] Nosek et al. | La fecha de enmienda no se retrotrae al inicio experimental |
| Equivalencia práctica y límites interpretativos | [7] Lakens | p>0,05 no demuestra equivalencia; margen sustantivo debe justificarse con anticipación |

### Texto propuesto para el apartado de métodos

El contraste inferencial se efectuará por exposiciones de tratamiento y no utilizando ensayos TCP intraventana como réplicas independientes [1], [2]. Se verificará el protocolo instrumental y se distinguirán los regímenes TCP documentados para evitar combinaciones no comparables [3]. Los fallos de asociación, ventanas incompletas y registros ausentes se clasificarán según su mecanismo y se estudiarán mediante escenarios de sensibilidad transparentes [4], [5]. El carácter confirmatorio se reservará exclusivamente a decisiones cuya preespecificación anterior a la adquisición quede acreditada; las propuestas del 20/11 se etiquetan exploratorias [6]. No se afirmará equivalencia práctica entre fases sin margen predefinido ni prueba pertinente [7].

### Advertencias para la revisión

- El umbral 36 pares válidos y 9 horas civiles de cobertura es una decisión local que requiere acta/versión/hashes y justificación técnica propia; no se atribuye a Jain ni TriScale.
- La identificación de P01_S04, P03_S01 y el cambio original TCP 15 s/2 s a 8 s/1 s se respalda con SQLite, eventos, código y auditoría de 17/11 de la investigación, no con referencias bibliográficas.
- Un documento incorporado el 20/11 no adquiere condición de preregistro, aun si precede al cierre del 05/12.
- El repositorio público contiene únicamente métodos depurados; tesis completa, registros crudos, credenciales, firmas y dictámenes permanecen privados.

## Referencias estilo IEEE

[1] R. Jain, *The Art of Computer Systems Performance Analysis: Techniques for Experimental Design, Measurement, Simulation, and Modeling*. Wiley, 1991, ISBN 9780471503361. https://www.cse.wustl.edu/~jain/books/perfbook.htm

[2] R. Jacob, M. Zimmerling, C. A. Boano, L. Vanbever y L. Thiele, “Designing Replicable Networking Experiments With TriScale,” *Journal of Systems Research*, vol. 1, no. 1, 2021, doi: 10.5070/SR31155408. https://doi.org/10.5070/SR31155408

[3] B. Constantine, G. Forget, R. Geib y R. Schrage, “Framework for TCP Throughput Testing,” IETF RFC 6349, 2011. https://www.rfc-editor.org/info/rfc6349

[4] D. B. Rubin, “Inference and missing data,” *Biometrika*, vol. 63, no. 3, pp. 581–592, 1976, doi: 10.1093/biomet/63.3.581. https://doi.org/10.1093/biomet/63.3.581

[5] S. Steegen, F. Tuerlinckx, A. Gelman y W. Vanpaemel, “Increasing Transparency Through a Multiverse Analysis,” *Perspectives on Psychological Science*, vol. 11, no. 5, pp. 702–712, 2016, doi: 10.1177/1745691616658637. https://doi.org/10.1177/1745691616658637

[6] B. A. Nosek, C. R. Ebersole, A. C. DeHaven y D. T. Mellor, “The preregistration revolution,” *PNAS*, vol. 115, no. 11, pp. 2600–2606, 2018, doi: 10.1073/pnas.1708274114. https://doi.org/10.1073/pnas.1708274114

[7] D. Lakens, “Equivalence Tests: A Practical Primer for t Tests, Correlations, and Meta-Analyses,” *Social Psychological and Personality Science*, vol. 8, no. 4, pp. 355–362, 2017, doi: 10.1177/1948550617697177. https://doi.org/10.1177/1948550617697177

**Documento relacionado:** [Anexo XV — sensibilidad y auditoría metodológica](ANEXO_XV_SENSIBILIDAD_REVISION_METODOLOGICA_20261120.md).