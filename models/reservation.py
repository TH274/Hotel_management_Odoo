from odoo import models, fields, api, exceptions, _
from datetime import timedelta

class HotelReservation(models.Model):
    _name = 'hotel.reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Reservation'

    guest_name = fields.Char(string='Guest Name', compute='_compute_guest_name', store=True, tracking=True)
    customer_id = fields.Many2one('hotel.customer', string='Customer', required=True)
    room_id = fields.Many2one('hotel.room', string='Room', required=True, domain="[('status', '=', 'available')]", tracking=True)
    check_in_date = fields.Date(string='Check-in Date', required=True, tracking=True)
    check_out_date = fields.Date(string='Check-out Date', required=True, tracking=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True, tracking=True)

    @api.onchange('customer_id')
    def _onchange_customer(self):
        if self.customer_id:
            self.check_in_date = self.customer_id.check_in_date
            self.check_out_date = self.customer_id.check_out_date

    @api.depends('room_id', 'check_in_date', 'check_out_date')
    def _compute_total_amount(self):
        for record in self:
            if record.room_id and record.check_in_date and record.check_out_date:
                nights = (record.check_out_date - record.check_in_date).days
                record.total_amount = nights * record.room_id.price
    
    @api.depends('customer_id')
    def _compute_guest_name(self):
        for record in self:
            record.guest_name = record.customer_id.name if record.customer_id else ''