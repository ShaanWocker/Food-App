"""
Menu screen for browsing available meals.
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.toast import toast
from datetime import datetime
from kivy_app.services.meal_service import get_meals
from kivy_app.services.cart_service import add_to_cart


class MenuScreen(Screen):
    """Menu screen for browsing meals."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.meals = []
        self.build_ui()
    
    def build_ui(self):
        """Build the menu screen UI."""
        layout = MDBoxLayout(
            orientation="vertical",
            padding="10dp",
            spacing="10dp"
        )
        
        # Header
        header = MDBoxLayout(
            size_hint_y=None,
            height="50dp",
            spacing="10dp"
        )
        
        back_btn = MDIconButton(
            icon="arrow-left",
            on_release=self.go_back
        )
        header.add_widget(back_btn)
        
        title = MDLabel(
            text="Menu",
            theme_text_color="Primary",
            font_style="H5"
        )
        header.add_widget(title)
        
        layout.add_widget(header)
        
        # Meals list
        self.meals_list = MDList()
        scroll = MDScrollView()
        scroll.add_widget(self.meals_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Called when entering the screen."""
        self.load_meals()
    
    def load_meals(self):
        """Load meals from API."""
        try:
            # Get current month and year
            now = datetime.now()
            self.meals = get_meals(month=now.month, year=now.year)
            self.display_meals()
        except Exception as e:
            toast(f"Failed to load meals: {str(e)}")
    
    def display_meals(self):
        """Display meals in the list."""
        self.meals_list.clear_widgets()
        
        if not self.meals:
            no_meals = MDLabel(
                text="No meals available for this month",
                halign="center"
            )
            self.meals_list.add_widget(no_meals)
            return
        
        for meal in self.meals:
            item = TwoLineListItem(
                text=meal.get("name", ""),
                secondary_text=f"${meal.get('price', 0):.2f}",
                on_release=lambda x, m=meal: self.add_meal_to_cart(m)
            )
            self.meals_list.add_widget(item)
    
    def add_meal_to_cart(self, meal):
        """Add meal to cart."""
        try:
            add_to_cart(meal["id"], 1)
            toast(f"Added {meal['name']} to cart")
        except Exception as e:
            toast(f"Failed to add to cart: {str(e)}")
    
    def go_back(self, *args):
        """Navigate back to home."""
        self.manager.current = "home"
