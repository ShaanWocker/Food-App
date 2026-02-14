"""
Registration screen for new users.
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from kivy_app.services.auth_service import register, login
from kivy_app.utils.validators import validate_email, validate_password, validate_phone


class RegisterScreen(Screen):
    """Registration screen for new users."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """Build the registration screen UI."""
        layout = MDBoxLayout(
            orientation="vertical",
            padding="20dp",
            spacing="10dp"
        )
        
        # Title
        title = MDLabel(
            text="Create Account",
            halign="center",
            theme_text_color="Primary",
            font_style="H5"
        )
        layout.add_widget(title)
        
        # Full name field
        self.full_name_field = MDTextField(
            hint_text="Full Name",
            mode="rectangle"
        )
        layout.add_widget(self.full_name_field)
        
        # Username field
        self.username_field = MDTextField(
            hint_text="Username",
            mode="rectangle"
        )
        layout.add_widget(self.username_field)
        
        # Email field
        self.email_field = MDTextField(
            hint_text="Email",
            mode="rectangle"
        )
        layout.add_widget(self.email_field)
        
        # Phone field
        self.phone_field = MDTextField(
            hint_text="Phone Number (Optional)",
            mode="rectangle"
        )
        layout.add_widget(self.phone_field)
        
        # Password field
        self.password_field = MDTextField(
            hint_text="Password",
            password=True,
            mode="rectangle"
        )
        layout.add_widget(self.password_field)
        
        # Confirm password field
        self.confirm_password_field = MDTextField(
            hint_text="Confirm Password",
            password=True,
            mode="rectangle"
        )
        layout.add_widget(self.confirm_password_field)
        
        # Register button
        register_btn = MDRaisedButton(
            text="Register",
            size_hint_x=1,
            on_release=self.do_register
        )
        layout.add_widget(register_btn)
        
        # Back to login
        back_btn = MDRaisedButton(
            text="Already have an account? Login",
            size_hint_x=1,
            on_release=self.go_to_login
        )
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def do_register(self, *args):
        """Handle registration action."""
        full_name = self.full_name_field.text.strip()
        username = self.username_field.text.strip()
        email = self.email_field.text.strip()
        phone = self.phone_field.text.strip()
        password = self.password_field.text
        confirm_password = self.confirm_password_field.text
        
        # Validate inputs
        if not all([full_name, username, email, password, confirm_password]):
            toast("Please fill in all required fields")
            return
        
        if not validate_email(email):
            toast("Please enter a valid email address")
            return
        
        if phone and not validate_phone(phone):
            toast("Please enter a valid phone number")
            return
        
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            toast(error_msg)
            return
        
        if password != confirm_password:
            toast("Passwords do not match")
            return
        
        try:
            # Register user
            register(username, email, password, full_name, phone if phone else None)
            toast("Registration successful! Logging in...")
            
            # Auto login after registration
            login(email, password)
            
            # Navigate to home
            self.manager.current = "home"
            
            # Clear fields
            self.clear_fields()
        
        except Exception as e:
            toast(f"Registration failed: {str(e)}")
    
    def clear_fields(self):
        """Clear all input fields."""
        self.full_name_field.text = ""
        self.username_field.text = ""
        self.email_field.text = ""
        self.phone_field.text = ""
        self.password_field.text = ""
        self.confirm_password_field.text = ""
    
    def go_to_login(self, *args):
        """Navigate to login screen."""
        self.manager.current = "login"
