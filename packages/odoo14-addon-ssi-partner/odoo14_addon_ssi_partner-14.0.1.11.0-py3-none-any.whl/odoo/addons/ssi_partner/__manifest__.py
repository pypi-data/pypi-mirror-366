# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=C8101
{
    "name": "Partner App",
    "version": "14.0.1.11.0",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "contacts",
        "partner_contact_personal_information_page",
        "partner_contact_nationality",
        "partner_contact_gender",
        "partner_contact_birthdate",
        "partner_contact_birthplace",
        "ssi_master_data_mixin",
    ],
    "data": [
        "security/ir_module_category_data.xml",
        "security/res_group_data.xml",
        "security/ir.model.access.csv",
        "menu.xml",
        "views/res_partner_views.xml",
        "views/res_partner_category_views.xml",
        "views/res_partner_title_views.xml",
        "views/res_partner_industry_views.xml",
        "views/res_country_views.xml",
        "views/res_country_state_views.xml",
        "views/res_country_group_views.xml",
        "views/res_bank_views.xml",
        "views/res_partner_bank_views.xml",
        "views/company_ownership_type_views.xml",
        "views/company_entity_type_views.xml",
        "views/partner_contact_group_views.xml",
        "views/res_partner_religion_views.xml",
        "views/res_partner_ethnicity_views.xml",
    ],
    "demo": [],
}
