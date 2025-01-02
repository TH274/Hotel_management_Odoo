from odoo import models, fields, api, exceptions, _
from datetime import timedelta


class HotelService(models.Model):
    _name = 'hotel.service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Service'

    name = fields.Char(string='Service Name', required=True)
    service_type = fields.Selection([
        ('room_service', 'Room Service'),
        ('laundry', 'Laundry'),
        ('spa', 'Spa & Wellness'),
        ('transportation', 'Transportation'),
        ('restaurant', 'Restaurant'),
        ('fitness', 'Fitness Center'),
        ('parking', 'Parking'),
        ('mini_bar', 'Mini Bar'),
        ('event_booking', 'Event Booking'),
        ('other', 'Other'),
    ], string='Service Type', required=True, default='other', tracking=True)
    description = fields.Text(string='Service Description', tracking=True)
    price = fields.Float(string='Service Price', required=True, tracking=True)
    duration = fields.Float(string='Service Duration (in hours)', help="Duration in hours for services like Spa, Room Service, etc.", tracking=True)
    available = fields.Boolean(string='Available', default=True, tracking=True)
    room_id = fields.Many2one('hotel.room', string='Room', ondelete='set null', help="Room where the service is requested", tracking=True)

    reservation_id = fields.Many2one('hotel.reservation', string='Reservation', help="Link to the Reservation if service is associated with a specific booking", tracking=True)
    customer_id = fields.Many2one('hotel.customer', string='Customer', help="Customer requesting the service", tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('room_id'):
            room = self.env['hotel.room'].browse(vals['room_id'])
            vals['reservation_id'] = room.reservation_ids.filtered(lambda r: r.state == 'confirmed').id
        return super(HotelService, self).create(vals)

    @api.depends('price', 'duration')
    def _compute_total_cost(self):
        for service in self:
            service.total_cost = service.price * service.duration 

    total_cost = fields.Float(string="Total Cost", compute='_compute_total_cost', store=True)

    def book_service(self):
        if not self.room_id:
            raise ValueError("The service must be associated with a room.")
        if not self.customer_id:
            raise ValueError("The service must be associated with a customer.")

        if not self.reservation_id:
            reservation = self.env['hotel.reservation'].search([
                ('room_id', '=', self.room_id.id),
                ('state', '=', 'confirmed')
            ], limit=1)
            if reservation:
                self.reservation_id = reservation.id

        self.write({
            'available': False,
            'message': "Service has been successfully booked."
        })
        self.message_post(
            body="Service has been booked for customer: %s" % self.customer_id.name,
            subtype='mail.mt_comment'
        )

    def mark_as_completed(self):
        if self.available:
            raise ValueError("The service is already completed or unavailable.")

        self.write({'available': False})

        if self.reservation_id:
            self._add_service_cost_to_invoice()

        self.message_post(
            body="Service '%s' has been completed." % self.name,
            subtype='mail.mt_comment'
        )

    def _add_service_cost_to_invoice(self):
        if not self.reservation_id:
            raise ValueError("No reservation found to add the service cost.")

        invoice = self.reservation_id.invoice_ids.filtered(lambda i: i.state == 'draft')
        if not invoice:
            invoice = self.env['account.move'].create({
                'partner_id': self.customer_id.partner_id.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
            })

        self.env['account.move.line'].create({
            'move_id': invoice.id,
            'product_id': self.env['product.product'].search([('name', '=', self.name)], limit=1).id,
            'quantity': 1,
            'price_unit': self.total_cost,
            'name': self.name,
        })
        
        invoice.action_post()

    def cancel_service(self):
        if self.available:
            raise ValueError("The service is already available or not booked.")

        self.write({'available': True})

        if self.reservation_id:
            self._remove_service_cost_from_invoice()

        self.message_post(
            body="Service '%s' has been canceled." % self.name,
            subtype='mail.mt_comment'
        )

    def _remove_service_cost_from_invoice(self):
        if not self.reservation_id:
            raise ValueError("No reservation found to remove the service cost.")

        invoice = self.reservation_id.invoice_ids.filtered(lambda i: i.state == 'draft')
        if invoice:
            service_line = invoice.line_ids.filtered(lambda line: line.name == self.name)
            if service_line:
                service_line.unlink()
            invoice.action_cancel()