# Orquestador seguro — campaña 6 GHz de Luisita Adalid

Controla exclusivamente el AP Force 4600C de CU01. El SM conserva sus listas de exploración 6475/6655/7000 MHz para 20/40 MHz y se reasocia automáticamente.

## Flujo validado

1. Comprueba AP `192.168.1.8`, SM `192.168.1.9` y RPi `192.168.1.4`.
2. Lee `get_param` con `act=config_regular` y obtiene dinámicamente `template_props.config_id`.
3. Envía `set_param` con `trial=1`; `wirelessInterfaceHTMode` usa `1` para 20 MHz y `2` para 40 MHz.
4. Espera hasta 180 s y exige 10 sondeos consecutivos correctos.
5. Verifica la configuración y confirma con `set_trial_param`, `apply=true`.
6. Si ocurre un error antes de confirmar, cancela el trial mediante `apply=false`; si esa solicitud falla, permanece disponible la reversión automática a los 300 s.
7. Si ocurre un error después de confirmar, aplica explícitamente la frecuencia y el ancho anteriores mediante un nuevo trial verificado.
8. Registra el resultado y el escenario activo mediante escritura atómica.

`centerFrequency2` nunca se modifica. No se guardan contraseñas ni tokens.

## Validación sin tocar el radio

```bash
cd ~/Proyectos/EstacionMeteorologica/luisita_campaign
python3 -m unittest -v test_campaign_orchestrator
python3 campaign_orchestrator.py validate --config campaign_plan.template.json
python3 campaign_orchestrator.py plan --config campaign_plan.template.json
python3 campaign_orchestrator.py switch --config campaign_plan.template.json --scenario F7000_B40 --dry-run
```

## Transición real supervisada

Copie solamente el `stok` de la URL de una sesión administrativa activa:

```bash
read -rsp 'STOK activo: ' CAMBIUM_AP_STOK; echo
export CAMBIUM_AP_STOK
python3 campaign_orchestrator.py switch --config campaign_plan.template.json --scenario F7000_B40
unset CAMBIUM_AP_STOK
```

No realice cambios sin supervisión hasta validar el inicio de sesión automático. Los eventos quedan en `campaign_runtime/campaign_events.jsonl`, el estado confirmado en `campaign_state.json` y el calendario en `campaign_schedule.csv`.

Escenarios: `F6475_B20`, `F6475_B40`, `F6655_B20`, `F6655_B40`, `F7000_B20` y `F7000_B40`. Cada tratamiento totaliza siete días en bloques de 3, 2 y 2 días.
