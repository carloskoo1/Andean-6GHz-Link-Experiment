import tempfile,json
from pathlib import Path
from unittest import TestCase,mock
import session_api as m

class SessionTests(TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.path=Path(self.t.name)/'private/session.json'
  self.cfg={'api':{'scheme':'https','tls_verify':False,'request_timeout_seconds':3},'network':{'ap_ip':'192.168.1.8'}}
 def tearDown(self):self.t.cleanup()
 def test_login_installs_gui_cookies_and_protected_recovery_journal(self):
  a=m.SessionAPI(self.cfg,self.path)
  with mock.patch.object(m.CambiumAPI,'request',return_value={'stok':'x'*32,'userRole':'admin'}):
   a.request(a.base+'/cgi-bin/luci',{'username':'admin','password':'unit-test-only'})
  names={c.name for c in m.jar_of(a)}
  self.assertEqual(names,{'stok_443','usernameType_443'})
  self.assertEqual(self.path.stat().st_mode & 0o777,0o600)
  self.assertEqual(json.loads(self.path.read_text())['stok'],'x'*32)
 def test_failed_logout_preserves_reusable_owned_session(self):
  a=m.SessionAPI(self.cfg,self.path);a.stok='x'*32;a.role='admin'
  with mock.patch.object(a,'request',return_value={'success':0}):
   with self.assertRaisesRegex(m.CampaignError,'retained'):a.logout()
  self.assertEqual(a.stok,'x'*32);self.assertTrue(self.path.exists())
 def test_logout_does_not_accept_an_old_token_that_still_authenticates(self):
  a=m.SessionAPI(self.cfg,self.path);a.stok='x'*32;a.role='admin'
  with mock.patch.object(a,'request',return_value={'success':1}),mock.patch.object(m.CambiumAPI,'request',return_value={'test':1}):
   with self.assertRaisesRegex(m.CampaignError,'invalidate'):a.logout()
  self.assertTrue(self.path.exists())
 def test_successful_logout_clears_only_its_owned_session(self):
  a=m.SessionAPI(self.cfg,self.path);a.stok='x'*32;a.role='admin';a._save()
  with mock.patch.object(a,'request',return_value={'success':1}),mock.patch.object(m.CambiumAPI,'request',return_value={'success':0}):a.logout()
  self.assertEqual(a.stok,'');self.assertFalse(self.path.exists())
 def test_saved_valid_session_is_reused_without_another_login(self):
  a=m.SessionAPI(self.cfg,self.path);a.stok='x'*32;a.role='admin';a._save()
  b=m.SessionAPI(self.cfg,self.path)
  with mock.patch.object(b,'request',return_value={'test':1}),mock.patch.object(m.CambiumAPI,'authenticate') as login:
   self.assertTrue(b.authenticate('not-read'))
  login.assert_not_called()
