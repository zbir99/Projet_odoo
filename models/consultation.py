from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Consultation(models.Model):
    _name = 'medical.consultation'
    _description = 'Consultation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_consultation desc'

    name = fields.Char(string='Référence', readonly=True, copy=False)
    patient_id = fields.Many2one('medical.patient', string='Patient', required=True)
    medecin_id = fields.Many2one('medical.medecin', string='Médecin', required=True)
    date_consultation = fields.Datetime(string='Date de consultation', required=True)
    
    diagnostic = fields.Text(string='Diagnostic')
    ordonnance = fields.Text(string='Ordonnance')
    examens = fields.Text(string='Examens prescrits')
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirm', 'Confirmé'),
        ('done', 'Terminé'),
        ('cancel', 'Annulé')
    ], string='État', default='draft', tracking=True)
    
    facture_id = fields.Many2one('medical.facture', string='Facture associée', readonly=True)
    rendez_vous_id = fields.Many2one('medical.rendez.vous', string='Rendez-vous associé')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medical.consultation.sequence')
        return super().create(vals_list)

    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirm'

    def action_done(self):
        self.ensure_one()
        if not self.diagnostic:
            raise UserError(_("Vous devez saisir un diagnostic avant de terminer la consultation."))
        self.state = 'done'
        
        # Désactivation de la création automatique de factures
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Consultation terminée'),
                'message': _('La consultation a été terminée avec succès. Pour créer une facture, veuillez utiliser le module Facturation d\'Odoo.'),
                'sticky': False,
                'type': 'success',
            }
        }

    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancel'
        
    def action_create_invoice(self):
        self.ensure_one()
        if self.facture_id:
            raise UserError(_("Une facture existe déjà pour cette consultation."))
        
        # Prix standard pour une consultation médicale
        prix_consultation = 350.0
        prix_examens = 200.0
        
        # Créer la facture avec notre modèle personnalisé
        vals_facture = {
            'patient_id': self.patient_id.id,
            'medecin_id': self.medecin_id.id,
            'consultation_id': self.id,
            'date_creation': fields.Date.today(),
            'ligne_ids': [
                (0, 0, {
                    'name': f"Consultation médicale - Dr. {self.medecin_id.name}",
                    'quantite': 1.0,
                    'prix_unitaire': prix_consultation,
                })
            ],
        }
        
        # Ajouter des examens si prescrits
        if self.examens and self.examens.strip():
            vals_facture['ligne_ids'].append(
                (0, 0, {
                    'name': f"Examens médicaux: {self.examens}",
                    'quantite': 1.0,
                    'prix_unitaire': prix_examens,
                })
            )
        
        try:
            # Créer la facture
            facture = self.env['medical.facture'].create(vals_facture)
            self.facture_id = facture.id
            
            # Ouvrir la facture nouvellement créée
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'medical.facture',
                'res_id': facture.id,
                'view_mode': 'form',
                'target': 'current',
            }
        except Exception as e:
            raise UserError(_("Erreur lors de la création de la facture: %s") % str(e))

    def _create_invoice(self):
        self.ensure_one()
        if self.facture_id:
            raise UserError(_("Une facture existe déjà pour cette consultation."))
            
        # Rechercher un journal de vente existant
        sale_journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        if not sale_journal:
            raise UserError(_("Aucun journal de vente n'a été trouvé. Veuillez configurer un journal de vente dans le module Comptabilité."))
        
        # Prix de base pour une consultation
        prix_consultation = 350.0
        
        # Créer une facture simple
        invoice_vals = {
            'partner_id': self.patient_id.partner_id.id if hasattr(self.patient_id, 'partner_id') and self.patient_id.partner_id else self.patient_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'journal_id': sale_journal.id,
            'ref': self.name,
            'invoice_line_ids': [
                (0, 0, {
                    'name': f"Consultation médicale - Dr. {self.medecin_id.name} {self.medecin_id.prenom if hasattr(self.medecin_id, 'prenom') else ''}",
                    'quantity': 1,
                    'price_unit': prix_consultation,
                })
            ],
        }
        
        # Ajouter des examens si nécessaire
        if self.examens and self.examens.strip():
            invoice_vals['invoice_line_ids'].append(
                (0, 0, {
                    'name': f"Examens médicaux prescrits",
                    'quantity': 1,
                    'price_unit': 200.0,
                })
            )
        
        # Créer la facture (en brouillon)
        try:
            facture = self.env['account.move'].create(invoice_vals)
            self.facture_id = facture.id
            return facture
        except Exception as e:
            raise UserError(_("Erreur lors de la création de la facture: %s") % str(e))
