from flask import Blueprint, request, jsonify
from decimal import Decimal, InvalidOperation
from db import db
from models import FuelType, Inventory

bp = Blueprint("fuel_types", __name__, url_prefix="/fuel-types")

@bp.post("")
def create_fuel_type():
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    price = data.get("price", 0)

    if not name:
        return jsonify({"error": "name is required"}), 400
    try:
        price = Decimal(str(price))
    except InvalidOperation:
        return jsonify({"error": "price must be numeric"}), 400
    if price < 0:
        return jsonify({"error": "price must be >= 0"}), 400

    if FuelType.query.filter_by(name=name).first():
        return jsonify({"error": "fuel type already exists"}), 409

    ft = FuelType(name=name, price=price)
    db.session.add(ft)
    db.session.flush()  # get id before creating inventory
    inv = Inventory(fuel_type_id=ft.id, litres=Decimal("0"))
    db.session.add(inv)
    db.session.commit()
    return jsonify({"id": ft.id, "name": ft.name, "price": str(ft.price)}), 201

@bp.get("")
def list_fuel_types():
    items = FuelType.query.order_by(FuelType.id).all()
    return jsonify([{"id": x.id, "name": x.name, "price": str(x.price)} for x in items]), 200

@bp.patch("/<int:fuel_type_id>/price")
def update_price(fuel_type_id: int):
    data = request.get_json(force=True, silent=True) or {}
    if "price" not in data:
        return jsonify({"error": "price is required"}), 400
    try:
        new_price = Decimal(str(data["price"]))
    except InvalidOperation:
        return jsonify({"error": "price must be numeric"}), 400
    if new_price < 0:
        return jsonify({"error": "price must be >= 0"}), 400

    ft = FuelType.query.get(fuel_type_id)
    if not ft:
        return jsonify({"error": "fuel type not found"}), 404

    ft.price = new_price
    db.session.commit()
    return jsonify({"id": ft.id, "name": ft.name, "price": str(ft.price)}), 200
