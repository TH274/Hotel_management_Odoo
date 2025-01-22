# models/reports.py
from odoo import models, fields, api
from datetime import datetime, timedelta

class RoomAvailabilityReport(models.TransientModel):
    _name = 'hotel.room.availability.report'
    _description = 'Room Availability Report'

    date_from = fields.Date(string='From Date', default=fields.Date.today)
    date_to = fields.Date(string='To Date', default=fields.Date.today)
    room_type = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
        ('all', 'All')
    ], string='Room Type', default='all')

    def action_print_report(self):
        return self.env.ref('hotel_management.action_room_availability_report').report_action(self)

    def get_available_rooms(self):
        self.ensure_one()
        domain = [('status', '=', 'available')]
        
        if self.room_type != 'all':
            domain.append(('room_type', '=', self.room_type))
            
        rooms = self.env['hotel.room'].search(domain)
        
        # Check reservations for the period
        reservations = self.env['hotel.customer'].search([
            ('check_in_date', '<=', self.date_to),
            ('check_out_date', '>=', self.date_from)
        ])
        
        occupied_room_ids = reservations.mapped('room_id.id')
        available_rooms = rooms.filtered(lambda r: r.id not in occupied_room_ids)
        
        return available_rooms

class RevenueReport(models.TransientModel):
    _name = 'hotel.revenue.report'
    _description = 'Revenue Report'

    report_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('room', 'By Room'),
        ('customer', 'By Customer')
    ], string='Report Type', required=True, default='daily')

    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)

    def action_print_report(self):
        return self.env.ref('hotel_management.action_revenue_report').report_action(self)

   def get_revenue_data(self):
        self.ensure_one()
        domain = [
            ('payment_status', '=', 'paid'),
            ('payment_date', '>=', self.date_from),
            ('payment_date', '<=', self.date_to)
        ]
        
        bookings = self.env['hotel.customer'].search(domain)
        
        if not bookings:
            return []

        if self.report_type == 'room':
            return self._group_by_room(bookings)
        elif self.report_type == 'customer':
            return self._group_by_customer(bookings)
        else:
            return self._group_by_time(bookings)

    def _group_by_time(self, bookings):
        date_format = {
            'daily': '%Y-%m-%d',
            'weekly': '%Y-W%W',
            'monthly': '%Y-%m'
        }.get(self.report_type, '%Y-%m-%d')

        time_data = {}
        for booking in bookings:
            key = booking.payment_date.strftime(date_format)
            if key not in time_data:
                time_data[key] = {
                    'name': key,
                    'total': 0
                }
            time_data[key]['total'] += booking.payment_amount
        
        return sorted(time_data.values(), key=lambda x: x['name'])

    def _group_by_room(self, bookings):
        room_data = {}
        for booking in bookings:
            room = booking.room_id
            if room.id not in room_data:
                room_data[room.id] = {
                    'name': room.room_number,
                    'type': room.room_type,
                    'total': 0
                }
            room_data[room.id]['total'] += booking.payment_amount
        return list(room_data.values())

    def _group_by_customer(self, bookings):
        customer_data = {}
        for booking in bookings:
            customer = booking.partner_id
            if customer.id not in customer_data:
                customer_data[customer.id] = {
                    'name': customer.name,
                    'total': 0
                }
            customer_data[customer.id]['total'] += booking.payment_amount
        return list(customer_data.values())