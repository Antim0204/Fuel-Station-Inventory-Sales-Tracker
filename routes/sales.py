from flask import Blueprint, request, jsonify
from decimal import Decimal, InvalidOperation
from sqlalchemy import select, text
from sqlalchemy.orm import joinedload
from db import db
from models import Inventory, FuelType, Sale

bp = Blueprint("sales", __name__, url_prefix="/sales")

@bp.post("")
def create_sale():
    data = request.get_json(force=True, silent=True) or {}
    fuel_type_id = data.get("fuel_type_id")
    litres = data.get("litres")

    if not isinstance(fuel_type_id, int):
        return jsonify({"error": "fuel_type_id must be integer"}), 400
    try:
        litres = Decimal(str(litres))
    except InvalidOperation:
        return jsonify({"error": "litres must be numeric"}), 400
    if litres is None or litres <= 0:
        return jsonify({"error": "litres must be > 0"}), 400

    # Use a transaction and row lock to avoid race conditions.
    with db.session.begin():
        ft = db.session.get(FuelType, fuel_type_id, with_for_update=False)
        if not ft:
            return jsonify({"error": "fuel type not found"}), 404

        # Lock inventory row FOR UPDATE to avoid overselling
        inv = db.session.execute(
            select(Inventory).where(Inventory.fuel_type_id == fuel_type_id).with_for_update()
        ).scalar_one_or_none()
        if not inv:
            return jsonify({"error": "inventory row missing for fuel type"}), 500

        if inv.litres < litres:
            return jsonify({"error": "insufficient stock", "available": str(inv.litres)}), 400

        price_at_sale = ft.price
        amount = (price_at_sale * litres).quantize(Decimal("0.01"))

        inv.litres = inv.litres - litres

        sale = Sale(
            fuel_type_id=fuel_type_id,
            litres=litres,
            price_at_sale=price_at_sale,
            amount=amount
        )
        db.session.add(sale)
        # session committed by context manager

    return jsonify({
        "id": sale.id,
        "fuel_type_id": fuel_type_id,
        "litres": str(sale.litres),
        "price_at_sale": str(sale.price_at_sale),
        "amount": str(sale.amount),
        "created_at": sale.created_at.isoformat() + "Z"
    }), 201


@bp.get("")
def list_sales():
    # Optional filters: ?from=YYYY-MM-DD&to=YYYY-MM-DD
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    q = Sale.query.options(joinedload(Sale.fuel_type)).order_by(Sale.created_at.desc())
    if date_from:
        q = q.filter(Sale.created_at >= date_from)
    if date_to:
        q = q.filter(Sale.created_at < date_to)

    items = q.all()
    resp = []
    total = Decimal("0.00")
    for s in items:
        total += s.amount
        resp.append({
            "id": s.id,
            "fuel_type_id": s.fuel_type_id,
            "fuel_name": s.fuel_type.name if s.fuel_type else None,
            "litres": str(s.litres),
            "price_at_sale": str(s.price_at_sale),
            "amount": str(s.amount),
            "created_at": s.created_at.isoformat() + "Z"
        })
    return jsonify({"sales": resp, "total_revenue": str(total)}), 200


# Bonus: simple daily summary /reports/daily?date=YYYY-MM-DD
@bp.get("/reports/daily")
def daily_report():
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "date is required (YYYY-MM-DD)"}), 400

    rows = db.session.execute(text("""
        SELECT ft.name, SUM(s.litres) AS litres, SUM(s.amount) AS revenue
        FROM sales s
        JOIN fuel_types ft ON ft.id = s.fuel_type_id
        WHERE CAST(s.created_at AS DATE) = :day
        GROUP BY ft.name
        ORDER BY ft.name
    """), {"day": date}).mappings().all()

    return jsonify([{
        "fuel_name": r["name"],
        "litres": str(r["litres"] or 0),
        "revenue": str(r["revenue"] or 0)
    } for r in rows]), 200
