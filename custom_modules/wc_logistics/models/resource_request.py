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
    picking_id = fields.Many2one('stock.picking', string='Transfert de stock associé', readonly=True)

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
        for record in self:
            if not record.picking_id:
                if not record.stadium_id or not record.stadium_id.location_id:
                    continue
                
                # Emplacement client de destination
                customer_loc = self.env.ref('stock.stock_location_customers', raise_if_not_found=False)
                customer_loc_id = customer_loc.id if customer_loc else False

                # Type de transfert : Livraison
                picking_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'outgoing')
                ], limit=1)
                if not picking_type:
                    picking_type = self.env['stock.picking.type'].search([
                        ('code', '=', 'internal')
                    ], limit=1)
                picking_type_id = picking_type.id if picking_type else False

                # Création du Bon de Transfert
                picking = self.env['stock.picking'].create({
                    'picking_type_id': picking_type_id,
                    'location_id': record.stadium_id.location_id.id,
                    'location_dest_id': customer_loc_id,
                    'origin': record.name,
                })

                # Création des lignes de mouvement de stock
                for line in record.line_ids:
                    if line.resource_id.product_id:
                        self.env['stock.move'].create({
                            'name': line.resource_id.name,
                            'product_id': line.resource_id.product_id.id,
                            'product_uom_qty': float(line.quantity),
                            'product_uom': line.resource_id.product_id.uom_id.id,
                            'location_id': record.stadium_id.location_id.id,
                            'location_dest_id': customer_loc_id,
                            'picking_id': picking.id,
                        })
                
                # Confirmer et réserver les quantités
                picking.action_confirm()
                picking.action_assign()
                
                record.picking_id = picking.id

    def action_deliver(self):
        self.write({'state': 'delivered'})
        for record in self:
            if record.picking_id and record.picking_id.state not in ('done', 'cancel'):
                # Valider le transfert de stock associé
                for move in record.picking_id.move_ids:
                    if hasattr(move, 'quantity'):
                        move.quantity = move.product_uom_qty
                    elif hasattr(move, 'quantity_done'):
                        move.quantity_done = move.product_uom_qty
                
                record.picking_id.button_validate()

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        for record in self:
            if record.picking_id and record.picking_id.state not in ('done', 'cancel'):
                record.picking_id.action_cancel()

    def action_reset(self):
        self.write({'state': 'draft'})
        for record in self:
            if record.picking_id and record.picking_id.state not in ('done', 'cancel'):
                record.picking_id.action_cancel()
            record.picking_id = False
