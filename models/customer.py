import logging
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from datetime import date

_logger = logging.getLogger(__name__)

class HotelCustomer(models.Model):
    _name = 'hotel.customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Customer'

    partner_id = fields.Many2one('res.partner', string='Customer Name', required=True, tracking=True)
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
        ('reserved', 'Reserved'),
        ('checkin','Checkin'),
        ('checkout','Checkout'),
        ('done','Done'),
        ('cancelled', 'Cancelled'),
    ], string='Booking Status', default='new', tracking=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    tag_ids = fields.Many2many('customer.tag', string='Tags')
    service_line_ids = fields.One2many(
        'product.template', 'customer_id', string="Services Availed",
        help="List of services availed by the customer."
    )
    sale_order_ids = fields.One2many('sale.order', 'origin', string='Sale Orders')

    @api.model
    def create(self, vals):
        _logger.debug('Creating a new booking with values: %s', vals)
        if not vals.get('booking_code') or vals['booking_code'] == 'New':
            if 'partner_id' in vals:
                partner_id = vals['partner_id']
                vals['booking_code'] = f"{partner_id}"
            else:
                vals['booking_code'] = self.env['ir.sequence'].next_by_code('hotel.customer') or _('New')
        record = super().create(vals)
        record.message_post(
            body=_('A new booking has been created with code: %s' % record.booking_code),
            subject=_('Booking Created'),
            message_type='notification'
        )
        _logger.info('Created new booking with ID: %s and booking code: %s', record.id, record.booking_code)
        return record

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

    @api.depends('room_id.price', 'check_in_date', 'check_out_date', 'service_line_ids.total_cost')
    def _compute_total_amount(self):
        for record in self:
            total_service_cost = sum(service.total_cost for service in record.service_line_ids)
            room_cost = 0
            if record.check_in_date and record.check_out_date and record.room_id:
                duration = (record.check_out_date - record.check_in_date).days
                room_cost = duration * record.room_id.price

            record.total_amount = room_cost + total_service_cost
            _logger.debug(
                'Computed total amount for booking %s: Room Cost = %s, Service Cost = %s, Total = %s',
                record.id, room_cost, total_service_cost, record.total_amount
            )
            
    def action_checkin(self):
        for record in self:
            if record.status != 'reserved':
                raise ValidationError("Only reservations with status 'Reserved' can be checked in.")
            record.status = 'checkin'
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Successfully Checked In',
                    'type': 'rainbow_man',
                    }
                }

    def action_checkout(self):
        for record in self:
            if record.status != 'checkin':
                raise ValidationError("Only reservations with status 'Checkin' can be checked out.")
            record.status = 'checkout'
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Successfully Checked Out',
                    'type': 'rainbow_man',
                    }
                }

    def action_done(self):
        for record in self:
            if record.status == 'checkout':
                record.status = 'done'
                record.room_id.status = 'available'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Task completed successfully',
                        'type': 'rainbow_man',
                    }
                }
            else:
                raise ValidationError("Cannot be done")

    def action_cancel(self):
        for record in self:
            if record.status != 'cancelled':
                record.status = 'cancelled'
                record.room_id.status = 'available'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Successfully Cancelled',
                        'type': 'rainbow_man',
                    }
                }
            else:
                raise ValidationError("Cannot be cancelled")