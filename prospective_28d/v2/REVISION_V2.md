# Revisión técnica V2 — 19 de octubre de 2026, Perú

Estado: prototipo offline probado; no instalable como ejecutor de producción.

## Cambios y evidencia

35 pruebas pasan en Python normal y con -O: 15 originales y 20 adicionales.
Se incluye salida íntegra del segundo ensayo en PRUEBAS_OPTIMIZACION.txt.

El planificador sustituye assert por excepciones explícitas; rechaza niveles
duplicados, inicio fuera de medianoche, referencia alterada y precondiciones vacías.
La validación del CSV exige igualdad exacta con el calendario generado.
El controlador también compara calendario completo y huella SHA-256 del plan.

controller_sim.py incorpora bloqueo exclusivo Linux, SQLite con intención durable
antes del cambio, detección de ejecución duplicada y detención ante una intención
interrumpida. Los cambios tardíos o saltados no se reproducen automáticamente.
AP y SM se comprueban antes y después; una aplicación parcial bloquea la campaña.
No hay rollback automático: sin conocer la conectividad y secuencia reales, podría
agravar la pérdida de acceso. Se exige conciliación manual.

Se simulan 49 transiciones, incluidas las siete reservas. El fin del calendario
no aplica cambios ni certifica referencia final. Cada resultado declara que no es
elegible para análisis científico. La estabilización de 300 s y tolerancia de 60 s
son valores de laboratorio, NO parámetros aprobados para campo. El simulador no
espera cinco minutos ni verifica estabilidad sostenida: calcula una marca temporal.
No hay cliente Cambium, SSH, iperf, timer ni instalación en CU01.

## Observaciones metodológicas

La rotación de seis ciclos balancea posiciones y franjas, pero no demuestra una
asignación aleatoria independiente de tratamientos por bloque ni balance de
arrastre. No debe describirse como aleatorización completa. El séptimo ciclo deja
cuatro exposiciones en una franja y tres en la otra por configuración.

Las siete aplicaciones temporales por configuración corresponden al mismo enlace;
no equivalen a siete enlaces independientes. La unidad experimental, el análisis
por bloques/ciclos, la dependencia temporal, el efecto de franja y las exclusiones
por transición deben quedar definidos por el Experto 3 antes de iniciar.
Las 84 h nominales por configuración incluyen tiempo de transición/estabilización;
la exposición analizable será menor y debe calcularse con registros reales.
La reserva es referencia programada y no recuperación automática de datos perdidos.
No se modifica la secuencia tras un fallo para aparentar balance completo.

## Pendiente para un ejecutor real

1. Obtener copia del ejecutor actual, interfaces AP/SM y lecturas de configuración,
   sin incluir secretos, para diseñar el adaptador contra evidencia real.
2. Acreditar cierre original y conciliar 27/28 de octubre con calendario y logs.
   Esta revisión no accedió a CU01 ni verificó el estado actual de sus servicios.
3. Aprobar calendario, controles RF, estabilización, tolerancia, criterios de QC,
   manejo de faltantes y protocolo TCP (8/1 y 15/2 permanecen sin resolver).
4. Implementar precheck real: identidad AP/SM, asociación, parámetros RF completos,
   relojes, rutas de gestión y datos, respaldo/restauración, exclusión mutua con
   ejecutor original y pruebas de throughput. Ninguno está certificado aquí.
5. Diseñar y probar recuperación supervisada con acceso alternativo. Persistir
   respuesta real, tiempos efectivos y evidencia; los fallos no se borran.
6. Verificar 48 h de estabilidad mediante observaciones y criterios acordados;
   completar conformidades y habilitar únicamente después del cierre original.

## Reproducción

Desde esta carpeta, en Linux y Python 3.10 o posterior con zona America/Lima:

    python3 -m unittest discover -v
    python3 -O -m unittest discover -v
    python3 prospective_plan.py build
    python3 prospective_plan.py validate

No ejecutar con sudo. No existe comando de activación RF.
El estado de simulación se crea únicamente en el directorio dado a tick(); usar
un directorio temporal exclusivo, nunca rutas del ejecutor vigente.
