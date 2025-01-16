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

        if not booking.room_id:
            raise exceptions.ValidationError(_('Room information is missing for the booking.'))

        check_in_date = fields.Date.from_string(self.booking_id.check_in_date)
        check_out_date = fields.Date.from_string(self.booking_id.check_out_date)
        duration_days = (check_out_date - check_in_date).days

        # Ensure a product template exists for the room
        product_template = booking.room_id.product_template_id
        if not product_template or not product_template.exists():
            # Create a new product template for the room
            product_template = self.env['product.template'].create({
                'name': f'Room {booking.room_id.room_number} - {booking.hotel_id.name}',
                'type': 'service',
                'list_price': booking.room_id.price,
                'default_code': booking.room_id.room_number,
                'description': _('Product created for room: %s' % booking.room_id.room_number),
                'customer_id': booking.id,
            })
            # Link the newly created product template to the room
            booking.room_id.write({'product_template_id': product_template.id})

        if not product_template.exists():
            raise exceptions.ValidationError(_('The product associated with this room does not exist or has been deleted.'))

        # Update payment information and booking status
        booking.write({
            'payment_status': 'paid',
            'payment_date': datetime.now(),
            'payment_amount': self.payment_amount,
            'status': 'reserved',
        })

        # Update room status
        booking.room_id.write({'status': 'reserved'})

        # Create a quotation in Sale module
        sale_order = self.env['sale.order'].create({
            'partner_id': booking.create_uid.partner_id.id,
            'origin': booking.booking_code,
            'order_line': [(0, 0, {
                'product_id': product_template.product_variant_id.id,
                'product_uom_qty': duration_days,
                'price_unit': product_template.list_price,
                'name': product_template.name,
            })],
        })

        # Log the action
        booking.message_post(
            body=_('Quotation created/updated in Sales module with ID: %s' % sale_order.id),
            subject=_('Quotation Processed'),
            message_type='notification'
        )

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Payment successfully processed, product created, and quotation updated.',
                'type': 'rainbow_man',
            },
            'type': 'ir.actions.act_window_close'
        }

