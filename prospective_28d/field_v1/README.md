# Luisita: candidato de campo prospectivo — 30/10/2026

Autorización: Carlos solicitó verificar las 48 horas e iniciar la campaña prospectiva. La instalación administrativa se ejecuta directamente en su terminal; la conexión remota rechaza sudo. No es necesaria una nueva autorización científica para esta acción ya solicitada.

Estado de preparación: auditoría y respaldo comprobados; 16 pruebas del controlador pasan en Python normal y optimizado. Las comprobaciones reales de solo lectura verificaron API, ruta, identidad AP/SM, firmware 5.4, referencia 7000/20, potencias 10/3 dBm, ganancias 26/26 dBi y TDD 50/50 de 5 ms. No se presenta una inspección física ni un piloto RF nuevo como realizados.

## Calendario y protocolo

Inicio programado: 30/10/2026 12:00 Perú. Fin: 27/11/2026 12:00 Perú. Siete ciclos: seis exposiciones de 12 horas y una reserva de 24 horas. Son 42 exposiciones factoriales y siete reservas, no 49 réplicas factoriales. Primera configuración 6655/40. Se conserva el orden equilibrado por franjas de la propuesta del 27/10; se concreta retorno a 7000/20 durante reservas y al final. Esta política sustituye para campo la alternativa documental NO_RF_CHANGE, sin alterar documentos históricos.

Perfil: TCP 8 s/omisión 1 s/un flujo, DL y UL secuenciales cada 15 minutos; un intento por dirección, sin reintentos ocultos. DL corresponde a cliente Controlador hacia servidor 192.168.1.4; UL utiliza reverse, conservando la convención de la fuente original. La ruta se comprueba antes de adquirir. Cada oportunidad se registra antes del lanzamiento para evitar duplicados tras reinicio. Los resultados OK/ERROR se conservan en active_throughput_6g con campaign_id LUISITA_PROSPECTIVE_28D_20261030; los datos previos no se recategorizan. Las oportunidades no adquiridas se identifican en events.jsonl.

Exclusión temporal: 30 minutos después de verificación dual efectiva, no del inicio nominal. Una caída de RSSI no invalida por sí sola el tratamiento. Cobertura propuesta congelada: 36 pruebas DL válidas de 48 oportunidades nominales y presencia en nueve horas de la ventana; sensibilidades 50/75/90 %. La clasificación analítica se realiza después sin borrar registros. Emparejamiento RF <=300 s y meteorología secundaria <=120 s como criterios analíticos; se conservan también observaciones que no los satisfacen. No se interpreta ausencia de evento como ausencia del mecanismo. O5 examina estabilidad de contrastes e incertidumbre, sin declarar equivalencia sin margen técnico previamente justificado.

## Instalación administrativa

En el terminal del Controlador, ejecutar:

```bash
sudo bash /home/carlos/Proyectos/Andean-6GHz-Link-Experiment/prospective_28d/field_v1/install.sh
```

La contraseña se ingresa allí, nunca en el chat. El script valida hashes y plazo, deshabilita exclusivamente los tres timers previos de RF/TCP, espera que sus servicios estén libres, recarga el colector RF corregido y comprueba el estado real antes de habilitar el nuevo timer. Mantiene meteorología, sincronización y respaldo. Se detiene si falla un paso. Antes de D0 el controlador solo indica WAITING_START: no cambia RF ni inicia pruebas. No desplaza ni retrodata exposiciones. Si se instala a menos de 15 minutos del inicio, exige regenerar y volver a congelar el calendario.

## Persistencia y seguridad

Un solo servicio y una guardia flock común serializan transiciones y TCP. El diario PENDING se escribe y sincroniza antes del trial; una respuesta perdida o reinicio con intención pendiente bloquea todas las transiciones. No hay repetición automática ni cancelación ciega. La confirmación requiere lectura dual, conectividad y margen; diez comprobaciones consecutivas antes y después. Un inicio de ventana perdido por más de diez minutos detiene el calendario. No se repone ni desplaza automáticamente una ventana fallida. Con HALT o PENDING no eliminar archivos para forzar continuación: cotejar radios, eventos y decisión metodológica.

Los comandos manuales de cambio mediante el orquestador original, su ejecutor y el colector TCP anterior quedan bloqueados al existir prospective_runtime/ENABLED.json. Las credenciales permanecen en sus archivos anteriores fuera de Git. freeze.json identifica el código, protocolo y dependencias usadas. El backend reutiliza el contrato CambiumAPI de la campaña original; V2–V6 de laboratorio no se habilitan ni se parchean para campo.

## Dependencias corregidas

Se respalda primero la base SQLite mediante backup online (1,77 GB), se verifica lectura/quick_check y se calculan SHA-256. Ubicación y resultados: PRESTART_AUDIT_20261030.json. La primera ventana de 48 horas contiene una consulta incompleta; las últimas 48 horas auditadas contienen 574 lecturas duales concordantes. Esta es evidencia muestreada, no certificación de ausencia de toda interrupción breve.

El archivo fuente del colector RF solo mapeaba código 1 a 20 MHz, aunque el histórico contiene código 2 a 40 MHz. Se añade el mapeo verificado 2→40; no se modifica historia. Los diffs exactos de ambas dependencias AtmosLink están en dependency_patches. La comprobación de campo de la primera transición y la primera prueba prospectiva permanece pendiente hasta su ejecución real.

## Comprobar operación

```bash
systemctl status luisita-prospective.timer --no-pager
journalctl -u luisita-prospective.service -n 30 --no-pager
```

Estado y eventos: prospective_runtime/. Un timer habilitado no acredita una transición ni una medición: exigir WINDOW_VERIFIED y los registros TCP del identificador prospectivo. Las reservas se excluyen del análisis factorial por sus intervalos del calendario, aunque también se monitoricen.
