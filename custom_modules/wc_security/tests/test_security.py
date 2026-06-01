from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.fields import Date, Datetime
from datetime import date, timedelta

class TestWcSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWcSecurity, cls).setUpClass()

        # Create test stadium (using unique code TTS to avoid conflicts)
        cls.stadium = cls.env['wc.stadium'].create({
            'name': 'Stade de Sécurité Test',
            'city': 'Casablanca',
            'capacity': 80000,
            'country': 'morocco',
            'fifa_code': 'TTS',
        })

        # Create stadium zone
        cls.zone_tribune = cls.env['wc.stadium.zone'].create({
            'name': 'Tribune Test Nord',
            'stadium_id': cls.stadium.id,
            'zone_type': 'tribune',
            'capacity': 20000,
        })

        # Create test match
        cls.match = cls.env['wc.match'].create({
            'team_a': 'Morocco Test',
            'team_b': 'Portugal Test',
            'stadium_id': cls.stadium.id,
            'date_time': Datetime.now(),
            'phase': 'semi',
        })

    def test_security_deployment_logic(self):
        # 1. Create a deployment
        deployment = self.env['wc.security.deployment'].create({
            'match_id': self.match.id,
            'stadium_zone_id': self.zone_tribune.id,
            'deployment_type': 'police',
            'agent_count': 50,
        })
        
        # 2. Check reference naming is computed correctly
        self.assertIn("SEC-Morocco Test vs Portugal Test", deployment.name)
        self.assertIn("Tribune Test Nord", deployment.name)

        # 3. Test agent count validation
        with self.assertRaises(ValidationError):
            deployment.write({'agent_count': 0})
        
        with self.assertRaises(ValidationError):
            deployment.write({'agent_count': -5})

    def test_security_agreement_dates_and_validation(self):
        # 1. Create a valid agreement
        agreement = self.env['wc.security.agreement'].create({
            'name': 'Accord Test de Coopération',
            'partner_country': 'france',
            'agreement_type': 'anti_drone',
            'effective_date': date.today(),
            'expiration_date': date.today() + timedelta(days=30),
            'personnel_deployed': 10,
        })
        self.assertEqual(agreement.personnel_deployed, 10)

        # 2. Test expiration date validation
        with self.assertRaises(ValidationError):
            agreement.write({
                'expiration_date': date.today() - timedelta(days=1)
            })
            self.env.flush_all()

        # 3. Test personnel validation
        with self.assertRaises(ValidationError):
            agreement.write({
                'personnel_deployed': -1
            })
            self.env.flush_all()

    def test_crowd_monitoring_density_and_alerts(self):
        # 1. Create a crowd monitoring instance
        monitoring = self.env['wc.crowd.monitoring'].create({
            'match_id': self.match.id,
            'stadium_zone_id': self.zone_tribune.id,
            'current_headcount': 1000,
            'zone_area': 1000.0,
        })

        # Check density and green safety status (1.0 pers/m2)
        self.assertEqual(monitoring.density_per_sqm, 1.0)
        self.assertEqual(monitoring.safety_status, 'green')

        # Check density and orange warning status (3.0 pers/m2)
        monitoring.write({'current_headcount': 3000})
        self.assertEqual(monitoring.density_per_sqm, 3.0)
        self.assertEqual(monitoring.safety_status, 'orange')

        # Check density and red critical status (5.0 pers/m2)
        monitoring.write({'current_headcount': 5000})
        self.assertEqual(monitoring.density_per_sqm, 5.0)
        self.assertEqual(monitoring.safety_status, 'red')

        # Test validation constraint: negative headcount
        with self.assertRaises(ValidationError):
            monitoring.write({'current_headcount': -10})

        # Test validation constraint: zero or negative area
        with self.assertRaises(ValidationError):
            monitoring.write({'zone_area': 0.0})
        
        with self.assertRaises(ValidationError):
            monitoring.write({'zone_area': -100.0})

    def test_incident_security_extensions(self):
        # Create deployment
        deployment = self.env['wc.security.deployment'].create({
            'match_id': self.match.id,
            'stadium_zone_id': self.zone_tribune.id,
            'deployment_type': 'police',
            'agent_count': 50,
        })

        # Create incident with security fields
        incident = self.env['wc.logistics.incident'].create({
            'name': 'Intrusion sur le terrain de test',
            'description': 'Supporter ayant couru sur le terrain',
            'stadium_id': self.stadium.id,
            'zone_id': self.zone_tribune.id,
            'match_id': self.match.id,
            'incident_type': 'security',
            'severity': '3',
            'intervention_force_required': True,
            'police_informed': True,
            'drone_intercepted': False,
            'security_deployment_id': deployment.id,
        })

        self.assertTrue(incident.intervention_force_required)
        self.assertTrue(incident.police_informed)
        self.assertFalse(incident.drone_intercepted)
        self.assertEqual(incident.security_deployment_id, deployment)
