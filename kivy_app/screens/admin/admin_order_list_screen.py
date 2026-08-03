"""
Admin screen for viewing all orders and updating their status.
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, ThreeLineListItem
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from kivy_app.services.order_service import get_all_orders_admin, update_order_status_admin

# Mirrors app.models.order.OrderStatus values.
ORDER_STATUSES = ["All", "Pending", "Preparing", "Out for Delivery", "Delivered", "Cancelled"]


class AdminOrderListScreen(Screen):
    """Admin screen listing all orders with status-change actions."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orders = []
        self._active_status = None
        self._status_dialog = None
        self._status_buttons = {}
        self.build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def build_ui(self):
        """Build the admin order list UI."""
        root = MDBoxLayout(orientation="vertical", padding="10dp", spacing="8dp")

        header = MDBoxLayout(size_hint_y=None, height="56dp", spacing="8dp")
        back_btn = MDIconButton(icon="arrow-left", on_release=self.go_back)
        header.add_widget(back_btn)
        title = MDLabel(text="Manage Orders", theme_text_color="Primary", font_style="H5")
        header.add_widget(title)
        refresh_btn = MDIconButton(icon="refresh", on_release=lambda *a: self.load_orders())
        header.add_widget(refresh_btn)
        root.add_widget(header)

        # ---- Status filter row ----
        filter_scroll = MDScrollView(size_hint_y=None, height="48dp", do_scroll_y=False)
        filter_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            spacing="6dp",
            padding=("4dp", "4dp"),
        )
        filter_row.bind(minimum_width=filter_row.setter("width"))
        self._filter_buttons = {}
        for status in ORDER_STATUSES:
            btn = MDFlatButton(
                text=status,
                size_hint_x=None,
                width="130dp",
                on_release=lambda b, s=status: self._filter_by_status(s),
            )
            filter_row.add_widget(btn)
            self._filter_buttons[status] = btn
        filter_scroll.add_widget(filter_row)
        root.add_widget(filter_scroll)

        self.status_label = MDLabel(
            text="",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp",
        )
        root.add_widget(self.status_label)

        self.orders_list = MDList()
        scroll = MDScrollView()
        scroll.add_widget(self.orders_list)
        root.add_widget(scroll)

        self.add_widget(root)

    # ------------------------------------------------------------------
    # Screen lifecycle
    # ------------------------------------------------------------------

    def on_enter(self):
        """Called when entering the screen."""
        self.load_orders()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load_orders(self):
        """Load all orders, optionally filtered by status."""
        self.status_label.text = "Loading…"
        self.orders_list.clear_widgets()
        try:
            self.orders = get_all_orders_admin(status=self._active_status)
            self.status_label.text = ""
            self._display_orders()
        except Exception as e:
            self.status_label.text = "Failed to load orders."
            toast(f"Error: {str(e)}")

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def _display_orders(self):
        """Render the order list, most recent first."""
        self.orders_list.clear_widgets()
        if not self.orders:
            self.orders_list.add_widget(MDLabel(text="No orders found.", halign="center"))
            return

        orders_sorted = sorted(self.orders, key=lambda o: o.get("created_at", ""), reverse=True)
        for order in orders_sorted:
            self._add_order_row(order)

    def _add_order_row(self, order: dict):
        """Add a single order row with a tap-to-change-status action."""
        short_id = str(order.get("id", ""))[:8]
        short_user = str(order.get("user_id", ""))[:8]
        created_at = str(order.get("created_at", ""))[:16].replace("T", " ")
        total = float(order.get("total_price", 0))

        item = ThreeLineListItem(
            text=f"Order #{short_id}  (user {short_user})",
            secondary_text=f"Placed: {created_at}  •  ${total:.2f}",
            tertiary_text=f"Status: {order.get('order_status', '')}  •  Payment: {order.get('payment_status', '')}",
            on_release=lambda x, o=order: self._open_status_dialog(o),
        )
        self.orders_list.add_widget(item)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _filter_by_status(self, status: str):
        """Filter the order list by status."""
        self._active_status = None if status == "All" else status
        for s, btn in self._filter_buttons.items():
            btn.md_bg_color = self.theme_cls.primary_color if s == status else (0, 0, 0, 0)
        self.load_orders()

    def _open_status_dialog(self, order: dict):
        """Open a dialog to change this order's status."""
        if self._status_dialog:
            self._status_dialog.dismiss()

        buttons = [
            MDFlatButton(
                text=status,
                on_release=lambda b, s=status: self._change_status(order, s),
            )
            for status in ORDER_STATUSES[1:]  # skip "All"
        ]
        buttons.append(MDFlatButton(text="CANCEL", on_release=lambda b: self._status_dialog.dismiss()))

        self._status_dialog = MDDialog(
            title=f"Update Order #{str(order.get('id', ''))[:8]}",
            text="Select the new order status:",
            buttons=buttons,
        )
        self._status_dialog.open()

    def _change_status(self, order: dict, new_status: str):
        """Apply a status change to an order."""
        if self._status_dialog:
            self._status_dialog.dismiss()
        try:
            update_order_status_admin(order["id"], new_status)
            toast(f"Order updated to {new_status}")
            self.load_orders()
        except Exception as e:
            toast(f"Failed to update order: {str(e)}")

    def go_back(self, *args):
        """Navigate back to home."""
        self.manager.current = "home"
