from odoo import models, fields, api


class WcDashboard(models.Model):
    _name = 'wc.dashboard'
    _description = 'Tableau de Bord - Coupe du Monde 2030'

    name = fields.Char(string='Période', default='Dashboard WC 2030', required=True)
    date_refresh = fields.Datetime(string='Dernière actualisation', readonly=True)

    # ============ KPI VOLONTAIRES ============
    vol_total = fields.Integer(string='Total volontaires', compute='_compute_volunteer_kpis')
    vol_candidates = fields.Integer(string='Candidats', compute='_compute_volunteer_kpis')
    vol_preselected = fields.Integer(string='Présélectionnés', compute='_compute_volunteer_kpis')
    vol_trained = fields.Integer(string='Formés', compute='_compute_volunteer_kpis')
    vol_assigned = fields.Integer(string='Affectés', compute='_compute_volunteer_kpis')
    vol_active = fields.Integer(string='Actifs', compute='_compute_volunteer_kpis')
    vol_avg_score = fields.Float(string='Score moyen', compute='_compute_volunteer_kpis', digits=(5, 1))

    # ============ KPI STADES ============
    stadium_total = fields.Integer(string='Total stades', compute='_compute_stadium_kpis')
    stadium_ready = fields.Integer(string='Stades prêts', compute='_compute_stadium_kpis')
    stadium_total_capacity = fields.Integer(string='Capacité totale', compute='_compute_stadium_kpis')

    # ============ KPI MATCHS ============
    match_total = fields.Integer(string='Total matchs', compute='_compute_match_kpis')
    match_planned = fields.Integer(string='Matchs planifiés', compute='_compute_match_kpis')
    match_done = fields.Integer(string='Matchs terminés', compute='_compute_match_kpis')

    # ============ KPI ACCRÉDITATIONS ============
    badge_total = fields.Integer(string='Total badges', compute='_compute_badge_kpis')
    badge_active = fields.Integer(string='Badges actifs', compute='_compute_badge_kpis')
    badge_expired = fields.Integer(string='Badges expirés', compute='_compute_badge_kpis')
    badge_revoked = fields.Integer(string='Badges révoqués', compute='_compute_badge_kpis')
    badge_total_scans = fields.Integer(string='Total scans', compute='_compute_badge_kpis')

    # ============ KPI LOGISTIQUE ============
    incident_total = fields.Integer(string='Total incidents', compute='_compute_logistics_kpis')
    incident_open = fields.Integer(string='Incidents ouverts', compute='_compute_logistics_kpis')
    incident_critical = fields.Integer(string='Incidents critiques', compute='_compute_logistics_kpis')
    resource_out_of_stock = fields.Integer(string='Ressources en rupture', compute='_compute_logistics_kpis')
    transport_planned = fields.Integer(string='Navettes planifiées', compute='_compute_logistics_kpis')
    request_pending = fields.Integer(string='Demandes en attente', compute='_compute_logistics_kpis')

    # ============ COMPUTE METHODS ============
    def _compute_volunteer_kpis(self):
        Volunteer = self.env['wc.volunteer']
        for rec in self:
            all_vols = Volunteer.search([])
            rec.vol_total = len(all_vols)
            rec.vol_candidates = Volunteer.search_count([('state', '=', 'candidate')])
            rec.vol_preselected = Volunteer.search_count([('state', '=', 'preselected')])
            rec.vol_trained = Volunteer.search_count([('state', '=', 'trained')])
            rec.vol_assigned = Volunteer.search_count([('state', '=', 'assigned')])
            rec.vol_active = Volunteer.search_count([('state', '=', 'active')])
            scores = all_vols.mapped('matching_score')
            rec.vol_avg_score = sum(scores) / len(scores) if scores else 0

    def _compute_stadium_kpis(self):
        Stadium = self.env['wc.stadium']
        for rec in self:
            all_stadiums = Stadium.search([])
            rec.stadium_total = len(all_stadiums)
            rec.stadium_ready = Stadium.search_count([('state', '=', 'ready')])
            rec.stadium_total_capacity = sum(all_stadiums.mapped('capacity'))

    def _compute_match_kpis(self):
        Match = self.env['wc.match']
        for rec in self:
            rec.match_total = Match.search_count([])
            rec.match_planned = Match.search_count([('state', '=', 'planned')])
            rec.match_done = Match.search_count([('state', '=', 'done')])

    def _compute_badge_kpis(self):
        Badge = self.env['wc.accreditation']
        for rec in self:
            all_badges = Badge.search([])
            rec.badge_total = len(all_badges)
            rec.badge_active = Badge.search_count([('state', '=', 'active')])
            rec.badge_expired = Badge.search_count([('is_expired', '=', True)])
            rec.badge_revoked = Badge.search_count([('state', '=', 'revoked')])
            rec.badge_total_scans = sum(all_badges.mapped('scan_count'))

    def _compute_logistics_kpis(self):
        Incident = self.env['wc.logistics.incident']
        Resource = self.env['wc.logistics.resource']
        Transport = self.env['wc.logistics.transport']
        Request = self.env['wc.logistics.request']
        for rec in self:
            rec.incident_total = Incident.search_count([])
            rec.incident_open = Incident.search_count([('state', 'in', ('reported', 'in_progress'))])
            rec.incident_critical = Incident.search_count([('severity', '=', '4'), ('state', '!=', 'closed')])
            rec.resource_out_of_stock = Resource.search_count([('state', '=', 'out')])
            rec.transport_planned = Transport.search_count([('state', '=', 'planned')])
            rec.request_pending = Request.search_count([('state', 'in', ('draft', 'submitted'))])

    def action_refresh(self):
        """Force le recalcul de tous les KPIs."""
        self.write({'date_refresh': fields.Datetime.now()})
        return True


