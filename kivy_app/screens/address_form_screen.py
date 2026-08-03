"""
Form screen for creating or editing a delivery address.
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.toast import toast
from kivy_app.services.user_service import create_address, update_address


class AddressFormScreen(Screen):
    """Form screen for creating or editing a delivery address."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._address = None  # None = create mode, dict = edit mode
        self.build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def build_ui(self):
        """Build the form UI."""
        root = MDBoxLayout(orientation="vertical", padding="12dp", spacing="8dp")

        header = MDBoxLayout(size_hint_y=None, height="56dp", spacing="8dp")
        back_btn = MDIconButton(icon="arrow-left", on_release=self.go_back)
        header.add_widget(back_btn)
        self.title_label = MDLabel(text="Add Address", theme_text_color="Primary", font_style="H5")
        header.add_widget(self.title_label)
        root.add_widget(header)

        scroll = MDScrollView()
        form = MDBoxLayout(
            orientation="vertical",
            spacing="10dp",
            padding=("0dp", "4dp"),
            size_hint_y=None,
        )
        form.bind(minimum_height=form.setter("height"))

        self.street_field = MDTextField(
            hint_text="Street Address *",
            helper_text="Required",
            helper_text_mode="on_error",
            mode="rectangle",
        )
        form.add_widget(self.street_field)

        self.city_field = MDTextField(hint_text="City *", mode="rectangle")
        form.add_widget(self.city_field)

        self.state_field = MDTextField(hint_text="State *", mode="rectangle")
        form.add_widget(self.state_field)

        self.postal_field = MDTextField(hint_text="Postal Code *", mode="rectangle")
        form.add_widget(self.postal_field)

        self.country_field = MDTextField(hint_text="Country", mode="rectangle", text="USA")
        form.add_widget(self.country_field)

        self.instructions_field = MDTextField(
            hint_text="Delivery Instructions (optional)",
            mode="rectangle",
            multiline=True,
        )
        form.add_widget(self.instructions_field)

        default_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="48dp", spacing="8dp")
        default_row.add_widget(MDLabel(text="Set as default address", valign="center"))
        self.default_checkbox = MDCheckbox(size_hint_x=None, width="48dp")
        default_row.add_widget(self.default_checkbox)
        form.add_widget(default_row)

        scroll.add_widget(form)
        root.add_widget(scroll)

        btn_row = MDBoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
        cancel_btn = MDFlatButton(text="Cancel", size_hint_x=0.4, on_release=self.go_back)
        btn_row.add_widget(cancel_btn)
        self.save_btn = MDRaisedButton(text="Save", size_hint_x=0.6, on_release=self._save)
        btn_row.add_widget(self.save_btn)
        root.add_widget(btn_row)

        self.add_widget(root)

    # ------------------------------------------------------------------
    # Data loading (called by AddressScreen before navigation)
    # ------------------------------------------------------------------

    def load_address(self, address):
        """
        Populate form for editing an existing address, or reset for creation.

        Args:
            address: Existing address dict (edit mode) or None (create mode).
        """
        self._address = address
        if address is None:
            self.title_label.text = "Add Address"
            self.save_btn.text = "Create"
            self.street_field.text = ""
            self.city_field.text = ""
            self.state_field.text = ""
            self.postal_field.text = ""
            self.country_field.text = "USA"
            self.instructions_field.text = ""
            self.default_checkbox.active = False
        else:
            self.title_label.text = "Edit Address"
            self.save_btn.text = "Update"
            self.street_field.text = address.get("street_address", "")
            self.city_field.text = address.get("city", "")
            self.state_field.text = address.get("state", "")
            self.postal_field.text = address.get("postal_code", "")
            self.country_field.text = address.get("country", "USA")
            self.instructions_field.text = address.get("additional_instructions") or ""
            self.default_checkbox.active = bool(address.get("is_default", False))

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self):
        """Validate form fields. Returns (is_valid, error_message)."""
        if not self.street_field.text.strip():
            return False, "Street address is required."
        if not self.city_field.text.strip():
            return False, "City is required."
        if not self.state_field.text.strip():
            return False, "State is required."
        if not self.postal_field.text.strip():
            return False, "Postal code is required."
        return True, ""

    def _build_payload(self):
        """Build API payload from form fields."""
        return {
            "street_address": self.street_field.text.strip(),
            "city": self.city_field.text.strip(),
            "state": self.state_field.text.strip(),
            "postal_code": self.postal_field.text.strip(),
            "country": self.country_field.text.strip() or "USA",
            "additional_instructions": self.instructions_field.text.strip() or None,
            "is_default": self.default_checkbox.active,
        }

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _save(self, *args):
        """Validate and save (create or update) the address."""
        valid, error = self._validate()
        if not valid:
            toast(error)
            return

        payload = self._build_payload()
        try:
            if self._address is None:
                create_address(payload)
                toast("Address created")
            else:
                update_address(self._address["id"], payload)
                toast("Address updated")
            self.go_back()
        except Exception as e:
            toast(f"Failed to save: {str(e)}")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def go_back(self, *args):
        """Return to the address list and refresh it."""
        self.manager.current = "addresses"
        try:
            self.manager.get_screen("addresses").load_addresses()
        except Exception:
            pass
