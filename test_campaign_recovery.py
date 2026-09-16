#!/usr/bin/env python3

import unittest

from campaign_recovery import classify_health


class RecoveryClassificationTests(unittest.TestCase):

    def test_healthy(self):
        result = classify_health(
            ap_ping=True,
            ap_https=True,
            api_ok=True,
            sm_ping=True,
            rpi_ping=True,
            safe_abort=False,
            transition_failed=False,
        )
        self.assertEqual("HEALTHY", result)

    def test_api_degraded_is_not_recovery_required(self):
        result = classify_health(
            ap_ping=True,
            ap_https=True,
            api_ok=False,
            sm_ping=True,
            rpi_ping=True,
            safe_abort=False,
            transition_failed=False,
        )
        self.assertEqual("API_DEGRADED", result)

    def test_remote_link_degraded_without_safe_abort(self):
        result = classify_health(
            ap_ping=True,
            ap_https=True,
            api_ok=True,
            sm_ping=False,
            rpi_ping=False,
            safe_abort=False,
            transition_failed=False,
        )
        self.assertEqual("LINK_DEGRADED", result)

    def test_incident_signature_requires_recovery(self):
        result = classify_health(
            ap_ping=True,
            ap_https=True,
            api_ok=False,
            sm_ping=False,
            rpi_ping=False,
            safe_abort=True,
            transition_failed=True,
        )
        self.assertEqual("RECOVERY_REQUIRED", result)

    def test_safe_abort_without_complete_signature_fails_closed(self):
        result = classify_health(
            ap_ping=True,
            ap_https=True,
            api_ok=False,
            sm_ping=True,
            rpi_ping=True,
            safe_abort=True,
            transition_failed=True,
        )
        self.assertEqual("SAFE_ABORT", result)

    def test_no_recovery_if_ap_itself_is_unreachable(self):
        result = classify_health(
            ap_ping=False,
            ap_https=False,
            api_ok=False,
            sm_ping=False,
            rpi_ping=False,
            safe_abort=True,
            transition_failed=True,
        )
        self.assertEqual("SAFE_ABORT", result)


if __name__ == "__main__":
    unittest.main()


class RecoveryEligibilityTests(unittest.TestCase):

    def test_verified_cnmatrix_path_is_recovery_eligible(self):
        from campaign_recovery import recovery_eligible

        self.assertTrue(
            recovery_eligible(
                health_state="RECOVERY_REQUIRED",
                switch_identity_ok=True,
                target_port=6,
                target_description="Cunacales6",
                target_delivering_power=True,
                protected_port=3,
                protected_description="Cunacales",
            )
        )

    def test_wrong_switch_fails_closed(self):
        from campaign_recovery import recovery_eligible

        self.assertFalse(
            recovery_eligible(
                health_state="RECOVERY_REQUIRED",
                switch_identity_ok=False,
                target_port=6,
                target_description="Cunacales6",
                target_delivering_power=True,
                protected_port=3,
                protected_description="Cunacales",
            )
        )

    def test_wrong_target_port_fails_closed(self):
        from campaign_recovery import recovery_eligible

        self.assertFalse(
            recovery_eligible(
                health_state="RECOVERY_REQUIRED",
                switch_identity_ok=True,
                target_port=3,
                target_description="Cunacales6",
                target_delivering_power=True,
                protected_port=3,
                protected_description="Cunacales",
            )
        )

    def test_wrong_target_description_fails_closed(self):
        from campaign_recovery import recovery_eligible

        self.assertFalse(
            recovery_eligible(
                health_state="RECOVERY_REQUIRED",
                switch_identity_ok=True,
                target_port=6,
                target_description="UNKNOWN",
                target_delivering_power=True,
                protected_port=3,
                protected_description="Cunacales",
            )
        )

    def test_target_without_power_fails_closed(self):
        from campaign_recovery import recovery_eligible

        self.assertFalse(
            recovery_eligible(
                health_state="RECOVERY_REQUIRED",
                switch_identity_ok=True,
                target_port=6,
                target_description="Cunacales6",
                target_delivering_power=False,
                protected_port=3,
                protected_description="Cunacales",
            )
        )

    def test_wrong_protected_port_identity_fails_closed(self):
        from campaign_recovery import recovery_eligible

        self.assertFalse(
            recovery_eligible(
                health_state="RECOVERY_REQUIRED",
                switch_identity_ok=True,
                target_port=6,
                target_description="Cunacales6",
                target_delivering_power=True,
                protected_port=3,
                protected_description="UNKNOWN",
            )
        )

    def test_healthy_link_is_never_recovery_eligible(self):
        from campaign_recovery import recovery_eligible

        self.assertFalse(
            recovery_eligible(
                health_state="HEALTHY",
                switch_identity_ok=True,
                target_port=6,
                target_description="Cunacales6",
                target_delivering_power=True,
                protected_port=3,
                protected_description="Cunacales",
            )
        )


