"""
Screen for listing and managing the user's saved delivery addresses.
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, ThreeLineListItem
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from kivy_app.services.user_service import get_addresses, update_address, delete_address


class AddressScreen(Screen):
    """Screen to list all saved addresses with edit / delete / set-default actions."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.addresses = []
        self._confirm_dialog = None
        self.return_screen = "profile"
        self.build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def build_ui(self):
        """Build the address list UI."""
        root = MDBoxLayout(orientation="vertical", padding="10dp", spacing="8dp")

        header = MDBoxLayout(size_hint_y=None, height="56dp", spacing="8dp")
        back_btn = MDIconButton(icon="arrow-left", on_release=self.go_back)
        header.add_widget(back_btn)
        title = MDLabel(text="Delivery Addresses", theme_text_color="Primary", font_style="H5")
        header.add_widget(title)
        refresh_btn = MDIconButton(icon="refresh", on_release=lambda *a: self.load_addresses())
        header.add_widget(refresh_btn)
        root.add_widget(header)

        add_btn = MDRaisedButton(
            text="+ Add Address",
            size_hint_x=1,
            on_release=self._go_to_create_form,
        )
        root.add_widget(add_btn)

        self.status_label = MDLabel(
            text="",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp",
        )
        root.add_widget(self.status_label)

        self.address_list = MDList()
        scroll = MDScrollView()
        scroll.add_widget(self.address_list)
        root.add_widget(scroll)

        self.add_widget(root)

    # ------------------------------------------------------------------
    # Screen lifecycle
    # ------------------------------------------------------------------

    def on_enter(self):
        """Called when entering the screen."""
        self.load_addresses()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load_addresses(self):
        """Load addresses from API."""
        self.status_label.text = "Loading…"
        self.address_list.clear_widgets()
        try:
            self.addresses = get_addresses()
            self.status_label.text = ""
            self._display_addresses()
        except Exception as e:
            self.status_label.text = "Failed to load addresses."
            toast(f"Error: {str(e)}")

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def _display_addresses(self):
        """Render the address list."""
        self.address_list.clear_widgets()
        if not self.addresses:
            self.address_list.add_widget(
                MDLabel(text="No saved addresses. Add one above.", halign="center")
            )
            return

        for address in self.addresses:
            self._add_address_row(address)

    def _add_address_row(self, address: dict):
        """Add a single address row with default / edit / delete actions."""
        is_default = address.get("is_default", False)
        primary = address.get("street_address", "")
        if is_default:
            primary = f"★ {primary}"
        secondary = f"{address.get('city', '')}, {address.get('state', '')} {address.get('postal_code', '')}"
        tertiary = address.get("additional_instructions") or address.get("country", "")

        row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="72dp",
            spacing="4dp",
            padding=("4dp", "4dp"),
        )

        info = ThreeLineListItem(
            text=primary,
            secondary_text=secondary,
            tertiary_text=tertiary,
            size_hint_x=0.55,
        )
        row.add_widget(info)

        default_btn = MDIconButton(
            icon="star" if is_default else "star-outline",
            size_hint_x=None,
            width="40dp",
            pos_hint={"center_y": 0.5},
            disabled=is_default,
            on_release=lambda btn, a=address: self._set_default(a),
        )
        row.add_widget(default_btn)

        edit_btn = MDIconButton(
            icon="pencil",
            size_hint_x=None,
            width="40dp",
            pos_hint={"center_y": 0.5},
            on_release=lambda btn, a=address: self._go_to_edit_form(a),
        )
        row.add_widget(edit_btn)

        del_btn = MDIconButton(
            icon="delete",
            size_hint_x=None,
            width="40dp",
            pos_hint={"center_y": 0.5},
            on_release=lambda btn, a=address: self._confirm_delete(a),
        )
        row.add_widget(del_btn)

        self.address_list.add_widget(row)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _go_to_create_form(self, *args):
        """Navigate to the address form in create mode."""
        form_screen = self.manager.get_screen("address_form")
        form_screen.load_address(None)
        self.manager.current = "address_form"

    def _go_to_edit_form(self, address: dict):
        """Navigate to the address form in edit mode."""
        form_screen = self.manager.get_screen("address_form")
        form_screen.load_address(address)
        self.manager.current = "address_form"

    def _set_default(self, address: dict):
        """Mark an address as the default delivery address."""
        try:
            update_address(address["id"], {"is_default": True})
            toast("Default address updated")
            self.load_addresses()
        except Exception as e:
            toast(f"Failed to update: {str(e)}")

    def _confirm_delete(self, address: dict):
        """Show confirmation dialog before deleting an address."""
        if self._confirm_dialog:
            self._confirm_dialog.dismiss()

        self._confirm_dialog = MDDialog(
            title="Delete Address",
            text=f"Delete '{address.get('street_address', '')}'? This cannot be undone.",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda btn: self._confirm_dialog.dismiss()),
                MDRaisedButton(text="DELETE", on_release=lambda btn: self._do_delete(address)),
            ],
        )
        self._confirm_dialog.open()

    def _do_delete(self, address: dict):
        """Perform the delete action."""
        if self._confirm_dialog:
            self._confirm_dialog.dismiss()
        try:
            delete_address(address["id"])
            toast("Address deleted")
            self.load_addresses()
        except Exception as e:
            toast(f"Failed to delete: {str(e)}")

    def go_back(self, *args):
        """Navigate back to whichever screen sent us here (profile or checkout)."""
        self.manager.current = self.return_screen
