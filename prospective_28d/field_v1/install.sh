#!/bin/bash
set -euo pipefail
TASK_ROOT=/home/carlos/Proyectos/Andean-6GHz-Link-Experiment
TASK_RELEASE="$TASK_ROOT/prospective_28d/field_v1"
TASK_PYTHON=/home/carlos/Proyectos/EstacionMeteorologica/venv/bin/python
if [ "$(id -u)" -ne 0 ]; then
  echo 'Ejecutar este archivo con sudo en el terminal del Controlador.' >&2
  exit 1
fi
cd "$TASK_ROOT"
"$TASK_PYTHON" "$TASK_RELEASE/controller.py" validate
"$TASK_PYTHON" - "$TASK_RELEASE" <<'PY'
import sys,json,hashlib,datetime
from pathlib import Path
p=Path(sys.argv[1]);plan=json.loads((p/'plan.json').read_text())
for name,h in json.loads((p/'freeze.json').read_text()).items():
 if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=h:raise SystemExit('Hash no coincide: '+name)
start=datetime.datetime.fromisoformat(plan['windows'][0]['start_local'])
if datetime.datetime.now(datetime.timezone.utc)>=start-datetime.timedelta(minutes=15):
 raise SystemExit('Inicio demasiado próximo o vencido: regenerar calendario antes de instalar.')
print('Hashes y plazo de instalación verificados.')
PY
systemctl disable --now andean-campaign.timer andean-throughput.timer atmoslink-throughput-6g.timer
for task_unit in andean-campaign.service andean-throughput.service atmoslink-throughput-6g.service; do
  task_status=$(systemctl is-active "$task_unit" || true)
  if [ "$task_status" != inactive ] && [ "$task_status" != failed ]; then
    echo "Servicio aún ocupado: $task_unit; esperar su finalización." >&2
    exit 1
  fi
done
install -d -m 0750 -o carlos -g carlos "$TASK_ROOT/prospective_runtime"
systemctl restart atmoslink-radio-config-6g.service
runuser -u carlos -- "$TASK_PYTHON" "$TASK_RELEASE/controller.py" preflight
install -m 0644 "$TASK_RELEASE/luisita-prospective.service" /etc/systemd/system/luisita-prospective.service
install -m 0644 "$TASK_RELEASE/luisita-prospective.timer" /etc/systemd/system/luisita-prospective.timer
runuser -u carlos -- "$TASK_PYTHON" - "$TASK_ROOT/prospective_runtime" <<'PY'
import sys,json,datetime,os
from pathlib import Path
p=Path(sys.argv[1]);out=p/'ENABLED.json'
if out.exists():raise SystemExit('Ya existe una habilitación: revisar antes de reinstalar.')
with out.open('x') as f:
 json.dump({'enabled_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'authorization':'Carlos: verificar e iniciar campaña prospectiva, conversación 30/10/2026',
            'automatic_RF_before_D0':False},f,indent=2);f.flush();os.fsync(f.fileno())
PY
systemctl daemon-reload
systemctl enable --now luisita-prospective.timer
systemctl start luisita-prospective.service
systemctl status luisita-prospective.timer --no-pager
echo 'INSTALACIÓN COMPLETADA. El primer tick antes de D0 debe indicar WAITING_START.'
echo 'No se ha adelantado ni retrodatado ninguna exposición.'
