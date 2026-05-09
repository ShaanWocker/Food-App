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
        self._admin_btn = None
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
            on_release=self.show_coming_soon
        )
        layout.add_widget(orders_btn)

        # Profile button
        profile_btn = MDRaisedButton(
            text="Profile",
            size_hint_x=1,
            on_release=self.show_coming_soon
        )
        layout.add_widget(profile_btn)

        # Admin panel button (hidden by default; shown in on_enter for admins)
        self._admin_btn = MDRaisedButton(
            text="Admin: Manage Meals",
            size_hint_x=1,
            on_release=self.go_to_admin_meals,
        )
        self._admin_btn.opacity = 0
        self._admin_btn.disabled = True
        layout.add_widget(self._admin_btn)

        # Logout button
        logout_btn = MDRaisedButton(
            text="Logout",
            size_hint_x=1,
            on_release=self.do_logout
        )
        layout.add_widget(logout_btn)

        self.add_widget(layout)

    def on_enter(self):
        """Called when entering the screen. Show admin button for admin users."""
        if is_admin_user():
            self._admin_btn.opacity = 1
            self._admin_btn.disabled = False
        else:
            self._admin_btn.opacity = 0
            self._admin_btn.disabled = True

    def go_to_menu(self, *args):
        """Navigate to menu screen."""
        self.manager.current = "menu"

    def go_to_cart(self, *args):
        """Navigate to cart screen."""
        self.manager.current = "cart"

    def go_to_admin_meals(self, *args):
        """Navigate to admin meal management screen."""
        self.manager.current = "admin_meal_list"

    def show_coming_soon(self, *args):
        """Show coming soon message."""
        toast("Feature coming soon!")

    def do_logout(self, *args):
        """Handle logout."""
        logout()
        toast("Logged out successfully")
        self.manager.current = "login"
