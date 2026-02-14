"""
Meal model for menu items.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Boolean, Column, String, DateTime, Numeric, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Meal(Base):
    """
    Meal model representing menu items available for ordering.
    """
    __tablename__ = "meals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    image_url = Column(String, nullable=True)
    available_month = Column(Date, index=True, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="meal")
    cart_items = relationship("CartItem", back_populates="meal")
    
    def __repr__(self):
        return f"<Meal {self.name}>"
