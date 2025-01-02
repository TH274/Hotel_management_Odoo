from odoo import models, fields, api, _

class HotelSales(models.Model):
    _name = 'hotel.sales'
    _description = 'Hotel Sales'

    name = fields.Char(string='Sale Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    sale_date = fields.Date(string='Sale Date', default=fields.Date.context_today, required=True)
    amount_total = fields.Float(string='Total Amount', compute='_compute_amount_total', store=True)
    sale_line_ids = fields.One2many('hotel.sales.line', 'sale_id', string='Sale Lines')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hotel.sales') or _('New')
        return super(HotelSales, self).create(vals)

    @api.depends('sale_line_ids.price_subtotal')
    def _compute_amount_total(self):
        for sale in self:
            sale.amount_total = sum(line.price_subtotal for line in sale.sale_line_ids)

class HotelSalesLine(models.Model):
    _name = 'hotel.sales.line'
    _description = 'Hotel Sales Line'

    sale_id = fields.Many2one('hotel.sales', string='Sale Reference', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    price_unit = fields.Float(string='Unit Price', required=True)
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit