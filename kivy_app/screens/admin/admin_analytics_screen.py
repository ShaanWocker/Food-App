"""
Admin analytics dashboard - revenue summary and popular meals.
"""
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from kivy_app.services.order_service import get_revenue_analytics, get_popular_meals

PERIOD_OPTIONS = [("7 Days", 7), ("30 Days", 30), ("90 Days", 90), ("1 Year", 365)]


class AdminAnalyticsScreen(Screen):
    """Admin screen showing revenue and popular-meal analytics."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._days = 30
        self._period_buttons = {}
        self.build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def build_ui(self):
        """Build the analytics dashboard UI."""
        root = MDBoxLayout(orientation="vertical", padding="10dp", spacing="8dp")

        header = MDBoxLayout(size_hint_y=None, height="56dp", spacing="8dp")
        back_btn = MDIconButton(icon="arrow-left", on_release=self.go_back)
        header.add_widget(back_btn)
        title = MDLabel(text="Analytics", theme_text_color="Primary", font_style="H5")
        header.add_widget(title)
        refresh_btn = MDIconButton(icon="refresh", on_release=lambda *a: self.load_data())
        header.add_widget(refresh_btn)
        root.add_widget(header)

        # ---- Period selector ----
        period_row = MDBoxLayout(size_hint_y=None, height="40dp", spacing="6dp")
        for label, days in PERIOD_OPTIONS:
            btn = MDFlatButton(
                text=label,
                on_release=lambda b, d=days: self._select_period(d),
            )
            period_row.add_widget(btn)
            self._period_buttons[days] = btn
        root.add_widget(period_row)

        scroll = MDScrollView()
        body = MDBoxLayout(orientation="vertical", spacing="10dp", size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        self.revenue_label = MDLabel(
            text="",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height="120dp",
        )
        body.add_widget(self.revenue_label)

        self.status_breakdown_label = MDLabel(
            text="",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="120dp",
        )
        body.add_widget(self.status_breakdown_label)

        body.add_widget(
            MDLabel(text="Most Popular Meals", font_style="Subtitle1", size_hint_y=None, height="30dp")
        )
        self.popular_list = MDList()
        body.add_widget(self.popular_list)

        scroll.add_widget(body)
        root.add_widget(scroll)

        self.add_widget(root)

    # ------------------------------------------------------------------
    # Screen lifecycle
    # ------------------------------------------------------------------

    def on_enter(self):
        """Called when entering the screen."""
        self._select_period(self._days)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load_data(self):
        """Load revenue analytics and popular meals."""
        try:
            revenue = get_revenue_analytics(days=self._days)
            self.revenue_label.text = (
                f"Total Revenue: ${revenue.get('total_revenue', 0):.2f}\n"
                f"Total Orders: {revenue.get('total_orders', 0)}\n"
                f"Average Order Value: ${revenue.get('average_order_value', 0):.2f}"
            )
            status_counts = revenue.get("orders_by_status", {})
            self.status_breakdown_label.text = "Orders by Status:\n" + "\n".join(
                f"  {status}: {count}" for status, count in status_counts.items()
            )
        except Exception as e:
            toast(f"Failed to load revenue analytics: {str(e)}")

        try:
            popular = get_popular_meals(limit=10)
            self.popular_list.clear_widgets()
            if not popular:
                self.popular_list.add_widget(MDLabel(text="No orders yet.", halign="center"))
            for meal in popular:
                self.popular_list.add_widget(
                    TwoLineListItem(
                        text=meal.get("meal_name", ""),
                        secondary_text=f"Ordered {meal.get('total_ordered', 0)} times",
                    )
                )
        except Exception as e:
            toast(f"Failed to load popular meals: {str(e)}")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _select_period(self, days: int):
        """Select an analytics time period and reload."""
        self._days = days
        theme_cls = MDApp.get_running_app().theme_cls
        for d, btn in self._period_buttons.items():
            btn.md_bg_color = theme_cls.primary_color if d == days else (0, 0, 0, 0)
        self.load_data()

    def go_back(self, *args):
        """Navigate back to home."""
        self.manager.current = "home"
