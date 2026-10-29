# Running the Odoo 16 database `mydb` on Odoo 17

`mydb` was initialised by Odoo 16 (modules at `16.0.x`: base, web, web_editor, web_tour, base_import, bus, auth_totp, web_kanban_gauge, estate).
Odoo 17 cannot open it as-is, because the stored views and data use Odoo 16 conventions.
This is a **local development workaround**, not an official upgrade path. Community Odoo ships no migration scripts between major versions. For anything beyond a throwaway database, use OpenUpgrade or Odoo's upgrade service instead.

The original `mydb` was never modified. All work happened on a copy named `mydb_v17`.

## Steps

All commands run from the repo root with the venv active. `psql` here is PostgreSQL 18 (`C:\Program Files\PostgreSQL\18\bin`).

### 1. Copy the database and its filestore

```powershell
psql -h localhost -U odoo -d postgres -c "CREATE DATABASE mydb_v17 TEMPLATE mydb OWNER odoo"
Copy-Item -Recurse "$env:LOCALAPPDATA\OpenERP S.A\Odoo\filestore\mydb" "$env:LOCALAPPDATA\OpenERP S.A\Odoo\filestore\mydb_v17"
```

`CREATE DATABASE ... TEMPLATE` copies only the database rows. Without the filestore copy, Odoo logs `FileNotFoundError` for attachments.
`mydb` uses `C` for both collation and ctype, so it does not hit the Windows collation error described in the setup notes.

### 2. First attempt, which fails

```powershell
python odoo-bin -c odoo.conf -d mydb_v17 -u all --stop-after-init
```

```
ParseError: ... ir_module_category_data.xml:22
Since 17.0, the "attrs" and "states" attributes are no longer used.
View: res.users.groups (base.user_groups_view)
```

The Odoo 16 database still stores view architectures that use `attrs=` and `states=`. These are the base views and the inheriting views from `auth_totp`, `estate` and `web`.
While loading base data, Odoo regenerates and validates `base.user_groups_view` and the views that inherit from it, and the stale ones are rejected.

### 3. Delete the stale stored views

Delete every view whose stored XML contains `attrs=` or `states=`, along with any views inheriting from them. Their `ir_model_data` rows go too. The upgrade then recreates them from the Odoo 17 XML files (33 views in this database).

```sql
create temp table stale as
with recursive s as (
  select id from ir_ui_view where arch_db::text like '%attrs=%' or arch_db::text like '% states=%'
  union select v.id from ir_ui_view v join s on v.inherit_id = s.id)
select id from s;
delete from ir_model_data where model='ir.ui.view' and res_id in (select id from stale);
delete from ir_ui_view where id in (select id from stale);
```

This is safe only because none of these views were customised by hand. Check for Studio or manually edited views before doing this on a database that matters.

### 4. Fix the two remaining blockers

Re-running `-u all` then failed on two leftovers:

- **`web_kanban_gauge` is "inconsistent".** The module does not exist in Odoo 17. It is marked uninstalled so the upgrade ignores it.
- **`DELETE FROM res_groups WHERE id IN (12)` violates a foreign key.** The group `base.group_private_addresses` no longer exists in Odoo 17, but record rule `base.res_partner_rule_private_group` (id 11) still references it. Delete the rule so the obsolete group can be cleaned up.

```sql
delete from ir_model_data where model='ir.rule' and res_id=11;
delete from ir_rule where id=11;
update ir_module_module set state='uninstalled' where name='web_kanban_gauge';
```

### 5. Run the upgrade again

```powershell
python odoo-bin -c odoo.conf -d mydb_v17 -u all --stop-after-init
```

It finished with `Modules loaded.` and `Registry loaded`, with no errors.

## Result

All previously installed modules are now at `17.0.x`: base, web, web_editor, web_tour, base_import, bus, auth_totp and estate. The database has 5 users and 0 `estate.property` rows (there was no property data to carry over).

**Not verified:** I did not log in to the web UI on `mydb_v17`. Open it and check the estate menus, the property form and the user preferences screen before relying on it.

## Running it

```powershell
python odoo-bin -c odoo.conf -d mydb_v17
```

Do not run Odoo 17 against `mydb` itself. Odoo 17 would start upgrading it and leave it unusable for Odoo 16.
