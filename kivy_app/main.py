"""
Main Kivy application entry point.
"""
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy_app.screens.login_screen import LoginScreen
from kivy_app.screens.register_screen import RegisterScreen
from kivy_app.screens.home_screen import HomeScreen
from kivy_app.screens.menu_screen import MenuScreen
from kivy_app.screens.cart_screen import CartScreen
from kivy_app.services.auth_service import init_auth


class FoodOrderingApp(MDApp):
    """Main application class."""
    
    def build(self):
        """
        Build the application.
        
        Returns:
            Root widget (ScreenManager)
        """
        self.theme_cls.primary_palette = "DeepOrange"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.theme_style = "Light"
        
        # Create screen manager
        self.screen_manager = ScreenManager()
        
        # Add screens
        self.screen_manager.add_widget(LoginScreen(name="login"))
        self.screen_manager.add_widget(RegisterScreen(name="register"))
        self.screen_manager.add_widget(HomeScreen(name="home"))
        self.screen_manager.add_widget(MenuScreen(name="menu"))
        self.screen_manager.add_widget(CartScreen(name="cart"))
        
        # Check if user is already logged in
        if init_auth():
            self.screen_manager.current = "home"
        else:
            self.screen_manager.current = "login"
        
        return self.screen_manager
    
    def on_start(self):
        """Called when the application starts."""
        pass
    
    def on_stop(self):
        """Called when the application stops."""
        pass


if __name__ == "__main__":
    FoodOrderingApp().run()
