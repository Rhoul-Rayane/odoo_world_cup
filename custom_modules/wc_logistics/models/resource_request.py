from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LogisticsRequest(models.Model):
    _name = 'wc.logistics.request'
    _description = 'Demande de Ressources Logistiques'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date_needed'

    name = fields.Char(string='Référence', readonly=True, default='Nouveau', copy=False)
    match_id = fields.Many2one('wc.match', string='Match concerné')
    stadium_id = fields.Many2one('wc.stadium', string='Stade', required=True, tracking=True)
    zone_id = fields.Many2one('wc.stadium.zone', string='Zone de destination',
                              domain="[('stadium_id', '=', stadium_id)]")
    requester_id = fields.Many2one('res.users', string='Demandeur',
                                    default=lambda self: self.env.user, readonly=True)
    date_needed = fields.Datetime(string='Date et heure souhaitées', required=True)

    line_ids = fields.One2many('wc.logistics.request.line', 'request_id',
                                string='Ressources demandées')
    total_items = fields.Integer(string='Total articles', compute='_compute_total_items')

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
        ('2', 'Urgent'),
        ('3', 'Critique'),
    ], string='Priorité', default='0', tracking=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumise'),
        ('approved', 'Approuvée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ], string='Statut', default='draft', tracking=True)

    notes = fields.Text(string='Instructions spéciales')

    @api.depends('line_ids.quantity')
    def _compute_total_items(self):
        for record in self:
            record.total_items = sum(record.line_ids.mapped('quantity'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('wc.logistics.request') or 'Nouveau'
        return super().create(vals_list)

    def action_submit(self):
        for record in self:
            if not record.line_ids:
                raise ValidationError("Ajoutez au moins une ressource à la demande.")
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_deliver(self):
        self.write({'state': 'delivered'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset(self):
        self.write({'state': 'draft'})
