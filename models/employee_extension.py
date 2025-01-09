from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        user = super(ResUsers, self).create(vals)
        self.env['hr.employee'].create({
            'name': user.name,
            'user_id': user.id,
            'work_email': user.email,
        })
        return user

        