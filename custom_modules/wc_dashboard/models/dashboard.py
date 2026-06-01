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

    # ============ KPI TRANSPORT ============
    transport_line_total = fields.Integer(string='Lignes de transport', compute='_compute_transport_kpis')
    transport_station_total = fields.Integer(string='Stations', compute='_compute_transport_kpis')
    parking_total = fields.Integer(string='Zones de parking', compute='_compute_transport_kpis')
    parking_avg_occupancy = fields.Float(string='Occupation moyenne parkings (%)', compute='_compute_transport_kpis', digits=(5, 1))
    parking_full = fields.Integer(string='Parkings pleins (>90%)', compute='_compute_transport_kpis')
    schedule_total = fields.Integer(string='Trajets programmés', compute='_compute_transport_kpis')

    # ============ KPI SÉCURITÉ ============
    security_deployment_total = fields.Integer(string='Déploiements sécurité', compute='_compute_security_kpis')
    security_agents_total = fields.Integer(string='Agents déployés', compute='_compute_security_kpis')
    security_agreement_total = fields.Integer(string='Accords internationaux', compute='_compute_security_kpis')
    crowd_monitoring_total = fields.Integer(string='Points monitoring', compute='_compute_security_kpis')
    crowd_alert_red = fields.Integer(string='Alertes rouges', compute='_compute_security_kpis')
    crowd_alert_orange = fields.Integer(string='Alertes orange', compute='_compute_security_kpis')

    # ============ KPI DURABILITÉ ============
    waste_total_kg = fields.Float(string='Déchets totaux (kg)', compute='_compute_sustainability_kpis', digits=(12, 1))
    waste_diversion_avg = fields.Float(string='Taux détournement moyen (%)', compute='_compute_sustainability_kpis', digits=(5, 1))
    carbon_total_emission = fields.Float(string='Émissions CO₂ (tonnes)', compute='_compute_sustainability_kpis', digits=(12, 2))
    carbon_total_offset = fields.Float(string='Compensations CO₂ (tonnes)', compute='_compute_sustainability_kpis', digits=(12, 2))
    carbon_net = fields.Float(string='Émissions nettes CO₂', compute='_compute_sustainability_kpis', digits=(12, 2))
    audit_total = fields.Integer(string='Audits ISO 20121', compute='_compute_sustainability_kpis')
    audit_compliant = fields.Integer(string='Audits conformes', compute='_compute_sustainability_kpis')
    audit_non_conformity = fields.Integer(string='Non-conformités', compute='_compute_sustainability_kpis')

    # ============ KPI FINANCE ============
    budget_total_planned = fields.Float(string='Budget prévu (MAD)', compute='_compute_finance_kpis', digits=(14, 2))
    budget_total_spent = fields.Float(string='Budget dépensé (MAD)', compute='_compute_finance_kpis', digits=(14, 2))
    budget_consumption_avg = fields.Float(string='Consommation budget (%)', compute='_compute_finance_kpis', digits=(5, 1))
    revenue_total_projected = fields.Float(string='Revenus projetés (MAD)', compute='_compute_finance_kpis', digits=(14, 2))
    revenue_total_actual = fields.Float(string='Revenus réalisés (MAD)', compute='_compute_finance_kpis', digits=(14, 2))
    revenue_variance_pct = fields.Float(string='Variance revenus (%)', compute='_compute_finance_kpis', digits=(5, 1))
    ticket_total_available = fields.Integer(string='Billets disponibles', compute='_compute_finance_kpis')
    ticket_total_sold = fields.Integer(string='Billets vendus', compute='_compute_finance_kpis')
    ticket_fill_rate = fields.Float(string='Taux remplissage (%)', compute='_compute_finance_kpis', digits=(5, 1))

    # ============ BENCHMARKS QATAR 2022 ============
    # Chiffres réels de Qatar 2022 (source : FIFA, Supreme Committee)
    qatar_volunteers = fields.Integer(string='Qatar 2022 : Volontaires', default=20000, readonly=True)
    qatar_stadiums = fields.Integer(string='Qatar 2022 : Stades', default=8, readonly=True)
    qatar_capacity = fields.Integer(string='Qatar 2022 : Capacité totale', default=437000, readonly=True)
    qatar_matches = fields.Integer(string='Qatar 2022 : Matchs', default=64, readonly=True)
    qatar_attendance = fields.Integer(string='Qatar 2022 : Spectateurs', default=3404252, readonly=True)
    qatar_carbon_tons = fields.Float(string='Qatar 2022 : CO₂ (tonnes)', default=3630000, readonly=True)
    qatar_waste_diverted_pct = fields.Float(string='Qatar 2022 : Taux recyclage (%)', default=79.0, readonly=True)
    qatar_budget_usd_bn = fields.Float(string='Qatar 2022 : Budget (Mrd $)', default=220.0, readonly=True)

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

    def _compute_transport_kpis(self):
        Line = self.env['wc.transport.line']
        Station = self.env['wc.transport.station']
        Parking = self.env['wc.parking.zone']
        Schedule = self.env['wc.transport.schedule']
        for rec in self:
            rec.transport_line_total = Line.search_count([])
            rec.transport_station_total = Station.search_count([])
            all_parkings = Parking.search([])
            rec.parking_total = len(all_parkings)
            occupancies = all_parkings.mapped('occupancy_rate')
            rec.parking_avg_occupancy = sum(occupancies) / len(occupancies) if occupancies else 0
            rec.parking_full = Parking.search_count([('occupancy_rate', '>', 90)])
            rec.schedule_total = Schedule.search_count([])

    def _compute_security_kpis(self):
        Deployment = self.env['wc.security.deployment']
        Agreement = self.env['wc.security.agreement']
        Crowd = self.env['wc.crowd.monitoring']
        for rec in self:
            all_deployments = Deployment.search([])
            rec.security_deployment_total = len(all_deployments)
            rec.security_agents_total = sum(all_deployments.mapped('agent_count'))
            rec.security_agreement_total = Agreement.search_count([])
            rec.crowd_monitoring_total = Crowd.search_count([])
            rec.crowd_alert_red = Crowd.search_count([('safety_status', '=', 'danger')])
            rec.crowd_alert_orange = Crowd.search_count([('safety_status', '=', 'warning')])

    def _compute_sustainability_kpis(self):
        Waste = self.env['wc.waste.tracking']
        Carbon = self.env['wc.carbon.footprint']
        Audit = self.env['wc.sustainability.audit']
        for rec in self:
            all_waste = Waste.search([])
            rec.waste_total_kg = sum(all_waste.mapped('quantity_kg'))
            diversions = all_waste.mapped('diversion_rate')
            rec.waste_diversion_avg = sum(diversions) / len(diversions) if diversions else 0
            all_carbon = Carbon.search([])
            rec.carbon_total_emission = sum(all_carbon.mapped('emission_tons_co2'))
            rec.carbon_total_offset = sum(all_carbon.mapped('offset_tons_co2'))
            rec.carbon_net = sum(all_carbon.mapped('net_emission'))
            rec.audit_total = Audit.search_count([])
            rec.audit_compliant = Audit.search_count([('compliance_level', '=', 'full')])
            rec.audit_non_conformity = Audit.search_count([('state', '=', 'non_conformity')])

    def _compute_finance_kpis(self):
        Budget = self.env['wc.budget.line']
        Revenue = self.env['wc.revenue.stream']
        Pricing = self.env['wc.ticket.pricing']
        for rec in self:
            all_budgets = Budget.search([])
            rec.budget_total_planned = sum(all_budgets.mapped('planned_amount'))
            rec.budget_total_spent = sum(all_budgets.mapped('spent_amount'))
            consumptions = all_budgets.mapped('consumption_rate')
            rec.budget_consumption_avg = sum(consumptions) / len(consumptions) if consumptions else 0
            all_revenues = Revenue.search([])
            rec.revenue_total_projected = sum(all_revenues.mapped('projected_amount'))
            rec.revenue_total_actual = sum(all_revenues.mapped('actual_amount'))
            total_proj = rec.revenue_total_projected
            rec.revenue_variance_pct = ((rec.revenue_total_actual - total_proj) / total_proj * 100) if total_proj else 0
            all_pricing = Pricing.search([])
            rec.ticket_total_available = sum(all_pricing.mapped('total_available'))
            rec.ticket_total_sold = sum(all_pricing.mapped('total_sold'))
            rec.ticket_fill_rate = (rec.ticket_total_sold / rec.ticket_total_available * 100) if rec.ticket_total_available else 0

    def action_refresh(self):
        """Force le recalcul de tous les KPIs."""
        self.write({'date_refresh': fields.Datetime.now()})
        return True

    # ============ ACTIONS DE RACCOURCI ============
    def action_open_critical_incidents(self):
        """Ouvre la liste des incidents critiques ouverts."""
        return {
            'type': 'ir.actions.act_window',
            'name': '🚨 Incidents Critiques',
            'res_model': 'wc.logistics.incident',
            'view_mode': 'list,form',
            'domain': [('severity', '=', '4'), ('state', '!=', 'closed')],
            'context': {'default_severity': '4'},
        }

    def action_open_out_of_stock(self):
        """Ouvre la liste des ressources en rupture de stock."""
        return {
            'type': 'ir.actions.act_window',
            'name': '⚠️ Ressources en rupture',
            'res_model': 'wc.logistics.resource',
            'view_mode': 'list,form',
            'domain': [('state', '=', 'out')],
        }

    def action_open_crowd_alerts(self):
        """Ouvre les alertes foule (rouge + orange)."""
        return {
            'type': 'ir.actions.act_window',
            'name': '🔴 Alertes Foule',
            'res_model': 'wc.crowd.monitoring',
            'view_mode': 'list,form',
            'domain': [('safety_status', 'in', ['danger', 'warning'])],
        }

    def action_open_parking_full(self):
        """Ouvre les parkings avec occupation > 90%."""
        return {
            'type': 'ir.actions.act_window',
            'name': '🅿️ Parkings Pleins',
            'res_model': 'wc.parking.zone',
            'view_mode': 'list,form',
            'domain': [('occupancy_rate', '>', 90)],
        }

    def action_open_non_conformity(self):
        """Ouvre les audits en non-conformité."""
        return {
            'type': 'ir.actions.act_window',
            'name': '❌ Non-Conformités ISO',
            'res_model': 'wc.sustainability.audit',
            'view_mode': 'list,form',
            'domain': [('state', '=', 'non_conformity')],
        }

    def action_open_budget_overspent(self):
        """Ouvre les budgets en surconsommation (>80%)."""
        return {
            'type': 'ir.actions.act_window',
            'name': '💸 Budgets en alerte',
            'res_model': 'wc.budget.line',
            'view_mode': 'list,form',
            'domain': [('consumption_rate', '>', 80)],
        }

    def action_open_pending_requests(self):
        """Ouvre les demandes logistiques en attente."""
        return {
            'type': 'ir.actions.act_window',
            'name': '📋 Demandes en attente',
            'res_model': 'wc.logistics.request',
            'view_mode': 'list,form',
            'domain': [('state', 'in', ('draft', 'submitted'))],
        }


