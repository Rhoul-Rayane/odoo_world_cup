import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CrowdMonitoring(models.Model):
    _name = 'wc.crowd.monitoring'
    _description = 'Suivi de Densité de Foule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'last_updated desc'
    _rec_name = 'name'

    name = fields.Char(string='Nom', compute='_compute_name', store=True)

    match_id = fields.Many2one('wc.match', string='Match', required=True, ondelete='cascade')
    match_stadium_id = fields.Many2one('wc.stadium', related='match_id.stadium_id', readonly=True)

    stadium_zone_id = fields.Many2one(
        'wc.stadium.zone',
        string='Zone du stade',
        required=True,
        domain="[('stadium_id', '=', match_stadium_id)]"
    )

    current_headcount = fields.Integer(
        string='Affluence instantanée (pers)', required=True, default=0, tracking=True
    )
    zone_area = fields.Float(
        string='Superficie de la zone (m²)', required=True, default=1000.0
    )
    density_per_sqm = fields.Float(
        string='Densité (pers/m²)', compute='_compute_density', store=True, digits=(10, 2)
    )

    safety_status = fields.Selection([
        ('green', '🟢 Normal'),
        ('orange', '🟠 Attention'),
        ('red', '🔴 Critique'),
    ], string='Statut de sécurité', compute='_compute_safety_status', store=True, tracking=True)

    # Champs d'aide à la décision
    security_agents_deployed = fields.Integer(
        string='Agents de sécurité déployés', default=0
    )
    agent_ratio = fields.Float(
        string='Ratio agents/spectateurs',
        compute='_compute_agent_ratio', store=True,
        help='1 agent pour X spectateurs (objectif : 1 pour 50)',
        digits=(10, 1)
    )
    recommended_agents = fields.Integer(
        string='Agents recommandés',
        compute='_compute_recommended_agents', store=True
    )
    agent_deficit = fields.Integer(
        string='Déficit d\'agents',
        compute='_compute_agent_deficit', store=True
    )

    last_updated = fields.Datetime(
        string='Dernière mise à jour', default=fields.Datetime.now
    )
    last_alert_level = fields.Selection([
        ('none', 'Aucun'),
        ('orange', 'Orange émise'),
        ('red', 'Rouge émise'),
    ], string='Dernière alerte émise', default='none')

    @api.depends('match_id', 'stadium_zone_id')
    def _compute_name(self):
        for rec in self:
            match_name = rec.match_id.name or ''
            zone_name = rec.stadium_zone_id.name or ''
            rec.name = f"Foule — {match_name} ({zone_name})"

    @api.depends('current_headcount', 'zone_area')
    def _compute_density(self):
        for record in self:
            if record.zone_area > 0:
                record.density_per_sqm = record.current_headcount / record.zone_area
            else:
                record.density_per_sqm = 0.0

    @api.depends('density_per_sqm')
    def _compute_safety_status(self):
        for record in self:
            if record.density_per_sqm >= 4.0:
                record.safety_status = 'red'
            elif record.density_per_sqm >= 2.0:
                record.safety_status = 'orange'
            else:
                record.safety_status = 'green'

    @api.depends('security_agents_deployed', 'current_headcount')
    def _compute_agent_ratio(self):
        for record in self:
            if record.security_agents_deployed > 0:
                record.agent_ratio = record.current_headcount / record.security_agents_deployed
            else:
                record.agent_ratio = 0.0

    @api.depends('current_headcount')
    def _compute_recommended_agents(self):
        """1 agent pour 50 spectateurs."""
        for record in self:
            record.recommended_agents = max(1, (record.current_headcount + 49) // 50)

    @api.depends('recommended_agents', 'security_agents_deployed')
    def _compute_agent_deficit(self):
        for record in self:
            record.agent_deficit = max(0, record.recommended_agents - record.security_agents_deployed)

    @api.constrains('current_headcount', 'zone_area')
    def _check_crowd_values(self):
        for record in self:
            if record.current_headcount < 0:
                raise ValidationError("L'affluence de foule ne peut pas être négative.")
            if record.zone_area <= 0:
                raise ValidationError("La superficie de la zone doit être strictement supérieure à zéro.")

    def write(self, vals):
        """Override write pour déclencher les alertes automatiques."""
        result = super().write(vals)
        if 'current_headcount' in vals:
            for record in self:
                record._check_security_alerts()
        return result

    def _check_security_alerts(self):
        """Vérifie les seuils et génère les alertes/incidents automatiquement."""
        self.ensure_one()

        # === SEUIL ORANGE (Densité >= 2.0 pers/m²) ===
        if self.density_per_sqm >= 2.0 and self.last_alert_level == 'none':
            # Vérifier le ratio agents/spectateurs
            deficit_msg = ''
            if self.agent_deficit > 0:
                deficit_msg = (
                    f"\n⚠️ INSUFFISANCE D'AGENTS : {self.security_agents_deployed} déployés, "
                    f"{self.recommended_agents} recommandés (déficit de {self.agent_deficit}).\n"
                    f"→ Recommandation : déployer {self.agent_deficit} steward(s) supplémentaire(s) "
                    f"vers la zone {self.stadium_zone_id.name}."
                )

            alert_msg = (
                f"🟠 ALERTE ATTENTION — Densité de foule élevée\n"
                f"Zone : {self.stadium_zone_id.name}\n"
                f"Match : {self.match_id.name}\n"
                f"Affluence : {self.current_headcount} personnes\n"
                f"Densité : {self.density_per_sqm:.2f} pers/m²\n"
                f"Superficie : {self.zone_area} m²"
                f"{deficit_msg}"
            )
            self.message_post(
                body=alert_msg,
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )
            self.sudo().write({'last_alert_level': 'orange'})
            _logger.warning(
                "ALERTE ORANGE : %s — Densité %.2f pers/m²",
                self.name, self.density_per_sqm
            )

        # === SEUIL ROUGE (Densité >= 4.0 pers/m²) ===
        if self.density_per_sqm >= 4.0 and self.last_alert_level != 'red':
            # Créer automatiquement un incident critique
            incident_vals = {
                'name': f"🔴 SURPOPULATION CRITIQUE — {self.stadium_zone_id.name}",
                'description': (
                    f"Incident automatique généré par le système de monitoring.\n\n"
                    f"Zone : {self.stadium_zone_id.name}\n"
                    f"Match : {self.match_id.name}\n"
                    f"Affluence instantanée : {self.current_headcount} personnes\n"
                    f"Densité : {self.density_per_sqm:.2f} pers/m² (seuil critique : 4.0)\n"
                    f"Superficie : {self.zone_area} m²\n\n"
                    f"🚨 ACTION REQUISE : Rediriger immédiatement les spectateurs "
                    f"vers les portes adjacentes moins denses.\n"
                    f"Déployer des renforts de stewards en urgence."
                ),
                'stadium_id': self.match_id.stadium_id.id,
                'zone_id': self.stadium_zone_id.id,
                'match_id': self.match_id.id,
                'incident_type': 'crowd',
                'severity': '4',
                'state': 'reported',
            }
            self.env['wc.logistics.incident'].sudo().create(incident_vals)

            critical_msg = (
                f"🔴 ALERTE CRITIQUE — Surpopulation détectée !\n"
                f"Zone : {self.stadium_zone_id.name}\n"
                f"Densité actuelle : {self.density_per_sqm:.2f} pers/m² (CRITIQUE ≥ 4.0)\n"
                f"Un incident a été automatiquement créé.\n"
                f"🚨 Redirection des spectateurs REQUISE immédiatement."
            )
            self.message_post(
                body=critical_msg,
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )
            self.sudo().write({'last_alert_level': 'red'})
            _logger.critical(
                "ALERTE ROUGE : %s — Densité %.2f pers/m² — Incident créé",
                self.name, self.density_per_sqm
            )

        # === RETOUR À LA NORMALE ===
        if self.density_per_sqm < 2.0 and self.last_alert_level != 'none':
            self.message_post(
                body=(
                    f"🟢 RETOUR À LA NORMALE\n"
                    f"Zone : {self.stadium_zone_id.name}\n"
                    f"Densité actuelle : {self.density_per_sqm:.2f} pers/m²\n"
                    f"Situation stabilisée."
                ),
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )
            self.sudo().write({'last_alert_level': 'none'})
            _logger.info(
                "RETOUR NORMAL : %s — Densité %.2f pers/m²",
                self.name, self.density_per_sqm
            )
