from odoo import models, fields, api, exceptions, _

class HotelHotel(models.Model):
    _name = 'hotel.hotel'
    _description = 'Hotel Management'
    _rec_name = 'name'

    reference = fields.Char(string='Hotel Code', default=lambda self: _('New'))  
    name = fields.Char(string='Hotel Name', required=True)
    address = fields.Char(string='Hotel Address')  
    num_floors = fields.Integer(string='Number of Floors')  
    room_ids = fields.One2many('hotel.room', 'hotel_id', string='Rooms')
    num_rooms = fields.Integer(string='Number of Rooms', compute='_compute_num_rooms', store=True)

    @api.model
    def create(self, vals):
        if not vals.get('reference') or vals['reference'] == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code('hotel.room') or _('New')

        if vals.get('room_number'):
            vals['reference'] = "{}-{}".format(vals['reference'], vals['room_number'])

        return super().create(vals)

    @api.depends('room_ids')
    def _compute_num_rooms(self):
        for hotel in self:
            hotel.num_rooms = len(hotel.room_ids)
