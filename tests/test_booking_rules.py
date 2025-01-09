from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError

@tagged('hotel_management', 'security')  # Tags for organizing and filtering tests
class TestBookingRules(TransactionCase):
    def setUp(self):
        super(TestBookingRules, self).setUp()
        # Create test users with specific groups
        self.employee_user = self.env['res.users'].create({
            'name': 'Employee User',
            'login': 'employee_user',
            'groups_id': [(6, 0, [self.ref('hotel_management.group_hotel_employee')])],
        })

        self.manager_user = self.env['res.users'].create({
            'name': 'Manager User',
            'login': 'manager_user',
            'groups_id': [(6, 0, [self.ref('hotel_management.group_hotel_manager')])],
        })

        # Create a sample record
        self.booking = self.env['hotel.customer'].create({
            'name': 'John Doe',
            'hotel_id': self.env.ref('hotel_management.hotel_1').id,
        })

    def test_employee_access(self):
        # Test if employee can access only their own records
        with self.assertRaises(AccessError):
            self.booking.with_user(self.employee_user).read()

    def test_manager_access(self):
        # Test if manager can access bookings in their assigned hotel
        booking = self.booking.with_user(self.manager_user)
        self.assertTrue(booking)

    def test_admin_access(self):
        # Admins should have full access
        admin_user = self.env.ref('base.user_admin')
        booking = self.booking.with_user(admin_user)
        self.assertTrue(booking)
