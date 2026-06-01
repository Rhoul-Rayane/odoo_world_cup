from odoo.tests.common import TransactionCase
from odoo.fields import Datetime

class TestWcBase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWcBase, cls).setUpClass()
        cls.stadium = cls.env['wc.stadium'].create({
            'name': 'Grand Stade de Casablanca',
            'city': 'Casablanca',
            'capacity': 115000,
            'country': 'morocco',
        })
        cls.zone_vip = cls.env['wc.stadium.zone'].create({
            'name': 'Zone VIP A',
            'stadium_id': cls.stadium.id,
            'zone_type': 'vip',
            'capacity': 1000,
        })
        cls.match = cls.env['wc.match'].create({
            'team_a': 'Morocco',
            'team_b': 'Spain',
            'stadium_id': cls.stadium.id,
            'date_time': Datetime.now(),
            'phase': 'semi',
        })

    def test_stadium_computes_and_actions(self):
        # Test stadium computed fields
        self.assertEqual(self.stadium.zone_count, 1)
        self.assertEqual(self.stadium.match_count, 1)

        # Test stadium actions
        self.assertEqual(self.stadium.state, 'construction')
        self.stadium.action_set_ready()
        self.assertEqual(self.stadium.state, 'ready')
        self.stadium.action_set_maintenance()
        self.assertEqual(self.stadium.state, 'maintenance')

    def test_stadium_zone_display_name(self):
        # Test _compute_display_name (replaces deprecated name_get)
        self.assertEqual(self.zone_vip.display_name, "Grand Stade de Casablanca - Zone VIP A")

    def test_match_computes_and_actions(self):
        # Test match computed name
        self.assertEqual(self.match.name, "Morocco vs Spain")

        # Test match actions
        self.assertEqual(self.match.state, 'planned')
        self.match.action_start()
        self.assertEqual(self.match.state, 'ongoing')
        self.match.action_end()
        self.assertEqual(self.match.state, 'done')
