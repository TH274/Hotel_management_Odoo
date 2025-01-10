import logging
from odoo import models, fields, api, exceptions, _
from datetime import date

_logger = logging.getLogger(__name__)

class HotelCustomer(models.Model):
    _name = 'hotel.customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Customer'

    name = fields.Char(string='Customer Name', required=True, tracking=True)
    booking_code = fields.Char(string='Booking Code', readonly=True, default=lambda self: _('New'))
    hotel_id = fields.Many2one('hotel.hotel', string='Hotel', required=True, tracking=True)
    room_id = fields.Many2one('hotel.room', string='Room', required=True, tracking=True,
        domain="[('hotel_id', '=', hotel_id), ('room_type', '=', room_type), ('status', '=', 'available')]",
        context={'show_room_number': True}
    )
    room_type = fields.Selection([('single', 'Single'), ('double', 'Double')], string='Room Type', tracking=True)
    check_in_date = fields.Date(string='Check-In Date', required=True, tracking=True)
    check_out_date = fields.Date(string='Check-Out Date', required=True, tracking=True)
    status = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Booking Status', default='new', tracking=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    tag_ids = fields.Many2many('customer.tag', string='Tags')

    @api.constrains('check_in_date', 'check_out_date')
    def _check_dates(self):
        for record in self:
            if record.check_in_date > record.check_out_date:
                _logger.error('Invalid dates for booking %s: check-in date %s is later than check-out date %s', record.id, record.check_in_date, record.check_out_date)
                raise exceptions.ValidationError(_('Check-In Date cannot be later than Check-Out Date.'))
           
    @api.constrains('room_id')
    def _check_room_availability(self):
        for record in self:
            if record.room_id.status != 'available':
                _logger.error('Room %s is not available for booking %s', record.room_id.id, record.id)
                raise exceptions.ValidationError(_('The selected room is not available.'))

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if len(record.name) < 3:
                _logger.error('Invalid customer name for booking %s: name %s is too short', record.id, record.name)
                raise exceptions.ValidationError(_('The customer name must be at least 3 characters long.'))

    @api.model
    def create(self, vals):
        _logger.debug('Creating a new booking with values: %s', vals)
        if not vals.get('booking_code') or vals['booking_code'] == 'New':
            vals['booking_code'] = self.env['ir.sequence'].next_by_code('hotel.customer') or _('New')
        record = super().create(vals)
        _logger.info('Created new booking with ID: %s and booking code: %s', record.id, record.booking_code)
        return record

    @api.depends('room_id.price', 'check_in_date', 'check_out_date')
    def _compute_total_amount(self):
        for record in self:
            if record.check_in_date and record.check_out_date:
                duration = (record.check_out_date - record.check_in_date).days
                record.total_amount = duration * record.room_id.price
                _logger.debug('Computed total amount for booking %s: %s', record.id, record.total_amount)

    def action_confirm_booking(self):
        for record in self:
            if record.status == 'new':
                record.status = 'confirmed'
                record.room_id.status = 'reserved'

    def action_confirm(self):
        self.write({'status': 'confirmed'})

    def action_cancel(self):
        self.write({'status': 'new'})

