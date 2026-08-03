"""
Profile screen - view account info, edit name/phone, and manage addresses.
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from kivy_app.services.user_service import get_profile, update_profile


class ProfileScreen(Screen):
    """Screen showing account details with an editable name/phone."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.profile = None
        self.build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def build_ui(self):
        """Build the profile screen UI."""
        root = MDBoxLayout(orientation="vertical", padding="12dp", spacing="8dp")

        header = MDBoxLayout(size_hint_y=None, height="56dp", spacing="8dp")
        back_btn = MDIconButton(icon="arrow-left", on_release=self.go_back)
        header.add_widget(back_btn)
        title = MDLabel(text="Profile", theme_text_color="Primary", font_style="H5")
        header.add_widget(title)
        root.add_widget(header)

        scroll = MDScrollView()
        body = MDBoxLayout(orientation="vertical", spacing="10dp", size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        self.email_label = MDLabel(text="", theme_text_color="Secondary", size_hint_y=None, height="30dp")
        body.add_widget(self.email_label)

        self.username_label = MDLabel(text="", theme_text_color="Secondary", size_hint_y=None, height="30dp")
        body.add_widget(self.username_label)

        self.full_name_field = MDTextField(hint_text="Full Name", mode="rectangle")
        body.add_widget(self.full_name_field)

        self.phone_field = MDTextField(hint_text="Phone Number", mode="rectangle")
        body.add_widget(self.phone_field)

        save_btn = MDRaisedButton(text="Save Changes", size_hint_x=1, on_release=self._save)
        body.add_widget(save_btn)

        addresses_btn = MDRaisedButton(
            text="Manage Delivery Addresses",
            size_hint_x=1,
            on_release=self.go_to_addresses,
        )
        body.add_widget(addresses_btn)

        scroll.add_widget(body)
        root.add_widget(scroll)

        self.add_widget(root)

    # ------------------------------------------------------------------
    # Screen lifecycle
    # ------------------------------------------------------------------

    def on_enter(self):
        """Called when entering the screen."""
        self.load_profile()

    def load_profile(self):
        """Load profile from API and populate fields."""
        try:
            self.profile = get_profile()
            self.email_label.text = f"Email: {self.profile.get('email', '')}"
            self.username_label.text = f"Username: {self.profile.get('username', '')}"
            self.full_name_field.text = self.profile.get("full_name", "")
            self.phone_field.text = self.profile.get("phone_number") or ""
        except Exception as e:
            toast(f"Failed to load profile: {str(e)}")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _save(self, *args):
        """Save profile changes."""
        full_name = self.full_name_field.text.strip()
        if not full_name:
            toast("Full name is required.")
            return
        try:
            self.profile = update_profile(
                full_name=full_name,
                phone_number=self.phone_field.text.strip() or None,
            )
            toast("Profile updated")
        except Exception as e:
            toast(f"Failed to update profile: {str(e)}")

    def go_to_addresses(self, *args):
        """Navigate to the address management screen."""
        self.manager.current = "addresses"

    def go_back(self, *args):
        """Navigate back to home."""
        self.manager.current = "home"
