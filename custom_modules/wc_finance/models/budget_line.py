from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BudgetLine(models.Model):
    _name = 'wc.budget.line'
    _description = 'Ligne budgétaire analytique'
    _inherit = ['mail.thread']
    _order = 'stadium_id, category'

    name = fields.Char(
        string='Intitulé',
        required=True,
        tracking=True,
    )
    stadium_id = fields.Many2one(
        'wc.stadium',
        string='Stade',
        required=True,
        tracking=True,
    )
    category = fields.Selection([
        ('infrastructure', 'Infrastructure & BTP'),
        ('technology', 'Technologie & IT'),
        ('security', 'Sécurité'),
        ('logistics', 'Logistique'),
        ('hospitality', 'Hospitalité & Accueil'),
        ('marketing', 'Marketing & Communication'),
        ('hr', 'Ressources Humaines'),
        ('medical', 'Services Médicaux'),
        ('sustainability', 'Durabilité & Environnement'),
        ('other', 'Autre'),
    ], string='Catégorie', required=True, tracking=True)
    budget_type = fields.Selection([
        ('capex', 'CAPEX (Investissement)'),
        ('opex', 'OPEX (Fonctionnement)'),
    ], string='Type de budget', required=True, default='opex', tracking=True)
    planned_amount = fields.Float(
        string='Budget prévisionnel (MAD)',
        required=True,
    )
    committed_amount = fields.Float(
        string='Montant engagé (MAD)',
        default=0,
    )
    spent_amount = fields.Float(
        string='Montant dépensé (MAD)',
        default=0,
    )
    remaining_amount = fields.Float(
        string='Reste à dépenser (MAD)',
        compute='_compute_remaining_and_rate',
        store=True,
    )
    consumption_rate = fields.Float(
        string='Taux de consommation (%)',
        compute='_compute_remaining_and_rate',
        store=True,
    )
    fiscal_year = fields.Char(
        string='Exercice fiscal',
        required=True,
        default='2030',
    )
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user,
    )
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('approved', 'Approuvé'),
        ('locked', 'Verrouillé'),
        ('closed', 'Clôturé'),
    ], string='Statut', default='draft', tracking=True)
    notes = fields.Text(string='Notes')

    # ---- Computed fields ----

    @api.depends('planned_amount', 'spent_amount')
    def _compute_remaining_and_rate(self):
        for rec in self:
            rec.remaining_amount = rec.planned_amount - rec.spent_amount
            if rec.planned_amount:
                rec.consumption_rate = (rec.spent_amount / rec.planned_amount) * 100
            else:
                rec.consumption_rate = 0.0

    # ---- Constraints ----

    @api.constrains('planned_amount')
    def _check_planned_amount(self):
        for rec in self:
            if rec.planned_amount <= 0:
                raise ValidationError(
                    "Le budget prévisionnel doit être strictement positif."
                )

    @api.constrains('spent_amount', 'planned_amount')
    def _check_spent_amount(self):
        for rec in self:
            if rec.spent_amount > rec.planned_amount:
                raise ValidationError(
                    "Le montant dépensé ne peut pas dépasser le budget prévisionnel."
                )

    @api.constrains('committed_amount')
    def _check_committed_amount(self):
        for rec in self:
            if rec.committed_amount < 0:
                raise ValidationError(
                    "Le montant engagé ne peut pas être négatif."
                )

    # ---- Workflow actions ----

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_lock(self):
        self.write({'state': 'locked'})

    def action_close(self):
        self.write({'state': 'closed'})
