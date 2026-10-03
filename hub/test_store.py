import tempfile
import unittest
from pathlib import Path
from store import Store


class PermissionsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name) / 'lab.sqlite')
        self.user = self.store.save({'userName': 'ingeniero@example.test', 'title': 'mantenimiento', 'active': True})

    def tearDown(self):
        self.temp.cleanup()

    def test_maintenance_cannot_administer(self):
        self.assertTrue(self.store.permitted(self.user['id'], 'mantenimiento'))
        self.assertFalse(self.store.permitted(self.user['id'], 'admin'))

    def test_demotion_removes_previous_permission(self):
        self.store.save({'title': 'auditor'}, self.user['id'])
        self.assertFalse(self.store.permitted(self.user['id'], 'mantenimiento'))
        self.assertTrue(self.store.permitted(self.user['id'], 'registros'))

    def test_deactivation_blocks_existing_user_id(self):
        self.store.save({'active': False}, self.user['id'])
        self.assertFalse(self.store.permitted(self.user['id'], 'consulta'))

    def test_string_false_is_not_truthy(self):
        self.store.save({'active': 'false'}, self.user['id'])
        self.assertFalse(self.store.permitted(self.user['id'], 'consulta'))

    def test_unknown_role_is_denied(self):
        self.store.save({'title': 'director'}, self.user['id'])
        self.assertFalse(self.store.permitted(self.user['id'], 'consulta'))

    def test_identity_cannot_be_rebound(self):
        self.assertTrue(self.store.bind_identity(self.user['id'], 'subject-a'))
        self.assertFalse(self.store.bind_identity(self.user['id'], 'subject-b'))

    def test_deletion_blocks_old_session(self):
        self.store.remove(self.user['id'])
        self.assertFalse(self.store.permitted(self.user['id'], 'consulta'))

    def test_operational_data_round_trip(self):
        device = self.store.save_device({'name': 'NVR-01', 'kind': 'nvr', 'address': '10.31.0.20', 'status': 'online'})
        event = self.store.add_access_event({'reader': 'PUERTA-01', 'credential': 'TARJETA-001', 'movement': 'entrada', 'result': 'permitido'})
        incident = self.store.add_incident({'title': 'Prueba controlada', 'severity': 'media', 'summary': 'Dato ficticio'}, self.user['id'])
        self.assertEqual(self.store.devices()[0]['id'], device['id'])
        self.assertEqual(self.store.access_events()[0]['id'], event['id'])
        self.assertEqual(self.store.incidents()[0]['id'], incident['id'])
        self.assertEqual(self.store.dashboard()['devices_online'], 1)

    def test_invalid_operational_values_are_rejected(self):
        with self.assertRaises(ValueError):
            self.store.save_device({'name': 'X', 'kind': 'shell', 'status': 'online'})
        with self.assertRaises(ValueError):
            self.store.add_access_event({'reader': 'X', 'credential': 'Y', 'movement': 'abrir', 'result': 'OK'})

    def test_role_override_and_card_lifecycle(self):
        self.store.set_role(self.user['id'], 'soc', 'PUESTO-TI')
        self.assertTrue(self.store.permitted(self.user['id'], 'incidentes'))
        card = self.store.add_card({'uid': 'A1B2C3D4', 'label': 'TARJETA-001', 'user_id': self.user['id']}, 'PUESTO-FISICO', 'P'*48)
        self.assertNotIn('A1B2C3D4', card['uid_hash'])
        self.assertTrue(self.store.check_card('A1 B2 C3 D4', 'P'*48)['allowed'])
        self.store.set_card_active(card['id'], False, 'PUESTO-FISICO')
        self.assertFalse(self.store.check_card('A1B2C3D4', 'P'*48)['allowed'])


if __name__ == '__main__':
    unittest.main()
