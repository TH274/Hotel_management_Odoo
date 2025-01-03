from odoo import models, fields, api, exceptions, _
from datetime import date

class HotelCustomer(models.Model):
    _name = 'hotel.customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Customer'

    name = fields.Char(string='Customer Name', required=True, tracking=True)
    booking_code = fields.Char(string='Booking Code', readonly=True, default=lambda self: _('New'))
    booking_date = fields.Date(string='Booking Date', default=fields.Date.today, readonly=True, tracking=True)
    hotel_id = fields.Many2one('hotel.hotel', string='Hotel', required=True, tracking=True)
    room_id = fields.Many2one('hotel.room', string='Room', required=True, tracking=True,
        domain="[('hotel_id', '=', hotel_id), ('room_type', '=', room_type), ('status', '=', 'available')]")
    room_type = fields.Selection([('single', 'Single'), ('double', 'Double')], string='Room Type', tracking=True)
    check_in_date = fields.Date(string='Check-In Date', required=True, tracking=True)
    check_out_date = fields.Date(string='Check-Out Date', required=True, tracking=True)
    status = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Booking Status', default='new', tracking=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)


    @api.constrains('check_in_date', 'check_out_date')
    def _check_dates(self):
        for record in self:
            if record.check_in_date > record.check_out_date:
                raise exceptions.ValidationError(_('Check-In Date cannot be later than Check-Out Date.'))

    @api.model
    def create(self, vals):
        if not vals.get('booking_code') or vals['booking_code'] == 'New':
            vals['booking_code'] = self.env['ir.sequence'].next_by_code('hotel.customer') or _('New')
        return super().create(vals)

    def action_confirm_booking(self):
        for record in self:
            if record.status == 'new':
                record.status = 'confirmed'
                record.room_id.status = 'reserved'

    @api.depends('room_id.price', 'check_in_date', 'check_out_date')
    def _compute_total_amount(self):
        for record in self:
            if record.check_in_date and record.check_out_date and record.room_id:
                days = (record.check_out_date - record.check_in_date).days
                record.total_amount = days * record.room_id.price
            else:
                record.total_amount = 0.0

    def action_confirm(self):
        self.write({'status': 'confirmed'})

    def action_cancel(self):
        self.write({'status': 'new'})

