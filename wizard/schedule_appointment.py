from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta

class ScheduleAppointment(models.TransientModel):
    _name = 'medical.schedule.appointment.wizard'
    _description = 'Assistant de planification de rendez-vous'

    patient_id = fields.Many2one('medical.patient', string='Patient', required=True)
    medecin_id = fields.Many2one('medical.medecin', string='Médecin', required=True)
    date_rendez_vous = fields.Datetime(string='Date du rendez-vous', required=True)
    duree = fields.Float(string='Durée (heures)', default=0.5)
    motif = fields.Text(string='Motif du rendez-vous', required=True)
    notes = fields.Text(string='Notes')
    
    @api.onchange('medecin_id', 'date_rendez_vous')
    def _check_availability(self):
        if self.medecin_id and self.date_rendez_vous:
            # Vérifier si le médecin a déjà un rendez-vous à cette heure
            domain = [
                ('medecin_id', '=', self.medecin_id.id),
                ('state', 'in', ['draft', 'confirm']),
                ('date_rendez_vous', '<=', self.date_rendez_vous),
                ('date_rendez_vous', '>=', self.date_rendez_vous - timedelta(hours=1))
            ]
            conflicting_appointments = self.env['medical.rendez.vous'].search_count(domain)
            if conflicting_appointments > 0:
                return {
                    'warning': {
                        'title': _('Attention'),
                        'message': _('Le médecin a déjà un rendez-vous prévu à cette heure ou à proximité.')
                    }
                }
    
    def action_schedule_appointment(self):
        self.ensure_one()
        
        # Vérifier à nouveau la disponibilité
        domain = [
            ('medecin_id', '=', self.medecin_id.id),
            ('state', 'in', ['draft', 'confirm']),
            ('date_rendez_vous', '<=', self.date_rendez_vous),
            ('date_rendez_vous', '>=', self.date_rendez_vous - timedelta(hours=1))
        ]
        conflicting_appointments = self.env['medical.rendez.vous'].search_count(domain)
        if conflicting_appointments > 0:
            raise UserError(_('Le médecin a déjà un rendez-vous prévu à cette heure ou à proximité.'))
        
        # Créer le rendez-vous
        rendez_vous = self.env['medical.rendez.vous'].create({
            'patient_id': self.patient_id.id,
            'medecin_id': self.medecin_id.id,
            'date_rendez_vous': self.date_rendez_vous,
            'duree': self.duree,
            'motif': self.motif,
            'notes': self.notes,
        })
        
        # Confirmer le rendez-vous
        rendez_vous.action_confirm()
        
        # Retourner une action pour afficher le rendez-vous créé
        return {
            'name': _('Rendez-vous'),
            'view_mode': 'form',
            'res_model': 'medical.rendez.vous',
            'res_id': rendez_vous.id,
            'type': 'ir.actions.act_window',
        }
