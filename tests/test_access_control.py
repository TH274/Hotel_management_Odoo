from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError

class TestHotelManagementAccessControl(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestHotelManagementAccessControl, cls).setUpClass()

        # Create users
        cls.employee_user = cls.env['res.users'].create({
            'name': 'Employee User',
            'login': 'employee_user',
            'groups_id': [(6, 0, [cls.env.ref('hotel_management.group_hotel_employee').id])]
        })
        cls.manager_user = cls.env['res.users'].create({
            'name': 'Manager User',
            'login': 'manager_user',
            'groups_id': [(6, 0, [cls.env.ref('hotel_management.group_hotel_manager').id])]
        })
        cls.admin_user = cls.env['res.users'].create({
            'name': 'Admin User',
            'login': 'admin_user',
            'groups_id': [(6, 0, [cls.env.ref('hotel_management.group_hotel_admin').id])]
        })

        # Create hotel and customer records
        cls.hotel = cls.env['hotel.hotel'].create({
            'name': 'Test Hotel',
            'reference': 'TH001',
            'num_floors': 5,
        })
        cls.hotel_customer = cls.env['hotel.customer'].create({
            'name': 'John Doe',
            'hotel_id': cls.hotel.id,
            'room_id': cls.env['hotel.room'].create({
                'room_number': 101,
                'room_type': 'single',
                'hotel_id': cls.hotel.id,
                'price': 100.0,
            }).id,
            'check_in_date': '2025-01-01',
            'check_out_date': '2025-01-05',
        })

    def test_employee_access(self):
        """Test that an employee can create and read their own records."""
        employee_env = self.env['hotel.customer'].with_user(self.employee_user)

        # Employee creates their own record
        employee_customer = employee_env.create({
            'name': 'Jane Doe',
            'hotel_id': self.hotel.id,
            'room_id': self.env['hotel.room'].create({
                'room_number': 102,
                'room_type': 'single',
                'hotel_id': self.hotel.id,
                'price': 100.0,
            }).id,
            'check_in_date': '2025-01-01',
            'check_out_date': '2025-01-05',
        })
        self.assertTrue(employee_env.browse(employee_customer.id).read())

    def test_manager_access(self):
        """Test that a manager can access records for hotels they manage."""
        manager_env = self.env['hotel.customer'].with_user(self.manager_user)

        # Assign the manager to the hotel and verify access
        self.hotel.manager_id = self.manager_user.id
        self.assertTrue(manager_env.browse(self.hotel_customer.id).read())

    def test_admin_access(self):
        """Test that an admin can access all records."""
        admin_env = self.env['hotel.customer'].with_user(self.admin_user)

        # Admin should have unrestricted access
        self.assertTrue(admin_env.browse(self.hotel_customer.id).read())

    def test_unauthorized_user_access(self):
        """Test that an unauthorized user cannot access any records."""
        unauthorized_user = self.env['res.users'].create({
            'name': 'Unauthorized User',
            'login': 'unauthorized_user',
        })
        unauthorized_env = self.env['hotel.customer'].with_user(unauthorized_user)

        # Unauthorized read attempt
        with self.assertRaises(AccessError):
            unauthorized_env.browse(self.hotel_customer.id).read()

        # Unauthorized create attempt
        with self.assertRaises(AccessError):
            unauthorized_env.create({
                'name': 'Unauthorized Booking',
                'hotel_id': self.hotel.id,
                'room_id': self.env['hotel.room'].create({
                    'room_number': 103,
                    'room_type': 'single',
                    'hotel_id': self.hotel.id,
                    'price': 100.0,
                }).id,
                'check_in_date': '2025-01-01',
                'check_out_date': '2025-01-05',
            })