# ============ SQL VIEWS FOR CHARTS ============

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


class BudgetByCategory(models.Model):
    """Vue SQL : répartition du budget par catégorie."""
    _name = 'wc.dashboard.budget.category'
    _description = 'Répartition budget par catégorie'
    _auto = False
    _order = 'category'

    category = fields.Selection([
        ('infrastructure', 'Infrastructure'),
        ('technology', 'Technologie'),
        ('security', 'Sécurité'),
        ('logistics', 'Logistique'),
        ('hospitality', 'Hospitalité'),
        ('sustainability', 'Durabilité'),
        ('communication', 'Communication'),
        ('other', 'Autre'),
    ], string='Catégorie', readonly=True)
    total_planned = fields.Float(string='Prévu (MAD)', readonly=True)
    total_spent = fields.Float(string='Dépensé (MAD)', readonly=True)
    avg_consumption = fields.Float(string='Consommation (%)', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW wc_dashboard_budget_category AS (
                SELECT
                    ROW_NUMBER() OVER () AS id,
                    category,
                    COALESCE(SUM(planned_amount), 0) AS total_planned,
                    COALESCE(SUM(spent_amount), 0) AS total_spent,
                    CASE WHEN SUM(planned_amount) > 0
                         THEN SUM(spent_amount) / SUM(planned_amount) * 100
                         ELSE 0 END AS avg_consumption
                FROM wc_budget_line
                GROUP BY category
            )
        """)


class WasteByType(models.Model):
    """Vue SQL : déchets par type."""
    _name = 'wc.dashboard.waste.type'
    _description = 'Répartition déchets par type'
    _auto = False
    _order = 'waste_type'

    waste_type = fields.Selection([
        ('organic', 'Organique'),
        ('plastic', 'Plastique'),
        ('paper', 'Papier/Carton'),
        ('glass', 'Verre'),
        ('metal', 'Métal'),
        ('electronic', 'Électronique'),
        ('mixed', 'Mélangé'),
    ], string='Type', readonly=True)
    total_kg = fields.Float(string='Total (kg)', readonly=True)
    recycled_kg = fields.Float(string='Recyclé (kg)', readonly=True)
    avg_diversion = fields.Float(string='Détournement (%)', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW wc_dashboard_waste_type AS (
                SELECT
                    ROW_NUMBER() OVER () AS id,
                    waste_type,
                    COALESCE(SUM(quantity_kg), 0) AS total_kg,
                    COALESCE(SUM(recycled_kg), 0) AS recycled_kg,
                    CASE WHEN SUM(quantity_kg) > 0
                         THEN (SUM(recycled_kg) + SUM(diverted_kg)) / SUM(quantity_kg) * 100
                         ELSE 0 END AS avg_diversion
                FROM wc_waste_tracking
                GROUP BY waste_type
            )
        """)


