from datetime import datetime, timedelta
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class HotelRoom(models.Model):
    _inherit = 'hotel.room'

    last_reserved_date = fields.Date(string='Last Reserved Date', tracking=True)

    @api.model
    def check_and_notify_unrented_rooms(self):
        """
        Scheduled job to check for rooms not rented for one week
        and notify or reduce prices accordingly.
        """
        _logger.info("Running job to check unrented rooms for the last 7 days.")
        seven_days_ago = fields.Date.today() - timedelta(days=7)
        _logger.debug(f"Date to check against: {seven_days_ago}")

        # Find rooms that haven't been rented in the last week
        unrented_rooms = self.search([
            ('last_reserved_date', '<=', seven_days_ago),
            ('status', '=', 'available')
        ])
        _logger.debug(f"Unrented Rooms Found: {[room.id for room in unrented_rooms]}")


        for room in unrented_rooms:
            # Log the rooms for monitoring
            _logger.warning(f"Room {room.room_number} in {room.hotel_id.name} "
                            f"has not been rented since {room.last_reserved_date}.")

            # Optional: Reduce the price by 10% if needed
            old_price = room.price
            room.price *= 0.9
            _logger.info(f"Reduced price of room {room.room_number} from {old_price} to {room.price}.")

            # Notify the hotel manager (or take other actions as required)
            room.message_post(
                body=_(
                    f"Room {room.room_number} has not been rented for over a week. "
                    f"The price has been reduced from {old_price} to {room.price}."
                ),
                subject=_("Room Rental Notification")
            )

    @api.model
    def update_last_reserved_date(self, room_id):
        """
        Helper function to update the last reserved date of a room.
        Should be called during a reservation.
        """
        room = self.browse(room_id)
        room.last_reserved_date = fields.Date.today()
        _logger.info(f"Updated last reserved date for room {room.room_number} to {fields.Date.today()}.")




