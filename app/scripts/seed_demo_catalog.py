"""Seed dummy categories, brands, products/variants and suppliers for the demo store.

Run once per environment: `python -m app.scripts.seed_demo_catalog`
Idempotent — safe to re-run; existing rows (matched by slug/sku/name) are left alone.
"""

from app.db.session import SessionLocal
from app.models.brand import Brand
from app.models.category import Category
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.store import Store
from app.models.supplier import Supplier

STORE_SUBDOMAIN = "demo"

CATEGORIES = ["Apparel", "Accessories"]
BRANDS = ["Acme"]

SUPPLIERS = [
    {"name": "Chattogram Textile Mills", "phone": "+8801711000001", "email": "sales@ctm.example.com"},
    {"name": "Dhaka Leather Works", "phone": "+8801711000002", "email": "orders@dlw.example.com"},
]

# (name, category, sku_prefix, base_price, [(size, stock), ...])
PRODUCTS = [
    ("Classic Tee", "Apparel", "TEE-CLS", "550.00", [("S", 20), ("M", 15), ("L", 10)]),
    ("Denim Jacket", "Apparel", "JKT-DNM", "2200.00", [("S", 8), ("M", 5), ("L", 3)]),
    ("Cargo Pants", "Apparel", "PNT-CGO", "1450.00", [("S", 6), ("M", 4), ("L", 2)]),
    ("Canvas Tote Bag", "Accessories", "BAG-CNV", "450.00", [("One Size", 30)]),
    ("Leather Belt", "Accessories", "BLT-LTH", "650.00", [("S", 12), ("M", 9), ("L", 0)]),
    ("Wool Scarf", "Accessories", "SCF-WOL", "380.00", [("One Size", 25)]),
]


def slugify(name: str) -> str:
    return name.lower().replace(" ", "-")


def run() -> None:
    db = SessionLocal()
    try:
        store = db.query(Store).filter(Store.subdomain == STORE_SUBDOMAIN).first()
        if store is None:
            raise SystemExit(f"No store with subdomain '{STORE_SUBDOMAIN}' — run alembic migrations first.")

        category_by_name: dict[str, Category] = {}
        for name in CATEGORIES:
            slug = slugify(name)
            category = db.query(Category).filter(Category.store_id == store.id, Category.slug == slug).first()
            if category is None:
                category = Category(store_id=store.id, name=name, slug=slug)
                db.add(category)
                db.flush()
                print(f"Created category: {name}")
            category_by_name[name] = category

        brand_by_name: dict[str, Brand] = {}
        for name in BRANDS:
            slug = slugify(name)
            brand = db.query(Brand).filter(Brand.store_id == store.id, Brand.slug == slug).first()
            if brand is None:
                brand = Brand(store_id=store.id, name=name, slug=slug)
                db.add(brand)
                db.flush()
                print(f"Created brand: {name}")
            brand_by_name[name] = brand

        acme = brand_by_name["Acme"]
        for name, category_name, sku_prefix, price, variants in PRODUCTS:
            existing = db.query(Product).filter(Product.store_id == store.id, Product.name == name).first()
            if existing is not None:
                continue
            product = Product(
                store_id=store.id,
                category_id=category_by_name[category_name].id,
                brand_id=acme.id,
                name=name,
                description=f"{name} — a demo product seeded for local development.",
            )
            db.add(product)
            db.flush()
            for size, stock in variants:
                suffix = size.upper().replace(" ", "")
                db.add(
                    ProductVariant(
                        store_id=store.id,
                        product_id=product.id,
                        sku=f"{sku_prefix}-{suffix}",
                        price=price,
                        stock_quantity=stock,
                        attributes={"size": size},
                    )
                )
            print(f"Created product: {name} ({len(variants)} variant(s))")

        for supplier_in in SUPPLIERS:
            existing = db.query(Supplier).filter(Supplier.store_id == store.id, Supplier.name == supplier_in["name"]).first()
            if existing is not None:
                continue
            db.add(Supplier(store_id=store.id, **supplier_in))
            print(f"Created supplier: {supplier_in['name']}")

        db.commit()
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
