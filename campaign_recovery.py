#!/usr/bin/env python3
"""
AtmosLink campaign recovery state classification.

This module initially contains only pure decision logic.
It performs no RF changes, PoE operations, HTTP requests or subprocess calls.
"""


def classify_health(
    *,
    ap_ping,
    ap_https,
    api_ok,
    sm_ping,
    rpi_ping,
    safe_abort,
    transition_failed,
):
    """
    Classify the observed campaign/link state.

    RECOVERY_REQUIRED is deliberately conservative. It requires:
      - persistent SAFE_ABORT;
      - evidence of a failed transition;
      - AP reachable by ICMP;
      - AP basic HTTPS reachable;
      - authenticated API unhealthy;
      - SM unreachable;
      - remote Raspberry Pi unreachable.

    Even RECOVERY_REQUIRED does not authorize a PoE operation. It only
    indicates that the observed signature warrants entering the recovery
    workflow.
    """

    # Persistent SAFE_ABORT always dominates normal classifications.
    if safe_abort:
        incident_signature = all(
            (
                transition_failed,
                ap_ping,
                ap_https,
                not api_ok,
                not sm_ping,
                not rpi_ping,
            )
        )

        if incident_signature:
            return "RECOVERY_REQUIRED"

        return "SAFE_ABORT"

    # Fully healthy end-to-end state.
    if ap_ping and ap_https and api_ok and sm_ping and rpi_ping:
        return "HEALTHY"

    # Management API degraded while the complete data path remains alive.
    # This must never be interpreted as justification for a power cycle.
    if ap_ping and ap_https and not api_ok and sm_ping and rpi_ping:
        return "API_DEGRADED"

    # Any other incomplete connectivity condition is degraded but does not
    # independently authorize recovery.
    return "LINK_DEGRADED"


def recovery_eligible(
    *,
    health_state,
    switch_identity_ok,
    target_port,
    target_description,
    target_delivering_power,
    protected_port,
    protected_description,
):
    """
    Determine whether the observed infrastructure is eligible to enter
    the supervised PoE recovery procedure.

    This function performs no recovery action.

    Eligibility requires all safety invariants to hold simultaneously.
    Any ambiguity fails closed.
    """

    if health_state != "RECOVERY_REQUIRED":
        return False

    if not switch_identity_ok:
        return False

    # The 6 GHz CU01 AP is exclusively connected to PoE port 6.
    if target_port != 6:
        return False

    if target_description != "Cunacales6":
        return False

    # A recovery power cycle only makes sense if the verified target
    # is currently receiving PoE.
    if not target_delivering_power:
        return False

    # Port 3 is the 5.8 GHz AP and is explicitly protected.
    if protected_port != 3:
        return False

    if protected_description != "Cunacales":
        return False

    # Defensive invariant: target and protected ports can never coincide.
    if target_port == protected_port:
        return False

    return True


def build_diagnostic(
    config,
    *,
    ping_probe,
    https_probe,
    api_probe,
    safe_abort,
    transition_failed,
):
    """
    Collect read-only observations through injected probes and classify
    the resulting operational state.

    Probe exceptions are converted into negative observations and
    recorded in errors. No probe exception may abort the diagnostic.

    The function has no RF or PoE mutation capability.
    """
    network = config["network"]
    ap_ip = network["ap_ip"]
    sm_ip = network["sm_ip"]
    rpi_ip = network["rpi_ip"]

    errors = {}

    def probe(name, function, *args):
        try:
            return bool(function(*args))
        except Exception as exc:
            errors[name] = (
                f"{type(exc).__name__}: {exc}"
            )
            return False

    observations = {
        "ap_ping": probe(
            "ap_ping",
            ping_probe,
            ap_ip,
        ),
        "ap_https": probe(
            "ap_https",
            https_probe,
            ap_ip,
        ),
        "api_ok": probe(
            "api",
            api_probe,
        ),
        "sm_ping": probe(
            "sm_ping",
            ping_probe,
            sm_ip,
        ),
        "rpi_ping": probe(
            "rpi_ping",
            ping_probe,
            rpi_ip,
        ),
        "safe_abort": bool(safe_abort),
        "transition_failed": bool(transition_failed),
    }

    health_state = classify_health(
        ap_ping=observations["ap_ping"],
        ap_https=observations["ap_https"],
        api_ok=observations["api_ok"],
        sm_ping=observations["sm_ping"],
        rpi_ping=observations["rpi_ping"],
        safe_abort=observations["safe_abort"],
        transition_failed=observations["transition_failed"],
    )

    return {
        "health_state": health_state,
        "observations": observations,
        "errors": errors,
    }

