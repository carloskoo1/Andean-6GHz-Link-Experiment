# Propuesta de protocolo prospectivo — 27/10/2026

Versión documental V1 al 27/10/2026, definida antes de adquirir datos prospectivos. Esta especificación hace explícitas las decisiones propuestas y no declara habilitado el ejecutor real. Debe cotejarse contra su implementación y aprobarse operativamente antes de D0; no exige reabrir la conservación de S16 ni cambiar los datos originales.

Configuraciones calendario y reservas

Siete ciclos de cuatro días; seis exposiciones de 12 horas y reserva de 24 horas por ciclo. Se conserva el orden candidato equilibrado 3/4 o 4/3 entre franjas y no se reordena por clima. Durante reservas se propone retorno verificado a 7000/20, como candidato V5–V6; la implementación y recuperación real deben verificarse. La reserva no aporta réplicas factoriales.

Medición y unidad de análisis

Perfil propuesto TCP 8 s/omisión 1 s, un flujo, DL y UL secuenciales, oportunidad cada 15 minutos, sin coexistir con pruebas activas que compitan por el enlace. Respuesta primaria: mediana TCP DL por exposición. Conservar ambos sentidos, fallos, rutas, intervalos efectivos y salida original. La aplicación del perfil y la exclusividad de carga deben comprobarse antes de iniciar.

Inicio válido y estabilización

Se propone excluir los primeros 30 minutos posteriores a la confirmación dual y al SWITCH_COMMITTED, como margen operativo fijo que contiene seis oportunidades nominales de telemetría de cinco minutos. No es un tiempo físico universal ni se ha validado aún para este ejecutor; la duración debe verificarse técnicamente antes de congelar. Una señal baja por sí sola no invalida un tratamiento correctamente aplicado ni autoriza esperar a obtener buen throughput.

Cobertura y datos faltantes

Regla propuesta previa a nuevos datos: al menos 36 pruebas DL técnicamente válidas de 48 oportunidades nominales (75 %) y presencia de medición en al menos nueve horas civiles de la ventana de 12 horas. Se limita a la prospectiva y no se aplica retroactivamente al conjunto original. Es una tolerancia operativa de hasta un cuarto de oportunidades, no un umbral validado de ausencia de sesgo. Conservar cobertura por mitad de ventana y reportar sensibilidades 50/75/90 %; no seleccionar el umbral que favorezca una hipótesis. Si falta cobertura, registrar la exposición como incompleta y no imputar el resultado.

Configuración y emparejamientos

Exigir estado OK, protocolo/ruta homogéneos, prueba enteramente dentro de exposición elegible, configuración AP/SM coincidente y RF asociada a ≤300 s. Registrar separación y sensibilidad ≤120 s. Para meteorología secundaria usar observación más cercana por extremo a ≤120 s, con banderas válidas. Falta meteorológica no invalida por sí sola la respuesta primaria TCP.

Contrastes y concordancia

Modelo por exposición con factorial frecuencia×ancho, ciclo y franja; comprobar rango y residuos. Contrastes marginales igual ponderados y familia global/frecuencia/ancho/interacción con Holm. Comparar los mismos contrastes por fase, diferencias e incertidumbre. Los IC convencionales se etiquetarán según supuestos y se examinará sensibilidad a dependencia y ciclo. Sin margen técnico justificado no se declarará equivalencia. Si pérdidas o rango impiden el ajuste, presentar estimaciones descriptivas y declarar lo no identificable.

Seguimiento de episodios

Conservar todas las series y condiciones antes, durante y después, incluidos controles sin caída. Usar resultados secundarios continuos de RSSI/SNR DL/UL, tasas y TCP, y las reglas de análogos del informe retrospectivo. No añadir umbrales confirmatorios de evento después de ver resultados. No afirmar ausencia del mecanismo si no reaparece durante los 28 días.

Relojes adquisición y trazabilidad

El Controlador reporta NTP sincronizado y America/Lima. En una adquisición del 27/10 a las 19:22:57 UTC, AP reporta 28/10 06:22:56 y SM 27/10 19:22:55; las zonas de los radios no están verificadas. Utilizar tiempos del colector, preservar originales y conciliar cnMaestro sin modificar relojes durante este análisis. El auditor pasivo comprobó 287 RF duales y 190 TCP OK en las 24 horas al corte de 14:27:18 Perú, con meteorología válida de ambos extremos; no acredita por sí solo seguridad de campo.

Congelación e implementación

El documento propone parámetros explícitos, pero el calendario efectivo, los parámetros del ejecutor, la estabilización y cobertura requieren prueba de compatibilidad y aceptación antes de iniciar. Conservar versión y hash del protocolo, calendario y referencia horaria; registrar cambios posteriores sin sobrescritura. El ejecutor de laboratorio sigue sin habilitación RF. El cierre documental no sustituye la verificación técnica restante.
