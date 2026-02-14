"""
Login screen for user authentication.
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from kivy.properties import StringProperty
from kivy_app.services.auth_service import login
from kivy_app.utils.validators import validate_email


class LoginScreen(Screen):
    """Login screen for user authentication."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """Build the login screen UI."""
        layout = MDBoxLayout(
            orientation="vertical",
            padding="20dp",
            spacing="15dp"
        )
        
        # Title
        title = MDLabel(
            text="Food Ordering App",
            halign="center",
            theme_text_color="Primary",
            font_style="H4"
        )
        layout.add_widget(title)
        
        # Subtitle
        subtitle = MDLabel(
            text="Login to your account",
            halign="center",
            theme_text_color="Secondary"
        )
        layout.add_widget(subtitle)
        
        # Email field
        self.email_field = MDTextField(
            hint_text="Email",
            helper_text="Enter your email address",
            helper_text_mode="on_focus",
            mode="rectangle"
        )
        layout.add_widget(self.email_field)
        
        # Password field
        self.password_field = MDTextField(
            hint_text="Password",
            helper_text="Enter your password",
            helper_text_mode="on_focus",
            password=True,
            mode="rectangle"
        )
        layout.add_widget(self.password_field)
        
        # Login button
        login_btn = MDRaisedButton(
            text="Login",
            size_hint_x=1,
            on_release=self.do_login
        )
        layout.add_widget(login_btn)
        
        # Register link
        register_btn = MDRaisedButton(
            text="Don't have an account? Register",
            size_hint_x=1,
            on_release=self.go_to_register
        )
        layout.add_widget(register_btn)
        
        self.add_widget(layout)
    
    def do_login(self, *args):
        """Handle login action."""
        email = self.email_field.text.strip()
        password = self.password_field.text
        
        # Validate inputs
        if not email or not password:
            toast("Please fill in all fields")
            return
        
        if not validate_email(email):
            toast("Please enter a valid email address")
            return
        
        try:
            # Call login service
            response = login(email, password)
            toast("Login successful!")
            
            # Navigate to home screen
            self.manager.current = "home"
            
            # Clear fields
            self.email_field.text = ""
            self.password_field.text = ""
        
        except Exception as e:
            toast(f"Login failed: {str(e)}")
    
    def go_to_register(self, *args):
        """Navigate to register screen."""
        self.manager.current = "register"
