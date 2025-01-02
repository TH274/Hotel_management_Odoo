from odoo import models, fields, api, exceptions, _
from datetime import timedelta

class HotelRoom(models.Model):
    _name = 'hotel.room'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Room'

    reference = fields.Char(string='Reference', default=lambda self: _('New'))
    room_number = fields.Char(string='Room Number', required=True, tracking=True)
    room_type = fields.Selection(
        [('single', 'Single'), ('double', 'Double'), ('suite', 'Suite')],
        string='Room Type', required=True, tracking=True
    )
    hotel_id = fields.Many2one('hotel.hotel', string='Hotel', required=True, tracking=True)
    hotel_location = fields.Char(string='Hotel Location', related='hotel_id.address', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    capacity = fields.Integer(string='Capacity', required=True, default=1, tracking=True)
    tag_ids = fields.Many2many('room.tag', string='Tags')
    price = fields.Float(string='Price per Night', required=True, tracking=True)
    status = fields.Selection(
        [('draft', 'Draft'), ('available', 'Available'), ('reserved', 'Reserved'), ('occupied', 'Occupied')],
        string='Status', default='available', tracking=True
    )
    notes = fields.Text(string='Notes', tracking=True)
    reservation_ids = fields.One2many('hotel.reservation', 'room_id', string='Reservations')

    @api.model
    def create(self, vals):
        if not vals.get('reference') or vals['reference'] == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code('hotel.room') or _('New')

        if vals.get('room_number'):
            vals['reference'] = "{}-{}".format(vals['reference'], vals['room_number'])

        return super().create(vals)

    @api.onchange('room_type')
    def _onchange_room_type(self):
        if self.room_type == 'single':
            self.capacity = 1
        elif self.room_type == 'double':
            self.capacity = 2
        elif self.room_type == 'suite':
            self.capacity = 0

    def action_available(self):
        self.write({'status': 'available'})

    def action_reserved(self):
        self.write({'status': 'reserved'})

    def action_occupied(self):
        self.write({'status': 'occupied'})
        