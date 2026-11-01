"""GUI-compatible, verified session closure; only this controller's own session."""
import copy
import http.cookiejar
import json
import os
from pathlib import Path
import urllib.parse
from campaign_orchestrator import CambiumAPI,CampaignError

PRIVATE=Path('/home/carlos/.local/state/luisita/ap_session.json')

def jar_of(api):
    return next(h.cookiejar for h in api.opener.handlers if hasattr(h,'cookiejar'))

def cookie(name,value,host,secure):
    return http.cookiejar.Cookie(0,name,value,None,False,host,False,False,'/',True,secure,None,True,None,None,{},False)

class SessionAPI(CambiumAPI):
    def __init__(self,c,session_path=PRIVATE):
        super().__init__(c)
        self.session_path=Path(session_path)
        self.role=None
        self.base=c['api'].get('scheme','http')+'://'+c['network']['ap_ip']
        parsed=urllib.parse.urlsplit(self.base)
        self.port=str(parsed.port or (443 if parsed.scheme=='https' else 80))
        self.host=parsed.hostname
        self.secure=parsed.scheme=='https'

    def _save(self):
        p=self.session_path;p.parent.mkdir(parents=True,exist_ok=True);os.chmod(p.parent,0o700)
        data={'host':self.host,'port':self.port,'stok':self.stok,'role':self.role,
              'cookies':[{k:getattr(x,k) for k in ['name','value','domain','path','secure']} for x in jar_of(self)]}
        tmp=p.with_suffix('.tmp');fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
        with os.fdopen(fd,'w') as f:json.dump(data,f);f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)

    def request(self,url,form):
        data=super().request(url,form)
        if url==self.base+'/cgi-bin/luci' and len(str(data.get('stok','')))==32:
            self.stok=str(data['stok']);self.role=str(data.get('userRole',''))
            if not self.role:raise CampaignError('Login response missing userRole')
            jar=jar_of(self)
            jar.set_cookie(cookie('stok_'+self.port,self.stok,self.host,self.secure))
            jar.set_cookie(cookie('usernameType_'+self.port,self.role,self.host,self.secure))
            self._save()
        return data

    def authenticate(self,credentials_path):
        if self.session_path.exists():
            if self.session_path.stat().st_mode & 0o077:raise CampaignError('Private session file permissions must be 600')
            data=json.loads(self.session_path.read_text())
            if data.get('host')!=self.host or data.get('port')!=self.port:raise CampaignError('Owned session target mismatch')
            self.stok=data['stok'];self.role=data['role']
            for x in data['cookies']:
                jar_of(self).set_cookie(cookie(x['name'],x['value'],x['domain'],x['secure']))
            check=self.request(self.base+'/cgi-bin/luci/;stok='+urllib.parse.quote(self.stok,safe='')+'/admin/test_connect',{'debug':'0'})
            if str(check.get('test'))=='1':return True
            self.session_path.unlink();self.stok='';jar_of(self).clear()
        return super().authenticate(credentials_path)

    def logout(self):
        if not self.stok:return
        token=self.stok
        previous=[copy.copy(x) for x in jar_of(self)]
        url=self.base+'/cgi-bin/luci/;stok='+urllib.parse.quote(token,safe='')+'/admin/'
        response=self.request(url+'logout',{'debug':'0'})
        if str(response.get('success')).lower() not in {'1','true'}:
            self._save()
            raise CampaignError('AP logout rejected; own session retained for controlled reuse')
        probe=CambiumAPI(self.c,stok=token)
        for x in previous:jar_of(probe).set_cookie(x)
        check=probe.request(url+'test_connect',{'debug':'0'})
        if str(check.get('test'))=='1':
            self._save();raise CampaignError('AP logout did not invalidate prior token')
        self.stok='';self.config_id=None
        if self.session_path.exists():
            saved=json.loads(self.session_path.read_text())
            if saved.get('stok')==token:self.session_path.unlink()
        jar_of(self).clear()
