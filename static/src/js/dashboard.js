odoo.define('cabinet_medecin.dashboard', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    var MedicalDashboard = AbstractAction.extend({
        template: 'MedicalDashboard',
        events: {},

        init: function(parent, action) {
            this._super(parent, action);
            this.dashboardData = {};
        },

        willStart: function() {
            var self = this;
            return this._super().then(function() {
                return self._fetchDashboardData();
            });
        },

        start: function() {
            var self = this;
            return this._super().then(function() {
                self._renderDashboard();
            });
        },

        _fetchDashboardData: function() {
            var self = this;
            return rpc.query({
                route: '/cabinet_medecin/dashboard_data',
            }).then(function(result) {
                self.dashboardData = JSON.parse(result);
            });
        },

        _renderDashboard: function() {
            var self = this;
            
            // Consultations par jour
            var ctx1 = document.getElementById('consultationsChart').getContext('2d');
            var days = [];
            var counts = [];
            
            if (self.dashboardData.consultations_by_day) {
                self.dashboardData.consultations_by_day.forEach(function(item) {
                    days.push(item.day);
                    counts.push(item.count);
                });
            }
            
            new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: days,
                    datasets: [{
                        label: 'Nombre de consultations',
                        data: counts,
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
            
            // Recettes par médecin
            var ctx2 = document.getElementById('revenueChart').getContext('2d');
            var medecins = [];
            var revenues = [];
            
            if (self.dashboardData.revenues_by_medecin) {
                self.dashboardData.revenues_by_medecin.forEach(function(item) {
                    medecins.push(item.medecin);
                    revenues.push(item.revenue);
                });
            }
            
            new Chart(ctx2, {
                type: 'pie',
                data: {
                    labels: medecins,
                    datasets: [{
                        data: revenues,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.5)',
                            'rgba(54, 162, 235, 0.5)',
                            'rgba(255, 206, 86, 0.5)',
                            'rgba(75, 192, 192, 0.5)',
                            'rgba(153, 102, 255, 0.5)',
                            'rgba(255, 159, 64, 0.5)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'right',
                        },
                        title: {
                            display: true,
                            text: 'Recettes par médecin'
                        }
                    }
                }
            });
            
            // Taux d'occupation
            var ctx3 = document.getElementById('occupationChart').getContext('2d');
            var hours = [];
            var rates = [];
            
            if (self.dashboardData.occupation_rate) {
                self.dashboardData.occupation_rate.forEach(function(item) {
                    hours.push(item.hour);
                    rates.push(item.rate);
                });
            }
            
            new Chart(ctx3, {
                type: 'line',
                data: {
                    labels: hours,
                    datasets: [{
                        label: "Taux d'occupation (%)",
                        data: rates,
                        fill: false,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        },
    });

    core.action_registry.add('medical_dashboard', MedicalDashboard);

    return MedicalDashboard;
});
