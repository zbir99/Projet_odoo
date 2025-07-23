from odoo import models, fields, api

class Medecin(models.Model):
    _name = 'medical.medecin'
    _description = 'Médecin'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom', required=True, tracking=True)
    prenom = fields.Char(string='Prénom', required=True, tracking=True)
    specialite = fields.Char(string='Spécialité', required=True)
    
    consultation_ids = fields.One2many('medical.consultation', 'medecin_id', string='Consultations')
    rendez_vous_ids = fields.One2many('medical.rendez.vous', 'medecin_id', string='Rendez-vous')
    
    horaires_consultation = fields.Text(string='Horaires de consultation')
    user_id = fields.Many2one('res.users', string='Utilisateur associé', required=True)
    
    active = fields.Boolean(default=True)
    reference = fields.Char(string='Référence', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('medical.medecin.sequence')
        return super().create(vals_list)

    def name_get(self):
        result = []
        for medecin in self:
            name = f"Dr. {medecin.name} {medecin.prenom}"
            result.append((medecin.id, name))
        return result
