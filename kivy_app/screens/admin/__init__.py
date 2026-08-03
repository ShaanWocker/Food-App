"""
Admin screens package initialization.
"""
from kivy_app.screens.admin.admin_meal_list_screen import AdminMealListScreen
from kivy_app.screens.admin.admin_meal_form_screen import AdminMealFormScreen
from kivy_app.screens.admin.admin_order_list_screen import AdminOrderListScreen
from kivy_app.screens.admin.admin_analytics_screen import AdminAnalyticsScreen

__all__ = [
    "AdminMealListScreen",
    "AdminMealFormScreen",
    "AdminOrderListScreen",
    "AdminAnalyticsScreen",
]
