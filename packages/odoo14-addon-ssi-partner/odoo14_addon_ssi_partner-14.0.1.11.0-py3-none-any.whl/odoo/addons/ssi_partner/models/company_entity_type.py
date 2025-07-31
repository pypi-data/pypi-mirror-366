# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class CompanyEntityType(models.Model):
    _name = "company_entity_type"
    _inherit = ["mixin.master_data"]
    _description = "Company Entity Type"
