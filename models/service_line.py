from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class HotelServiceLine(models.Model):
    _name = 'hotel.service.line'
    _description = 'Service Line for Hotel Customers'

    customer_id = fields.Many2one('hotel.customer', string="Customer", required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product',
        string="Service Product",
        domain="[('detailed_type', '=', 'product')]",
        required=True,
        help="Select an existing service product."
    )
    description = fields.Text(string="Description")
    quantity = fields.Float(string="Quantity", default=1.0, required=True)
    price_unit = fields.Float(string="Price Unit", required=True)
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.description = line.product_id.description_sale or line.product_id.name
                line.price_unit = line.product_id.lst_price
