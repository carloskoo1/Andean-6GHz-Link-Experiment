"""Isolated transport checks. No real API, SSH, RF or TCP calls."""
import json
from unittest import TestCase, mock
import backend
import controller


class TransportTests(TestCase):
    def setUp(self):
        self.b=backend.Backend.__new__(backend.Backend)
        self.row={'segment_id':'TEST','frequency_mhz':6655,'bandwidth_mhz':40}
        self.good={'ap_f':6655,'ap_b':40,'sm_f':6655,'sm_b':40}
        self.clock=[0.0]

    def advance(self,n):
        self.clock[0]+=n

    def test_transient_read_failure_is_logged_and_requires_ten_good_samples(self):
        self.b.readback=mock.Mock(side_effect=[RuntimeError('SM unreachable')]+[self.good]*10)
        self.b.route=mock.Mock()
        with mock.patch.object(backend.time,'monotonic',side_effect=lambda:self.clock[0]), \
             mock.patch.object(backend.time,'sleep',side_effect=self.advance), \
             mock.patch.object(controller,'event') as events:
            self.b.wait_target(self.row,30)
        self.assertEqual(self.b.readback.call_count,11)
        self.assertEqual(self.b.route.call_count,10)
        self.assertTrue(any(c.kwargs.get('error')=='SM unreachable' for c in events.call_args_list))
        self.assertEqual(events.call_args_list[-1].kwargs['consecutive'],10)

    def test_route_failure_never_counts_as_stable_RF(self):
        self.b.readback=mock.Mock(return_value=self.good)
        self.b.route=mock.Mock(side_effect=RuntimeError('endpoint unreachable'))
        with mock.patch.object(backend.time,'monotonic',side_effect=lambda:self.clock[0]), \
             mock.patch.object(backend.time,'sleep',side_effect=self.advance), \
             mock.patch.object(controller,'event') as events:
            with self.assertRaisesRegex(RuntimeError,'endpoint unreachable'):
                self.b.wait_target(self.row,8)
        self.assertTrue(all(c.kwargs['consecutive']==0 for c in events.call_args_list))

    def test_expired_trial_never_sends_confirmation(self):
        self.b.trial_at=0;self.b.api=mock.Mock()
        with mock.patch.object(backend.time,'monotonic',return_value=211):
            with self.assertRaisesRegex(RuntimeError,'margin'):
                self.b.confirm()
        self.b.api.finish.assert_not_called()

    def test_empty_forty_scan_list_is_rejected_before_field_use(self):
        data={'device_props':{'wirelessInterfaceScanFrequencyBandwidth':'3',
                             'wirelessInterfaceScanFrequencyListTwenty':'6475 6655 7000',
                             'wirelessInterfaceScanFrequencyListForty':''}}
        with mock.patch.object(backend.rf,'run_ssh',return_value='banner\n'+json.dumps(data)):
            with self.assertRaisesRegex(RuntimeError,'Forty'):
                self.b.check_sm_scan()
