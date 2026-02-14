"""
Database initialization script with sample data.
"""
import sys
from datetime import date, datetime
from decimal import Decimal
from app.database import SessionLocal, engine, Base
from app.models import User, Meal, Address
from app.core.security import get_password_hash


def init_db():
    """Initialize database with sample data."""
    print("🔧 Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@foodapp.com").first()
        
        if not existing_admin:
            # Create admin user
            admin = User(
                email="admin@foodapp.com",
                username="admin",
                full_name="Admin User",
                password_hash=get_password_hash("AdminPass123!"),
                is_admin=True,
                is_active=True
            )
            db.add(admin)
            print("✅ Admin user created")
            print("   Email: admin@foodapp.com")
            print("   Password: AdminPass123!")
        else:
            print("ℹ️  Admin user already exists")
        
        # Create sample regular user
        existing_user = db.query(User).filter(User.email == "user@example.com").first()
        
        if not existing_user:
            user = User(
                email="user@example.com",
                username="johndoe",
                full_name="John Doe",
                phone_number="+1234567890",
                password_hash=get_password_hash("UserPass123!"),
                is_admin=False,
                is_active=True
            )
            db.add(user)
            db.flush()
            
            # Add sample address for user
            address = Address(
                user_id=user.id,
                street_address="123 Main St",
                city="New York",
                state="NY",
                postal_code="10001",
                country="USA",
                is_default=True
            )
            db.add(address)
            print("✅ Sample user created")
            print("   Email: user@example.com")
            print("   Password: UserPass123!")
        else:
            print("ℹ️  Sample user already exists")
        
        # Create sample meals
        current_month = date.today().replace(day=1)
        
        sample_meals = [
            {
                "name": "Classic Burger",
                "description": "Juicy beef patty with lettuce, tomato, and special sauce",
                "price": Decimal("12.99"),
                "category": "Burgers",
                "image_url": "https://example.com/burger.jpg"
            },
            {
                "name": "Margherita Pizza",
                "description": "Fresh mozzarella, tomatoes, and basil on thin crust",
                "price": Decimal("14.99"),
                "category": "Pizza",
                "image_url": "https://example.com/pizza.jpg"
            },
            {
                "name": "Caesar Salad",
                "description": "Crisp romaine lettuce with Caesar dressing and croutons",
                "price": Decimal("9.99"),
                "category": "Salads",
                "image_url": "https://example.com/salad.jpg"
            },
            {
                "name": "Grilled Salmon",
                "description": "Fresh Atlantic salmon with lemon butter sauce",
                "price": Decimal("19.99"),
                "category": "Seafood",
                "image_url": "https://example.com/salmon.jpg"
            },
            {
                "name": "Chicken Alfredo Pasta",
                "description": "Creamy Alfredo sauce with grilled chicken",
                "price": Decimal("15.99"),
                "category": "Pasta",
                "image_url": "https://example.com/pasta.jpg"
            },
            {
                "name": "Chocolate Lava Cake",
                "description": "Warm chocolate cake with molten center",
                "price": Decimal("7.99"),
                "category": "Desserts",
                "image_url": "https://example.com/cake.jpg"
            }
        ]
        
        meals_added = 0
        for meal_data in sample_meals:
            existing_meal = db.query(Meal).filter(
                Meal.name == meal_data["name"]
            ).first()
            
            if not existing_meal:
                meal = Meal(
                    **meal_data,
                    available_month=current_month,
                    is_available=True
                )
                db.add(meal)
                meals_added += 1
        
        if meals_added > 0:
            print(f"✅ {meals_added} sample meals created")
        else:
            print("ℹ️  Sample meals already exist")
        
        db.commit()
        print("\n✨ Database initialization complete!")
        print("\n📝 Summary:")
        print("   - Admin account: admin@foodapp.com / AdminPass123!")
        print("   - Test account: user@example.com / UserPass123!")
        print(f"   - {meals_added} meals available for {current_month.strftime('%B %Y')}")
        print("\n🚀 You can now start the application:")
        print("   Backend: uvicorn app.main:app --reload")
        print("   Frontend: python kivy_app/main.py")
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