class CarbonByCategory(models.Model):
    """Vue SQL : émissions carbone par catégorie."""
    _name = 'wc.dashboard.carbon.category'
    _description = 'Émissions carbone par catégorie'
    _auto = False
    _order = 'category'

    category = fields.Selection([
        ('energy', 'Énergie'),
        ('transport', 'Transport'),
        ('construction', 'Construction'),
        ('catering', 'Restauration'),
        ('waste', 'Déchets'),
        ('water', 'Eau'),
    ], string='Catégorie', readonly=True)
    total_emission = fields.Float(string='Émissions (t CO₂)', readonly=True)
    total_offset = fields.Float(string='Compensé (t CO₂)', readonly=True)
    net_emission = fields.Float(string='Net (t CO₂)', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW wc_dashboard_carbon_category AS (
                SELECT
                    ROW_NUMBER() OVER () AS id,
                    category,
                    COALESCE(SUM(emission_tons_co2), 0) AS total_emission,
                    COALESCE(SUM(offset_tons_co2), 0) AS total_offset,
                    COALESCE(SUM(emission_tons_co2 - offset_tons_co2), 0) AS net_emission
                FROM wc_carbon_footprint
                GROUP BY category
            )
        """)


class TransportByType(models.Model):
    """Vue SQL : lignes de transport par type."""
    _name = 'wc.dashboard.transport.type'
    _description = 'Lignes de transport par type'
    _auto = False
    _order = 'line_type'

    line_type = fields.Selection([
        ('bus', 'Bus / Navette'),
        ('tram', 'Tramway'),
        ('train', 'Train'),
        ('metro', 'Métro'),
    ], string='Type', readonly=True)
    line_count = fields.Integer(string='Lignes', readonly=True)
    total_capacity = fields.Integer(string='Capacité totale', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW wc_dashboard_transport_type AS (
                SELECT
                    ROW_NUMBER() OVER () AS id,
                    line_type,
                    COUNT(*) AS line_count,
                    COALESCE(SUM(capacity_per_hour), 0) AS total_capacity
                FROM wc_transport_line
                GROUP BY line_type
            )
        """)
