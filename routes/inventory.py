from flask import Blueprint, request, jsonify
from decimal import Decimal, InvalidOperation
from sqlalchemy import select
from db import db
from models import Inventory, FuelType

bp = Blueprint("inventory", __name__, url_prefix="/inventory")

@bp.post("/refill")
def refill():
    data = request.get_json(force=True, silent=True) or {}
    fuel_type_id = data.get("fuel_type_id")
    litres = data.get("litres")

    if not isinstance(fuel_type_id, int):
        return jsonify({"error": "fuel_type_id must be integer"}), 400
    try:
        litres = Decimal(str(litres))
    except InvalidOperation:
        return jsonify({"error": "litres must be numeric"}), 400
    if litres <= 0:
        return jsonify({"error": "litres must be > 0"}), 400

    inv = Inventory.query.filter_by(fuel_type_id=fuel_type_id).first()
    if not inv:
        return jsonify({"error": "fuel type not found"}), 404

    inv.litres = inv.litres + litres
    db.session.commit()
    return jsonify({"fuel_type_id": fuel_type_id, "litres": str(inv.litres)}), 201

@bp.get("")
def get_levels():
    rows = db.session.execute(
        select(Inventory, FuelType).join(FuelType, FuelType.id == Inventory.fuel_type_id)
    ).all()
    resp = []
    for inv, ft in rows:
        resp.append({
            "fuel_type_id": ft.id,
            "fuel_name": ft.name,
            "price": str(ft.price),
            "litres": str(inv.litres),
        })
    return jsonify(resp), 200