class RecoveryDiagnosticTests(unittest.TestCase):

    def test_build_diagnostic_healthy(self):
        from campaign_recovery import build_diagnostic

        config = {
            "network": {
                "ap_ip": "192.168.1.8",
                "sm_ip": "192.168.1.9",
                "rpi_ip": "192.168.1.4",
            }
        }

        def fake_ping(ip):
            return True

        def fake_https(ip):
            return True

        def fake_api():
            return True

        result = build_diagnostic(
            config,
            ping_probe=fake_ping,
            https_probe=fake_https,
            api_probe=fake_api,
            safe_abort=False,
            transition_failed=False,
        )

        self.assertEqual("HEALTHY", result["health_state"])
        self.assertTrue(result["observations"]["ap_ping"])
        self.assertTrue(result["observations"]["ap_https"])
        self.assertTrue(result["observations"]["api_ok"])
        self.assertTrue(result["observations"]["sm_ping"])
        self.assertTrue(result["observations"]["rpi_ping"])

    def test_build_diagnostic_incident_signature(self):
        from campaign_recovery import build_diagnostic

        config = {
            "network": {
                "ap_ip": "192.168.1.8",
                "sm_ip": "192.168.1.9",
                "rpi_ip": "192.168.1.4",
            }
        }

        def fake_ping(ip):
            return ip == "192.168.1.8"

        def fake_https(ip):
            return True

        def fake_api():
            return False

        result = build_diagnostic(
            config,
            ping_probe=fake_ping,
            https_probe=fake_https,
            api_probe=fake_api,
            safe_abort=True,
            transition_failed=True,
        )

        self.assertEqual(
            "RECOVERY_REQUIRED",
            result["health_state"],
        )
        self.assertTrue(result["observations"]["ap_ping"])
        self.assertFalse(result["observations"]["sm_ping"])
        self.assertFalse(result["observations"]["rpi_ping"])
        self.assertFalse(result["observations"]["api_ok"])

    def test_build_diagnostic_api_degraded(self):
        from campaign_recovery import build_diagnostic

        config = {
            "network": {
                "ap_ip": "192.168.1.8",
                "sm_ip": "192.168.1.9",
                "rpi_ip": "192.168.1.4",
            }
        }

        result = build_diagnostic(
            config,
            ping_probe=lambda ip: True,
            https_probe=lambda ip: True,
            api_probe=lambda: False,
            safe_abort=False,
            transition_failed=False,
        )

        self.assertEqual(
            "API_DEGRADED",
            result["health_state"],
        )


