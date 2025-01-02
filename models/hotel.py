from odoo import models, fields, api, exceptions

class Hotel(models.Model):
    _name = 'hotel.hotel'
    _description = 'Hotel'

    name = fields.Char(string='Hotel Name', required=True, tracking=True)
    address = fields.Char(string='Address', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    website = fields.Char(string='Website', tracking=True)
    # You can add more fields as needed

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            raise exceptions.ValidationError("Hotel Name is required.")
        return super(Hotel, self).create(vals)
