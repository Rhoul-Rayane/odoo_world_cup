from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.fields import Datetime
from datetime import date
from dateutil.relativedelta import relativedelta

class TestWcData(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWcData, cls).setUpClass()
        # Create a tournament
        cls.tournament = cls.env['wc.tournament'].create({
            'key': 'WC-2030-TEST',
            'name': '2030 FIFA World Cup Test',
            'year': 2030,
            'host_country': 'Morocco',
            'winner': 'Morocco',
            'teams_count': 48,
        })
        # Create teams
        cls.team_mar = cls.env['wc.team'].create({
            'name': 'Maroc Test',
            'code_fifa': 'TMA',
            'confederation': 'CAF',
            'fifa_ranking': 10,
            'lpi_score': 3.5,
            'lpi_rank': 25,
        })
        cls.team_esp = cls.env['wc.team'].create({
            'name': 'Espagne Test',
            'code_fifa': 'TES',
            'confederation': 'UEFA',
            'fifa_ranking': 8,
            'lpi_score': 3.8,
            'lpi_rank': 15,
        })
        # Create a stadium
        cls.stadium = cls.env['wc.stadium'].create({
            'name': 'Grand Stade Hassan II Test',
            'city': 'Benslimane',
            'capacity': 115000,
            'country': 'morocco',
            'fifa_code': 'TCA',
            'gps_lat': 33.6214,
            'gps_lng': -7.5028,
        })

    def test_tournament_computes_and_constraints(self):
        # Test display_name (replaces deprecated name_get)
        self.assertEqual(self.tournament.display_name, "2030 - Morocco")
        
        # Test key uniqueness constraint
        with self.assertRaises(Exception):
            self.env['wc.tournament'].create({
                'key': 'WC-2030-TEST',
                'name': 'Another Tournament',
                'year': 2034,
            })
            self.env.cr.flush()

    def test_team_computes_and_constraints(self):
        # Test display_name (replaces deprecated name_get)
        self.assertEqual(self.team_mar.display_name, "Maroc Test (TMA)")
        
        # Test FIFA code uniqueness constraint
        with self.assertRaises(Exception):
            self.env['wc.team'].create({
                'name': 'Maroc Bis',
                'code_fifa': 'TMA',
            })
            self.env.cr.flush()

    def test_stadium_extended_fields_and_constraints(self):
        self.assertEqual(self.stadium.gps_lat, 33.6214)
        self.assertEqual(self.stadium.gps_lng, -7.5028)
        self.assertEqual(self.stadium.fifa_code, 'TCA')

        # Test FIFA code uniqueness constraint
        with self.assertRaises(Exception):
            self.env['wc.stadium'].create({
                'name': 'Another Stadium',
                'city': 'Casablanca',
                'capacity': 80000,
                'country': 'morocco',
                'fifa_code': 'TCA',
            })
            self.env.cr.flush()

    def test_match_extended_fields_and_autosync(self):
        # Create match setting team_a_id and team_b_id (without team_a and team_b)
        # It should automatically sync names
        match = self.env['wc.match'].create({
            'team_a_id': self.team_mar.id,
            'team_b_id': self.team_esp.id,
            'stadium_id': self.stadium.id,
            'date_time': Datetime.now(),
            'phase': 'final',
            'tournament_id': self.tournament.id,
            'is_historical': True,
        })
        
        self.assertEqual(match.team_a, 'Maroc Test')
        self.assertEqual(match.team_b, 'Espagne Test')
        self.assertEqual(match.name, 'Maroc Test vs Espagne Test')
        self.assertTrue(match.is_historical)
        self.assertEqual(match.tournament_id, self.tournament)

        # Test write synchronization
        team_fra = self.env['wc.team'].create({
            'name': 'France Test',
            'code_fifa': 'TFR',
            'confederation': 'UEFA',
        })
        match.write({'team_b_id': team_fra.id})
        self.assertEqual(match.team_b, 'France Test')
        self.assertEqual(match.name, 'Maroc Test vs France Test')

    def test_volunteer_extended_fields(self):
        volunteer = self.env['wc.volunteer'].create({
            'name': 'Volontaire Data Test',
            'email': 'voldatatest@example.com',
            'date_of_birth': date.today() - relativedelta(years=20),
            'availability': 'full',
            'skill_ids': [], # Many2many can be empty in test case
            'language_ids': [],
            'functional_area': 'security',
            'training_level': 'basic',
            'hours_worked': 24,
            'attendance_rate': 95.5,
        })
        
        self.assertEqual(volunteer.functional_area, 'security')
        self.assertEqual(volunteer.training_level, 'basic')
        self.assertEqual(volunteer.hours_worked, 24)
        self.assertEqual(volunteer.attendance_rate, 95.5)