class RecoveryPersistentStateTests(unittest.TestCase):

    def test_load_safe_abort_absent(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from campaign_recovery import load_safe_abort

        with TemporaryDirectory() as tmp:
            result = load_safe_abort(Path(tmp) / "SAFE_ABORT.json")

        self.assertFalse(result["exists"])
        self.assertFalse(result["readable"])
        self.assertEqual("ABSENT", result["status"])

    def test_load_safe_abort_valid(self):
        import json
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from campaign_recovery import load_safe_abort

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "SAFE_ABORT.json"
            path.write_text(
                json.dumps({
                    "status": "RECOVERY_REQUIRED",
                    "automatic_rf_transitions_blocked": True,
                }),
                encoding="utf-8",
            )

            result = load_safe_abort(path)

        self.assertTrue(result["exists"])
        self.assertTrue(result["readable"])
        self.assertEqual(
            "RECOVERY_REQUIRED",
            result["status"],
        )

    def test_load_safe_abort_malformed_fails_closed(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from campaign_recovery import load_safe_abort

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "SAFE_ABORT.json"
            path.write_text(
                "{esto-no-es-json",
                encoding="utf-8",
            )

            result = load_safe_abort(path)

        self.assertTrue(result["exists"])
        self.assertFalse(result["readable"])
        self.assertEqual("UNREADABLE", result["status"])

    def test_unreadable_safe_abort_must_be_considered_active(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from campaign_recovery import load_safe_abort

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "SAFE_ABORT.json"
            path.write_text(
                "CORRUPT",
                encoding="utf-8",
            )

            result = load_safe_abort(path)

        self.assertTrue(result["active"])


class RecoveryRunDiagnosticTests(unittest.TestCase):

    def test_run_diagnostic_uses_persistent_state(self):
        import json
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from campaign_recovery import run_diagnostic

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = root / "runtime"
            runtime.mkdir()

            config = {
                "network": {
                    "ap_ip": "192.168.1.8",
                    "sm_ip": "192.168.1.9",
                    "rpi_ip": "192.168.1.4",
                },
                "outputs": {
                    "directory": "runtime",
                },
            }

            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(config),
                encoding="utf-8",
            )

            (runtime / "executor_failure.json").write_text(
                json.dumps({
                    "error": "simulated transition failure"
                }),
                encoding="utf-8",
            )

            result = run_diagnostic(
                config_path,
                ping_probe=lambda ip: True,
                https_probe=lambda ip: True,
                api_probe=lambda: True,
            )

        self.assertEqual("HEALTHY", result["health_state"])
        self.assertFalse(result["observations"]["safe_abort"])
        self.assertTrue(
            result["observations"]["transition_failed"]
        )

    def test_run_diagnostic_valid_safe_abort_is_active(self):
        import json
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from campaign_recovery import run_diagnostic

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = root / "runtime"
            runtime.mkdir()

            config = {
                "network": {
                    "ap_ip": "192.168.1.8",
                    "sm_ip": "192.168.1.9",
                    "rpi_ip": "192.168.1.4",
                },
                "outputs": {
                    "directory": "runtime",
                },
            }

            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(config),
                encoding="utf-8",
            )

            (runtime / "SAFE_ABORT.json").write_text(
                json.dumps({
                    "status": "RECOVERY_REQUIRED"
                }),
                encoding="utf-8",
            )

            (runtime / "executor_failure.json").write_text(
                json.dumps({
                    "error": "simulated transition failure"
                }),
                encoding="utf-8",
            )

            result = run_diagnostic(
                config_path,
                ping_probe=lambda ip: ip == "192.168.1.8",
                https_probe=lambda ip: True,
                api_probe=lambda: False,
            )

        self.assertEqual(
            "RECOVERY_REQUIRED",
            result["health_state"],
        )
        self.assertTrue(result["safe_abort"]["active"])
        self.assertEqual(
            "RECOVERY_REQUIRED",
            result["safe_abort"]["status"],
        )

    def test_run_diagnostic_malformed_safe_abort_fails_closed(self):
        import json
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from campaign_recovery import run_diagnostic

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = root / "runtime"
            runtime.mkdir()

            config = {
                "network": {
                    "ap_ip": "192.168.1.8",
                    "sm_ip": "192.168.1.9",
                    "rpi_ip": "192.168.1.4",
                },
                "outputs": {
                    "directory": "runtime",
                },
            }

            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(config),
                encoding="utf-8",
            )

            (runtime / "SAFE_ABORT.json").write_text(
                "CORRUPT",
                encoding="utf-8",
            )

            result = run_diagnostic(
                config_path,
                ping_probe=lambda ip: True,
                https_probe=lambda ip: True,
                api_probe=lambda: True,
            )

        self.assertEqual("SAFE_ABORT", result["health_state"])
        self.assertTrue(result["safe_abort"]["active"])
        self.assertFalse(result["safe_abort"]["readable"])
        self.assertEqual(
            "UNREADABLE",
            result["safe_abort"]["status"],
        )


