from odoo import models, fields, api, exceptions, _
from datetime import timedelta

class HotelRoom(models.Model):
    _name = 'hotel.room'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Room'

    reference = fields.Char(string='Reference', default=lambda self: _('New'))
    room_number = fields.Char(string='Room Number', required=True, tracking=True)
    room_type = fields.Selection(
        [('single', 'Single'), ('double', 'Double'), ('suite', 'Suite')],
        string='Room Type', required=True, tracking=True
    )
    hotel_id = fields.Many2one('hotel.hotel', string='Hotel', required=True, tracking=True)
    hotel_location = fields.Char(string='Hotel Location', related='hotel_id.address', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    capacity = fields.Integer(string='Capacity', required=True, default=1, tracking=True)
    price = fields.Float(string='Price per Night', required=True, tracking=True)
    status = fields.Selection(
        [('draft', 'Draft'), ('available', 'Available'), ('reserved', 'Reserved'), ('occupied', 'Occupied')],
        string='Status', default='available', tracking=True
    )
    notes = fields.Text(string='Notes', tracking=True)
    reservation_ids = fields.One2many('hotel.reservation', 'room_id', string='Reservations')

    @api.model
    def create(self, vals):
        if not vals.get('reference') or vals['reference'] == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code('hotel.room') or _('New')

        if vals.get('room_number'):
            vals['reference'] = "{}-{}".format(vals['reference'], vals['room_number'])

        return super().create(vals)

    @api.onchange('room_type')
    def _onchange_room_type(self):
        if self.room_type == 'single':
            self.capacity = 1
        elif self.room_type == 'double':
            self.capacity = 2
        elif self.room_type == 'suite':
            self.capacity = 0

    def action_available(self):
        self.write({'status': 'available'})

    def action_reserved(self):
        self.write({'status': 'reserved'})

    def action_occupied(self):
        self.write({'status': 'occupied'})
        

class HotelReservation(models.Model):
    _name = 'hotel.reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hotel Reservation'

    guest_name = fields.Char(string='Guest Name', compute='_compute_guest_name', store=True, tracking=True)
    customer_id = fields.Many2one('hotel.customer', string='Customer', required=True)
    room_id = fields.Many2one('hotel.room', string='Room', required=True, domain="[('status', '=', 'available')]", tracking=True)
    check_in_date = fields.Date(string='Check-in Date', required=True, tracking=True)
    check_out_date = fields.Date(string='Check-out Date', required=True, tracking=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True, tracking=True)

    @api.onchange('customer_id')
    def _onchange_customer(self):
        if self.customer_id:
            self.check_in_date = self.customer_id.check_in_date
            self.check_out_date = self.customer_id.check_out_date

    @api.depends('room_id', 'check_in_date', 'check_out_date')
    def _compute_total_amount(self):
        for record in self:
            if record.room_id and record.check_in_date and record.check_out_date:
                nights = (record.check_out_date - record.check_in_date).days
                record.total_amount = nights * record.room_id.price
    
    @api.depends('customer_id')
    def _compute_guest_name(self):
        for record in self:
            record.guest_name = record.customer_id.name if record.customer_id else ''


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

