from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class FactureCabinet(models.Model):
    _name = 'medical.facture'
    _description = 'Facture Cabinet Médical'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_creation desc, id desc'

    name = fields.Char(string='Numéro', readonly=True, default=lambda self: _('Nouvelle Facture'))
    patient_id = fields.Many2one('medical.patient', string='Patient', required=True, tracking=True)
    medecin_id = fields.Many2one('medical.medecin', string='Médecin', required=True, tracking=True)
    consultation_id = fields.Many2one('medical.consultation', string='Consultation', ondelete='restrict')
    date_creation = fields.Date(string='Date de création', default=fields.Date.today, required=True)
    montant_total = fields.Float(string='Montant Total', compute='_compute_montant_total', store=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('paid', 'Payée'),
        ('cancelled', 'Annulée')
    ], string='État', default='draft', tracking=True)
    
    ligne_ids = fields.One2many('medical.facture.ligne', 'facture_id', string='Lignes de facture')
    paiement_ids = fields.One2many('medical.paiement', 'facture_id', string='Paiements')
    montant_paye = fields.Float(string='Montant payé', compute='_compute_montant_paye', store=True)
    montant_restant = fields.Float(string='Reste à payer', compute='_compute_montant_paye', store=True)
    note = fields.Text(string='Notes')
    
    @api.depends('ligne_ids.montant_total')
    def _compute_montant_total(self):
        for facture in self:
            facture.montant_total = sum(ligne.montant_total for ligne in facture.ligne_ids)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouvelle Facture')) == _('Nouvelle Facture'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medical.facture') or _('Nouvelle Facture')
        return super(FactureCabinet, self).create(vals_list)
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_pay(self):
        self.write({'state': 'paid'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
        
    @api.depends('paiement_ids.montant', 'montant_total')
    def _compute_montant_paye(self):
        for facture in self:
            montant_paye = sum(paiement.montant for paiement in facture.paiement_ids)
            facture.montant_paye = montant_paye
            facture.montant_restant = facture.montant_total - montant_paye
            
            # Mettre à jour automatiquement l'état si entièrement payée
            if facture.montant_restant <= 0 and facture.state == 'confirmed':
                facture.action_pay()
            elif facture.montant_paye > 0 and facture.montant_restant > 0 and facture.state == 'paid':
                facture.write({'state': 'confirmed'})
    
    def action_register_payment(self):
        self.ensure_one()
        return {
            'name': _('Enregistrer un paiement'),
            'type': 'ir.actions.act_window',
            'res_model': 'medical.paiement',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_facture_id': self.id,
                'default_montant': self.montant_restant,
            },
        }


class FactureCabinetLigne(models.Model):
    _name = 'medical.facture.ligne'
    _description = 'Ligne de Facture Cabinet Médical'
    
    facture_id = fields.Many2one('medical.facture', string='Facture', required=True, ondelete='cascade')
    name = fields.Char(string='Description', required=True)
    quantite = fields.Float(string='Quantité', default=1.0)
    prix_unitaire = fields.Float(string='Prix Unitaire')
    montant_total = fields.Float(string='Montant Total', compute='_compute_montant_total', store=True)
    
    @api.depends('quantite', 'prix_unitaire')
    def _compute_montant_total(self):
        for ligne in self:
            ligne.montant_total = ligne.quantite * ligne.prix_unitaire
