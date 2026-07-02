import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ProductIdentifier(Base):
    __tablename__ = "product_identifiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    identifier_value = Column(String(150), nullable=False, index=True)
    identifier_type = Column(String(50), nullable=False, default="EAN13")
    is_primary = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product", back_populates="identifiers")


class ProductIngredient(Base):
    __tablename__ = "product_ingredients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_name = Column(String(255), nullable=False, index=True)
    ingredient_order = Column(Integer, nullable=True)
    percentage = Column(Numeric(5, 2), nullable=True)
    is_additive = Column(Boolean, nullable=False, default=False)
    additive_code = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    product = relationship("Product", back_populates="ingredients")


class ProductAllergen(Base):
    __tablename__ = "product_allergens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    allergen_name = Column(String(150), nullable=False, index=True)
    allergen_type = Column(String(100), nullable=True)
    contains = Column(Boolean, nullable=False, default=True)
    may_contain = Column(Boolean, nullable=False, default=False)
    source_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product", back_populates="allergens")


class ProductNutrition(Base):
    __tablename__ = "product_nutrition"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    serving_size = Column(String(100), nullable=True)
    calories = Column(Numeric(10, 2), nullable=True)
    protein_g = Column(Numeric(10, 2), nullable=True)
    carbohydrates_g = Column(Numeric(10, 2), nullable=True)
    sugar_g = Column(Numeric(10, 2), nullable=True)
    fat_g = Column(Numeric(10, 2), nullable=True)
    saturated_fat_g = Column(Numeric(10, 2), nullable=True)
    sodium_mg = Column(Numeric(10, 2), nullable=True)
    fiber_g = Column(Numeric(10, 2), nullable=True)
    raw_nutrition_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    product = relationship("Product", back_populates="nutrition")


class ProductStorageRequirement(Base):
    __tablename__ = "product_storage_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    storage_type = Column(String(50), nullable=False)
    min_temperature_c = Column(Numeric(5, 2), nullable=True)
    max_temperature_c = Column(Numeric(5, 2), nullable=True)
    humidity_notes = Column(Text, nullable=True)
    handling_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product", back_populates="storage_requirements")
