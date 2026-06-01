from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class TestSustainability(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stadium = cls.env['wc.stadium'].create({
            'name': 'Stade Test Durabilité',
            'city': 'Casablanca',
            'capacity': 60000,
            'country': 'morocco',
        })

    # ----------------------------------------------------------------
    # Waste Tracking Tests
    # ----------------------------------------------------------------

    def test_waste_tracking_creation_and_diversion_rate(self):
        """Test creation and automatic diversion rate computation."""
        waste = self.env['wc.waste.tracking'].create({
            'stadium_id': self.stadium.id,
            'date': date.today(),
            'waste_type': 'plastic',
            'quantity_kg': 200.0,
            'recycled_kg': 80.0,
            'diverted_kg': 40.0,
        })
        # (80 + 40) / 200 * 100 = 60%
        self.assertAlmostEqual(waste.diversion_rate, 60.0, places=2)

    def test_waste_tracking_constraints(self):
        """Test that recycled + diverted > quantity raises ValidationError
        and that quantity <= 0 raises ValidationError."""
        # recycled + diverted > quantity
        with self.assertRaises(ValidationError):
            self.env['wc.waste.tracking'].create({
                'stadium_id': self.stadium.id,
                'date': date.today(),
                'waste_type': 'organic',
                'quantity_kg': 100.0,
                'recycled_kg': 80.0,
                'diverted_kg': 30.0,
            })

        # quantity <= 0
        with self.assertRaises(ValidationError):
            self.env['wc.waste.tracking'].create({
                'stadium_id': self.stadium.id,
                'date': date.today(),
                'waste_type': 'organic',
                'quantity_kg': 0.0,
            })

    def test_waste_workflow(self):
        """Test workflow: draft → confirmed → validated."""
        waste = self.env['wc.waste.tracking'].create({
            'stadium_id': self.stadium.id,
            'date': date.today(),
            'waste_type': 'glass',
            'quantity_kg': 50.0,
        })
        self.assertEqual(waste.state, 'draft')

        waste.action_confirm()
        self.assertEqual(waste.state, 'confirmed')

        waste.action_validate()
        self.assertEqual(waste.state, 'validated')

    # ----------------------------------------------------------------
    # Carbon Footprint Tests
    # ----------------------------------------------------------------

    def test_carbon_footprint_net_emission(self):
        """Test net emission = emission - offset."""
        footprint = self.env['wc.carbon.footprint'].create({
            'stadium_id': self.stadium.id,
            'period_start': date(2030, 1, 1),
            'period_end': date(2030, 6, 30),
            'category': 'energy',
            'emission_tons_co2': 500.0,
            'offset_tons_co2': 120.0,
        })
        self.assertAlmostEqual(footprint.net_emission, 380.0, places=2)

    def test_carbon_footprint_date_constraint(self):
        """Test that period_end < period_start raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.env['wc.carbon.footprint'].create({
                'stadium_id': self.stadium.id,
                'period_start': date(2030, 6, 30),
                'period_end': date(2030, 1, 1),
                'category': 'transport',
                'emission_tons_co2': 200.0,
            })

    # ----------------------------------------------------------------
    # Sustainability Audit Tests
    # ----------------------------------------------------------------

    def test_audit_compliance_level(self):
        """Test compliance_level computed from score."""
        audit_full = self.env['wc.sustainability.audit'].create({
            'name': 'Audit Conforme',
            'stadium_id': self.stadium.id,
            'audit_date': date.today(),
            'auditor_name': 'Auditeur A',
            'iso_category': 'governance',
            'score': 85,
        })
        self.assertEqual(audit_full.compliance_level, 'full')

        audit_partial = self.env['wc.sustainability.audit'].create({
            'name': 'Audit Partiel',
            'stadium_id': self.stadium.id,
            'audit_date': date.today(),
            'auditor_name': 'Auditeur B',
            'iso_category': 'planning',
            'score': 65,
        })
        self.assertEqual(audit_partial.compliance_level, 'partial')

        audit_non = self.env['wc.sustainability.audit'].create({
            'name': 'Audit Non Conforme',
            'stadium_id': self.stadium.id,
            'audit_date': date.today(),
            'auditor_name': 'Auditeur C',
            'iso_category': 'operation',
            'score': 30,
        })
        self.assertEqual(audit_non.compliance_level, 'non_compliant')

    def test_audit_workflow(self):
        """Test workflow: planned → in_progress → completed."""
        audit = self.env['wc.sustainability.audit'].create({
            'name': 'Audit Workflow',
            'stadium_id': self.stadium.id,
            'audit_date': date.today(),
            'auditor_name': 'Auditeur D',
            'iso_category': 'support',
            'score': 70,
        })
        self.assertEqual(audit.state, 'planned')

        audit.action_start()
        self.assertEqual(audit.state, 'in_progress')

        audit.action_complete()
        self.assertEqual(audit.state, 'completed')

    def test_audit_nonconformity_workflow(self):
        """Test workflow: planned → in_progress → non_conformity."""
        audit = self.env['wc.sustainability.audit'].create({
            'name': 'Audit Non-Conformité',
            'stadium_id': self.stadium.id,
            'audit_date': date.today(),
            'auditor_name': 'Auditeur E',
            'iso_category': 'performance',
            'score': 40,
        })
        self.assertEqual(audit.state, 'planned')

        audit.action_start()
        self.assertEqual(audit.state, 'in_progress')

        audit.action_flag_nonconformity()
        self.assertEqual(audit.state, 'non_conformity')

    def test_audit_score_constraint(self):
        """Test that score outside 0-100 raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.env['wc.sustainability.audit'].create({
                'name': 'Audit Score Invalide',
                'stadium_id': self.stadium.id,
                'audit_date': date.today(),
                'auditor_name': 'Auditeur F',
                'iso_category': 'improvement',
                'score': 150,
            })

        with self.assertRaises(ValidationError):
            self.env['wc.sustainability.audit'].create({
                'name': 'Audit Score Négatif',
                'stadium_id': self.stadium.id,
                'audit_date': date.today(),
                'auditor_name': 'Auditeur G',
                'iso_category': 'improvement',
                'score': -10,
            })

    def test_audit_next_date_constraint(self):
        """Test that next_audit_date <= audit_date raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.env['wc.sustainability.audit'].create({
                'name': 'Audit Date Invalide',
                'stadium_id': self.stadium.id,
                'audit_date': date.today(),
                'auditor_name': 'Auditeur H',
                'iso_category': 'governance',
                'score': 80,
                'next_audit_date': date.today() - timedelta(days=10),
            })
