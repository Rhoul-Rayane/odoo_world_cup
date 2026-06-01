from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SustainabilityAudit(models.Model):
    _name = 'wc.sustainability.audit'
    _description = 'Audit ISO 20121'
    _inherit = ['mail.thread']
    _order = 'audit_date desc'

    name = fields.Char(
        string="Titre de l'audit",
        required=True,
        tracking=True,
    )
    stadium_id = fields.Many2one(
        'wc.stadium',
        string='Stade',
        required=True,
        tracking=True,
    )
    audit_date = fields.Date(
        string="Date de l'audit",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    auditor_name = fields.Char(
        string='Auditeur',
        required=True,
    )
    iso_category = fields.Selection(
        [
            ('governance', 'Gouvernance & Leadership'),
            ('planning', 'Planification'),
            ('support', 'Support & Ressources'),
            ('operation', 'Opérations'),
            ('performance', 'Évaluation des performances'),
            ('improvement', 'Amélioration continue'),
        ],
        string='Catégorie ISO',
        required=True,
        tracking=True,
    )
    score = fields.Integer(
        string='Score (0-100)',
        default=0,
    )
    state = fields.Selection(
        [
            ('planned', 'Planifié'),
            ('in_progress', 'En cours'),
            ('completed', 'Terminé'),
            ('non_conformity', 'Non-conformité détectée'),
        ],
        string='État',
        default='planned',
        tracking=True,
    )
    findings = fields.Html(
        string='Constats',
    )
    corrective_actions = fields.Html(
        string='Actions correctives',
    )
    next_audit_date = fields.Date(
        string='Prochain audit',
    )
    compliance_level = fields.Selection(
        [
            ('full', 'Conforme'),
            ('partial', 'Partiellement conforme'),
            ('non_compliant', 'Non conforme'),
        ],
        string='Niveau de conformité',
        compute='_compute_compliance_level',
        store=True,
    )

    @api.depends('score')
    def _compute_compliance_level(self):
        for record in self:
            if record.score >= 80:
                record.compliance_level = 'full'
            elif record.score >= 50:
                record.compliance_level = 'partial'
            else:
                record.compliance_level = 'non_compliant'

    @api.constrains('score')
    def _check_score_range(self):
        for record in self:
            if record.score < 0 or record.score > 100:
                raise ValidationError(
                    "Le score doit être compris entre 0 et 100."
                )

    @api.constrains('next_audit_date', 'audit_date')
    def _check_next_audit_date(self):
        for record in self:
            if record.next_audit_date and record.audit_date and record.next_audit_date <= record.audit_date:
                raise ValidationError(
                    "La date du prochain audit doit être postérieure à la date "
                    "de l'audit actuel."
                )

    def action_start(self):
        for record in self:
            record.state = 'in_progress'

    def action_complete(self):
        for record in self:
            record.state = 'completed'

    def action_flag_nonconformity(self):
        for record in self:
            record.state = 'non_conformity'
