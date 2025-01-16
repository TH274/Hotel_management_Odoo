from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    name = fields.Char(default="New Service", required=True) 
    service_type = fields.Selection([
        ('manual', 'Manual'),
    ], string="Service Type", default='manual', required=True)
    customer_id = fields.Many2one('hotel.customer', string="Customer", help="Customer availing the service.")
    product_id = fields.Many2one('product.product', string="Product", help="Reference to the product.")
    description = fields.Text(string="Service Description")
    duration = fields.Float(string="Duration (hours)", help="Duration of the service in hours.")
    available = fields.Boolean(string="Available", default=True)
    price_unit = fields.Float(string="Price Unit", help="Cost per unit of duration.")
    room_id = fields.Many2one('hotel.room', string="Room", help="Room associated with the service.")
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True)
    hotel_room_id = fields.Many2one('hotel.room', string='Hotel Room', readonly=True, help='Related hotel room for this product.')

    @api.depends('duration', 'price_unit')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = record.duration * record.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
                record.description = record.product_id.description_sale or record.product_id.name
                record.price_unit = record.product_id.list_price
