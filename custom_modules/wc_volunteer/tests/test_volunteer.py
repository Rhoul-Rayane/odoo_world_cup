from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

class TestWcVolunteer(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWcVolunteer, cls).setUpClass()
        cls.stadium = cls.env['wc.stadium'].create({
            'name': 'Stade Ibn Batouta',
            'city': 'Tanger',
            'capacity': 65000,
            'country': 'morocco',
        })
        
        cls.skill_first_aid = cls.env['wc.volunteer.skill'].create({'name': 'Secourisme', 'color': 1})
        cls.skill_it = cls.env['wc.volunteer.skill'].create({'name': 'IT Support', 'color': 2})
        
        cls.lang_ar = cls.env['wc.volunteer.language'].create({'name': 'Arabe', 'color': 1})
        cls.lang_fr = cls.env['wc.volunteer.language'].create({'name': 'Français', 'color': 2})
        cls.lang_en = cls.env['wc.volunteer.language'].create({'name': 'Anglais', 'color': 3})

    def test_volunteer_matching_score(self):
        volunteer = self.env['wc.volunteer'].create({
            'name': 'Ali Alaoui',
            'email': 'ali@example.com',
            'date_of_birth': date.today() - relativedelta(years=25),
            'availability': 'full',
            'education_level': 'bac5',
            'has_driving_license': True,
            'has_vehicle': True,
            'has_first_aid': True,
            'skill_ids': [(6, 0, [self.skill_first_aid.id, self.skill_it.id])],
            'language_ids': [(6, 0, [self.lang_ar.id, self.lang_fr.id, self.lang_en.id])],
        })
        # Score calculation:
        # Languages: 3 * 6 = 18
        # Skills: 2 * 5 = 10
        # Driving license: 10
        # Vehicle: 5
        # First aid: 10
        # Availability (full): 10
        # Education level (bac5): 4
        # Total score = 18 + 10 + 10 + 5 + 10 + 10 + 4 = 67
        self.assertEqual(volunteer.matching_score, 67.0)

    def test_volunteer_age_constraint(self):
        with self.assertRaises(ValidationError):
            self.env['wc.volunteer'].create({
                'name': 'Jeune Volontaire',
                'email': 'jeune@example.com',
                'date_of_birth': date.today() - relativedelta(years=17),
                'availability': 'weekend',
                'skill_ids': [(6, 0, [self.skill_first_aid.id])],
                'language_ids': [(6, 0, [self.lang_ar.id])],
            })

    def test_volunteer_email_uniqueness(self):
        self.env['wc.volunteer'].create({
            'name': 'Volontaire A',
            'email': 'common@example.com',
            'date_of_birth': date.today() - relativedelta(years=20),
            'availability': 'full',
            'skill_ids': [(6, 0, [self.skill_first_aid.id])],
            'language_ids': [(6, 0, [self.lang_ar.id])],
        })
        
        with self.assertRaises(Exception):
            self.env['wc.volunteer'].create({
                'name': 'Volontaire B',
                'email': 'common@example.com',
                'date_of_birth': date.today() - relativedelta(years=22),
                'availability': 'full',
                'skill_ids': [(6, 0, [self.skill_it.id])],
                'language_ids': [(6, 0, [self.lang_fr.id])],
            })
            self.env.cr.flush()

    def test_volunteer_workflow(self):
        volunteer = self.env['wc.volunteer'].create({
            'name': 'Samir Benali',
            'email': 'samir@example.com',
            'date_of_birth': date.today() - relativedelta(years=30),
            'availability': 'full',
            'skill_ids': [(6, 0, [self.skill_first_aid.id])],
            'language_ids': [(6, 0, [self.lang_ar.id])],
        })
        self.assertEqual(volunteer.state, 'candidate')
        
        volunteer.action_preselect()
        self.assertEqual(volunteer.state, 'preselected')
        
        volunteer.action_train()
        self.assertEqual(volunteer.state, 'trained')
        self.assertEqual(volunteer.training_date, date.today())
        
        with self.assertRaises(ValidationError):
            volunteer.action_assign()
            
        volunteer.assigned_stadium_id = self.stadium.id
        volunteer.action_assign()
        self.assertEqual(volunteer.state, 'assigned')
        
        volunteer.action_activate()
        self.assertEqual(volunteer.state, 'active')
        
        volunteer.action_archive_volunteer()
        self.assertEqual(volunteer.state, 'archived')
        self.assertFalse(volunteer.active)
        
        volunteer.action_reset_to_candidate()
        self.assertEqual(volunteer.state, 'candidate')

    def test_volunteer_gamification_and_roles(self):
        # 1. Create role and badge
        role = self.env['wc.volunteer.role'].create({
            'name': 'Welcome Host',
            'functional_area': 'protocol',
            'description': 'VIP welcome',
        })
        badge = self.env['wc.volunteer.badge'].create({
            'name': 'Test Badge',
            'points_reward': 150,
        })

        # 2. Create volunteer
        volunteer = self.env['wc.volunteer'].create({
            'name': 'Brahim Test',
            'email': 'brahimtest@example.com',
            'date_of_birth': date.today() - relativedelta(years=22),
            'availability': 'full',
            'skill_ids': [(6, 0, [self.skill_first_aid.id])],
            'language_ids': [(6, 0, [self.lang_ar.id])],
        })

        # Check initial values
        self.assertEqual(volunteer.points, 0)
        self.assertEqual(volunteer.badge_count, 0)
        self.assertFalse(volunteer.role_id)

        # 3. Assign role
        volunteer.write({'role_id': role.id})
        self.assertEqual(volunteer.role_id, role)

        # 4. Earn badge
        volunteer.action_add_badge(badge)
        self.env.flush_all()
        self.assertEqual(volunteer.badge_count, 1)
        self.assertEqual(volunteer.points, 150)
        self.assertIn(badge, volunteer.badge_ids)

        # Re-adding same badge should not duplicate
        volunteer.action_add_badge(badge)
        self.env.flush_all()
        self.assertEqual(volunteer.badge_count, 1)
        self.assertEqual(volunteer.points, 150)

        # 5. Create stadium volunteer quota
        quota = self.env['wc.stadium.volunteer.quota'].create({
            'stadium_id': self.stadium.id,
            'role_id': role.id,
            'quota_required': 5,
        })
        self.assertEqual(quota.quota_assigned, 0)

        # 6. Assign volunteer to stadium and activate to test quota increment
        volunteer.write({
            'assigned_stadium_id': self.stadium.id,
            'state': 'active',
        })
        self.env.flush_all()
        self.env.invalidate_all()
        self.assertEqual(quota.quota_assigned, 1)

