from odoo import models, fields, api, exceptions, _
from datetime import datetime

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
    _description = 'Payment Wizard'

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

        product = self.env['product.product'].search([
            ('default_code', '=', f'ROOM-{booking.room_id.room_number}'),
            ('detailed_type', '=', 'service')
        ], limit=1)

        if not product:
            product = self.env['product.product'].create({
                'name': f'Room {booking.room_id.room_number} - {booking.hotel_id.name}',
                'default_code': f'ROOM-{booking.room_id.room_number}',
                'detailed_type': 'service',
                'list_price': booking.room_id.price,
            })

        # Calculate duration
        check_in_date = fields.Date.from_string(booking.check_in_date)
        check_out_date = fields.Date.from_string(booking.check_out_date)
        duration_days = (check_out_date - check_in_date).days

        # Create sale order
        sale_order = self.env['sale.order'].create({
            'partner_id': booking.partner_id.id,
            'origin': booking.booking_code,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': duration_days,
                'price_unit': product.list_price,
                'name': f"Room {booking.room_id.room_number} ({duration_days} nights)",
            })]
        })

        # Update booking status
        booking.write({
            'payment_status': 'paid',
            'payment_date': datetime.now(),
            'payment_amount': self.payment_amount,
            'status': 'occupied',
        })

        # Add services to sale order
        for service in booking.service_line_ids:
            sale_order.write({
                'order_line': [(0, 0, {
                    'product_id': service.product_id.id,
                    'product_uom_qty': service.quantity,
                    'price_unit': service.product_id.list_price,
                    'name': service.product_id.name,
                })]
            })

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Payment processed and quotation created successfully!',
                'type': 'rainbow_man',
            },
            'type': 'ir.actions.act_window_close'
        }