class RecoveryExitCodeTests(unittest.TestCase):

    def test_healthy_exit_zero(self):
        from campaign_recovery import diagnostic_exit_code
        self.assertEqual(0, diagnostic_exit_code("HEALTHY"))

    def test_degraded_exit_two(self):
        from campaign_recovery import diagnostic_exit_code

        for state in (
            "API_DEGRADED",
            "LINK_DEGRADED",
        ):
            with self.subTest(state=state):
                self.assertEqual(
                    2,
                    diagnostic_exit_code(state),
                )

    def test_safety_states_exit_three(self):
        from campaign_recovery import diagnostic_exit_code

        for state in (
            "SAFE_ABORT",
            "RECOVERY_REQUIRED",
        ):
            with self.subTest(state=state):
                self.assertEqual(
                    3,
                    diagnostic_exit_code(state),
                )

    def test_unknown_state_fails_closed(self):
        from campaign_recovery import diagnostic_exit_code
        self.assertEqual(
            3,
            diagnostic_exit_code("UNKNOWN_STATE"),
        )


class RecoveryProbeFailureTests(unittest.TestCase):

    def test_api_probe_exception_fails_closed(self):
        from campaign_recovery import build_diagnostic

        def broken_api():
            raise RuntimeError("simulated API timeout")

        result = build_diagnostic(
            {
                "network": {
                    "ap_ip": "192.168.1.8",
                    "sm_ip": "192.168.1.9",
                    "rpi_ip": "192.168.1.4",
                }
            },
            ping_probe=lambda ip: True,
            https_probe=lambda ip: True,
            api_probe=broken_api,
            safe_abort=False,
            transition_failed=False,
        )

        self.assertEqual(
            "API_DEGRADED",
            result["health_state"],
        )
        self.assertFalse(result["observations"]["api_ok"])
        self.assertIn("api", result["errors"])

    def test_ping_probe_exception_becomes_link_degraded(self):
        from campaign_recovery import build_diagnostic

        def ping_probe(ip):
            if ip == "192.168.1.9":
                raise RuntimeError("simulated ICMP error")
            return True

        result = build_diagnostic(
            {
                "network": {
                    "ap_ip": "192.168.1.8",
                    "sm_ip": "192.168.1.9",
                    "rpi_ip": "192.168.1.4",
                }
            },
            ping_probe=ping_probe,
            https_probe=lambda ip: True,
            api_probe=lambda: True,
            safe_abort=False,
            transition_failed=False,
        )

        self.assertEqual(
            "LINK_DEGRADED",
            result["health_state"],
        )
        self.assertFalse(result["observations"]["sm_ping"])
        self.assertIn("sm_ping", result["errors"])

    def test_https_probe_exception_becomes_link_degraded(self):
        from campaign_recovery import build_diagnostic

        def broken_https(ip):
            raise RuntimeError("simulated HTTPS error")

        result = build_diagnostic(
            {
                "network": {
                    "ap_ip": "192.168.1.8",
                    "sm_ip": "192.168.1.9",
                    "rpi_ip": "192.168.1.4",
                }
            },
            ping_probe=lambda ip: True,
            https_probe=broken_https,
            api_probe=lambda: True,
            safe_abort=False,
            transition_failed=False,
        )

        self.assertEqual(
            "LINK_DEGRADED",
            result["health_state"],
        )
        self.assertFalse(result["observations"]["ap_https"])
        self.assertIn("ap_https", result["errors"])


