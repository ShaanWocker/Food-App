"""
Home screen - main dashboard after login.
"""
import os
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.toast import toast
from kivy_app.services.auth_service import logout, is_admin_user

# kivy_app/screens/home_screen.py -> kivy_app/assets/images/home_hero.jpg
HERO_IMAGE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "images", "home_hero.jpg",
)

CARD_HEIGHT = dp(156)
CARD_ELEVATION_REST = 1
CARD_ELEVATION_HOVER = 8
ROW_SPACING = "22dp"


class _DarkOverlay(Widget):
    """Semi-transparent scrim drawn over the hero image so white text stays legible."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0, 0, 0, 0.45)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size


class NavCard(MDCard):
    """Clickable card used for home-screen navigation, with hover lift and ripple feedback."""

    icon = StringProperty("")
    text = StringProperty("")

    def __init__(self, icon, text, on_press=None, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(1, 1),
            padding="20dp",
            spacing="10dp",
            radius=[dp(18)] * 4,
            elevation=CARD_ELEVATION_REST,
            ripple_behavior=True,
            focus_behavior=True,
            md_bg_color=(1, 1, 1, 1),
            focus_color=(0.99, 0.93, 0.88, 1),
            unfocus_color=(1, 1, 1, 1),
            **kwargs,
        )
        self.icon = icon
        self.text = text
        self._on_press = on_press

        self.add_widget(
            MDIcon(
                icon=self.icon,
                halign="center",
                theme_text_color="Custom",
                text_color=(0.90, 0.32, 0.13, 1),
                font_size="36sp",
                size_hint_y=None,
                height="42dp",
            )
        )
        self.add_widget(
            MDLabel(
                text=self.text,
                halign="center",
                theme_text_color="Primary",
                font_style="Subtitle1",
                bold=True,
            )
        )

    def on_release(self):
        if self._on_press:
            self._on_press()

    def on_enter(self):
        """Mouse entered the card: lift it and let FocusBehavior tint the background."""
        super().on_enter()
        Animation.cancel_all(self, "elevation")
        Animation(elevation=CARD_ELEVATION_HOVER, d=0.15, t="out_quad").start(self)

    def on_leave(self):
        """Mouse left the card: settle back down."""
        super().on_leave()
        Animation.cancel_all(self, "elevation")
        Animation(elevation=CARD_ELEVATION_REST, d=0.15, t="out_quad").start(self)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            Animation.cancel_all(self, "elevation")
            Animation(elevation=CARD_ELEVATION_REST + 1, d=0.05, t="out_quad").start(self)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            target = CARD_ELEVATION_HOVER if self.hovering else CARD_ELEVATION_REST
            Animation.cancel_all(self, "elevation")
            Animation(elevation=target, d=0.12, t="out_quad").start(self)
        return super().on_touch_up(touch)


class HomeScreen(Screen):
    """Home screen showing a hero banner and card-based navigation."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        """Build the home screen UI."""
        root = MDBoxLayout(orientation="vertical")

        # ---- Hero banner: background photo + scrim + welcome text ----
        hero = FloatLayout(size_hint=(1, None), height=dp(260))
        hero.add_widget(
            Image(
                source=HERO_IMAGE,
                allow_stretch=True,
                keep_ratio=False,
                size_hint=(1, 1),
                pos_hint={"x": 0, "y": 0},
            )
        )
        hero.add_widget(_DarkOverlay(size_hint=(1, 1), pos_hint={"x": 0, "y": 0}))

        hero_text = MDBoxLayout(
            orientation="vertical",
            size_hint=(0.9, None),
            height=dp(90),
            spacing="4dp",
            pos_hint={"center_x": 0.5, "center_y": 0.52},
        )
        hero_text.add_widget(
            MDLabel(
                text="Welcome to Food Ordering App",
                halign="center",
                font_style="H4",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                bold=True,
            )
        )
        hero_text.add_widget(
            MDLabel(
                text="Fresh meals, prepared with care and delivered warm.",
                halign="center",
                font_style="Subtitle1",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 0.92),
            )
        )
        hero.add_widget(hero_text)

        hero.add_widget(
            MDIconButton(
                icon="logout",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                pos_hint={"right": 0.97, "top": 0.93},
                on_release=self.do_logout,
            )
        )

        root.add_widget(hero)

        # ---- Navigation cards ----
        self._base_card_specs = [
            ("silverware-fork-knife", "Browse Menu", self.go_to_menu),
            ("cart", "View Cart", self.go_to_cart),
            ("clipboard-text", "My Orders", self.go_to_orders),
            ("account", "Profile", self.go_to_profile),
        ]
        self._admin_card_specs = [
            ("food-variant", "Admin: Manage Meals", self.go_to_admin_meals),
            ("clipboard-list", "Admin: Manage Orders", self.go_to_admin_orders),
            ("chart-bar", "Admin: Analytics", self.go_to_admin_analytics),
        ]

        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            padding="28dp",
            spacing="20dp",
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(
            MDLabel(
                text="What would you like to do?",
                font_style="Subtitle1",
                theme_text_color="Secondary",
                size_hint_y=None,
                height="28dp",
            )
        )

        self.rows_box = MDBoxLayout(
            orientation="vertical", spacing=ROW_SPACING, size_hint_y=None
        )
        self.rows_box.bind(minimum_height=self.rows_box.setter("height"))
        content.add_widget(self.rows_box)

        scroll.add_widget(content)
        root.add_widget(scroll)

        self.add_widget(root)

    def _make_row(self, specs):
        """Build a row of cards that stretch evenly to fill the full row width."""
        row = MDBoxLayout(
            orientation="horizontal",
            spacing=ROW_SPACING,
            size_hint_y=None,
            height=CARD_HEIGHT,
        )
        for icon, text, callback in specs:
            row.add_widget(NavCard(icon, text, callback))
        return row

    def on_enter(self):
        """Called when entering the screen. Rebuild cards, showing admin ones for admins."""
        is_admin = is_admin_user()
        self.rows_box.clear_widgets()
        self.rows_box.add_widget(self._make_row(self._base_card_specs))
        if is_admin:
            self.rows_box.add_widget(self._make_row(self._admin_card_specs))

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
