from odoo import models, fields, api, _
from odoo.exceptions import UserError

class GenerateOrdonnance(models.TransientModel):
    _name = 'medical.generate.ordonnance.wizard'
    _description = 'Assistant de génération d\'ordonnance'

    consultation_id = fields.Many2one('medical.consultation', string='Consultation', required=True)
    patient_id = fields.Many2one('medical.patient', string='Patient', related='consultation_id.patient_id', readonly=True)
    medecin_id = fields.Many2one('medical.medecin', string='Médecin', related='consultation_id.medecin_id', readonly=True)
    date_consultation = fields.Datetime(string='Date de consultation', related='consultation_id.date_consultation', readonly=True)
    
    diagnostic = fields.Text(string='Diagnostic', required=True)
    ordonnance = fields.Text(string='Ordonnance', required=True)
    examens = fields.Text(string='Examens prescrits')
    
    @api.model
    def default_get(self, fields_list):
        res = super(GenerateOrdonnance, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            consultation = self.env['medical.consultation'].browse(active_id)
            res.update({
                'consultation_id': consultation.id,
                'diagnostic': consultation.diagnostic or '',
                'ordonnance': consultation.ordonnance or '',
                'examens': consultation.examens or '',
            })
        return res
    
    def action_generate_ordonnance(self):
        self.ensure_one()
        if not self.consultation_id:
            raise UserError(_("Aucune consultation sélectionnée."))
            
        self.consultation_id.write({
            'diagnostic': self.diagnostic,
            'ordonnance': self.ordonnance,
            'examens': self.examens,
        })
        
        # Si la consultation est en brouillon, la confirmer
        if self.consultation_id.state == 'draft':
            self.consultation_id.action_confirm()
        
        # Générer le rapport d'ordonnance
        return self.env.ref('cabinet_medecin.report_medical_ordonnance').report_action(self.consultation_id)
