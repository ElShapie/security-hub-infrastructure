import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'hub'))

def load_app(db_path):
    env = {'APP_SECRET':'A'*48, 'SCIM_TOKEN':'B'*48, 'DEVICE_TOKEN':'C'*48,
           'CARD_PEPPER':'D'*48, 'APP_BASE_URL':'https://security-hub.example.test',
           'OIDC_CLIENT_ID':'fixture', 'OIDC_CLIENT_SECRET':'fixture',
           'OIDC_METADATA_URL':'https://idp.example.test/.well-known/openid-configuration',
           'APP_DB':str(db_path), 'NVR_BASE_URL':''}
    spec = importlib.util.spec_from_file_location('security_hub_web', ROOT / 'hub/app.py')
    module = importlib.util.module_from_spec(spec)
    with patch.dict(os.environ, env):
        spec.loader.exec_module(module)
    return module

class HubIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.web = load_app(Path(self.temp.name) / 'hub.sqlite')
        self.client = self.web.app.test_client()
        self.token = {'Authorization':'Bearer '+'C'*48}

    def tearDown(self):
        self.temp.cleanup()

    def login(self, user):
        with self.client.session_transaction() as session:
            session.update(uid=user['id'], csrf='test-csrf')

    def test_ti_assigns_role_and_card(self):
        ti = self.web.store.save({'userName':'ti@example.test','externalId':'LAB-001','title':'ti','active':True})
        employee = self.web.store.save({'userName':'persona@example.test','externalId':'LAB-021','title':'consulta','active':True})
        self.login(ti)
        self.assertEqual(self.client.post('/usuarios/'+employee['id']+'/rol', data={'csrf':'test-csrf','role':'soc'}).status_code, 302)
        self.assertTrue(self.web.store.permitted(employee['id'], 'incidentes'))
        self.assertEqual(self.client.post('/tarjetas', data={'csrf':'test-csrf','uid':'A1B2C3D4','label':'TARJETA-021','user_id':employee['id']}).status_code, 302)
        decision = self.client.post('/api/v1/access/check', json={'uid':'A1B2C3D4','reader':'PUERTA-01','movement':'ENTRADA'}, headers=self.token)
        self.assertEqual(decision.status_code, 200)
        self.assertTrue(decision.json['allowed'])

    def test_unprivileged_user_cannot_change_role(self):
        soc = self.web.store.save({'userName':'soc@example.test','externalId':'LAB-010','title':'soc','active':True})
        employee = self.web.store.save({'userName':'persona@example.test','externalId':'LAB-022','title':'consulta','active':True})
        self.login(soc)
        self.assertEqual(self.client.post('/usuarios/'+employee['id']+'/rol', data={'csrf':'test-csrf','role':'admin'}).status_code, 403)

    def test_raw_card_uid_is_not_listed(self):
        user = self.web.store.save({'userName':'persona@example.test','externalId':'LAB-023','title':'consulta','active':True})
        self.web.store.add_card({'uid':'DEADBEEF','label':'TARJETA-023','user_id':user['id']}, 'LAB-001', 'D'*48)
        self.assertNotIn('uid_hash', self.web.store.cards()[0])
        self.assertNotIn('DEADBEEF', str(self.web.store.cards()))

if __name__ == '__main__':
    unittest.main()
