from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class PaiementCabinet(models.Model):
    _name = 'medical.paiement'
    _description = 'Paiement Cabinet Médical'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_paiement desc, id desc'

    name = fields.Char(string='Référence', readonly=True, default=lambda self: _('Nouveau Paiement'))
    facture_id = fields.Many2one('medical.facture', string='Facture', required=True, tracking=True)
    patient_id = fields.Many2one(related='facture_id.patient_id', string='Patient', store=True, readonly=True)
    date_paiement = fields.Date(string='Date de paiement', default=fields.Date.today, required=True)
    montant = fields.Float(string='Montant', required=True)
    
    mode_paiement = fields.Selection([
        ('especes', 'Espèces'),
        ('carte', 'Carte bancaire'),
        ('cheque', 'Chèque'),
        ('virement', 'Virement bancaire'),
        ('autre', 'Autre')
    ], string='Mode de paiement', default='especes', required=True, tracking=True)
    
    reference_externe = fields.Char(string='Référence externe', help="Numéro de chèque, référence de transaction, etc.")
    note = fields.Text(string='Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau Paiement')) == _('Nouveau Paiement'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medical.paiement') or _('Nouveau Paiement')
        
        result = super(PaiementCabinet, self).create(vals_list)
        
        # Mettre à jour l'état de la facture associée
        for record in result:
            if record.facture_id.state != 'paid':
                record.facture_id.action_pay()
        
        return result
    
    def unlink(self):
        # Vérifier si la suppression affecte l'état des factures
        factures_to_check = self.mapped('facture_id')
        result = super(PaiementCabinet, self).unlink()
        
        # Remettre les factures à l'état confirmé si tous leurs paiements sont supprimés
        for facture in factures_to_check:
            remaining_payments = self.env['medical.paiement'].search_count([('facture_id', '=', facture.id)])
            if remaining_payments == 0 and facture.state == 'paid':
                facture.action_confirm()
        
        return result
