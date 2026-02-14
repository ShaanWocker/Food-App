"""
Cart screen for managing shopping cart.
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, ThreeLineListItem
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from kivy_app.services.cart_service import get_cart, remove_from_cart, clear_cart


class CartScreen(Screen):
    """Cart screen for viewing and managing cart items."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_data = None
        self.build_ui()
    
    def build_ui(self):
        """Build the cart screen UI."""
        layout = MDBoxLayout(
            orientation="vertical",
            padding="10dp",
            spacing="10dp"
        )
        
        # Header
        header = MDBoxLayout(
            size_hint_y=None,
            height="50dp",
            spacing="10dp"
        )
        
        back_btn = MDIconButton(
            icon="arrow-left",
            on_release=self.go_back
        )
        header.add_widget(back_btn)
        
        title = MDLabel(
            text="Shopping Cart",
            theme_text_color="Primary",
            font_style="H5"
        )
        header.add_widget(title)
        
        layout.add_widget(header)
        
        # Cart items list
        self.cart_list = MDList()
        scroll = MDScrollView()
        scroll.add_widget(self.cart_list)
        layout.add_widget(scroll)
        
        # Total section
        self.total_label = MDLabel(
            text="Total: $0.00",
            halign="center",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height="50dp"
        )
        layout.add_widget(self.total_label)
        
        # Action buttons
        btn_layout = MDBoxLayout(
            size_hint_y=None,
            height="50dp",
            spacing="10dp"
        )
        
        clear_btn = MDRaisedButton(
            text="Clear Cart",
            on_release=self.do_clear_cart
        )
        btn_layout.add_widget(clear_btn)
        
        checkout_btn = MDRaisedButton(
            text="Checkout",
            on_release=self.do_checkout
        )
        btn_layout.add_widget(checkout_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Called when entering the screen."""
        self.load_cart()
    
    def load_cart(self):
        """Load cart from API."""
        try:
            self.cart_data = get_cart()
            self.display_cart()
        except Exception as e:
            toast(f"Failed to load cart: {str(e)}")
    
    def display_cart(self):
        """Display cart items."""
        self.cart_list.clear_widgets()
        
        if not self.cart_data or not self.cart_data.get("items"):
            empty_label = MDLabel(
                text="Your cart is empty",
                halign="center"
            )
            self.cart_list.add_widget(empty_label)
            self.total_label.text = "Total: $0.00"
            return
        
        items = self.cart_data.get("items", [])
        for item in items:
            meal = item.get("meal", {})
            list_item = ThreeLineListItem(
                text=meal.get("name", ""),
                secondary_text=f"Quantity: {item.get('quantity', 0)}",
                tertiary_text=f"Price: ${meal.get('price', 0):.2f}",
                on_release=lambda x, i=item: self.remove_item(i)
            )
            self.cart_list.add_widget(list_item)
        
        # Update total
        total = self.cart_data.get("total", 0)
        self.total_label.text = f"Total: ${total:.2f}"
    
    def remove_item(self, item):
        """Remove item from cart."""
        try:
            remove_from_cart(item["id"])
            toast("Item removed from cart")
            self.load_cart()
        except Exception as e:
            toast(f"Failed to remove item: {str(e)}")
    
    def do_clear_cart(self, *args):
        """Clear all items from cart."""
        try:
            clear_cart()
            toast("Cart cleared")
            self.load_cart()
        except Exception as e:
            toast(f"Failed to clear cart: {str(e)}")
    
    def do_checkout(self, *args):
        """Proceed to checkout."""
        if not self.cart_data or not self.cart_data.get("items"):
            toast("Cart is empty")
            return
        
        toast("Checkout feature coming soon!")
    
    def go_back(self, *args):
        """Navigate back to home."""
        self.manager.current = "home"