class RecoveryConcreteProbeTests(unittest.TestCase):

    def test_https_probe_accepts_successful_response(self):
        from unittest.mock import patch, MagicMock
        from campaign_recovery import https_probe

        response = MagicMock()

        with patch(
            "campaign_recovery.urllib.request.urlopen",
            return_value=response,
        ):
            self.assertTrue(
                https_probe(
                    "192.168.1.8",
                    scheme="https",
                    timeout=15,
                    tls_verify=False,
                )
            )

        response.close.assert_called_once()

    def test_https_probe_accepts_http_error_as_reachable(self):
        from unittest.mock import patch
        import urllib.error
        from campaign_recovery import https_probe

        error = urllib.error.HTTPError(
            url="https://192.168.1.8/",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=None,
        )

        with patch(
            "campaign_recovery.urllib.request.urlopen",
            side_effect=error,
        ):
            self.assertTrue(
                https_probe(
                    "192.168.1.8",
                    scheme="https",
                    timeout=15,
                    tls_verify=False,
                )
            )

    def test_cambium_api_probe_authenticates_only(self):
        from unittest.mock import patch, MagicMock
        from campaign_recovery import cambium_api_probe

        config = {
            "api": {
                "credentials_file": "/tmp/fake.json",
            },
            "network": {
                "ap_ip": "192.168.1.8",
            },
        }

        fake_api = MagicMock()
        fake_api.authenticate.return_value = True

        with patch(
            "campaign_recovery.CambiumAPI",
            return_value=fake_api,
        ) as api_class:
            result = cambium_api_probe(config)

        self.assertTrue(result)
        api_class.assert_called_once_with(config)
        fake_api.authenticate.assert_called_once()

        # Diagnostic API probe must not read or mutate RF configuration.
        fake_api.read.assert_not_called()
        fake_api.trial.assert_not_called()
        fake_api.finish.assert_not_called()


class RecoveryCliTests(unittest.TestCase):

    def test_diagnose_command_healthy_returns_zero(self):
        from unittest.mock import patch
        from campaign_recovery import main

        result = {
            "health_state": "HEALTHY",
            "observations": {},
            "errors": {},
            "safe_abort": {
                "active": False,
                "status": "ABSENT",
            },
        }

        with patch(
            "campaign_recovery.run_live_diagnostic",
            return_value=result,
        ):
            rc = main([
                "diagnose",
                "--config",
                "campaign_plan.template.json",
            ])

        self.assertEqual(0, rc)

    def test_diagnose_command_degraded_returns_two(self):
        from unittest.mock import patch
        from campaign_recovery import main

        result = {
            "health_state": "API_DEGRADED",
            "observations": {},
            "errors": {"api": "simulated timeout"},
            "safe_abort": {
                "active": False,
                "status": "ABSENT",
            },
        }

        with patch(
            "campaign_recovery.run_live_diagnostic",
            return_value=result,
        ):
            rc = main([
                "diagnose",
                "--config",
                "campaign_plan.template.json",
            ])

        self.assertEqual(2, rc)

    def test_diagnose_command_safe_abort_returns_three(self):
        from unittest.mock import patch
        from campaign_recovery import main

        result = {
            "health_state": "SAFE_ABORT",
            "observations": {},
            "errors": {},
            "safe_abort": {
                "active": True,
                "status": "RECOVERY_REQUIRED",
            },
        }

        with patch(
            "campaign_recovery.run_live_diagnostic",
            return_value=result,
        ):
            rc = main([
                "diagnose",
                "--config",
                "campaign_plan.template.json",
            ])

        self.assertEqual(3, rc)

    def test_live_diagnostic_uses_read_only_probes(self):
        from pathlib import Path
        from unittest.mock import patch
        from campaign_recovery import run_live_diagnostic

        config = {
            "network": {
                "ap_ip": "192.168.1.8",
                "sm_ip": "192.168.1.9",
                "rpi_ip": "192.168.1.4",
            },
            "api": {
                "scheme": "https",
                "request_timeout_seconds": 15,
                "tls_verify": False,
                "credentials_file": "/tmp/fake.json",
            },
            "outputs": {
                "directory": "campaign_runtime",
            },
        }

        with patch(
            "campaign_recovery.load_config",
            return_value=config,
        ), patch(
            "campaign_recovery.run_diagnostic",
            return_value={
                "health_state": "HEALTHY",
                "observations": {},
                "errors": {},
            },
        ) as runner:
            result = run_live_diagnostic(
                Path("campaign_plan.template.json")
            )

        self.assertEqual("HEALTHY", result["health_state"])
        runner.assert_called_once()

        kwargs = runner.call_args.kwargs
        self.assertIn("ping_probe", kwargs)
        self.assertIn("https_probe", kwargs)
        self.assertIn("api_probe", kwargs)


