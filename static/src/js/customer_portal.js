/** @odoo-module **/

import { Component, useState } from '@odoo/owl';
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class CustomerPortal extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            availableRooms: [],
            selectedRoom: null,
            checkInDate: '',
            checkOutDate: '',
            selectedServices: [],
        });

        this.loadAvailableRooms();
    }

    async loadAvailableRooms() {
        this.state.availableRooms = await this.orm.call("hotel.room", "search_read", [
            [['status', '=', 'available']],
            ['room_number', 'room_type', 'price']
        ]);
    }

    async bookRoom() {
        if (!this.state.selectedRoom || !this.state.checkInDate || !this.state.checkOutDate) {
            this.notification.add("Please complete booking details", { type: "warning" });
            return;
        }

        const result = await this.orm.call("hotel.customer", "create", [{
            room_id: this.state.selectedRoom.id,
            check_in_date: this.state.checkInDate,
            check_out_date: this.state.checkOutDate,
        }]);

        this.notification.add("Booking confirmed!", { type: "success" });
    }

    selectRoom(room) {
        this.state.selectedRoom = room;
    }
}

CustomerPortal.template = "hotel_management.CustomerPortal";

registry.category("actions").add("customer_portal", CustomerPortal);
