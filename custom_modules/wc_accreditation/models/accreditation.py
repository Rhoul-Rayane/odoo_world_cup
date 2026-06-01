import base64
import io
import hashlib
import json
from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


class Accreditation(models.Model):
    _name = 'wc.accreditation'
    _description = 'Badge & Accréditation - Coupe du Monde 2030'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # ============ IDENTITÉ ============
    name = fields.Char(string='Référence Badge', compute='_compute_name', store=True)
    holder_name = fields.Char(string='Nom du titulaire', required=True, tracking=True)
    holder_email = fields.Char(string='Email')
    holder_phone = fields.Char(string='Téléphone')
    holder_photo = fields.Binary(string='Photo', attachment=True)
    organization = fields.Char(string='Organisation')
    function = fields.Char(string='Fonction / Rôle')

    # Lien optionnel avec un volontaire
    volunteer_id = fields.Many2one('wc.volunteer', string='Volontaire lié',
                                   help='Si le titulaire est un volontaire enregistré')

    # ============ CATÉGORIE & ACCÈS ============
    category = fields.Selection([
        ('fifa', 'FIFA Official'),
        ('team', 'Équipe / Staff technique'),
        ('media', 'Média / Presse'),
        ('volunteer', 'Volontaire'),
        ('vip', 'VIP / Sponsor'),
        ('logistics', 'Logistique / Sécurité'),
        ('medical', 'Médical'),
    ], string='Catégorie', required=True, tracking=True)

    badge_color = fields.Char(string='Couleur du badge', compute='_compute_badge_color', store=True)

    zone_ids = fields.Many2many('wc.stadium.zone', string='Zones autorisées', required=True)
    match_ids = fields.Many2many('wc.match', string='Matchs autorisés')
    stadium_ids = fields.Many2many('wc.stadium', string='Stades autorisés')

    # ============ VALIDITÉ ============
    date_start = fields.Date(string='Date de début', required=True,
                             default=fields.Date.today)
    date_end = fields.Date(string='Date de fin', required=True)
    is_expired = fields.Boolean(string='Expiré', compute='_compute_is_expired', store=True)

    # ============ QR CODE ============
    qr_code = fields.Binary(string='QR Code', compute='_compute_qr_code', store=True)
    qr_token = fields.Char(string='Token unique', readonly=True, copy=False)

    # ============ WORKFLOW ============
    state = fields.Selection([
        ('draft', 'Demandé'),
        ('approved', 'Approuvé'),
        ('printed', 'Imprimé'),
        ('active', 'Activé'),
        ('suspended', 'Suspendu'),
        ('revoked', 'Révoqué'),
    ], string='Statut', default='draft', tracking=True, group_expand='_expand_states')

    # ============ TRAÇABILITÉ ============
    approved_by = fields.Many2one('res.users', string='Approuvé par', readonly=True)
    approved_date = fields.Datetime(string='Date d\'approbation', readonly=True)
    scan_count = fields.Integer(string='Nombre de scans', default=0, readonly=True)
    last_scan_date = fields.Datetime(string='Dernier scan', readonly=True)
    notes = fields.Text(string='Notes internes')
    active = fields.Boolean(default=True)

    # ============ CONTRAINTES ============
    _qr_token_unique = models.Constraint(
        'unique(qr_token)',
        'Le token QR doit être unique.',
    )

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end and record.date_start > record.date_end:
                raise ValidationError("La date de fin doit être postérieure à la date de début.")

    # ============ CHAMPS CALCULÉS ============
    @api.depends('holder_name', 'category', 'qr_token')
    def _compute_name(self):
        for record in self:
            cat_short = (record.category or 'X')[:3].upper()
            token_short = (record.qr_token or 'XXXX')[-4:]
            record.name = f"WC2030-{cat_short}-{token_short}"

    @api.depends('category')
    def _compute_badge_color(self):
        color_map = {
            'fifa': '#DC2626',       # Rouge
            'team': '#2563EB',       # Bleu
            'media': '#16A34A',      # Vert
            'volunteer': '#EAB308',  # Jaune
            'vip': '#9333EA',        # Violet
            'logistics': '#1F2937',  # Noir/Gris foncé
            'medical': '#FFFFFF',    # Blanc
        }
        for record in self:
            record.badge_color = color_map.get(record.category, '#6B7280')

    @api.depends('date_end')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for record in self:
            record.is_expired = record.date_end and record.date_end < today

    # ============ GÉNÉRATION QR CODE ============
    def _generate_token(self):
        """Génère un token unique basé sur les données du badge."""
        data = f"{self.id}-{self.holder_name}-{self.category}-{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16].upper()

    @api.depends('qr_token')
    def _compute_qr_code(self):
        for record in self:
            if not record.qr_token or not HAS_QRCODE:
                record.qr_code = False
                continue

            # Données encodées dans le QR code
            qr_data = json.dumps({
                'token': record.qr_token,
                'name': record.holder_name,
                'category': record.category,
                'badge_ref': record.name,
            })

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            record.qr_code = base64.b64encode(buffer.getvalue())

    # ============ ACTIONS WORKFLOW ============
    def action_approve(self):
        for record in self:
            if not record.qr_token:
                record.qr_token = record._generate_token()
            record.write({
                'state': 'approved',
                'approved_by': self.env.uid,
                'approved_date': fields.Datetime.now(),
            })

    def action_print(self):
        self.write({'state': 'printed'})

    def action_activate(self):
        for record in self:
            if record.is_expired:
                raise ValidationError("Impossible d'activer un badge expiré.")
            record.write({'state': 'active'})

    def action_suspend(self):
        self.write({'state': 'suspended'})

    def action_revoke(self):
        self.write({'state': 'revoked'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    def action_view_scans(self):
        """Stat button action — opens the current record's form (scan info section)."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Détails Scans',
            'res_model': 'wc.accreditation',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    # ============ VÉRIFICATION SCAN ============
    def action_scan(self):
        """Simule un scan de badge — incrémente le compteur."""
        for record in self:
            if record.state != 'active':
                raise ValidationError(f"Badge {record.name} non actif (statut: {record.state}).")
            if record.is_expired:
                raise ValidationError(f"Badge {record.name} expiré depuis le {record.date_end}.")
            record.write({
                'scan_count': record.scan_count + 1,
                'last_scan_date': fields.Datetime.now(),
            })
            record.message_post(body=f"✅ Scan validé — Total scans : {record.scan_count}")

    @api.model
    def verify_token(self, token):
        """API : Vérifie un token QR et retourne les infos du badge."""
        badge = self.search([('qr_token', '=', token)], limit=1)
        if not badge:
            return {'valid': False, 'error': 'Token inconnu'}
        if badge.state != 'active':
            return {'valid': False, 'error': f'Badge non actif ({badge.state})'}
        if badge.is_expired:
            return {'valid': False, 'error': 'Badge expiré'}

        return {
            'valid': True,
            'holder': badge.holder_name,
            'category': badge.category,
            'badge_ref': badge.name,
            'zones': [z.name for z in badge.zone_ids],
            'organization': badge.organization or '',
        }

    # ============ GROUP EXPAND (Kanban) ============
    @api.model
    def _expand_states(self, states, domain):
        return [key for key, val in type(self).state.selection]
