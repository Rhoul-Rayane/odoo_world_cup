import hashlib
import uuid
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Ticket(models.Model):
    _name = 'wc.ticket'
    _description = 'Billet de Match'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(
        string='N° Billet', required=True, copy=False, readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('wc.ticket') or 'TKT-NEW'
    )
    match_id = fields.Many2one('wc.match', string='Match', required=True, ondelete='cascade')
    stadium_id = fields.Many2one(
        'wc.stadium', string='Stade',
        related='match_id.stadium_id', store=True, readonly=True
    )
    stadium_zone_id = fields.Many2one(
        'wc.stadium.zone', string='Zone / Tribune', required=True,
        domain="[('stadium_id', '=', stadium_id)]"
    )
    barcode = fields.Char(
        string='Code-barres / QR', required=True, copy=False, index=True,
        default=lambda self: self._generate_barcode()
    )
    holder_name = fields.Char(string='Nom du porteur')
    category = fields.Selection([
        ('standard', 'Standard'),
        ('vip', 'VIP'),
        ('press', 'Presse'),
        ('hospitality', 'Hospitalité'),
    ], string='Catégorie', default='standard', required=True)
    state = fields.Selection([
        ('purchased', 'Acheté'),
        ('scanned', 'Scanné ✅'),
        ('cancelled', 'Annulé'),
    ], string='Statut', default='purchased', tracking=True)
    scan_datetime = fields.Datetime(string='Date/Heure du scannage', readonly=True)
    scanned_by_id = fields.Many2one('res.users', string='Scanné par', readonly=True)

    _sql_constraints = [
        ('barcode_uniq', 'unique(barcode)', 'Le code-barres de chaque billet doit être unique !'),
    ]

    @staticmethod
    def _generate_barcode():
        """Génère un code-barres unique basé sur UUID."""
        raw = uuid.uuid4().hex
        return hashlib.sha256(raw.encode()).hexdigest()[:16].upper()

    def action_scan(self):
        """Marque le billet comme scanné et met à jour le suivi de foule."""
        self.ensure_one()
        if self.state == 'scanned':
            raise ValidationError("Ce billet a déjà été scanné !")
        if self.state == 'cancelled':
            raise ValidationError("Ce billet a été annulé !")

        self.write({
            'state': 'scanned',
            'scan_datetime': fields.Datetime.now(),
            'scanned_by_id': self.env.user.id,
        })

        # Incrémenter le compteur de foule dans wc.crowd.monitoring
        crowd_record = self.env['wc.crowd.monitoring'].search([
            ('match_id', '=', self.match_id.id),
            ('stadium_zone_id', '=', self.stadium_zone_id.id),
        ], limit=1)
        if crowd_record:
            crowd_record.sudo().write({
                'current_headcount': crowd_record.current_headcount + 1,
                'last_updated': fields.Datetime.now(),
            })

        return True

    def action_cancel(self):
        """Annule un billet."""
        for ticket in self:
            if ticket.state == 'scanned':
                raise ValidationError("Impossible d'annuler un billet déjà scanné.")
            ticket.state = 'cancelled'
