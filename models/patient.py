from odoo import models, fields, api
from datetime import date

class Patient(models.Model):
    _name = 'medical.patient'
    _description = 'Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom', required=True, tracking=True)
    prenom = fields.Char(string='Prénom', required=True, tracking=True)
    date_naissance = fields.Date(string='Date de naissance', required=True)
    age = fields.Integer(string='Âge', compute='_compute_age', store=True)
    sexe = fields.Selection([
        ('homme', 'Homme'),
        ('femme', 'Femme')
    ], string='Sexe', required=True)
    
    medecin_id = fields.Many2one('medical.medecin', string='Médecin Traitant', tracking=True)
    
    groupe_sanguin = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ], string='Groupe sanguin')
    
    allergies = fields.Text(string='Allergies')
    antecedents = fields.Text(string='Antécédents médicaux')
    mutuelle = fields.Char(string='Mutuelle')
    
    consultation_ids = fields.One2many('medical.consultation', 'patient_id', string='Consultations')
    rendez_vous_ids = fields.One2many('medical.rendez.vous', 'patient_id', string='Rendez-vous')
    
    active = fields.Boolean(default=True)
    reference = fields.Char(string='Référence', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('medical.patient.sequence')
        return super().create(vals_list)

    @api.depends('date_naissance')
    def _compute_age(self):
        for patient in self:
            if patient.date_naissance:
                today = date.today()
                patient.age = today.year - patient.date_naissance.year - \
                    ((today.month, today.day) < (patient.date_naissance.month, patient.date_naissance.day))
