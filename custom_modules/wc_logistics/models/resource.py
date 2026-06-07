from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LogisticsResource(models.Model):
    _name = 'wc.logistics.resource'
    _description = 'Ressource Logistique'
    _inherit = ['mail.thread']
    _order = 'category, name'

    name = fields.Char(string='Désignation', required=True, tracking=True)
    category = fields.Selection([
        ('furniture', 'Mobilier (chaises, tables, tentes)'),
        ('signage', 'Signalétique (panneaux, bannières)'),
        ('tech', 'Équipement technique (écrans, son)'),
        ('medical', 'Matériel médical'),
        ('security', 'Équipement sécurité'),
        ('cleaning', 'Matériel entretien'),
        ('catering', 'Restauration (frigos, fontaines)'),
        ('communication', 'Communication (talkies, radios)'),
    ], string='Catégorie', required=True, tracking=True)

    total_qty = fields.Integer(string='Stock initial', required=True, default=1)
    available_qty = fields.Integer(string='Quantité disponible',
                                   compute='_compute_available_qty', store=True)
    unit = fields.Char(string='Unité', default='unité')

    stadium_id = fields.Many2one('wc.stadium', string='Stade de stockage', tracking=True)
    zone_id = fields.Many2one('wc.stadium.zone', string='Zone',
                              domain="[('stadium_id', '=', stadium_id)]")

    state = fields.Selection([
        ('available', 'Disponible'),
        ('low', 'Stock faible'),
        ('out', 'Rupture'),
    ], string='État', compute='_compute_state', store=True)

    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    product_id = fields.Many2one('product.product', string='Article Odoo associé', ondelete='cascade')
    cost = fields.Float(related='product_id.standard_price', string='Coût unitaire', readonly=False)

    # Relations
    request_line_ids = fields.One2many('wc.logistics.request.line', 'resource_id',
                                       string='Demandes liées')

    @api.depends('product_id', 'stadium_id.location_id')
    def _compute_available_qty(self):
        for record in self:
            if record.product_id and record.stadium_id and record.stadium_id.location_id:
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', record.product_id.id),
                    ('location_id', '=', record.stadium_id.location_id.id)
                ])
                # Quantité disponible = Quantité en main - Quantité réservée
                record.available_qty = sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity'))
            else:
                record.available_qty = 0

    @api.depends('available_qty', 'total_qty')
    def _compute_state(self):
        for record in self:
            if record.available_qty <= 0:
                record.state = 'out'
            elif record.available_qty < (record.total_qty * 0.2):
                record.state = 'low'
            else:
                record.state = 'available'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('product_id'):
                # Création automatique de l'article stockable Odoo (non vendable, uniquement achetable)
                product_vals = {
                    'name': vals.get('name', 'Ressource logistique'),
                    'type': 'consu',
                    'is_storable': True,
                    'sale_ok': False,
                    'purchase_ok': True,
                }
                if 'cost' in vals:
                    product_vals['standard_price'] = vals['cost']
                
                product = self.env['product.product'].create(product_vals)
                vals['product_id'] = product.id
        
        resources = super(LogisticsResource, self).create(vals_list)
        
        # Initialisation du stock physique Odoo avec le stock initial
        for record in resources:
            if record.total_qty > 0 and record.stadium_id and record.stadium_id.location_id:
                self.env['stock.quant'].with_context(inventory_mode=True).create({
                    'product_id': record.product_id.id,
                    'location_id': record.stadium_id.location_id.id,
                    'inventory_quantity': record.total_qty,
                }).action_apply_inventory()
                
        return resources

    def write(self, vals):
        res = super(LogisticsResource, self).write(vals)
        for record in self:
            product_vals = {}
            if 'name' in vals:
                product_vals['name'] = vals['name']
            if 'cost' in vals:
                product_vals['standard_price'] = vals['cost']
            
            if product_vals and record.product_id:
                record.product_id.write(product_vals)
        return res

    @api.model
    def _register_hook(self):
        # Sécurité : vérifier que la table existe bien en base de données avant de requêter.
        # Cela évite de crasher au démarrage d'Odoo lors de la première installation/mise à jour.
        cr = self.env.cr
        cr.execute("SELECT 1 FROM information_schema.tables WHERE table_name='wc_logistics_resource'")
        if cr.fetchone():
            # 1. Création automatique d'articles pour les ressources existantes sans article
            resources_without_product = self.search([('product_id', '=', False)])
            for record in resources_without_product:
                product_vals = {
                    'name': record.name,
                    'type': 'consu',
                    'is_storable': True,
                    'sale_ok': False,
                    'purchase_ok': True,
                }
                if record.cost:
                    product_vals['standard_price'] = record.cost
                product = self.env['product.product'].create(product_vals)
                record.write({'product_id': product.id})

            # 2. Initialiser le stock Odoo pour TOUTES les ressources qui ont 0 stock mais un total_qty > 0
            all_resources = self.search([('product_id', '!=', False)])
            for record in all_resources:
                if record.stadium_id and record.stadium_id.location_id and record.total_qty > 0:
                    quants = self.env['stock.quant'].search([
                        ('product_id', '=', record.product_id.id),
                        ('location_id', '=', record.stadium_id.location_id.id)
                    ])
                    current_qty = sum(quants.mapped('quantity'))
                    if current_qty == 0:
                        self.env['stock.quant'].with_context(inventory_mode=True).create({
                            'product_id': record.product_id.id,
                            'location_id': record.stadium_id.location_id.id,
                            'inventory_quantity': record.total_qty,
                        }).action_apply_inventory()

        return super(LogisticsResource, self)._register_hook()

    def action_replenish(self):
        self.ensure_one()
        if not self.stadium_id or not self.stadium_id.location_id:
            raise ValidationError("Le stade de stockage n'a pas d'emplacement de stock associé.")
        
        # Emplacement fournisseur par défaut
        supplier_loc = self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False)
        supplier_loc_id = supplier_loc.id if supplier_loc else False

        # Type de transfert : Réception
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming')
        ], limit=1)
        picking_type_id = picking_type.id if picking_type else False

        # Création du Bon de Réception
        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type_id,
            'location_id': supplier_loc_id,
            'location_dest_id': self.stadium_id.location_id.id,
            'origin': f"Réapprovisionnement : {self.name}",
        })

        # Création de la ligne de mouvement
        self.env['stock.move'].create({
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_qty': 100.0, # Quantité par défaut à réapprovisionner
            'product_uom': self.product_id.uom_id.id,
            'location_id': supplier_loc_id,
            'location_dest_id': self.stadium_id.location_id.id,
            'picking_id': picking.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Bon de Réception',
            'res_model': 'stock.picking',
            'res_id': picking.id,
            'view_mode': 'form',
            'target': 'current',
        }


class LogisticsRequestLine(models.Model):
    _name = 'wc.logistics.request.line'
    _description = 'Ligne de demande de ressource'

    request_id = fields.Many2one('wc.logistics.request', string='Demande',
                                  required=True, ondelete='cascade')
    resource_id = fields.Many2one('wc.logistics.resource', string='Ressource', required=True)
    quantity = fields.Integer(string='Quantité demandée', required=True, default=1)
    state = fields.Selection(related='request_id.state', string='État', store=True)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model_create_multi
    def create(self, vals_list):
        quants = super(StockQuant, self).create(vals_list)
        self._recompute_wc_resources(quants)
        return quants

    def write(self, vals):
        res = super(StockQuant, self).write(vals)
        self._recompute_wc_resources(self)
        return res

    def unlink(self):
        self._recompute_wc_resources(self)
        return super(StockQuant, self).unlink()

    def _recompute_wc_resources(self, quants):
        product_ids = quants.mapped('product_id').ids
        location_ids = quants.mapped('location_id').ids
        resources = self.env['wc.logistics.resource'].search([
            ('product_id', 'in', product_ids),
            ('stadium_id.location_id', 'in', location_ids)
        ])
        if resources:
            resources.modified(['available_qty', 'state'])
