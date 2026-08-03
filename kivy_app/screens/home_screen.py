"""
Home screen - main dashboard after login.
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from kivy_app.services.auth_service import logout, is_admin_user


class HomeScreen(Screen):
    """Home screen showing main menu options."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._admin_buttons = []
        self.build_ui()

    def build_ui(self):
        """Build the home screen UI."""
        layout = MDBoxLayout(
            orientation="vertical",
            padding="20dp",
            spacing="15dp"
        )

        # Welcome message
        welcome = MDLabel(
            text="Welcome to Food Ordering App",
            halign="center",
            theme_text_color="Primary",
            font_style="H4"
        )
        layout.add_widget(welcome)

        # Browse menu button
        menu_btn = MDRaisedButton(
            text="Browse Menu",
            size_hint_x=1,
            on_release=self.go_to_menu
        )
        layout.add_widget(menu_btn)

        # View cart button
        cart_btn = MDRaisedButton(
            text="View Cart",
            size_hint_x=1,
            on_release=self.go_to_cart
        )
        layout.add_widget(cart_btn)

        # View orders button
        orders_btn = MDRaisedButton(
            text="My Orders",
            size_hint_x=1,
            on_release=self.go_to_orders
        )
        layout.add_widget(orders_btn)

        # Profile button
        profile_btn = MDRaisedButton(
            text="Profile",
            size_hint_x=1,
            on_release=self.go_to_profile
        )
        layout.add_widget(profile_btn)

        # Admin panel buttons (hidden by default; shown in on_enter for admins)
        admin_meals_btn = MDRaisedButton(
            text="Admin: Manage Meals",
            size_hint_x=1,
            on_release=self.go_to_admin_meals,
        )
        layout.add_widget(admin_meals_btn)
        self._admin_buttons.append(admin_meals_btn)

        admin_orders_btn = MDRaisedButton(
            text="Admin: Manage Orders",
            size_hint_x=1,
            on_release=self.go_to_admin_orders,
        )
        layout.add_widget(admin_orders_btn)
        self._admin_buttons.append(admin_orders_btn)

        admin_analytics_btn = MDRaisedButton(
            text="Admin: Analytics",
            size_hint_x=1,
            on_release=self.go_to_admin_analytics,
        )
        layout.add_widget(admin_analytics_btn)
        self._admin_buttons.append(admin_analytics_btn)

        for btn in self._admin_buttons:
            btn.opacity = 0
            btn.disabled = True

        # Logout button
        logout_btn = MDRaisedButton(
            text="Logout",
            size_hint_x=1,
            on_release=self.do_logout
        )
        layout.add_widget(logout_btn)

        self.add_widget(layout)

    def on_enter(self):
        """Called when entering the screen. Show admin buttons for admin users."""
        is_admin = is_admin_user()
        for btn in self._admin_buttons:
            btn.opacity = 1 if is_admin else 0
            btn.disabled = not is_admin

    def go_to_menu(self, *args):
        """Navigate to menu screen."""
        self.manager.current = "menu"

    def go_to_cart(self, *args):
        """Navigate to cart screen."""
        self.manager.current = "cart"

    def go_to_orders(self, *args):
        """Navigate to order history screen."""
        self.manager.current = "orders"

    def go_to_profile(self, *args):
        """Navigate to profile screen."""
        self.manager.current = "profile"

    def go_to_admin_meals(self, *args):
        """Navigate to admin meal management screen."""
        self.manager.current = "admin_meal_list"

    def go_to_admin_orders(self, *args):
        """Navigate to admin order management screen."""
        self.manager.current = "admin_order_list"

    def go_to_admin_analytics(self, *args):
        """Navigate to admin analytics screen."""
        self.manager.current = "admin_analytics"

    def do_logout(self, *args):
        """Handle logout."""
        logout()
        toast("Logged out successfully")
        self.manager.current = "login"
