from odoo import models, fields, api
from odoo.exceptions import ValidationError


class VolunteerSkill(models.Model):
    _name = 'wc.volunteer.skill'
    _description = 'Compétence Volontaire'
    _order = 'name'

    name = fields.Char(string='Compétence', required=True)
    color = fields.Integer(string='Couleur')


class VolunteerLanguage(models.Model):
    _name = 'wc.volunteer.language'
    _description = 'Langue Volontaire'
    _order = 'name'

    name = fields.Char(string='Langue', required=True)
    color = fields.Integer(string='Couleur')


class Volunteer(models.Model):
    _name = 'wc.volunteer'
    _description = 'Profil Volontaire - Coupe du Monde 2030'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'matching_score desc, name'

    # ============ INFORMATIONS PERSONNELLES ============
    name = fields.Char(string='Nom complet', required=True, tracking=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Téléphone')
    photo = fields.Binary(string='Photo', attachment=True)
    date_of_birth = fields.Date(string='Date de naissance')
    gender = fields.Selection([
        ('male', 'Homme'),
        ('female', 'Femme'),
    ], string='Genre')
    nationality = fields.Char(string='Nationalité')
    address = fields.Text(string='Adresse')
    id_number = fields.Char(string='CIN / Passeport')

    # ============ COMPÉTENCES ============
    skill_ids = fields.Many2many('wc.volunteer.skill', string='Compétences', required=True)
    language_ids = fields.Many2many('wc.volunteer.language', string='Langues parlées', required=True)
    has_driving_license = fields.Boolean(string='Permis de conduire')
    has_vehicle = fields.Boolean(string='Véhicule personnel')
    has_first_aid = fields.Boolean(string='Formation premiers secours')
    education_level = fields.Selection([
        ('bac', 'Baccalauréat'),
        ('bac2', 'Bac+2'),
        ('bac3', 'Licence / Bac+3'),
        ('bac5', 'Master / Bac+5'),
        ('phd', 'Doctorat'),
    ], string='Niveau d\'études')
    experience = fields.Text(string='Expérience bénévole antérieure')

    # ============ DISPONIBILITÉ & AFFECTATION ============
    availability = fields.Selection([
        ('full', 'Temps plein (toute la durée)'),
        ('morning', 'Matin uniquement'),
        ('evening', 'Soir uniquement'),
        ('weekend', 'Week-end uniquement'),
    ], string='Disponibilité', required=True)
    preferred_stadium_id = fields.Many2one('wc.stadium', string='Stade préféré')
    assigned_stadium_id = fields.Many2one('wc.stadium', string='Stade affecté', tracking=True)
    assigned_zone_id = fields.Many2one(
        'wc.stadium.zone', string='Zone affectée',
        domain="[('stadium_id', '=', assigned_stadium_id)]", tracking=True)

    # ============ PIPELINE ============
    state = fields.Selection([
        ('candidate', 'Candidat'),
        ('preselected', 'Présélectionné'),
        ('trained', 'Formé'),
        ('assigned', 'Affecté'),
        ('active', 'Actif'),
        ('archived', 'Archivé'),
    ], string='Statut', default='candidate', tracking=True, group_expand='_expand_states')

    # ============ SCORING & GAMIFICATION ============
    matching_score = fields.Float(string='Score de matching', compute='_compute_matching_score', store=True)
    badge_count = fields.Integer(string='Badges gagnés', default=0)
    points = fields.Integer(string='Points de gamification', default=0)

    # ============ DATES ============
    application_date = fields.Date(string='Date de candidature', default=fields.Date.today)
    training_date = fields.Date(string='Date de formation')
    active = fields.Boolean(default=True)

    # ============ CONTRAINTES ============
    _sql_constraints = [
        ('email_unique', 'UNIQUE(email)', 'Cet email est déjà utilisé par un autre volontaire.'),
    ]

    @api.constrains('date_of_birth')
    def _check_age(self):
        for record in self:
            if record.date_of_birth:
                from dateutil.relativedelta import relativedelta
                age = relativedelta(fields.Date.today(), record.date_of_birth).years
                if age < 18:
                    raise ValidationError("Le volontaire doit avoir au moins 18 ans.")

    # ============ ALGORITHME DE MATCHING ============
    @api.depends('skill_ids', 'language_ids', 'has_driving_license',
                 'has_vehicle', 'has_first_aid', 'availability', 'education_level')
    def _compute_matching_score(self):
        """
        Algorithme de scoring multicritère pour le matching des volontaires.
        Score sur 100 points :
        - Langues parlées : max 30 pts (6 pts par langue, plafonné à 5)
        - Compétences : max 30 pts (5 pts par compétence, plafonné à 6)
        - Permis de conduire : 10 pts
        - Véhicule personnel : 5 pts
        - Premiers secours : 10 pts
        - Disponibilité temps plein : 10 pts
        - Niveau d'études : max 5 pts
        """
        for record in self:
            score = 0.0

            # Langues (max 30 pts)
            nb_languages = len(record.language_ids)
            score += min(nb_languages * 6, 30)

            # Compétences (max 30 pts)
            nb_skills = len(record.skill_ids)
            score += min(nb_skills * 5, 30)

            # Permis de conduire (10 pts)
            if record.has_driving_license:
                score += 10

            # Véhicule personnel (5 pts)
            if record.has_vehicle:
                score += 5

            # Premiers secours (10 pts)
            if record.has_first_aid:
                score += 10

            # Disponibilité (max 10 pts)
            availability_scores = {
                'full': 10,
                'morning': 5,
                'evening': 5,
                'weekend': 3,
            }
            score += availability_scores.get(record.availability, 0)

            # Niveau d'études (max 5 pts)
            education_scores = {
                'bac': 1,
                'bac2': 2,
                'bac3': 3,
                'bac5': 4,
                'phd': 5,
            }
            score += education_scores.get(record.education_level, 0)

            record.matching_score = min(score, 100)

    # ============ ACTIONS DE PIPELINE ============
    def action_preselect(self):
        self.write({'state': 'preselected'})

    def action_train(self):
        self.write({'state': 'trained', 'training_date': fields.Date.today()})

    def action_assign(self):
        for record in self:
            if not record.assigned_stadium_id:
                raise ValidationError("Veuillez affecter un stade avant de valider l'affectation.")
            record.write({'state': 'assigned'})

    def action_activate(self):
        self.write({'state': 'active'})

    def action_archive_volunteer(self):
        self.write({'state': 'archived', 'active': False})

    def action_reset_to_candidate(self):
        self.write({'state': 'candidate'})

    # ============ GROUP EXPAND (Kanban) ============
    @api.model
    def _expand_states(self, states, domain):
        return [key for key, val in type(self).state.selection]