class RecoveryConfiguredEligibilityTests(unittest.TestCase):

    def setUp(self):
        self.recovery_config = {
            "cnmatrix": {
                "management_ipv4": "192.168.1.32",
                "management_ipv6_link_local":
                    "fe80::32cb:c7ff:feba:56e1%enp1s0",
                "expected_mac": "30:CB:C7:BA:56:E1",
            },
            "target": {
                "port": 6,
                "description": "Cunacales6",
            },
            "protected": {
                "port": 3,
                "description": "Cunacales",
            },
        }

    def test_configured_topology_is_eligible(self):
        from campaign_recovery import (
            configured_recovery_eligible,
        )

        self.assertTrue(
            configured_recovery_eligible(
                recovery_config=self.recovery_config,
                health_state="RECOVERY_REQUIRED",
                observed_switch_mac="30:CB:C7:BA:56:E1",
                observed_target_port=6,
                observed_target_description="Cunacales6",
                observed_target_delivering_power=True,
                observed_protected_port=3,
                observed_protected_description="Cunacales",
            )
        )

    def test_wrong_switch_mac_fails_closed(self):
        from campaign_recovery import (
            configured_recovery_eligible,
        )

        self.assertFalse(
            configured_recovery_eligible(
                recovery_config=self.recovery_config,
                health_state="RECOVERY_REQUIRED",
                observed_switch_mac="00:00:00:00:00:00",
                observed_target_port=6,
                observed_target_description="Cunacales6",
                observed_target_delivering_power=True,
                observed_protected_port=3,
                observed_protected_description="Cunacales",
            )
        )

    def test_swapped_target_and_protected_ports_fail_closed(self):
        from campaign_recovery import (
            configured_recovery_eligible,
        )

        self.assertFalse(
            configured_recovery_eligible(
                recovery_config=self.recovery_config,
                health_state="RECOVERY_REQUIRED",
                observed_switch_mac="30:CB:C7:BA:56:E1",
                observed_target_port=3,
                observed_target_description="Cunacales",
                observed_target_delivering_power=True,
                observed_protected_port=6,
                observed_protected_description="Cunacales6",
            )
        )

    def test_healthy_state_is_never_eligible(self):
        from campaign_recovery import (
            configured_recovery_eligible,
        )

        self.assertFalse(
            configured_recovery_eligible(
                recovery_config=self.recovery_config,
                health_state="HEALTHY",
                observed_switch_mac="30:CB:C7:BA:56:E1",
                observed_target_port=6,
                observed_target_description="Cunacales6",
                observed_target_delivering_power=True,
                observed_protected_port=3,
                observed_protected_description="Cunacales",
            )
        )
