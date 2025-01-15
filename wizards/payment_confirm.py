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

    def action_open_payment_wizard(self):
        return {
            'name': _('Confirm Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_booking_id': self.id,
                'default_hotel_id': self.hotel_id.id,
                'default_room_id': self.room_id.id,
                'default_payment_amount': self.total_amount,
            },
        }

class HotelPaymentWizard(models.TransientModel):
    _name = 'hotel.payment.wizard'
    _description = 'Wizard Thanh Toán'

    booking_id = fields.Many2one('hotel.customer', string='Booking', required=True, readonly=True)
    hotel_id = fields.Many2one('hotel.hotel', string='Hotel', readonly=True)
    room_id = fields.Many2one('hotel.room', string='Room', readonly=True)
    payment_amount = fields.Float(string='Total Payment Amount', required=True)

    @api.constrains('payment_amount')
    def _check_payment_amount(self):
        for record in self:
            if record.payment_amount <= 0:
                raise exceptions.ValidationError(_('Payment amount must be greater than 0.'))

    def action_confirm_payment(self):
        booking = self.booking_id
        if booking.status not in ['new', 'reserved']:
            raise exceptions.ValidationError(_('Payment can only be made for bookings in "New" or "Reserved" status.'))

        # Update payment information and change booking status to "reserved"
        booking.write({
            'payment_status': 'paid',
            'payment_date': datetime.now(),
            'payment_amount': self.payment_amount,
            'status': 'reserved',
        })

        if booking.room_id:
            booking.room_id.write({'status': 'reserved'})

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Order successfully Paid and status updated to Reserved',
                'type': 'rainbow_man',
            },
            'type': 'ir.actions.act_window_close'
        }
