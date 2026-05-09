"""
Admin screen for listing and managing meals.
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from kivy_app.services.meal_service import get_meals, update_meal, delete_meal


class AdminMealListScreen(Screen):
    """Admin screen to list all meals with CRUD actions."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.meals = []
        self._confirm_dialog = None
        self.build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def build_ui(self):
        """Build the admin meal list UI."""
        root = MDBoxLayout(orientation="vertical", padding="10dp", spacing="8dp")

        # ---- Header ----
        header = MDBoxLayout(size_hint_y=None, height="56dp", spacing="8dp")
        back_btn = MDIconButton(icon="arrow-left", on_release=self.go_back)
        header.add_widget(back_btn)
        title = MDLabel(
            text="Manage Meals",
            theme_text_color="Primary",
            font_style="H5",
        )
        header.add_widget(title)
        refresh_btn = MDIconButton(icon="refresh", on_release=lambda *a: self.load_meals())
        header.add_widget(refresh_btn)
        root.add_widget(header)

        # ---- Add Meal button ----
        add_btn = MDRaisedButton(
            text="+ Add New Meal",
            size_hint_x=1,
            on_release=self._go_to_create_form,
        )
        root.add_widget(add_btn)

        # ---- Status label ----
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
        """Load all meals (no availability filter for admin view)."""
        self.status_label.text = "Loading…"
        self.meals_list.clear_widgets()
        try:
            self.meals = get_meals(is_available=None)
            self.status_label.text = ""
            self._display_meals()
        except Exception as e:
            self.status_label.text = "Failed to load meals."
            toast(f"Error: {str(e)}")

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def _display_meals(self):
        """Render meals list with action buttons."""
        self.meals_list.clear_widgets()
        if not self.meals:
            self.meals_list.add_widget(
                MDLabel(text="No meals found. Add one above.", halign="center")
            )
            return

        for meal in self.meals:
            self._add_meal_row(meal)

    def _add_meal_row(self, meal: dict):
        """Add a single meal row with Edit / Toggle / Delete buttons."""
        name = meal.get("name", "Unknown")
        price = float(meal.get("price", 0))
        available = meal.get("is_available", True)
        category = meal.get("category") or "—"

        availability_text = "✓ Available" if available else "✗ Unavailable"
        secondary = f"${price:.2f}  •  {category}  •  {availability_text}"

        row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="72dp",
            spacing="4dp",
            padding=("4dp", "4dp"),
        )

        info = TwoLineListItem(
            text=name,
            secondary_text=secondary,
            size_hint_x=0.55,
        )
        row.add_widget(info)

        # Edit button
        edit_btn = MDIconButton(
            icon="pencil",
            size_hint_x=None,
            width="40dp",
            pos_hint={"center_y": 0.5},
            on_release=lambda btn, m=meal: self._go_to_edit_form(m),
        )
        row.add_widget(edit_btn)

        # Toggle availability button
        toggle_icon = "eye-off" if available else "eye"
        toggle_btn = MDIconButton(
            icon=toggle_icon,
            size_hint_x=None,
            width="40dp",
            pos_hint={"center_y": 0.5},
            on_release=lambda btn, m=meal: self._toggle_availability(m),
        )
        row.add_widget(toggle_btn)

        # Delete button
        del_btn = MDIconButton(
            icon="delete",
            size_hint_x=None,
            width="40dp",
            pos_hint={"center_y": 0.5},
            on_release=lambda btn, m=meal: self._confirm_delete(m),
        )
        row.add_widget(del_btn)

        self.meals_list.add_widget(row)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _go_to_create_form(self, *args):
        """Navigate to the meal form in create mode."""
        form_screen = self.manager.get_screen("admin_meal_form")
        form_screen.load_meal(None)
        self.manager.current = "admin_meal_form"

    def _go_to_edit_form(self, meal: dict):
        """Navigate to the meal form in edit mode."""
        form_screen = self.manager.get_screen("admin_meal_form")
        form_screen.load_meal(meal)
        self.manager.current = "admin_meal_form"

    def _toggle_availability(self, meal: dict):
        """Toggle meal availability."""
        meal_id = meal.get("id")
        new_value = not meal.get("is_available", True)
        try:
            update_meal(meal_id, {"is_available": new_value})
            status = "available" if new_value else "unavailable"
            toast(f"{meal['name']} marked as {status}")
            self.load_meals()
        except Exception as e:
            toast(f"Failed to update: {str(e)}")

    def _confirm_delete(self, meal: dict):
        """Show confirmation dialog before deleting a meal."""
        if self._confirm_dialog:
            self._confirm_dialog.dismiss()

        self._confirm_dialog = MDDialog(
            title="Delete Meal",
            text=f"Delete '{meal.get('name', '')}'? This cannot be undone.",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda btn: self._confirm_dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="DELETE",
                    on_release=lambda btn: self._do_delete(meal),
                ),
            ],
        )
        self._confirm_dialog.open()

    def _do_delete(self, meal: dict):
        """Perform the delete action."""
        if self._confirm_dialog:
            self._confirm_dialog.dismiss()
        try:
            delete_meal(meal["id"])
            toast(f"Deleted '{meal['name']}'")
            self.load_meals()
        except Exception as e:
            toast(f"Failed to delete: {str(e)}")

    def go_back(self, *args):
        """Navigate back to home."""
        self.manager.current = "home"
