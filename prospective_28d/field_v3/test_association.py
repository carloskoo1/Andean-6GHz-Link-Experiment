from unittest import TestCase
from controller import live_association,association_rows
class AssociationTests(TestCase):
 def setUp(self):
  self.ap={'cambiumSTAConnectedRFFrequency':'6655','cambiumSTAConnectedRFBandwidth':'2'}
  self.sm={'wirelessInterfaceConnectionState':'3','cambiumConnectedAPMACAddress':'BC:E6:7C:F0:A8:FC','cambiumSTAConnectedRFFrequency':'7000','cambiumSTAConnectedRFBandwidth':'2'}
  self.st=[{'connectedSTAMAC':'bc:e6:7c:f0:a8:24','connectedSTAIP':'192.168.1.9','connectedSTAChannel':'6655'}]
  self.sa=[{'connectedAPBSSID':'bc:e6:7c:f0:a8:fc','connectedAPFrequency':'6655','connectedAPBandwidth':'40'}]
 def test_live_frequency_verified_while_stale_dashboard_retained(self):
  result=live_association(self.ap,self.sm,self.st,self.sa)
  self.assertEqual(result['sm_f'],6655);self.assertEqual(result['sm_dashboard_f'],7000)
 def test_unassociated_SM_rejected(self):
  self.sm['wirelessInterfaceConnectionState']='0'
  with self.assertRaises(RuntimeError):live_association(self.ap,self.sm,self.st,self.sa)
 def test_other_bssid_rejected(self):
  self.sm['cambiumConnectedAPMACAddress']='00:00:00:00:00:00'
  with self.assertRaises(RuntimeError):live_association(self.ap,self.sm,self.st,self.sa)
 def test_peer_frequency_conflict_rejected(self):
  self.st[0]['connectedSTAChannel']='7000'
  with self.assertRaises(RuntimeError):live_association(self.ap,self.sm,self.st,self.sa)
 def test_multiple_candidate_peers_not_silently_accepted(self):
  with self.assertRaises(RuntimeError):live_association(self.ap,self.sm,self.st,self.sa*2)
 def test_row_parser_does_not_mix_two_APs(self):
  rows=association_rows('[table]\n [1]\n connectedAPBSSID first\n connectedAPFrequency 6655\n [2]\n connectedAPBSSID second\n connectedAPFrequency 7000\n')
  self.assertEqual([r['connectedAPFrequency'] for r in rows if 'connectedAPFrequency' in r],['6655','7000'])
