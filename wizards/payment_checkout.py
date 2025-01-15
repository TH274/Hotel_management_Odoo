from odoo import models, fields, api, exceptions, _
from datetime import date, datetime

class HotelCustomer(models.Model):
    _inherit = 'hotel.customer'

    payment_status = fields.Selection(
        [('unpaid', 'Unpaid'), ('paid', 'Paid')],
        string='Payment',
        default='unpaid',
        readonly=True,
        tracking=True,
    )
    payment_date = fields.Datetime(string='Payment Date', readonly=True)
    payment_amount = fields.Float(string='Total Payment Amount', readonly=True)
    
    def action_open_checkout_wizard(self):
        return {
            'name': _('Checkout'),
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.checkout.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_booking_id': self.id,
                'default_hotel_id': self.hotel_id.id,
                'default_room_id': self.room_id.id,
                'default_payment_amount': self.total_amount,
            },
        }
    
    class HotelCheckoutWizard(models.TransientModel):
        _name = 'hotel.checkout.wizard'
        _description = 'Hotel Checkout Wizard'

        booking_id = fields.Many2one('hotel.customer', string='Booking', required=True, readonly=True)
        hotel_id = fields.Many2one('hotel.hotel', string='Hotel', readonly=True)
        room_id = fields.Many2one('hotel.room', string='Room', readonly=True)
        payment_amount = fields.Float(string='Total Payment Amount', required=True)

        @api.constrains('payment_amount')
        def _check_payment_amount(self):
            for record in self:
                if record.payment_amount <= 0:
                    raise exceptions.ValidationError(_('Payment amount must be greater than 0.'))

        def action_confirm_checkout(self):
            booking = self.booking_id

            # Process checkout and mark payment as complete
            booking.write({
                'payment_status': 'paid',
                'payment_date': datetime.now(),
                'payment_amount': self.payment_amount,
                'status': 'done',
            })

            if booking.room_id:
                booking.room_id.write({'status': 'available'})

            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Payment successfully completed, and the booking is checked out.',
                    'type': 'rainbow_man',
                },
                'type': 'ir.actions.act_window_close'
            }
