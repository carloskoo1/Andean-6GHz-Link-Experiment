# Versión inicial y entrada compatible

La ejecución de campo activa es ../field_v2/. El intento original del 30/10 falló antes de obtener TCP prospectivo y su evidencia se conserva en ../recovery_20261031/ y docs/validation_28d/incident_20261031/.

controller.py es ahora únicamente el despachador compatible con la unidad systemd ya instalada. freeze.json, plan.json y el instalador de esta carpeta se conservan como históricos de V1; no describen el calendario activo ni deben reutilizarse para reinstalar. El manifiesto operativo está en ../field_v2/freeze.json e incluye el hash del despachador.
