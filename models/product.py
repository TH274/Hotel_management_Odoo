from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    name = fields.Char(default="New Service", required=True) 
    
    service_type = fields.Selection([
        ('room_service', 'Room Service'),
        ('laundry', 'Laundry'),
        ('spa', 'Spa'),
        ('transport', 'Transport'),
    ], string="Service Type", help="Type of service provided.")

    customer_id = fields.Many2one('hotel.customer', string="Customer", help="Customer availing the service.")
    product_id = fields.Many2one('product.product', string="Product", help="Reference to the product.")
    description = fields.Text(string="Service Description")
    duration = fields.Float(string="Duration (hours)", help="Duration of the service in hours.")
    available = fields.Boolean(string="Available", default=True)
    price_unit = fields.Float(string="Price Unit", help="Cost per unit of duration.")
    room_id = fields.Many2one('hotel.room', string="Room", help="Room associated with the service.")
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True)

    @api.depends('duration', 'price_unit')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = record.duration * record.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                record.description = record.product_id.description_sale or record.product_id.name
                record.price_unit = record.product_id.list_price
            else:
                record.description = ''
                record.price_unit = 0.0
