from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta

class RendezVous(models.Model):
    _name = 'medical.rendez.vous'
    _description = 'Rendez-vous'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_rendez_vous'

    name = fields.Char(string='Référence', readonly=True, copy=False)
    patient_id = fields.Many2one('medical.patient', string='Patient', required=True)
    medecin_id = fields.Many2one('medical.medecin', string='Médecin', required=True)
    date_rendez_vous = fields.Datetime(string='Date du rendez-vous', required=True)
    duree = fields.Float(string='Durée (heures)', default=0.5)
    
    motif = fields.Text(string='Motif du rendez-vous')
    notes = fields.Text(string='Notes')
    
    state = fields.Selection([
        ('draft', 'Planifié'),
        ('confirm', 'Confirmé'),
        ('done', 'Terminé'),
        ('cancel', 'Annulé')
    ], string='État', default='draft', tracking=True)
    
    calendar_event_id = fields.Many2one('calendar.event', string='Événement calendrier')
    consultation_id = fields.Many2one('medical.consultation', string='Consultation associée')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medical.rendez.vous.sequence')
        records = super().create(vals_list)
        for record in records:
            record._create_calendar_event()
        return records

    def _create_calendar_event(self):
        self.ensure_one()
        if not self.calendar_event_id:
            duration = self.duree * 60  # Conversion en minutes
            stop_dt = self.date_rendez_vous + timedelta(minutes=duration)
            
            event = self.env['calendar.event'].create({
                'name': f'RDV: {self.patient_id.name} - Dr. {self.medecin_id.name}',
                'start': self.date_rendez_vous,
                'stop': stop_dt,
                'duration': self.duree,
                'user_id': self.medecin_id.user_id.id,
                'partner_ids': [(4, self.medecin_id.user_id.partner_id.id)],
                'description': self.motif or '',
            })
            self.calendar_event_id = event.id

    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirm'

    def action_done(self):
        self.ensure_one()
        self.state = 'done'
        # Créer automatiquement une consultation
        consultation = self.env['medical.consultation'].create({
            'patient_id': self.patient_id.id,
            'medecin_id': self.medecin_id.id,
            'date_consultation': self.date_rendez_vous,
            'rendez_vous_id': self.id,
        })
        self.consultation_id = consultation.id

    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancel'
        if self.calendar_event_id:
            self.calendar_event_id.unlink()

    def write(self, vals):
        res = super().write(vals)
        if 'date_rendez_vous' in vals or 'duree' in vals:
            for record in self:
                if record.calendar_event_id:
                    duration = record.duree * 60
                    stop_dt = record.date_rendez_vous + timedelta(minutes=duration)
                    record.calendar_event_id.write({
                        'start': record.date_rendez_vous,
                        'stop': stop_dt,
                        'duration': record.duree,
                    })
        return res

    def unlink(self):
        for record in self:
            if record.calendar_event_id:
                record.calendar_event_id.unlink()
        return super().unlink()
