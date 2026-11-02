import unittest
from reconcile_weather import nearest,analyze,stamp
def sample(time,pk=1):
 return dict(source_id=pk,timestamp_utc=time,bme_ok=1,rain_ok=1,wind_ok=1)
class Tests(unittest.TestCase):
 def test_exact_match_is_zero_not_missing(self):
  s=sample('2026-11-02T05:00:00+00:00')
  self.assertEqual(nearest([s],stamp(s['timestamp_utc'])),s)
 def test_equal_distance_tie_prefers_earlier_regardless_order(self):
  earlier=sample('2026-11-02T04:59:30+00:00',2);later=sample('2026-11-02T05:00:30+00:00',1)
  self.assertEqual(nearest([later,earlier],stamp('2026-11-02T00:00:00-05:00')),earlier)
 def test_naive_time_rejected(self):
  with self.assertRaises(ValueError):stamp('2026-11-02T05:00:00')
 def test_missing_station_stays_unmatched(self):
  result=analyze(self.snapshot([]))['summary']['SJ01']
  self.assertEqual(result['unmatched'],1);self.assertEqual(result['immature'],1)
 def test_120_included_121_rejected_and_no_threshold_relaxation(self):
  for seconds,eligible in [('00',True),('01',False)]:
   result=analyze(self.snapshot([sample('2026-11-02T05:02:'+seconds+'+00:00')]))['summary']['SJ01']
   self.assertEqual(result['retrospective_within_120s'],int(eligible))
 def snapshot(self,samples):
  t=dict(id=1,test_id='test',direction='DL',timestamp_start_utc='2026-11-02T05:00:00+00:00')
  for st in ['cu01','sj01']:t.update({st+'_weather_time_delta_seconds':200,st+'_weather_timestamp_local':None})
  return {'tcp':[t],'weather':{'CU01':samples,'SJ01':samples}}
if __name__=='__main__':unittest.main()
