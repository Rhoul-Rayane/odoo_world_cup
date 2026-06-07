import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class TicketScannerController(http.Controller):

    @http.route('/ticket/scan', type='http', auth='user', website=False)
    def ticket_scan_page(self, **kwargs):
        """Affiche le portail de scannage de billets (interface mobile)."""
        return request.render('wc_finance.ticket_scan_template', {})

    @http.route('/ticket/scan/validate', type='json', auth='user', methods=['POST'], csrf=False)
    def ticket_scan_validate(self, **kwargs):
        """Valide un billet scanné via son code-barres.
        
        Reçoit: { 'barcode': 'ABCDEF1234567890' }
        Retourne: { 'success': bool, 'message': str, 'ticket_data': dict }
        """
        barcode = kwargs.get('barcode', '').strip().upper()
        
        if not barcode:
            return {
                'success': False,
                'message': '❌ Aucun code-barres détecté.',
                'ticket_data': {},
            }

        # Rechercher le billet par code-barres
        ticket = request.env['wc.ticket'].sudo().search([
            ('barcode', '=', barcode)
        ], limit=1)

        if not ticket:
            _logger.warning("Scan échoué : code-barres inconnu [%s]", barcode)
            return {
                'success': False,
                'message': '❌ Billet INCONNU — Code-barres non trouvé dans le système.',
                'ticket_data': {},
            }

        if ticket.state == 'scanned':
            return {
                'success': False,
                'message': f'⚠️ Billet DÉJÀ SCANNÉ le {ticket.scan_datetime.strftime("%d/%m/%Y à %H:%M")}',
                'ticket_data': {
                    'name': ticket.name,
                    'holder': ticket.holder_name or '-',
                    'match': ticket.match_id.name or '-',
                    'zone': ticket.stadium_zone_id.name or '-',
                    'category': ticket.category,
                    'state': ticket.state,
                },
            }

        if ticket.state == 'cancelled':
            return {
                'success': False,
                'message': '❌ Billet ANNULÉ — Accès refusé.',
                'ticket_data': {
                    'name': ticket.name,
                    'state': ticket.state,
                },
            }

        # Billet valide : procéder au scan
        try:
            ticket.with_user(request.env.user).action_scan()
            _logger.info("Billet %s scanné avec succès par %s", ticket.name, request.env.user.name)
            
            # Récupérer le headcount mis à jour
            crowd = request.env['wc.crowd.monitoring'].sudo().search([
                ('match_id', '=', ticket.match_id.id),
                ('stadium_zone_id', '=', ticket.stadium_zone_id.id),
            ], limit=1)
            
            return {
                'success': True,
                'message': f'✅ ACCÈS AUTORISÉ — Bienvenue au match !',
                'ticket_data': {
                    'name': ticket.name,
                    'holder': ticket.holder_name or '-',
                    'match': ticket.match_id.name or '-',
                    'zone': ticket.stadium_zone_id.name or '-',
                    'stadium': ticket.stadium_id.name or '-',
                    'category': ticket.category,
                    'state': 'scanned',
                    'scan_time': ticket.scan_datetime.strftime('%H:%M:%S') if ticket.scan_datetime else '-',
                    'current_headcount': crowd.current_headcount if crowd else 0,
                    'safety_status': crowd.safety_status if crowd else 'green',
                },
            }
        except Exception as e:
            _logger.error("Erreur lors du scan du billet %s: %s", barcode, str(e))
            return {
                'success': False,
                'message': f'❌ Erreur: {str(e)}',
                'ticket_data': {},
            }
