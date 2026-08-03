"""
Checkout screen: pick a delivery address, pick a test card, place the
order, and pay for it via Stripe (test mode).
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, ThreeLineListItem
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from kivy_app.services.cart_service import get_cart
from kivy_app.services.user_service import get_addresses
from kivy_app.services.order_service import create_order
from kivy_app.services.payment_service import TEST_CARDS, pay_for_order


class CheckoutScreen(Screen):
    """Screen for reviewing the cart, choosing an address/card, and paying."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_data = None
        self.addresses = []
        self._selected_address_id = None
        self._selected_card_token = None
        self._address_buttons = {}
        self._card_buttons = {}
        self.build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def build_ui(self):
        """Build the checkout screen UI."""
        root = MDBoxLayout(orientation="vertical", padding="10dp", spacing="8dp")

        header = MDBoxLayout(size_hint_y=None, height="56dp", spacing="8dp")
        back_btn = MDIconButton(icon="arrow-left", on_release=self.go_back)
        header.add_widget(back_btn)
        title = MDLabel(text="Checkout", theme_text_color="Primary", font_style="H5")
        header.add_widget(title)
        root.add_widget(header)

        scroll = MDScrollView()
        body = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        # ---- Order summary ----
        body.add_widget(MDLabel(text="Order Summary", font_style="Subtitle1", size_hint_y=None, height="30dp"))
        self.summary_list = MDList()
        body.add_widget(self.summary_list)
        self.total_label = MDLabel(
            text="Total: $0.00",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height="40dp",
        )
        body.add_widget(self.total_label)

        # ---- Address selection ----
        addr_header = MDBoxLayout(size_hint_y=None, height="30dp", spacing="8dp")
        addr_header.add_widget(MDLabel(text="Deliver To", font_style="Subtitle1"))
        manage_addr_btn = MDFlatButton(
            text="Manage Addresses",
            size_hint_x=None,
            width="160dp",
            on_release=self.go_to_addresses,
        )
        addr_header.add_widget(manage_addr_btn)
        body.add_widget(addr_header)

        self.address_box = MDBoxLayout(orientation="vertical", spacing="4dp", size_hint_y=None)
        self.address_box.bind(minimum_height=self.address_box.setter("height"))
        body.add_widget(self.address_box)

        # ---- Special instructions ----
        self.instructions_field = MDTextField(
            hint_text="Special Instructions (optional)",
            mode="rectangle",
            multiline=True,
        )
        body.add_widget(self.instructions_field)

        # ---- Test card selection ----
        body.add_widget(
            MDLabel(
                text="Payment (Stripe test mode)",
                font_style="Subtitle1",
                size_hint_y=None,
                height="30dp",
            )
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
        body.add_widget(self.card_box)

        scroll.add_widget(body)
        root.add_widget(scroll)

        # ---- Pay button ----
        self.pay_btn = MDRaisedButton(
            text="Place Order & Pay",
            size_hint_x=1,
            size_hint_y=None,
            height="50dp",
            on_release=self._place_order_and_pay,
        )
        root.add_widget(self.pay_btn)

        self.add_widget(root)

    # ------------------------------------------------------------------
    # Screen lifecycle
    # ------------------------------------------------------------------

    def on_enter(self):
        """Called when entering the screen."""
        self._selected_address_id = None
        self._selected_card_token = None
        self.load_cart()
        self.load_addresses()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load_cart(self):
        """Load cart summary."""
        self.summary_list.clear_widgets()
        try:
            self.cart_data = get_cart()
        except Exception as e:
            toast(f"Failed to load cart: {str(e)}")
            return

        items = (self.cart_data or {}).get("items", [])
        if not items:
            self.summary_list.add_widget(MDLabel(text="Your cart is empty.", halign="center"))
        for item in items:
            meal = item.get("meal", {})
            self.summary_list.add_widget(
                ThreeLineListItem(
                    text=meal.get("name", ""),
                    secondary_text=f"Quantity: {item.get('quantity', 0)}",
                    tertiary_text=f"Price: ${meal.get('price', 0):.2f}",
                )
            )
        total = (self.cart_data or {}).get("total", 0)
        self.total_label.text = f"Total: ${total:.2f}"

    def load_addresses(self):
        """Load saved addresses as selectable rows."""
        self.address_box.clear_widgets()
        self._address_buttons = {}
        try:
            self.addresses = get_addresses()
        except Exception as e:
            toast(f"Failed to load addresses: {str(e)}")
            return

        if not self.addresses:
            self.address_box.add_widget(
                MDLabel(
                    text="No saved addresses yet. Tap 'Manage Addresses' to add one.",
                    size_hint_y=None,
                    height="40dp",
                )
            )
            return

        default_address = next((a for a in self.addresses if a.get("is_default")), self.addresses[0])
        for address in self.addresses:
            label = f"{address['street_address']}, {address['city']}, {address['state']} {address['postal_code']}"
            btn = MDFlatButton(
                text=label,
                size_hint_y=None,
                height="40dp",
                on_release=lambda b, a=address: self._select_address(a["id"]),
            )
            self.address_box.add_widget(btn)
            self._address_buttons[address["id"]] = btn

        self._select_address(default_address["id"])

    # ------------------------------------------------------------------
    # Selection helpers
    # ------------------------------------------------------------------

    def _select_address(self, address_id: str):
        """Mark an address as selected and highlight its row."""
        self._selected_address_id = address_id
        for aid, btn in self._address_buttons.items():
            btn.md_bg_color = self.theme_cls.primary_light if aid == address_id else (0, 0, 0, 0)

    def _select_card(self, token: str):
        """Mark a test card as selected and highlight its row."""
        self._selected_card_token = token
        for tok, btn in self._card_buttons.items():
            btn.md_bg_color = self.theme_cls.primary_light if tok == token else (0, 0, 0, 0)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _place_order_and_pay(self, *args):
        """Create the order from the cart, then pay for it via Stripe test mode."""
        if not self.cart_data or not self.cart_data.get("items"):
            toast("Your cart is empty.")
            return
        if not self._selected_address_id:
            toast("Please select (or add) a delivery address.")
            return
        if not self._selected_card_token:
            toast("Please select a test card to pay with.")
            return

        self.pay_btn.disabled = True
        self.pay_btn.text = "Processing…"
        try:
            order = create_order(
                self._selected_address_id,
                self.instructions_field.text.strip() or None,
            )
            order_id = order["id"]

            succeeded, status = pay_for_order(order_id, self._selected_card_token)
            if succeeded:
                toast("Payment successful! Order placed.")
                detail_screen = self.manager.get_screen("order_detail")
                detail_screen.load_order(order_id)
                self.manager.current = "order_detail"
            else:
                toast(f"Payment failed ({status}). Your order is saved - retry from Order Details.")
                detail_screen = self.manager.get_screen("order_detail")
                detail_screen.load_order(order_id)
                self.manager.current = "order_detail"
        except Exception as e:
            toast(f"Checkout failed: {str(e)}")
        finally:
            self.pay_btn.disabled = False
            self.pay_btn.text = "Place Order & Pay"

    def go_to_addresses(self, *args):
        """Navigate to address management, returning here afterwards."""
        addr_screen = self.manager.get_screen("addresses")
        addr_screen.return_screen = "checkout"
        self.manager.current = "addresses"

    def go_back(self, *args):
        """Navigate back to the cart."""
        self.manager.current = "cart"
