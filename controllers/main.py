from odoo import http
from odoo.http import request
import json
from datetime import datetime, timedelta

class MedicalDashboard(http.Controller):
    @http.route('/cabinet_medecin/dashboard_data', type='http', auth='user')
    def get_dashboard_data(self):
        # Récupération de la date actuelle
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Consultations par jour (7 derniers jours)
        consultations_by_day = []
        for i in range(7):
            day = today - timedelta(days=i)
            count = request.env['medical.consultation'].search_count([
                ('date_consultation', '>=', day.strftime('%Y-%m-%d 00:00:00')),
                ('date_consultation', '<=', day.strftime('%Y-%m-%d 23:59:59'))
            ])
            consultations_by_day.append({
                'day': day.strftime('%d/%m'),
                'count': count
            })
        
        # Recettes par médecin (mois en cours)
        first_day_of_month = today.replace(day=1)
        medecins = request.env['medical.medecin'].search([])
        revenues_by_medecin = []
        
        for medecin in medecins:
            consultations = request.env['medical.consultation'].search([
                ('medecin_id', '=', medecin.id),
                ('state', '=', 'done'),
                ('date_consultation', '>=', first_day_of_month.strftime('%Y-%m-%d'))
            ])
            
            total_revenue = 0
            for consultation in consultations:
                if consultation.facture_id:
                    total_revenue += consultation.facture_id.amount_total
            
            revenues_by_medecin.append({
                'medecin': medecin.name + ' ' + medecin.prenom,
                'revenue': total_revenue
            })
        
        # Taux d'occupation des créneaux horaires
        # Calculé comme le nombre de rendez-vous confirmés divisé par le nombre total de créneaux disponibles
        # (Ceci est une simplification, une implémentation réelle nécessiterait une logique plus complexe)
        occupation_rate = []
        for hour in range(8, 19):  # De 8h à 18h
            rdvs_count = request.env['medical.rendez.vous'].search_count([
                ('date_rendez_vous', '>=', today.strftime(f'%Y-%m-%d {hour:02d}:00:00')),
                ('date_rendez_vous', '<', today.strftime(f'%Y-%m-%d {hour+1:02d}:00:00')),
                ('state', 'in', ['confirm', 'done'])
            ])
            
            # Supposons que chaque médecin peut avoir un rendez-vous par heure
            medecins_count = request.env['medical.medecin'].search_count([])
            total_slots = medecins_count
            
            if total_slots > 0:
                rate = (rdvs_count / total_slots) * 100
            else:
                rate = 0
                
            occupation_rate.append({
                'hour': f"{hour}:00 - {hour+1}:00",
                'rate': round(rate, 2)
            })
        
        data = {
            'consultations_by_day': consultations_by_day,
            'revenues_by_medecin': revenues_by_medecin,
            'occupation_rate': occupation_rate
        }
        
        return json.dumps(data)
