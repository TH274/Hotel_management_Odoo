from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_type = fields.Selection([
        ('room_service', 'Room Service'),
        ('laundry', 'Laundry'),
        ('spa', 'Spa'),
        ('transport', 'Transport'),
    ], string="Service Type", help="Type of service provided.")
    
    description = fields.Text(string="Service Description")
    duration = fields.Float(string="Duration (hours)", help="Duration of the service in hours.")
    available = fields.Boolean(string="Available", default=True)
    room_id = fields.Many2one('hotel.room', string="Room", help="Room associated with the service.")
    customer_id = fields.Many2one('res.partner', string="Customer", help="Customer availing the service.")
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True)

    @api.depends('duration', 'list_price')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = record.duration * record.list_price
