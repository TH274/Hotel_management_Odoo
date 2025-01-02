from odoo import api, models, fields

class HotelCustomer(models.Model):
    _name = 'hotel.customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Customer'

    name = fields.Char(string='Name', required=True, tracking=True)
    email = fields.Char(string='Email', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    address = fields.Text(string='Address', tracking=True)
    check_in_date = fields.Datetime(string='Check-In Date', tracking=True)
    check_out_date = fields.Datetime(string='Check-Out Date', tracking=True)
    room_id = fields.Many2one('hotel.room', string='Room', tracking=True)
    tag_ids = fields.Many2many('customer.tag', 'customer_tag_rel','customer_id','tag_id', string='Tags', tracking=True)
