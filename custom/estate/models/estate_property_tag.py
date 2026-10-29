from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer(string="Color Index")

    _sql_constraints = [
        ('check_name', 'UNIQUE(name)', 'The name must be unique')
    ]