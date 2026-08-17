"""
Order detail screen - shows one order's items, status, and delivery info.
Lets the user pay (or retry payment) for orders that aren't paid yet.
"""
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from kivy_app.services.order_service import get_order
from kivy_app.services.payment_service import TEST_CARDS, pay_for_order


class OrderDetailScreen(Screen):
    """Screen showing full details for a single order."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order = None
        self._order_id = None
        self._selected_card_token = None
        self._card_buttons = {}
        self.build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def build_ui(self):
        """Build the order detail UI."""
        root = MDBoxLayout(orientation="vertical", padding="10dp", spacing="8dp")

        header = MDBoxLayout(size_hint_y=None, height="56dp", spacing="8dp")
        back_btn = MDIconButton(icon="arrow-left", on_release=self.go_back)
        header.add_widget(back_btn)
        self.title_label = MDLabel(text="Order Details", theme_text_color="Primary", font_style="H5")
        header.add_widget(self.title_label)
        root.add_widget(header)

        scroll = MDScrollView()
        body = MDBoxLayout(orientation="vertical", spacing="10dp", size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        self.status_label = MDLabel(text="", theme_text_color="Secondary", size_hint_y=None, height="60dp")
        body.add_widget(self.status_label)

        self.address_label = MDLabel(text="", theme_text_color="Secondary", size_hint_y=None, height="60dp")
        body.add_widget(self.address_label)

        self.instructions_label = MDLabel(text="", theme_text_color="Secondary", size_hint_y=None, height="40dp")
        body.add_widget(self.instructions_label)

        body.add_widget(MDLabel(text="Items", font_style="Subtitle1", size_hint_y=None, height="30dp"))
        self.items_list = MDList()
        body.add_widget(self.items_list)

        self.total_label = MDLabel(
            text="Total: $0.00",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height="40dp",
        )
        body.add_widget(self.total_label)

        # ---- Pay now section (shown only when unpaid) ----
        self.pay_section = MDBoxLayout(orientation="vertical", spacing="6dp", size_hint_y=None)
        self.pay_section.bind(minimum_height=self.pay_section.setter("height"))
        self.pay_section.add_widget(
            MDLabel(text="Pay Now (Stripe test mode)", font_style="Subtitle1", size_hint_y=None, height="30dp")
        )
        self.card_box = MDBoxLayout(orientation="vertical", spacing="4dp", size_hint_y=None)
        self.card_box.bind(minimum_height=self.card_box.setter("height"))
        for label, token in TEST_CARDS:
            btn = MDFlatButton(
                text=label,
                size_hint_y=None,
                height="40dp",
                on_release=lambda b, t=token: self._select_card(t),
            )
            self.card_box.add_widget(btn)
            self._card_buttons[token] = btn
        self.pay_section.add_widget(self.card_box)
        self.pay_btn = MDRaisedButton(text="Pay Now", size_hint_x=1, on_release=self._pay_now)
        self.pay_section.add_widget(self.pay_btn)
        body.add_widget(self.pay_section)

        scroll.add_widget(body)
        root.add_widget(scroll)

        self.add_widget(root)

    # ------------------------------------------------------------------
    # Data loading (called by OrdersScreen / CheckoutScreen before navigation)
    # ------------------------------------------------------------------

    def load_order(self, order_id: str):
        """Load and display an order by ID."""
        self._order_id = order_id
        self._selected_card_token = None
        try:
            self.order = get_order(order_id)
            self._display_order()
        except Exception as e:
            toast(f"Failed to load order: {str(e)}")

    def _display_order(self):
        """Render the loaded order's details."""
        order = self.order
        short_id = str(order.get("id", ""))[:8]
        self.title_label.text = f"Order #{short_id}"

        created_at = str(order.get("created_at", ""))[:16].replace("T", " ")
        self.status_label.text = (
            f"Placed: {created_at}\n"
            f"Status: {order.get('order_status', '')}\n"
            f"Payment: {order.get('payment_status', '')}"
        )

        addr = order.get("delivery_address", {}) or {}
        self.address_label.text = (
            f"Deliver to: {addr.get('street_address', '')}, "
            f"{addr.get('city', '')}, {addr.get('state', '')} {addr.get('postal_code', '')}"
        )

        instructions = order.get("special_instructions")
        self.instructions_label.text = f"Instructions: {instructions}" if instructions else ""

        self.items_list.clear_widgets()
        for item in order.get("order_items", []):
            meal = item.get("meal", {})
            price = float(item.get("price_at_purchase", 0))
            self.items_list.add_widget(
                TwoLineListItem(
                    text=meal.get("name", "Meal"),
                    secondary_text=f"Qty {item.get('quantity', 0)} @ ${price:.2f}",
                )
            )

        self.total_label.text = f"Total: ${float(order.get('total_price', 0)):.2f}"

        is_paid = order.get("payment_status") == "Completed"
        self.pay_section.opacity = 0 if is_paid else 1
        self.pay_section.disabled = is_paid
        for btn in self._card_buttons.values():
            btn.md_bg_color = (0, 0, 0, 0)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _select_card(self, token: str):
        """Mark a test card as selected and highlight its row."""
        self._selected_card_token = token
        theme_cls = MDApp.get_running_app().theme_cls
        for tok, btn in self._card_buttons.items():
            btn.md_bg_color = theme_cls.primary_light if tok == token else (0, 0, 0, 0)

    def _pay_now(self, *args):
        """Pay for this (currently unpaid) order."""
        if not self._selected_card_token:
            toast("Please select a test card to pay with.")
            return

        self.pay_btn.disabled = True
        self.pay_btn.text = "Processing…"
        try:
            succeeded, status = pay_for_order(self._order_id, self._selected_card_token)
            if succeeded:
                toast("Payment successful!")
                self.load_order(self._order_id)
            else:
                toast(f"Payment failed ({status}). Try another test card.")
        except Exception as e:
            toast(f"Payment failed: {str(e)}")
        finally:
            self.pay_btn.disabled = False
            self.pay_btn.text = "Pay Now"

    def go_back(self, *args):
        """Navigate back to order history."""
        self.manager.current = "orders"
