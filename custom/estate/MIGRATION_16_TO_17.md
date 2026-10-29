# Migrating the estate module from Odoo 16 to Odoo 17

## What happened

The `estate` module was copied unchanged from an Odoo 16 setup into `custom/estate/` in this Odoo 17 checkout.
Installing it from the Apps menu failed with:

```
odoo.tools.convert.ParseError: while parsing .../custom/estate/views/estate_property_views.xml:47
Since 17.0, the "attrs" and "states" attributes are no longer used.
View: estate.property.form in estate/views/estate_property_views.xml
```

Odoo 17 removed the `attrs` and `states` view attributes. Instead, `invisible`, `readonly` and `required` now take a Python expression that is evaluated against the record's fields. Odoo 17 refuses to load a view that still uses the old attributes, so the module install is rolled back ("Failed to load registry").

## What was changed

Only the XML views needed changes. No Python models or security files were touched.

| File | Odoo 16 | Odoo 17 |
|------|---------|---------|
| `views/estate_property_views.xml` (Sold / Cancel buttons) | `states="new,offer_received,offer_accepted"` | `invisible="state not in ('new', 'offer_received', 'offer_accepted')"` |
| `views/estate_property_views.xml` (`garden_area`, `garden_orientation`) | `attrs="{'invisible': [('garden', '=', False)]}"` | `invisible="not garden"` |
| `views/estate_property_views.xml` (`offer_ids`) | `attrs="{'readonly': [('state', 'in', ('offer_accepted', 'sold', 'canceled'))]}"` | `readonly="state in ('offer_accepted', 'sold', 'canceled')"` |
| `views/estate_property_offer_views.xml` (Accept / Refuse buttons) | `attrs="{'invisible': [('status', '!=', False)]}"` | `invisible="status"` |

The offer-view buttons were not in the reported error, because Odoo stops at the first bad view. They used the same removed `attrs` attribute and would have failed next, so they were converted at the same time.

## How to apply the same fix elsewhere

1. Search the module for `attrs=` and `states=`.
2. Turn each domain into an expression:
   - `[('field', '=', False)]` becomes `not field`
   - `[('field', '!=', False)]` becomes `field`
   - `[('field', 'in', (...))]` becomes `field in (...)`
   - `states="a,b"` becomes `invisible="state not in ('a', 'b')"`
3. Reinstall or update with `python odoo-bin -c odoo.conf -d <db> -u estate`.

## Environment issues hit earlier in the same setup

These were not caused by the module, but they showed up while getting this checkout running on Windows with Python 3.10:

- **`libsass==0.20.1` failed to build.** There is no Windows wheel for it. Fix: `pip install libsass --only-binary=:all:` (0.23.0), then install the rest of `requirements.txt` without that line.
- **PostgreSQL error "collations with different collate and ctype values are not supported on this platform".** The database had been created with mismatched `LC_COLLATE` and `LC_CTYPE`. Fix: drop the database and recreate it with `TEMPLATE template0` and the same locale for both values.
