from odoo import http
from odoo.http import request

class HotelPortal(http.Controller):
    @http.route('/hotel/rooms', type='json', auth='public')
    def get_available_rooms(self, **kwargs):
        rooms = request.env['hotel.room'].sudo().search([('status', '=', 'available')])
        return [{'id': room.id, 'name': room.room_number, 'type': room.room_type, 'price': room.price} for room in rooms]

    @http.route('/hotel/services', type='json', auth='public')
    def get_services(self, **kwargs):
        services = request.env['hotel.service'].sudo().search([])
        return [{'id': service.id, 'name': service.name, 'price': service.price} for service in services]

    @http.route('/hotel/book', type='json', auth='public')
    def book_room(self, room_id, check_in_date, check_out_date, services=[]):
        room = request.env['hotel.room'].sudo().browse(room_id)
        if not room:
            return {'error': 'Room not found'}

        booking = request.env['hotel.customer'].sudo().create({
            'room_id': room.id,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'service_line_ids': [(6, 0, services)],
        })
        room.write({'status': 'occupied'})
        return {'message': f'Booking confirmed for {room.room_number}'}

    @http.route('/hotel/customer_portal', auth='user', website=True)
    def hotel_customer_portal(self, **kwargs):
        return request.render('hotel_management.CustomerPortalTemplate')
