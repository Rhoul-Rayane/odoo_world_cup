from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class TestWcAccreditation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWcAccreditation, cls).setUpClass()
        cls.stadium = cls.env['wc.stadium'].create({
            'name': 'Stade Adrar',
            'city': 'Agadir',
            'capacity': 45000,
            'country': 'morocco',
        })
        cls.zone = cls.env['wc.stadium.zone'].create({
            'name': 'Tribune Presse',
            'stadium_id': cls.stadium.id,
            'zone_type': 'press',
            'capacity': 200,
        })

    def test_accreditation_date_validation(self):
        # Create badge with invalid dates (end before start)
        with self.assertRaises(ValidationError):
            self.env['wc.accreditation'].create({
                'holder_name': 'Jean Dupont',
                'category': 'media',
                'zone_ids': [(6, 0, [self.zone.id])],
                'date_start': date.today(),
                'date_end': date.today() - timedelta(days=1),
            })

    def test_accreditation_computed_fields(self):
        # Create badge
        badge = self.env['wc.accreditation'].create({
            'holder_name': 'Jean Dupont',
            'category': 'media',
            'zone_ids': [(6, 0, [self.zone.id])],
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=10),
        })
        # Check defaults
        self.assertEqual(badge.state, 'draft')
        self.assertEqual(badge.badge_color, '#16A34A') # green for media
        self.assertFalse(badge.is_expired)
        
        # Approve badge to generate token and name
        badge.action_approve()
        self.assertTrue(badge.qr_token)
        self.assertEqual(badge.state, 'approved')
        self.assertEqual(badge.name, f"WC2030-MED-{badge.qr_token[-4:]}")

    def test_accreditation_expiration_computation(self):
        badge = self.env['wc.accreditation'].create({
            'holder_name': 'Expired Reporter',
            'category': 'media',
            'zone_ids': [(6, 0, [self.zone.id])],
            'date_start': date.today() - timedelta(days=20),
            'date_end': date.today() - timedelta(days=5),
        })
        self.assertTrue(badge.is_expired)

    def test_accreditation_workflow_and_scanning(self):
        badge = self.env['wc.accreditation'].create({
            'holder_name': 'Official VIP',
            'category': 'vip',
            'zone_ids': [(6, 0, [self.zone.id])],
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=5),
        })
        
        # Workflow transitions
        badge.action_approve()
        badge.action_print()
        self.assertEqual(badge.state, 'printed')
        
        badge.action_activate()
        self.assertEqual(badge.state, 'active')
        
        # Test scan
        self.assertEqual(badge.scan_count, 0)
        badge.action_scan()
        self.assertEqual(badge.scan_count, 1)
        self.assertTrue(badge.last_scan_date)
        
        # Test verify_token API
        res_valid = self.env['wc.accreditation'].verify_token(badge.qr_token)
        self.assertTrue(res_valid['valid'])
        self.assertEqual(res_valid['holder'], 'Official VIP')
        
        # Test invalid token verify
        res_invalid = self.env['wc.accreditation'].verify_token('UNKNOWN_TOKEN')
        self.assertFalse(res_invalid['valid'])
        self.assertEqual(res_invalid['error'], 'Token inconnu')

        # Test suspend
        badge.action_suspend()
        self.assertEqual(badge.state, 'suspended')
        
        # Scan suspended should raise error
        with self.assertRaises(ValidationError):
            badge.action_scan()
            
        res_suspended = self.env['wc.accreditation'].verify_token(badge.qr_token)
        self.assertFalse(res_suspended['valid'])
        self.assertEqual(res_suspended['error'], 'Badge non actif (suspended)')

        # Revoke and reset
        badge.action_revoke()
        self.assertEqual(badge.state, 'revoked')
        badge.action_reset_to_draft()
        self.assertEqual(badge.state, 'draft')
