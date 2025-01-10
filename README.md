# Hotel Management Odoo

This repository contains an Odoo module designed as an extension for the main [Hotel Management Odoo Module](https://github.com/TH274/Hotel_management_Odoo). This extension provides additional tools and features to enhance hotel operations.

## Features
- Hotel management
- Room management (availability, pricing, categories)
- Customer reservation and booking management
- Billing and invoicing (In development)
- Service tracking (In development)
- Reporting and analytics (In development)

## Requirements
- Odoo version 17
- Main Hotel Management Module: [Hotel Management Odoo Module](https://github.com/TH274/Hotel_management_Odoo)

## Installation
1. Ensure the main Hotel Management Module is installed:
   ```bash
   git clone https://github.com/TH274/Hotel_management_Odoo.git
   ```
   Follow its README instructions for installation.

2. This is the extension repository of module Hotel management:
   ```bash
   git clone https://github.com/TH274/Hotel-management-Extension.git
   ```
3. Restart the Odoo server to load the new module:
   ```bash
   ./odoo-bin odoo.conf --save
   ```
4. Log in to your Odoo instance and navigate to the Apps menu.
5. Search for "Hotel Management" and install the module.

## Configuration
1. After installation, go to the Hotel Management module in the Odoo interface.
2. Configure your hotel settings, such as room categories, pricing, and other preferences.

## Usage
- **Rooms:** Add and manage hotel rooms, including categories, pricing, and availability.
- **Reservations:** Manage customer bookings and check-in/check-out processes.
- **Billing:** Generate invoices and manage payment records.
- **Service:** Track room cleaning and maintenance tasks.
- **Reports:** View reports for occupancy, revenue, and other key metrics.

## Contributing
Contributions are welcome! Please follow these steps to contribute:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your message here"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Support
If you encounter any issues or have questions, please create an issue in the repository or contact the maintainer.

