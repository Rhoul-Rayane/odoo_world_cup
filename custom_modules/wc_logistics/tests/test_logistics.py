from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.fields import Datetime
from datetime import timedelta

class TestWcLogistics(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWcLogistics, cls).setUpClass()
        cls.stadium = cls.env['wc.stadium'].create({
            'name': 'Grand Stade de Marrakech',
            'city': 'Marrakech',
            'capacity': 45000,
            'country': 'morocco',
        })
        cls.zone = cls.env['wc.stadium.zone'].create({
            'name': 'Zone Tribune Est',
            'stadium_id': cls.stadium.id,
            'zone_type': 'tribune',
            'capacity': 5000,
        })
        cls.match = cls.env['wc.match'].create({
            'team_a': 'Morocco',
            'team_b': 'Portugal',
            'stadium_id': cls.stadium.id,
            'date_time': Datetime.now(),
            'phase': 'quarter',
        })

    def test_incident_workflow(self):
        # Create incident
        incident = self.env['wc.logistics.incident'].create({
            'name': 'Fuite d\'eau tribune Est',
            'description': 'Fuite importante sous les gradins',
            'stadium_id': self.stadium.id,
            'zone_id': self.zone.id,
            'incident_type': 'technical',
            'severity': '3',
        })
        self.assertEqual(incident.state, 'reported')
        
        # Test treatment
        incident.action_start_treatment()
        self.assertEqual(incident.state, 'in_progress')
        
        # Test resolve
        incident.action_resolve()
        self.assertEqual(incident.state, 'resolved')
        self.assertTrue(incident.resolved_date)
        
        # Test close
        incident.action_close()
        self.assertEqual(incident.state, 'closed')

    def test_resource_stock_and_requests(self):
        # Create resource
        resource = self.env['wc.logistics.resource'].create({
            'name': 'Talkies-walkies de test',
            'category': 'communication',
            'total_qty': 100,
            'unit': 'unité',
            'stadium_id': self.stadium.id,
            'zone_id': self.zone.id,
        })
        # Check initial state
        self.assertEqual(resource.available_qty, 100)
        self.assertEqual(resource.state, 'available')
        
        # Create request without lines (submitting should fail)
        req = self.env['wc.logistics.request'].create({
            'stadium_id': self.stadium.id,
            'zone_id': self.zone.id,
            'date_needed': Datetime.now() + timedelta(days=2),
        })
        self.assertEqual(req.state, 'draft')
        with self.assertRaises(ValidationError):
            req.action_submit()
            
        # Add a request line
        self.env['wc.logistics.request.line'].create({
            'request_id': req.id,
            'resource_id': resource.id,
            'quantity': 10,
        })
        self.assertEqual(req.total_items, 10)
        
        # Submit and approve the request
        req.action_submit()
        self.assertEqual(req.state, 'submitted')
        # Check stock not reserved yet (only reserved when approved or delivered)
        self.assertEqual(resource.available_qty, 100)
        
        req.action_approve()
        self.assertEqual(req.state, 'approved')
        # Check stock reserved
        self.assertEqual(resource.available_qty, 90)
        
        # Create another request that takes stock to low levels (< 20% left, so < 20 talkies left)
        req_bulk = self.env['wc.logistics.request'].create({
            'stadium_id': self.stadium.id,
            'date_needed': Datetime.now() + timedelta(days=2),
            'line_ids': [(0, 0, {
                'resource_id': resource.id,
                'quantity': 75,
            })]
        })
        req_bulk.action_submit()
        req_bulk.action_approve()
        
        # Available qty should be 15
        self.assertEqual(resource.available_qty, 15)
        self.assertEqual(resource.state, 'low')
        
        # Another request that consumes everything
        req_out = self.env['wc.logistics.request'].create({
            'stadium_id': self.stadium.id,
            'date_needed': Datetime.now() + timedelta(days=2),
            'line_ids': [(0, 0, {
                'resource_id': resource.id,
                'quantity': 15,
            })]
        })
        req_out.action_submit()
        req_out.action_approve()
        
        # Available qty should be 0
        self.assertEqual(resource.available_qty, 0)
        self.assertEqual(resource.state, 'out')

    def test_transport_workflow(self):
        dest_stadium = self.env['wc.stadium'].create({
            'name': 'Complexe Sportif Moulay Abdellah',
            'city': 'Rabat',
            'capacity': 65000,
            'country': 'morocco',
        })
        
        transport = self.env['wc.logistics.transport'].create({
            'name': 'SHUTTLE-MAR-RAB-01',
            'vehicle_type': 'bus',
            'capacity': 50,
            'origin_stadium_id': self.stadium.id,
            'destination_stadium_id': dest_stadium.id,
            'departure_time': Datetime.now() + timedelta(hours=4),
        })
        self.assertEqual(transport.state, 'planned')
        
        transport.action_board()
        self.assertEqual(transport.state, 'boarding')
        
        transport.action_depart()
        self.assertEqual(transport.state, 'transit')
        
        transport.action_arrive()
        self.assertEqual(transport.state, 'arrived')
