import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class HotelRoom(models.Model):
    _name = 'hotel.room'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Room'
    _rec_name = 'room_number' 

    reference = fields.Char(string='Hotel Code', default=lambda self: _('New'))
    room_number = fields.Integer(string='Room Number', required=True, tracking=True)
    room_type = fields.Selection(
        [('single', 'Single'), ('double', 'Double')],
        string='Room Type', required=True, tracking=True
    )
    hotel_id = fields.Many2one('hotel.hotel', string='Hotel', required=True, tracking=True)
    hotel_location = fields.Char(string='Hotel Location', related='hotel_id.address', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    capacity = fields.Integer(string='Capacity', required=True, default=1, tracking=True)
    tag_ids = fields.Many2many('room.tag', string='Features')
    price = fields.Float(string='Price per Night', required=True, tracking=True)
    status = fields.Selection(
        [('available', 'Available'), ('reserved', 'Reserved')],
        string='Status', default='available', tracking=True
    )
    notes = fields.Text(string='Notes', tracking=True)
    reservation_ids = fields.One2many('hotel.customer', 'room_id', string='Reservations')

    @api.model
    def create(self, vals):
        _logger.debug('Creating a new hotel room with values: %s', vals)
        if not vals.get('reference') or vals['reference'] == 'New':
            hotel_ref = self.env['hotel.hotel'].browse(vals.get('hotel_id')).reference or self.env['ir.sequence'].next_by_code('hotel.room')
            room_number = vals.get('room_number', _('NewRoom'))
            vals['reference'] = "{}-{}".format(hotel_ref, room_number)
        record = super().create(vals)
        _logger.info('Created new hotel room with ID: %s and reference: %s', record.id, record.reference)
        return record

    @api.onchange('room_type')
    def _onchange_room_type(self):
        _logger.debug('Room type changed to: %s', self.room_type)
        if self.room_type == 'single':
            self.capacity = 1
        elif self.room_type == 'double':
            self.capacity = 2
        else:
            self.capacity = 1
        _logger.debug('Room capacity set to: %s', self.capacity)

    def action_available(self):
        _logger.info('Setting room %s to available', self.id)
        self.write({'status': 'available'})

    def action_reserved(self):
        _logger.info('Setting room %s to reserved', self.id)
        self.write({'status': 'reserved'})

    @api.constrains('room_number')
    def _check_room_number(self):
        for record in self:
            if record.room_number <= 0:
                _logger.error('Invalid room number: %s', record.room_number)
                raise ValidationError(_('The room number must be greater than zero.'))

    @api.constrains('price')
    def _check_price(self):
        for record in self:
            if record.price <= 0:
                _logger.error('Invalid price: %s', record.price)
                raise ValidationError(_('The price per night must be greater than zero.'))

    @api.constrains('capacity')
    def _check_capacity(self):
        for record in self:
            if record.capacity <= 0:
                _logger.error('Invalid capacity: %s', record.capacity)
                raise ValidationError(_('The capacity must be greater than zero.'))

    def name_get(self):
        result = []
        for record in self:
            name = record.room_number or _('Unnamed Room')
            result.append((record.id, name))
            _logger.info(f"Name Get Called for Room: {name}")
        return result