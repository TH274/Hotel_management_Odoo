from odoo import models, fields

class CustomerTag(models.Model):
    _name = 'customer.tag'
    _description = 'Customer Tag'
    _order = 'sequence'

    name = fields.Char(string='Tag Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    color = fields.Integer(string='Color Index', default=0)

class RoomTag(models.Model):
    _name = 'room.tag'
    _description = 'Room Tag'

    name = fields.Char(string='Tag Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    color = fields.Integer(string='Color Index', default=0)