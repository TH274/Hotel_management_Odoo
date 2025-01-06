from odoo import models, fields, api, _

class HotelRoom(models.Model):
    _name = 'hotel.room'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Room'

    reference = fields.Char(string='Hotel Code', default=lambda self: _('New'))
    room_number = fields.Char(string='Room Number', required=True, tracking=True)
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
        if not vals.get('reference') or vals['reference'] == 'New':
            hotel_ref = self.env['hotel.hotel'].browse(vals.get('hotel_id')).reference or self.env['ir.sequence'].next_by_code('hotel.room')
            room_number = vals.get('room_number', _('NewRoom'))
            vals['reference'] = "{}-{}".format(hotel_ref, room_number)

        return super().create(vals)

    @api.onchange('room_type')
    def _onchange_room_type(self):
        if self.room_type == 'single':
            self.capacity = 1
        elif self.room_type == 'double':
            self.capacity = 2

    def action_available(self):
        self.write({'status': 'available'})

    def action_reserved(self):
        self.write({'status': 'reserved'})

    def name_get(self):
        result = []
        for record in self:
            name = record.room_number or _('Unnamed Room')
            result.append((record.id, name))
        return result
