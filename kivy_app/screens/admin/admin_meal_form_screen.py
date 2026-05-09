"""
Admin form screen for creating or editing a meal.
"""
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.toast import toast
from kivy_app.services.meal_service import create_meal, update_meal


class AdminMealFormScreen(Screen):
    """Form screen for creating or editing a meal."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._meal = None  # None = create mode, dict = edit mode
        self.build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def build_ui(self):
        """Build the form UI."""
        root = MDBoxLayout(orientation="vertical", padding="12dp", spacing="8dp")

        # ---- Header ----
        header = MDBoxLayout(size_hint_y=None, height="56dp", spacing="8dp")
        back_btn = MDIconButton(icon="arrow-left", on_release=self.go_back)
        header.add_widget(back_btn)
        self.title_label = MDLabel(
            text="Add Meal",
            theme_text_color="Primary",
            font_style="H5",
        )
        header.add_widget(self.title_label)
        root.add_widget(header)

        # ---- Scrollable form body ----
        scroll = MDScrollView()
        form = MDBoxLayout(
            orientation="vertical",
            spacing="10dp",
            padding=("0dp", "4dp"),
            size_hint_y=None,
        )
        form.bind(minimum_height=form.setter("height"))

        # Name
        self.name_field = MDTextField(
            hint_text="Meal Name *",
            helper_text="Required",
            helper_text_mode="on_error",
            mode="rectangle",
        )
        form.add_widget(self.name_field)

        # Description
        self.desc_field = MDTextField(
            hint_text="Description",
            mode="rectangle",
            multiline=True,
        )
        form.add_widget(self.desc_field)

        # Price
        self.price_field = MDTextField(
            hint_text="Price (e.g. 9.99) *",
            helper_text="Must be a positive number",
            helper_text_mode="on_error",
            mode="rectangle",
            input_filter="float",
        )
        form.add_widget(self.price_field)

        # Category
        self.category_field = MDTextField(
            hint_text="Category (e.g. Lunch)",
            mode="rectangle",
        )
        form.add_widget(self.category_field)

        # Available Month (YYYY-MM)
        self.month_field = MDTextField(
            hint_text="Available Month (YYYY-MM) *",
            helper_text="Format: YYYY-MM, e.g. 2024-05",
            helper_text_mode="on_error",
            mode="rectangle",
        )
        form.add_widget(self.month_field)

        # Image URL
        self.image_field = MDTextField(
            hint_text="Image URL (optional)",
            mode="rectangle",
        )
        form.add_widget(self.image_field)

        # Is Available checkbox row
        avail_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="48dp",
            spacing="8dp",
        )
        avail_label = MDLabel(
            text="Available for ordering",
            valign="center",
        )
        avail_row.add_widget(avail_label)
        self.avail_checkbox = MDCheckbox(
            size_hint_x=None,
            width="48dp",
            active=True,
        )
        avail_row.add_widget(self.avail_checkbox)
        form.add_widget(avail_row)

        scroll.add_widget(form)
        root.add_widget(scroll)

        # ---- Action buttons ----
        btn_row = MDBoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
        cancel_btn = MDFlatButton(
            text="Cancel",
            size_hint_x=0.4,
            on_release=self.go_back,
        )
        btn_row.add_widget(cancel_btn)
        self.save_btn = MDRaisedButton(
            text="Save",
            size_hint_x=0.6,
            on_release=self._save,
        )
        btn_row.add_widget(self.save_btn)
        root.add_widget(btn_row)

        self.add_widget(root)

    # ------------------------------------------------------------------
    # Data loading (called by AdminMealListScreen before navigation)
    # ------------------------------------------------------------------

    def load_meal(self, meal):
        """
        Populate form for editing an existing meal, or reset for creation.

        Args:
            meal: Existing meal dict (edit mode) or None (create mode).
        """
        self._meal = meal
        if meal is None:
            self.title_label.text = "Add Meal"
            self.save_btn.text = "Create"
            self.name_field.text = ""
            self.desc_field.text = ""
            self.price_field.text = ""
            self.category_field.text = ""
            self.month_field.text = ""
            self.image_field.text = ""
            self.avail_checkbox.active = True
        else:
            self.title_label.text = "Edit Meal"
            self.save_btn.text = "Update"
            self.name_field.text = meal.get("name", "")
            self.desc_field.text = meal.get("description") or ""
            self.price_field.text = str(meal.get("price", ""))
            self.category_field.text = meal.get("category") or ""
            # available_month arrives as "YYYY-MM-DD"; show "YYYY-MM"
            am = meal.get("available_month", "")
            self.month_field.text = am[:7] if am else ""
            self.image_field.text = meal.get("image_url") or ""
            self.avail_checkbox.active = bool(meal.get("is_available", True))

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _validate(self):
        """Validate form fields. Returns (is_valid, error_message)."""
        name = self.name_field.text.strip()
        if not name:
            return False, "Meal name is required."

        price_str = self.price_field.text.strip()
        if not price_str:
            return False, "Price is required."
        try:
            price = float(price_str)
            if price <= 0:
                return False, "Price must be greater than 0."
        except ValueError:
            return False, "Price must be a valid number."

        month_str = self.month_field.text.strip()
        if not month_str:
            return False, "Available month is required."
        # Expect YYYY-MM format
        parts = month_str.split("-")
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
            return False, "Month format must be YYYY-MM (e.g. 2024-05)."
        year_val, month_val = int(parts[0]), int(parts[1])
        current_year = datetime.now().year
        if not (current_year - 5 <= year_val <= current_year + 10) or not (1 <= month_val <= 12):
            return False, "Invalid year or month value."

        return True, ""

    def _build_payload(self):
        """Build API payload from form fields."""
        month_str = self.month_field.text.strip()
        available_month = f"{month_str}-01"  # API expects full date
        return {
            "name": self.name_field.text.strip(),
            "description": self.desc_field.text.strip() or None,
            "price": float(self.price_field.text.strip()),
            "category": self.category_field.text.strip() or None,
            "available_month": available_month,
            "image_url": self.image_field.text.strip() or None,
            "is_available": self.avail_checkbox.active,
        }

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _save(self, *args):
        """Validate and save (create or update) the meal."""
        valid, error = self._validate()
        if not valid:
            toast(error)
            return

        payload = self._build_payload()
        try:
            if self._meal is None:
                create_meal(payload)
                toast("Meal created successfully")
            else:
                update_meal(self._meal["id"], payload)
                toast("Meal updated successfully")
            self.go_back()
        except Exception as e:
            toast(f"Failed to save: {str(e)}")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def go_back(self, *args):
        """Return to admin meal list and refresh it."""
        self.manager.current = "admin_meal_list"
        # Refresh the list after a change
        try:
            self.manager.get_screen("admin_meal_list").load_meals()
        except Exception:
            pass
