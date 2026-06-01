from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TicketPricing(models.Model):
    _name = 'wc.ticket.pricing'
    _description = 'Grille tarifaire de billetterie'
    _order = 'phase, ticket_category, stadium_id'

    PHASE_SELECTION = [
        ('group', 'Phase de groupes'),
        ('round16', 'Huitièmes de finale'),
        ('quarter', 'Quarts de finale'),
        ('semi', 'Demi-finales'),
        ('third', 'Match pour la 3ème place'),
        ('final', 'Finale'),
    ]

    CATEGORY_SELECTION = [
        ('cat1', 'Catégorie 1 (Carré VIP)'),
        ('cat2', 'Catégorie 2 (Tribune centrale)'),
        ('cat3', 'Catégorie 3 (Tribune latérale)'),
        ('cat4', 'Catégorie 4 (Virage / Populaire)'),
    ]

    name = fields.Char(
        string='Tarif',
        compute='_compute_name',
        store=True,
    )
    stadium_id = fields.Many2one(
        'wc.stadium',
        string='Stade',
        required=True,
        tracking=True,
    )
    phase = fields.Selection(
        PHASE_SELECTION,
        string='Phase',
        required=True,
        tracking=True,
    )
    ticket_category = fields.Selection(
        CATEGORY_SELECTION,
        string='Catégorie de billet',
        required=True,
        tracking=True,
    )
    base_price = fields.Float(
        string='Prix de base (MAD)',
        required=True,
    )
    early_bird_price = fields.Float(
        string='Prix Early Bird (MAD)',
    )
    last_minute_price = fields.Float(
        string='Prix Last Minute (MAD)',
    )
    resident_discount_pct = fields.Float(
        string='Remise résidents (%)',
        default=20,
    )
    student_discount_pct = fields.Float(
        string='Remise étudiants (%)',
        default=40,
    )
    final_price_resident = fields.Float(
        string='Prix résident (MAD)',
        compute='_compute_final_prices',
        store=True,
    )
    final_price_student = fields.Float(
        string='Prix étudiant (MAD)',
        compute='_compute_final_prices',
        store=True,
    )
    total_available = fields.Integer(
        string='Places disponibles',
        required=True,
    )
    total_sold = fields.Integer(
        string='Places vendues',
        default=0,
    )
    fill_rate = fields.Float(
        string='Taux de remplissage (%)',
        compute='_compute_fill_rate',
        store=True,
    )
    active = fields.Boolean(default=True)

    # ---- SQL Constraints ----

    _sql_constraints = [
        (
            'unique_stadium_phase_category',
            'UNIQUE(stadium_id, phase, ticket_category)',
            'Une grille tarifaire existe déjà pour cette combinaison stade / phase / catégorie.',
        ),
    ]

    # ---- Computed fields ----

    @api.depends('phase', 'ticket_category', 'stadium_id', 'stadium_id.name')
    def _compute_name(self):
        phase_dict = dict(self.PHASE_SELECTION)
        category_dict = dict(self.CATEGORY_SELECTION)
        for rec in self:
            phase_label = phase_dict.get(rec.phase, '')
            category_label = category_dict.get(rec.ticket_category, '')
            stadium_name = rec.stadium_id.name or ''
            rec.name = f"{phase_label} - {category_label} - {stadium_name}"

    @api.depends('base_price', 'resident_discount_pct', 'student_discount_pct')
    def _compute_final_prices(self):
        for rec in self:
            rec.final_price_resident = rec.base_price * (1 - rec.resident_discount_pct / 100)
            rec.final_price_student = rec.base_price * (1 - rec.student_discount_pct / 100)

    @api.depends('total_sold', 'total_available')
    def _compute_fill_rate(self):
        for rec in self:
            if rec.total_available:
                rec.fill_rate = (rec.total_sold / rec.total_available) * 100
            else:
                rec.fill_rate = 0.0

    # ---- Constraints ----

    @api.constrains('base_price')
    def _check_base_price(self):
        for rec in self:
            if rec.base_price <= 0:
                raise ValidationError(
                    "Le prix de base doit être strictement positif."
                )

    @api.constrains('total_sold', 'total_available')
    def _check_total_sold(self):
        for rec in self:
            if rec.total_sold > rec.total_available:
                raise ValidationError(
                    "Le nombre de places vendues ne peut pas dépasser les places disponibles."
                )

    @api.constrains('resident_discount_pct')
    def _check_resident_discount(self):
        for rec in self:
            if rec.resident_discount_pct < 0 or rec.resident_discount_pct > 100:
                raise ValidationError(
                    "La remise résidents doit être comprise entre 0 et 100 %."
                )

    @api.constrains('student_discount_pct')
    def _check_student_discount(self):
        for rec in self:
            if rec.student_discount_pct < 0 or rec.student_discount_pct > 100:
                raise ValidationError(
                    "La remise étudiants doit être comprise entre 0 et 100 %."
                )
