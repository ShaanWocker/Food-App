"""
Menu screen for browsing available meals.
"""
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, ThreeLineListItem
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from datetime import datetime
from kivy_app.services.meal_service import get_meals
from kivy_app.services.cart_service import add_to_cart

# Common meal categories for filter buttons
CATEGORIES = ["All", "Breakfast", "Lunch", "Dinner", "Snack", "Dessert", "Beverage"]

# Max characters shown for meal description in list items
DESCRIPTION_MAX_LENGTH = 60


class MenuScreen(Screen):
    """Menu screen for browsing meals."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.meals = []
        self._active_category = None  # None = show all categories
        self._show_current_month_only = True
        self.build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def build_ui(self):
        """Build the menu screen UI."""
        root = MDBoxLayout(orientation="vertical", padding="10dp", spacing="8dp")

        # ---- Header ----
        header = MDBoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
        back_btn = MDIconButton(icon="arrow-left", on_release=self.go_back)
        header.add_widget(back_btn)
        title = MDLabel(text="Menu", theme_text_color="Primary", font_style="H5")
        header.add_widget(title)
        refresh_btn = MDIconButton(icon="refresh", on_release=lambda *a: self.load_meals())
        header.add_widget(refresh_btn)
        root.add_widget(header)

        # ---- Month filter toggle ----
        month_row = MDBoxLayout(size_hint_y=None, height="40dp", spacing="8dp")
        self.month_btn = MDRaisedButton(
            text="This Month",
            size_hint_x=None,
            width="140dp",
            on_release=self._toggle_month_filter,
        )
        month_row.add_widget(self.month_btn)
        month_label = MDLabel(
            text="Show all months",
            theme_text_color="Secondary",
            valign="center",
        )
        month_row.add_widget(month_label)
        root.add_widget(month_row)

        # ---- Category filter row ----
        cat_scroll = MDScrollView(size_hint_y=None, height="48dp", do_scroll_y=False)
        cat_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            spacing="6dp",
            padding=("4dp", "4dp"),
        )
        cat_row.bind(minimum_width=cat_row.setter("width"))
        self._cat_buttons = {}
        for cat in CATEGORIES:
            btn = MDFlatButton(
                text=cat,
                size_hint_x=None,
                width="100dp",
                on_release=lambda btn, c=cat: self._filter_by_category(c),
            )
            cat_row.add_widget(btn)
            self._cat_buttons[cat] = btn
        cat_scroll.add_widget(cat_row)
        root.add_widget(cat_scroll)

        # ---- Status / loading label ----
        self.status_label = MDLabel(
            text="",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp",
        )
        root.add_widget(self.status_label)

        # ---- Meals list ----
        self.meals_list = MDList()
        scroll = MDScrollView()
        scroll.add_widget(self.meals_list)
        root.add_widget(scroll)

        self.add_widget(root)

    # ------------------------------------------------------------------
    # Screen lifecycle
    # ------------------------------------------------------------------

    def on_enter(self):
        """Called when entering the screen."""
        self.load_meals()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load_meals(self):
        """Load meals from API."""
        self.status_label.text = "Loading meals…"
        self.meals_list.clear_widgets()
        try:
            now = datetime.now()
            kwargs = {"is_available": True}
            if self._show_current_month_only:
                kwargs["month"] = now.month
                kwargs["year"] = now.year
            category = None if self._active_category == "All" or self._active_category is None else self._active_category
            if category:
                kwargs["category"] = category
            self.meals = get_meals(**kwargs)
            self.status_label.text = ""
            self.display_meals()
        except Exception as e:
            self.status_label.text = "Failed to load meals."
            toast(f"Error: {str(e)}")

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def display_meals(self):
        """Display meals in the list."""
        self.meals_list.clear_widgets()

        if not self.meals:
            self.meals_list.add_widget(
                MDLabel(text="No meals available.", halign="center")
            )
            return

        for meal in self.meals:
            self._add_meal_row(meal)

    def _add_meal_row(self, meal: dict):
        """Add a single meal row with an Add-to-Cart button."""
        name = meal.get("name", "Unknown")
        price = float(meal.get("price", 0))
        category = meal.get("category") or ""
        description = meal.get("description") or ""
        available = meal.get("is_available", True)

        secondary = f"${price:.2f}"
        if category:
            secondary += f"  •  {category}"
        tertiary = description[:DESCRIPTION_MAX_LENGTH] + ("…" if len(description) > DESCRIPTION_MAX_LENGTH else "") if description else ""
        if not available:
            tertiary = "⚠ Currently unavailable"

        # Row container
        row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="80dp",
            spacing="4dp",
            padding=("8dp", "4dp"),
        )

        item = ThreeLineListItem(
            text=name,
            secondary_text=secondary,
            tertiary_text=tertiary,
            size_hint_x=0.75,
        )
        row.add_widget(item)

        if available:
            add_btn = MDRaisedButton(
                text="Add",
                size_hint_x=None,
                width="72dp",
                size_hint_y=None,
                height="40dp",
                pos_hint={"center_y": 0.5},
                on_release=lambda btn, m=meal: self._add_meal_to_cart(m),
            )
        else:
            add_btn = MDFlatButton(
                text="N/A",
                size_hint_x=None,
                width="72dp",
                size_hint_y=None,
                height="40dp",
                pos_hint={"center_y": 0.5},
                disabled=True,
            )
        row.add_widget(add_btn)
        self.meals_list.add_widget(row)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _add_meal_to_cart(self, meal: dict):
        """Add meal to cart."""
        try:
            add_to_cart(meal["id"], 1)
            toast(f"Added {meal['name']} to cart")
        except Exception as e:
            toast(f"Failed to add to cart: {str(e)}")

    def _toggle_month_filter(self, *args):
        """Toggle between current-month and all-months view."""
        self._show_current_month_only = not self._show_current_month_only
        self.month_btn.text = "This Month" if self._show_current_month_only else "All Months"
        self.load_meals()

    def _filter_by_category(self, category: str):
        """Filter meals by category."""
        self._active_category = category if category != "All" else None
        # Highlight active button
        theme_cls = MDApp.get_running_app().theme_cls
        for cat, btn in self._cat_buttons.items():
            btn.md_bg_color = (
                theme_cls.primary_color
                if cat == category
                else (0, 0, 0, 0)
            )
        self.load_meals()

    def go_back(self, *args):
        """Navigate back to home."""
        self.manager.current = "home"