class VolunteerByState(models.Model):
    """Vue SQL pour les graphiques de répartition des volontaires."""
    _name = 'wc.dashboard.volunteer.state'
    _description = 'Répartition volontaires par statut'
    _auto = False
    _order = 'state'

    state = fields.Selection([
        ('candidate', 'Candidat'),
        ('preselected', 'Présélectionné'),
        ('trained', 'Formé'),
        ('assigned', 'Affecté'),
        ('active', 'Actif'),
        ('archived', 'Archivé'),
    ], string='Statut', readonly=True)
    count = fields.Integer(string='Nombre', readonly=True)
    avg_score = fields.Float(string='Score moyen', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW wc_dashboard_volunteer_state AS (
                SELECT
                    ROW_NUMBER() OVER () AS id,
                    state,
                    COUNT(*) AS count,
                    COALESCE(AVG(matching_score), 0) AS avg_score
                FROM wc_volunteer
                GROUP BY state
            )
        """)


class AccreditationByCategory(models.Model):
    """Vue SQL pour les graphiques de répartition des badges."""
    _name = 'wc.dashboard.badge.category'
    _description = 'Répartition badges par catégorie'
    _auto = False
    _order = 'category'

    category = fields.Selection([
        ('fifa', 'FIFA Official'),
        ('team', 'Équipe / Staff'),
        ('media', 'Média / Presse'),
        ('volunteer', 'Volontaire'),
        ('vip', 'VIP / Sponsor'),
        ('logistics', 'Logistique / Sécurité'),
        ('medical', 'Médical'),
    ], string='Catégorie', readonly=True)
    count = fields.Integer(string='Nombre', readonly=True)
    active_count = fields.Integer(string='Actifs', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW wc_dashboard_badge_category AS (
                SELECT
                    ROW_NUMBER() OVER () AS id,
                    category,
                    COUNT(*) AS count,
                    SUM(CASE WHEN state = 'active' THEN 1 ELSE 0 END) AS active_count
                FROM wc_accreditation
                GROUP BY category
            )
        """)


class IncidentBySeverity(models.Model):
    """Vue SQL pour les graphiques d'incidents."""
    _name = 'wc.dashboard.incident.severity'
    _description = 'Répartition incidents par sévérité'
    _auto = False
    _order = 'severity'

    severity = fields.Selection([
        ('1', 'Faible'),
        ('2', 'Moyen'),
        ('3', 'Élevé'),
        ('4', 'Critique'),
    ], string='Sévérité', readonly=True)
    count = fields.Integer(string='Nombre', readonly=True)
    open_count = fields.Integer(string='Ouverts', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW wc_dashboard_incident_severity AS (
                SELECT
                    ROW_NUMBER() OVER () AS id,
                    severity,
                    COUNT(*) AS count,
                    SUM(CASE WHEN state IN ('reported', 'in_progress') THEN 1 ELSE 0 END) AS open_count
                FROM wc_logistics_incident
                GROUP BY severity
            )
        """)
