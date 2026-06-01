from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RevenueStream(models.Model):
    _name = 'wc.revenue.stream'
    _description = 'Flux de revenus'
    _inherit = ['mail.thread']
    _order = 'period, revenue_type'

    name = fields.Char(
        string='Source de revenu',
        required=True,
        tracking=True,
    )
    revenue_type = fields.Selection([
        ('ticketing', 'Billetterie'),
        ('sponsorship', 'Sponsoring'),
        ('broadcasting', 'Droits de diffusion'),
        ('merchandising', 'Merchandising'),
        ('hospitality', 'Hospitalité & VIP'),
        ('concession', 'Concessions alimentaires'),
        ('parking', 'Parking'),
        ('other', 'Autre'),
    ], string='Type de revenu', required=True, tracking=True)
    stadium_id = fields.Many2one(
        'wc.stadium',
        string='Stade',
    )
    match_id = fields.Many2one(
        'wc.match',
        string='Match',
    )
    projected_amount = fields.Float(
        string='Montant projeté (MAD)',
        required=True,
    )
    actual_amount = fields.Float(
        string='Montant réalisé (MAD)',
        default=0,
    )
    variance = fields.Float(
        string='Écart (MAD)',
        compute='_compute_variance',
        store=True,
    )
    variance_pct = fields.Float(
        string='Écart (%)',
        compute='_compute_variance',
        store=True,
    )
    period = fields.Selection([
        ('q1_2029', 'T1 2029'),
        ('q2_2029', 'T2 2029'),
        ('q3_2029', 'T3 2029'),
        ('q4_2029', 'T4 2029'),
        ('q1_2030', 'T1 2030'),
        ('q2_2030', 'T2 2030 (Pré-tournoi)'),
        ('q3_2030', 'T3 2030 (Tournoi)'),
        ('q4_2030', 'T4 2030 (Post-tournoi)'),
    ], string='Période', required=True, tracking=True)
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('forecast', 'Prévisionnel'),
        ('confirmed', 'Confirmé'),
        ('invoiced', 'Facturé'),
        ('collected', 'Encaissé'),
    ], string='Statut', default='forecast', tracking=True)

    # ---- Computed fields ----

    @api.depends('actual_amount', 'projected_amount')
    def _compute_variance(self):
        for rec in self:
            rec.variance = rec.actual_amount - rec.projected_amount
            if rec.projected_amount:
                rec.variance_pct = (
                    (rec.actual_amount - rec.projected_amount) / rec.projected_amount
                ) * 100
            else:
                rec.variance_pct = 0.0

    # ---- Constraints ----

    @api.constrains('projected_amount')
    def _check_projected_amount(self):
        for rec in self:
            if rec.projected_amount <= 0:
                raise ValidationError(
                    "Le montant projeté doit être strictement positif."
                )

    # ---- Workflow actions ----

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_invoice(self):
        self.write({'state': 'invoiced'})

    def action_collect(self):
        self.write({'state': 'collected'})
