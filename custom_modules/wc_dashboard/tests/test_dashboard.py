from odoo.tests.common import TransactionCase
from odoo.fields import Datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class TestWcDashboard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWcDashboard, cls).setUpClass()

        # ---- Base data ----
        cls.stadium = cls.env['wc.stadium'].create({
            'name': 'Stade de Test Dashboard',
            'city': 'Fes',
            'capacity': 35000,
            'state': 'ready',
            'country': 'morocco',
        })

        cls.match = cls.env['wc.match'].create({
            'team_a': 'Morocco',
            'team_b': 'France',
            'stadium_id': cls.stadium.id,
            'date_time': Datetime.now(),
            'phase': 'semi',
            'state': 'planned',
        })

        cls.skill = cls.env['wc.volunteer.skill'].create({'name': 'Accueil Dashboard', 'color': 1})
        cls.lang = cls.env['wc.volunteer.language'].create({'name': 'Arabe Dashboard', 'color': 1})

        cls.volunteer = cls.env['wc.volunteer'].create({
            'name': 'Volontaire Dashboard',
            'email': 'vol_dashboard@example.com',
            'date_of_birth': date.today() - relativedelta(years=22),
            'availability': 'full',
            'skill_ids': [(6, 0, [cls.skill.id])],
            'language_ids': [(6, 0, [cls.lang.id])],
            'state': 'active',
        })

        cls.badge = cls.env['wc.accreditation'].create({
            'holder_name': 'Presse Dashboard',
            'category': 'media',
            'zone_ids': [],
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=2),
            'state': 'active',
        })

        # ---- Transport data ----
        cls.transport_line = cls.env['wc.transport.line'].create({
            'name': 'Ligne Bus Dashboard',
            'line_type': 'bus',
            'capacity_per_hour': 500,
        })

        cls.station = cls.env['wc.transport.station'].create({
            'name': 'Station Dashboard',
            'code': 'SDASH',
        })

        cls.parking = cls.env['wc.parking.zone'].create({
            'name': 'Parking Dashboard',
            'stadium_id': cls.stadium.id,
            'zone_type': 'public',
            'total_capacity': 1000,
            'available_capacity': 100,
        })

        # ---- Security data ----
        zone = cls.env['wc.stadium.zone'].create({
            'name': 'Zone Dash',
            'stadium_id': cls.stadium.id,
            'zone_type': 'tribune',
            'capacity': 5000,
        })

        cls.deployment = cls.env['wc.security.deployment'].create({
            'match_id': cls.match.id,
            'stadium_zone_id': zone.id,
            'deployment_type': 'police',
            'agent_count': 50,
        })

        cls.crowd = cls.env['wc.crowd.monitoring'].create({
            'match_id': cls.match.id,
            'stadium_zone_id': zone.id,
            'current_headcount': 4800,
            'zone_area': 5000.0,
        })

        # ---- Sustainability data ----
        cls.waste = cls.env['wc.waste.tracking'].create({
            'stadium_id': cls.stadium.id,
            'waste_type': 'plastic',
            'quantity_kg': 500.0,
            'recycled_kg': 200.0,
            'diverted_kg': 100.0,
        })

        cls.carbon = cls.env['wc.carbon.footprint'].create({
            'stadium_id': cls.stadium.id,
            'category': 'energy',
            'emission_tons_co2': 150.0,
            'offset_tons_co2': 30.0,
            'period_start': date.today(),
            'period_end': date.today() + timedelta(days=30),
        })

        cls.audit = cls.env['wc.sustainability.audit'].create({
            'name': 'Audit Dashboard Test',
            'stadium_id': cls.stadium.id,
            'audit_date': date.today(),
            'auditor_name': 'Auditeur Test',
            'iso_category': 'governance',
            'score': 85,
        })

        # ---- Finance data ----
        cls.budget = cls.env['wc.budget.line'].create({
            'name': 'Budget Dashboard Test',
            'stadium_id': cls.stadium.id,
            'category': 'infrastructure',
            'budget_type': 'capex',
            'planned_amount': 1000000,
            'spent_amount': 600000,
            'fiscal_year': '2030',
        })

        cls.revenue = cls.env['wc.revenue.stream'].create({
            'name': 'Revenu Dashboard Test',
            'revenue_type': 'ticketing',
            'period': 'q3_2030',
            'projected_amount': 500000,
            'actual_amount': 450000,
        })

        cls.pricing = cls.env['wc.ticket.pricing'].create({
            'stadium_id': cls.stadium.id,
            'phase': 'group',
            'ticket_category': 'cat3',
            'base_price': 500,
            'total_available': 10000,
            'total_sold': 7000,
        })

    def test_original_kpis(self):
        """Test the original KPIs (volunteer, stadium, match, badge, logistics)."""
        dashboard = self.env['wc.dashboard'].create({'name': 'Test'})

        # Stadiums
        self.assertGreaterEqual(dashboard.stadium_total, 1)
        self.assertGreaterEqual(dashboard.stadium_ready, 1)
        self.assertGreater(dashboard.stadium_total_capacity, 0)

        # Matches
        self.assertGreaterEqual(dashboard.match_total, 1)
        self.assertGreaterEqual(dashboard.match_planned, 1)

        # Volunteers
        self.assertGreaterEqual(dashboard.vol_total, 1)
        self.assertGreaterEqual(dashboard.vol_active, 1)

        # Badges
        self.assertGreaterEqual(dashboard.badge_active, 1)

    def test_transport_kpis(self):
        """Test transport KPIs."""
        dashboard = self.env['wc.dashboard'].create({'name': 'Test Transport'})

        self.assertGreaterEqual(dashboard.transport_line_total, 1)
        self.assertGreaterEqual(dashboard.transport_station_total, 1)
        self.assertGreaterEqual(dashboard.parking_total, 1)
        self.assertGreater(dashboard.parking_avg_occupancy, 0)

    def test_security_kpis(self):
        """Test security KPIs."""
        dashboard = self.env['wc.dashboard'].create({'name': 'Test Security'})

        self.assertGreaterEqual(dashboard.security_deployment_total, 1)
        self.assertGreaterEqual(dashboard.security_agents_total, 50)
        self.assertGreaterEqual(dashboard.crowd_monitoring_total, 1)

    def test_sustainability_kpis(self):
        """Test sustainability KPIs."""
        dashboard = self.env['wc.dashboard'].create({'name': 'Test Sustainability'})

        self.assertGreater(dashboard.waste_total_kg, 0)
        self.assertGreater(dashboard.waste_diversion_avg, 0)
        self.assertGreater(dashboard.carbon_total_emission, 0)
        self.assertGreater(dashboard.carbon_total_offset, 0)
        self.assertGreaterEqual(dashboard.audit_total, 1)

    def test_finance_kpis(self):
        """Test finance KPIs."""
        dashboard = self.env['wc.dashboard'].create({'name': 'Test Finance'})

        self.assertGreater(dashboard.budget_total_planned, 0)
        self.assertGreater(dashboard.budget_total_spent, 0)
        self.assertGreater(dashboard.budget_consumption_avg, 0)
        self.assertGreater(dashboard.revenue_total_projected, 0)
        self.assertGreater(dashboard.revenue_total_actual, 0)
        self.assertGreaterEqual(dashboard.ticket_total_available, 10000)
        self.assertGreaterEqual(dashboard.ticket_total_sold, 7000)
        self.assertGreater(dashboard.ticket_fill_rate, 0)

    def test_qatar_benchmarks(self):
        """Test Qatar 2022 benchmark fields have default values."""
        dashboard = self.env['wc.dashboard'].create({'name': 'Test Benchmarks'})

        self.assertEqual(dashboard.qatar_volunteers, 20000)
        self.assertEqual(dashboard.qatar_stadiums, 8)
        self.assertEqual(dashboard.qatar_capacity, 437000)
        self.assertEqual(dashboard.qatar_matches, 64)
        self.assertEqual(dashboard.qatar_attendance, 3404252)
        self.assertAlmostEqual(dashboard.qatar_carbon_tons, 3630000)
        self.assertAlmostEqual(dashboard.qatar_waste_diverted_pct, 79.0)
        self.assertAlmostEqual(dashboard.qatar_budget_usd_bn, 220.0)

    def test_action_refresh(self):
        """Test the refresh action sets the date."""
        dashboard = self.env['wc.dashboard'].create({'name': 'Test Refresh'})
        self.assertFalse(dashboard.date_refresh)
        dashboard.action_refresh()
        self.assertTrue(dashboard.date_refresh)

    def test_shortcut_actions_return_dict(self):
        """All shortcut actions should return a proper action dict."""
        dashboard = self.env['wc.dashboard'].create({'name': 'Test Actions'})

        actions = [
            dashboard.action_open_critical_incidents(),
            dashboard.action_open_out_of_stock(),
            dashboard.action_open_crowd_alerts(),
            dashboard.action_open_parking_full(),
            dashboard.action_open_non_conformity(),
            dashboard.action_open_budget_overspent(),
            dashboard.action_open_pending_requests(),
        ]
        for action in actions:
            self.assertEqual(action['type'], 'ir.actions.act_window')
            self.assertIn('res_model', action)
            self.assertIn('domain', action)
            self.assertIn('view_mode', action)

    def test_sql_views_original(self):
        """Test existing SQL views (volunteer state, badge category, incident severity)."""
        vol_states = self.env['wc.dashboard.volunteer.state'].search([])
        active_state = vol_states.filtered(lambda r: r.state == 'active')
        self.assertTrue(active_state)

        badge_cats = self.env['wc.dashboard.badge.category'].search([])
        media_cat = badge_cats.filtered(lambda r: r.category == 'media')
        self.assertTrue(media_cat)

    def test_sql_views_new(self):
        """Test the 4 new SQL views: budget, waste, carbon, transport."""
        # Budget by category
        budgets = self.env['wc.dashboard.budget.category'].search([])
        infra = budgets.filtered(lambda r: r.category == 'infrastructure')
        self.assertTrue(infra)
        self.assertGreater(infra.total_planned, 0)
        self.assertGreater(infra.total_spent, 0)

        # Waste by type
        wastes = self.env['wc.dashboard.waste.type'].search([])
        plastic = wastes.filtered(lambda r: r.waste_type == 'plastic')
        self.assertTrue(plastic)
        self.assertGreater(plastic.total_kg, 0)

        # Carbon by category
        carbons = self.env['wc.dashboard.carbon.category'].search([])
        energy = carbons.filtered(lambda r: r.category == 'energy')
        self.assertTrue(energy)
        self.assertGreater(energy.total_emission, 0)

        # Transport by type
        transports = self.env['wc.dashboard.transport.type'].search([])
        bus = transports.filtered(lambda r: r.line_type == 'bus')
        self.assertTrue(bus)
        self.assertGreater(bus.total_capacity, 0)
