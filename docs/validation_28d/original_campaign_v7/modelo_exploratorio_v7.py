import json
from pathlib import Path
import numpy as np
from scipy.stats import f,t,shapiro
P=Path(__file__).parent
d=json.loads((P/'Cierre_original_V7.json').read_text())
def fit(rows,key='dl_median'):
 rows=[r for r in rows if r[key] is not None]
 blocks=sorted({r['block'] for r in rows});base=blocks[0]
 def xrow(freq,bw,block):
  a=float(freq==6655);b=float(freq==7000);w=float(bw==40)
  return [1,a,b,w,a*w,b*w]+[float(block==z) for z in blocks[1:]]
 X=np.array([xrow(r['f'],r['b'],r['block']) for r in rows]);y=np.array([r[key] for r in rows])
 rank=np.linalg.matrix_rank(X);df=len(y)-rank
 beta=np.linalg.lstsq(X,y,rcond=None)[0];res=y-X@beta;mse=float(res@res/df);V=np.linalg.inv(X.T@X)*mse
 def contrast(vector):
  v=np.array(vector);effect=float(v@beta);se=float(np.sqrt(v@V@v));q=t.ppf(.975,df)
  return {'effect':effect,'se':se,'ci_low':effect-q*se,'ci_high':effect+q*se}
 def test(C):
  C=np.array(C);u=C@beta;stat=float(u@np.linalg.inv(C@V@C.T)@u/len(C))
  return {'F':stat,'df1':len(C),'df2':int(df),'p':float(f.sf(stat,len(C),df))}
 z=np.zeros(rank);w=z.copy();w[3]=1;w[4:6]=1/3
 fc1=z.copy();fc1[1]=1;fc1[4]=.5
 fc2=z.copy();fc2[2]=1;fc2[5]=.5
 tests={'global':test(np.eye(rank)[1:6]),'frequency':test([fc1,fc2]),'bandwidth':test([w]),'interaction':test(np.eye(rank)[4:6])}
 order=sorted(tests,key=lambda k:tests[k]['p']);prev=0
 for i,k in enumerate(order):
  prev=max(prev,min(1,tests[k]['p']*(len(order)-i)));tests[k]['p_holm']=prev
 widths={}
 for freq in [6475,6655,7000]:
  vector=np.array(xrow(freq,40,base))-np.array(xrow(freq,20,base));widths[str(freq)]=contrast(vector)
 h=np.sum((X@np.linalg.inv(X.T@X))*X,axis=1)
 cook=(res**2/(rank*mse))*h/(1-h)**2
 sh=shapiro(res)
 diagnostics={'shapiro_W':float(sh.statistic),'shapiro_p':float(sh.pvalue),'max_cook':float(max(cook)),'max_cook_segment':rows[int(np.argmax(cook))]['segment'],'max_leverage':float(max(h)),'durbin_watson_chronological':float(np.sum(np.diff(res)**2)/np.sum(res**2))}
 return {'n':len(rows),'rank':int(rank),'residual_df':int(df),'mse':mse,'tests':tests,'width_avg':contrast(w),'width_by_frequency':widths,'frequency_6655_vs_6475':contrast(fc1),'frequency_7000_vs_6475':contrast(fc2),'segment_ids':[r['segment'] for r in rows],'diagnostics':diagnostics,'assumptions':'Exploratory OLS on one summary per segment; conventional model-based intervals; not randomization or robust causal inference'}
rows=d['segments']
out={'all17_medians':fit(rows),'without_low_coverage_s2':fit([r for r in rows if r['segment']!=2]),'complete_blocks_2_3':fit([r for r in rows if r['block'] in [2,3]]),'all17_means':fit(rows,'dl_mean')}
(P/'Modelo_exploratorio_V7.json').write_text(json.dumps(out,indent=2))
for k,r in out.items():print(k,r['n'],r['residual_df'],'width',r['width_avg'],'tests',r['tests'])
