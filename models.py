from datetime import datetime
from sqlalchemy import UniqueConstraint, CheckConstraint, func
from sqlalchemy.orm import validates
from db import db

# Use Numeric for money/volume. Adjust scales to your needs.
from sqlalchemy.types import Numeric

class FuelType(db.Model):
    __tablename__ = "fuel_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_fuel_price_nonnegative"),
    )

    @validates("price")
    def validate_price(self, key, value):
        if value is None or float(value) < 0:
            raise ValueError("Price must be >= 0")
        return value


class Inventory(db.Model):
    __tablename__ = "inventory"
    id = db.Column(db.Integer, primary_key=True)
    fuel_type_id = db.Column(db.Integer, db.ForeignKey("fuel_types.id", ondelete="CASCADE"), nullable=False, unique=True)
    litres = db.Column(Numeric(12, 3), nullable=False, default=0)

    fuel_type = db.relationship("FuelType", backref=db.backref("inventory_row", uselist=False))

    __table_args__ = (
        CheckConstraint("litres >= 0", name="ck_inventory_nonnegative"),
    )


class Sale(db.Model):
    __tablename__ = "sales"
    id = db.Column(db.Integer, primary_key=True)
    fuel_type_id = db.Column(db.Integer, db.ForeignKey("fuel_types.id", ondelete="SET NULL"))
    litres = db.Column(Numeric(12, 3), nullable=False)
    price_at_sale = db.Column(Numeric(10, 2), nullable=False)
    amount = db.Column(Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    fuel_type = db.relationship("FuelType")

    __table_args__ = (
        CheckConstraint("litres > 0", name="ck_sale_litres_positive"),
        CheckConstraint("price_at_sale >= 0", name="ck_sale_price_nonnegative"),
        CheckConstraint("amount >= 0", name="ck_sale_amount_nonnegative"),
    )
