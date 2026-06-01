from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.fields import Datetime
from datetime import datetime, timedelta

class TestWcTransport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWcTransport, cls).setUpClass()
        
        # Create a test stadium (using unique fifa_code TTR to avoid conflicts)
        cls.stadium = cls.env['wc.stadium'].create({
            'name': 'Stade de Transport Test',
            'city': 'Rabat',
            'capacity': 60000,
            'country': 'morocco',
            'fifa_code': 'TTR',
        })

        # Create a test match
        cls.match = cls.env['wc.match'].create({
            'team_a': 'Morocco Test',
            'team_b': 'Spain Test',
            'stadium_id': cls.stadium.id,
            'date_time': Datetime.now(),
            'phase': 'group',
        })

        # Create a transport line
        cls.line = cls.env['wc.transport.line'].create({
            'name': 'Tramway Test L1',
            'line_type': 'tram',
            'capacity_per_hour': 3000,
            'color': '#FF0000',
        })

        # Create a transport station
        cls.station = cls.env['wc.transport.station'].create({
            'name': 'Station Stade Test',
            'code': 'TSTAT',
            'gps_lat': 33.9984,
            'gps_lng': -6.8569,
            'stadium_id': cls.stadium.id,
            'line_ids': [(4, cls.line.id)],
        })

        # Create a parking zone
        cls.parking = cls.env['wc.parking.zone'].create({
            'name': 'Parking Test VIP',
            'stadium_id': cls.stadium.id,
            'zone_type': 'vip',
            'total_capacity': 100,
            'available_capacity': 100,
        })

    def test_parking_occupancy_and_constraints(self):
        # 1. Check initial occupancy is 0%
        self.assertEqual(self.parking.occupancy_rate, 0.0)

        # 2. Update available capacity and check occupancy rate
        self.parking.write({'available_capacity': 40})
        self.assertEqual(self.parking.occupancy_rate, 60.0)

        # 3. Test validation constraint: available > total
        with self.assertRaises(ValidationError):
            self.parking.write({'available_capacity': 150})
        
        # 4. Test validation constraint: negative total
        with self.assertRaises(ValidationError):
            self.parking.write({'total_capacity': -10})

        # 5. Test validation constraint: negative available
        with self.assertRaises(ValidationError):
            self.parking.write({'available_capacity': -5})

    def test_station_uniqueness_constraint(self):
        # Test station code uniqueness constraint
        with self.assertRaises(Exception):
            self.env['wc.transport.station'].create({
                'name': 'Station Stade Test 2',
                'code': 'TSTAT',
            })
            self.env.cr.flush()

    def test_schedule_and_date_constraints(self):
        start = datetime.now()
        end = start + timedelta(hours=2)

        # Create a valid schedule
        schedule = self.env['wc.transport.schedule'].create({
            'match_id': self.match.id,
            'line_id': self.line.id,
            'start_time': start,
            'end_time': end,
            'frequency_minutes': 4,
            'planned_passengers': 4000,
        })
        self.assertEqual(schedule.frequency_minutes, 4)

        # Test validation constraint: end_time before start_time
        with self.assertRaises(ValidationError):
            schedule.write({
                'end_time': start - timedelta(hours=1)
            })
