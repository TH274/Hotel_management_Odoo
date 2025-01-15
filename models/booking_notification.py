from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime

import logging

_logger = logging.getLogger(__name__)

class HotelCustomerNotification(models.Model):
    _inherit = 'hotel.customer'

    @api.model
    def _send_checkin_notification(self):
        """
        Automatically checks in customers whose check-in date is today and status is reserved.
        """
        today = date.today()
        bookings_to_checkin = self.search([('check_in_date', '=', today), ('status', '=', 'reserved')])
        
        for booking in bookings_to_checkin:
            booking.status = 'checkin'
            booking.message_post(
                body=_("The customer has been automatically checked in."),
                subject=_("Check-In Notification"),
                message_type='notification',
                subtype='mail.mt_comment',
                partner_ids=[booking.hotel_id.partner_id.id]
            )
            _logger.info(f"Check-in notification sent for booking {booking.id}. Status updated to 'checkin'.")

    @api.model
    def _send_checkout_notification(self):
        """
        Automatically checks out customers whose check-out date is today and status is 'checkin'.
        """
        today = date.today()
        bookings_to_checkout = self.search([('check_out_date', '=', today), ('status', '=', 'checkin')])
        
        for booking in bookings_to_checkout:
            booking.status = 'checkout'
            booking.message_post(
                body=_("The customer has been automatically checked out."),
                subject=_("Check-Out Notification"),
                message_type='notification',
                subtype='mail.mt_comment',
                partner_ids=[booking.hotel_id.partner_id.id]
            )
            _logger.info(f"Check-out notification sent for booking {booking.id}. Status updated to 'checkout'.")
