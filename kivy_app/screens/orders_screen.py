"""
Order history screen - lists the current user's past and pending orders.
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, ThreeLineListItem
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from kivy_app.services.order_service import get_orders


class OrdersScreen(Screen):
    """Screen listing the current user's orders."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orders = []
        self.build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def build_ui(self):
        """Build the order history UI."""
        root = MDBoxLayout(orientation="vertical", padding="10dp", spacing="8dp")

        header = MDBoxLayout(size_hint_y=None, height="56dp", spacing="8dp")
        back_btn = MDIconButton(icon="arrow-left", on_release=self.go_back)
        header.add_widget(back_btn)
        title = MDLabel(text="My Orders", theme_text_color="Primary", font_style="H5")
        header.add_widget(title)
        refresh_btn = MDIconButton(icon="refresh", on_release=lambda *a: self.load_orders())
        header.add_widget(refresh_btn)
        root.add_widget(header)

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
        """Load the current user's orders."""
        self.status_label.text = "Loading…"
        self.orders_list.clear_widgets()
        try:
            self.orders = get_orders()
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
            self.orders_list.add_widget(
                MDLabel(text="You haven't placed any orders yet.", halign="center")
            )
            return

        orders_sorted = sorted(self.orders, key=lambda o: o.get("created_at", ""), reverse=True)
        for order in orders_sorted:
            self._add_order_row(order)

    def _add_order_row(self, order: dict):
        """Add a single order row summarizing status and total."""
        short_id = str(order.get("id", ""))[:8]
        created_at = str(order.get("created_at", ""))[:16].replace("T", " ")
        total = float(order.get("total_price", 0))

        item = ThreeLineListItem(
            text=f"Order #{short_id}",
            secondary_text=f"Placed: {created_at}",
            tertiary_text=(
                f"Status: {order.get('order_status', '')}  •  "
                f"Payment: {order.get('payment_status', '')}  •  ${total:.2f}"
            ),
            on_release=lambda x, o=order: self._open_order(o),
        )
        self.orders_list.add_widget(item)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _open_order(self, order: dict):
        """Navigate to the order detail screen."""
        detail_screen = self.manager.get_screen("order_detail")
        detail_screen.load_order(order["id"])
        self.manager.current = "order_detail"

    def go_back(self, *args):
        """Navigate back to home."""
        self.manager.current = "home"
