from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
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

    @api.constrains('quantity')
    def _check_quantity_on_hand(self):
        for record in self:
            if record.product_id.qty_available < record.quantity:
                raise ValidationError(
                    _('Not enough quantity for product "%s". Available: %s, Requested: %s.') % 
                    (record.product_id.name, record.product_id.qty_available, record.quantity)
                )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        product = record.product_id
        if product.type == 'product':
            if product.qty_available < record.quantity:
                raise ValidationError(
                    _('Not enough quantity for product "%s". Available: %s, Requested: %s.') % 
                    (product.name, product.qty_available, record.quantity)
                )
            # Adjust stock using stock.quant
            stock_quant = self.env['stock.quant'].search([('product_id', '=', product.id)], limit=1)
            if stock_quant:
                stock_quant.sudo().quantity -= record.quantity
                _logger.info("Reduced stock for product %s by %s. New quantity: %s", 
                             product.name, record.quantity, stock_quant.quantity)
        return record

    def unlink(self):
        for record in self:
            product = record.product_id
            if product.type == 'product':
                # Revert the stock on hand when the service line is deleted
                stock_quant = self.env['stock.quant'].search([('product_id', '=', product.id)], limit=1)
                if stock_quant:
                    stock_quant.sudo().quantity += record.quantity
                    _logger.info("Reverted stock for product %s by %s. New quantity: %s", 
                                 product.name, record.quantity, stock_quant.quantity)
        return super().unlink()
