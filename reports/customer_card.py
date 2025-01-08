from odoo import models, fields, api

class CustomerCardReport(models.AbstractModel):
    _name = 'report.hotel_management.customer_card_report'
    _description = 'Customer Card Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['res.partner'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': docs,
            'data': data,
        }