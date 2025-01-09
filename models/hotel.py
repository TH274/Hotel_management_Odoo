import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class HotelHotel(models.Model):
    _name = 'hotel.hotel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Management'
    _rec_name = 'name'

    reference = fields.Char(string='Hotel Code', default=lambda self: _('New'))
    name = fields.Char(string='Hotel Name', required=True, tracking=True)
    address = fields.Char(string='Hotel Address', tracking=True)
    num_floors = fields.Integer(string='Number of Floors', tracking=True)
    room_ids = fields.One2many('hotel.room', 'hotel_id', string='Rooms', tracking=True)
    num_rooms = fields.Integer(string='Number of Rooms', compute='_compute_num_rooms', store=True, tracking=True)
    manager_id = fields.Many2one('hr.employee', string='Hotel Manager', tracking=True)
    employee_ids = fields.Many2many('hr.employee', 'hotel_id', string='Employees', tracking=True)
    room_date = fields.Date(string='Booking Date', default=fields.Date.today, readonly=True, tracking=True)



    @api.model
    def create(self, vals):
        _logger.debug('Creating a new hotel with values: %s', vals)
        if not vals.get('reference') or vals['reference'] == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code('hotel.room') or _('New')
        record = super().create(vals)
        _logger.info('Created new hotel with ID: %s and reference: %s', record.id, record.reference)
        return record

    @api.depends('room_ids')
    def _compute_num_rooms(self):
        for hotel in self:
            hotel.num_rooms = len(hotel.room_ids)
        _logger.debug('Computed number of rooms for hotel %s: %s', hotel.id, hotel.num_rooms)

    @api.constrains('num_floors')
    def _check_num_floors(self):
        for hotel in self:
            if hotel.num_floors <= 0:
                _logger.error('Invalid number of floors for hotel %s: %s', hotel.id, hotel.num_floors)
                raise ValidationError(_('The number of floors must be greater than zero.'))

    @api.constrains('name')
    def _check_name(self):
        for hotel in self:
            if len(hotel.name) < 3:
                _logger.error('Invalid hotel name for hotel %s: %s', hotel.id, hotel.name)
                raise ValidationError(_('The hotel name must be at least 3 characters long.'))