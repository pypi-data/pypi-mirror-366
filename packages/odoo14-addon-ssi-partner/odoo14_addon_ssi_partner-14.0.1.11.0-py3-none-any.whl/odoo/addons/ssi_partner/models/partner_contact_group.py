# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PartnerContactGroup(models.Model):
    _name = "partner_contact_group"
    _inherit = [
        "mixin.master_data",
    ]
    _description = "Partner Contact Group"

    commercial_contact_id = fields.Many2one(
        string="Commercial Contact",
        comodel_name="res.partner",
        domain=[
            ("parent_id", "=", False),
        ],
        required=True,
    )

    @api.depends(
        "commercial_contact_id",
    )
    def _compute_allowed_contact_ids(self):
        for record in self:
            result = []
            criteria = [("parent_id", "=", record.commercial_contact_id.id)]
            contact_ids = self.env["res.partner"].search(criteria).ids
            if contact_ids:
                result = contact_ids
            record.allowed_contact_ids = result

    allowed_contact_ids = fields.Many2many(
        string="Allowed Contacts",
        comodel_name="res.partner",
        compute="_compute_allowed_contact_ids",
        store=False,
        compute_sudo=True,
    )

    contact_ids = fields.Many2many(
        string="Contacts",
        comodel_name="res.partner",
        relation="rel_partner_contact_group_2_partner",
        column1="group_id",
        column2="partner_id",
        required=True,
    )

    @api.onchange(
        "commercial_contact_id",
    )
    def onchange_contact_ids(self):
        self.contact_ids = [(5, 0, 0)]
