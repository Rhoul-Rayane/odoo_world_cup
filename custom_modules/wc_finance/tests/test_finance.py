from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestFinance(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stadium = cls.env['wc.stadium'].create({
            'name': 'Grand Stade de Casablanca',
            'city': 'Casablanca',
            'capacity': 93000,
            'country': 'morocco',
        })
        cls.match = cls.env['wc.match'].create({
            'team_a': 'Maroc',
            'team_b': 'Espagne',
            'stadium_id': cls.stadium.id,
            'date_time': '2030-07-15 20:00:00',
            'phase': 'final',
        })

    # ================================================================
    # Budget Line Tests
    # ================================================================

    def test_budget_line_remaining_and_rate(self):
        """Test computed remaining_amount and consumption_rate."""
        budget = self.env['wc.budget.line'].create({
            'name': 'Rénovation pelouse',
            'stadium_id': self.stadium.id,
            'category': 'infrastructure',
            'budget_type': 'capex',
            'planned_amount': 1000000,
            'spent_amount': 250000,
        })
        self.assertAlmostEqual(budget.remaining_amount, 750000)
        self.assertAlmostEqual(budget.consumption_rate, 25.0)

    def test_budget_line_overspend_constraint(self):
        """Spending more than planned should raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.env['wc.budget.line'].create({
                'name': 'Éclairage',
                'stadium_id': self.stadium.id,
                'category': 'technology',
                'budget_type': 'opex',
                'planned_amount': 500000,
                'spent_amount': 600000,
            })

    def test_budget_workflow(self):
        """Test full workflow: draft → approved → locked → closed."""
        budget = self.env['wc.budget.line'].create({
            'name': 'Sécurité périmétrique',
            'stadium_id': self.stadium.id,
            'category': 'security',
            'budget_type': 'opex',
            'planned_amount': 200000,
        })
        self.assertEqual(budget.state, 'draft')
        budget.action_approve()
        self.assertEqual(budget.state, 'approved')
        budget.action_lock()
        self.assertEqual(budget.state, 'locked')
        budget.action_close()
        self.assertEqual(budget.state, 'closed')

    # ================================================================
    # Revenue Stream Tests
    # ================================================================

    def test_revenue_variance_computation(self):
        """Test variance and variance_pct computation."""
        revenue = self.env['wc.revenue.stream'].create({
            'name': 'Billetterie Finale',
            'revenue_type': 'ticketing',
            'stadium_id': self.stadium.id,
            'projected_amount': 5000000,
            'actual_amount': 5500000,
            'period': 'q3_2030',
        })
        self.assertAlmostEqual(revenue.variance, 500000)
        self.assertAlmostEqual(revenue.variance_pct, 10.0)

    def test_revenue_workflow(self):
        """Test full workflow: forecast → confirmed → invoiced → collected."""
        revenue = self.env['wc.revenue.stream'].create({
            'name': 'Sponsoring Nike',
            'revenue_type': 'sponsorship',
            'projected_amount': 10000000,
            'period': 'q1_2030',
        })
        self.assertEqual(revenue.state, 'forecast')
        revenue.action_confirm()
        self.assertEqual(revenue.state, 'confirmed')
        revenue.action_invoice()
        self.assertEqual(revenue.state, 'invoiced')
        revenue.action_collect()
        self.assertEqual(revenue.state, 'collected')

    # ================================================================
    # Ticket Pricing Tests
    # ================================================================

    def test_ticket_pricing_discounts(self):
        """Test computed resident and student prices."""
        pricing = self.env['wc.ticket.pricing'].create({
            'stadium_id': self.stadium.id,
            'phase': 'final',
            'ticket_category': 'cat1',
            'base_price': 5000,
            'resident_discount_pct': 20,
            'student_discount_pct': 40,
            'total_available': 10000,
        })
        self.assertAlmostEqual(pricing.final_price_resident, 4000)
        self.assertAlmostEqual(pricing.final_price_student, 3000)

    def test_ticket_pricing_fill_rate(self):
        """Test fill_rate computation."""
        pricing = self.env['wc.ticket.pricing'].create({
            'stadium_id': self.stadium.id,
            'phase': 'group',
            'ticket_category': 'cat3',
            'base_price': 500,
            'total_available': 20000,
            'total_sold': 15000,
        })
        self.assertAlmostEqual(pricing.fill_rate, 75.0)

    def test_ticket_pricing_unique_constraint(self):
        """Verify _sql_constraints is defined on the model."""
        model = self.env['wc.ticket.pricing']
        constraints = {c[0] for c in model._sql_constraints}
        self.assertIn(
            'unique_stadium_phase_category', constraints,
            "_sql_constraints should include 'unique_stadium_phase_category'",
        )

    def test_ticket_pricing_oversell_constraint(self):
        """total_sold > total_available should raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.env['wc.ticket.pricing'].create({
                'stadium_id': self.stadium.id,
                'phase': 'quarter',
                'ticket_category': 'cat4',
                'base_price': 300,
                'total_available': 5000,
                'total_sold': 6000,
            })