def load_safe_abort(path):
    """
    Read persistent SAFE_ABORT state using fail-closed semantics.

    ABSENT:
        No SAFE_ABORT file exists; recovery interlock is not active.

    Valid JSON:
        SAFE_ABORT exists and is active.

    UNREADABLE:
        SAFE_ABORT exists but cannot be interpreted safely. It remains
        active so that corruption can never silently re-enable RF actions.
    """
    import json
    from pathlib import Path

    path = Path(path)

    if not path.exists():
        return {
            "exists": False,
            "readable": False,
            "active": False,
            "status": "ABSENT",
            "data": None,
        }

    try:
        data = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError(
                "SAFE_ABORT root must be a JSON object"
            )

        status = str(
            data.get("status", "UNKNOWN")
        ).strip() or "UNKNOWN"

        return {
            "exists": True,
            "readable": True,
            "active": True,
            "status": status,
            "data": data,
        }

    except Exception as exc:
        return {
            "exists": True,
            "readable": False,
            "active": True,
            "status": "UNREADABLE",
            "data": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def run_diagnostic(
    config_path,
    *,
    ping_probe,
    https_probe,
    api_probe,
):
    """
    Run a read-only recovery diagnostic using persistent campaign state.

    This function performs no RF or PoE mutations. Network observations
    are obtained only through the injected probe functions.
    """
    import json
    from pathlib import Path

    config_path = Path(config_path)

    config = json.loads(
        config_path.read_text(encoding="utf-8")
    )

    output_dir = Path(config["outputs"]["directory"])
    if not output_dir.is_absolute():
        output_dir = config_path.parent / output_dir

    safe_abort_state = load_safe_abort(
        output_dir / "SAFE_ABORT.json"
    )

    failure_path = output_dir / "executor_failure.json"
    transition_failed = False

    if failure_path.exists():
        try:
            failure = json.loads(
                failure_path.read_text(encoding="utf-8")
            )
            transition_failed = bool(
                failure.get("error")
            )
        except Exception:
            # Fail closed: an unreadable failure record is still
            # evidence that the previous transition state is uncertain.
            transition_failed = True

    result = build_diagnostic(
        config,
        ping_probe=ping_probe,
        https_probe=https_probe,
        api_probe=api_probe,
        safe_abort=safe_abort_state["active"],
        transition_failed=transition_failed,
    )

    # An unreadable safety interlock can never authorize recovery.
    # Preserve SAFE_ABORT until its persistent state is understood.
    if (
        safe_abort_state["active"]
        and not safe_abort_state["readable"]
    ):
        result["health_state"] = "SAFE_ABORT"

    result["safe_abort"] = safe_abort_state

    return result


def diagnostic_exit_code(health_state):
    """
    Map recovery diagnostic states to process exit codes.

    0: operationally healthy
    2: degraded observation/connectivity state
    3: safety interlock, recovery required, or unknown state

    Unknown states fail closed.
    """
    if health_state == "HEALTHY":
        return 0

    if health_state in {
        "API_DEGRADED",
        "LINK_DEGRADED",
    }:
        return 2

    return 3


# ---------------------------------------------------------------------------
# Concrete read-only probes
# ---------------------------------------------------------------------------

import ssl
import urllib.error
import urllib.request
from pathlib import Path

from campaign_orchestrator import CambiumAPI


def https_probe(
    ip,
    *,
    scheme="https",
    timeout=15,
    tls_verify=True,
):
    """
    Check whether the AP HTTP(S) endpoint is reachable.

    Any HTTP response, including an HTTP error status, proves that the
    endpoint is reachable. Transport exceptions are intentionally allowed
    to propagate so build_diagnostic() can record them as probe errors.

    This function performs no RF or device configuration changes.
    """
    context = None

    if scheme == "https" and not tls_verify:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    request = urllib.request.Request(
        f"{scheme}://{ip}/",
        method="GET",
    )

    try:
        response = urllib.request.urlopen(
            request,
            timeout=timeout,
            context=context,
        )
        response.close()
        return True

    except urllib.error.HTTPError:
        return True


def cambium_api_probe(config):
    """
    Validate authenticated Cambium API availability.

    CambiumAPI.authenticate() performs login, obtains the STOK and
    validates test_connect. This diagnostic probe deliberately does not
    call read(), trial() or finish().
    """
    api = CambiumAPI(config)

    credentials = Path(
        config["api"]["credentials_file"]
    ).expanduser()

    api.authenticate(credentials)

    return True


# ---------------------------------------------------------------------------
# Read-only live diagnostic and CLI
# ---------------------------------------------------------------------------

import argparse
import json

from campaign_orchestrator import load_config, ping


def run_live_diagnostic(config_path):
    """
    Execute the recovery diagnostic against the live infrastructure.

    This path is strictly read-only:
    - ICMP reachability
    - HTTP(S) reachability
    - Cambium authentication + test_connect
    - persistent local campaign state

    It has no RF or PoE mutation capability.
    """
    config_path = Path(config_path)
    config = load_config(config_path)

    api_cfg = config["api"]

    def configured_https_probe(ip):
        return https_probe(
            ip,
            scheme=api_cfg.get("scheme", "https"),
            timeout=api_cfg.get(
                "request_timeout_seconds",
                15,
            ),
            tls_verify=api_cfg.get(
                "tls_verify",
                True,
            ),
        )

    def configured_api_probe():
        return cambium_api_probe(config)

    return run_diagnostic(
        config_path,
        ping_probe=ping,
        https_probe=configured_https_probe,
        api_probe=configured_api_probe,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "AtmosLink campaign recovery diagnostic "
            "(read-only)."
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    diagnose = subparsers.add_parser(
        "diagnose",
        help="Run read-only operational diagnosis.",
    )

    diagnose.add_argument(
        "--config",
        required=True,
        type=Path,
        help="Campaign configuration JSON.",
    )

    args = parser.parse_args(argv)

    if args.command == "diagnose":
        result = run_live_diagnostic(args.config)

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )

        return diagnostic_exit_code(
            result.get(
                "health_state",
                "UNKNOWN_STATE",
            )
        )

    return 3


if __name__ == "__main__":
    raise SystemExit(main())


# ---------------------------------------------------------------------------
# Config-driven recovery eligibility
# ---------------------------------------------------------------------------

def configured_recovery_eligible(
    *,
    recovery_config,
    health_state,
    observed_switch_mac,
    observed_target_port,
    observed_target_description,
    observed_target_delivering_power,
    observed_protected_port,
    observed_protected_description,
):
    """
    Determine whether the observed cnMatrix path matches the recovery
    topology declared in configuration.

    This function only evaluates eligibility. It does not authorize or
    perform any recovery action.
    """
    if health_state != "RECOVERY_REQUIRED":
        return False

    try:
        cnmatrix = recovery_config["cnmatrix"]
        target = recovery_config["target"]
        protected = recovery_config["protected"]

        expected_mac = str(
            cnmatrix["expected_mac"]
        ).strip().upper()

        observed_mac = str(
            observed_switch_mac
        ).strip().upper()

        expected_target_port = int(
            target["port"]
        )
        expected_protected_port = int(
            protected["port"]
        )

        expected_target_description = str(
            target["description"]
        ).strip()

        expected_protected_description = str(
            protected["description"]
        ).strip()

        observed_target_port = int(
            observed_target_port
        )
        observed_protected_port = int(
            observed_protected_port
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        return False

    if observed_mac != expected_mac:
        return False

    if observed_target_port != expected_target_port:
        return False

    if (
        str(observed_target_description).strip()
        != expected_target_description
    ):
        return False

    if not observed_target_delivering_power:
        return False

    if observed_protected_port != expected_protected_port:
        return False

    if (
        str(observed_protected_description).strip()
        != expected_protected_description
    ):
        return False

    # Target and protected paths must always be distinct.
    if expected_target_port == expected_protected_port:
        return False

    if observed_target_port == observed_protected_port:
        return False

    return True
