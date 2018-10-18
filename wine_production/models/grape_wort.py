from odoo import models, fields, api
from odoo import exceptions


class GrapeLot (models.Model):
    _name = 'wine.grape_lot'
    _description = "Lot of grapes"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Name', required='True')
    quantity = fields.Float("Quantity (q)")
    tank = fields.Many2one("wine.tank", "Vasca o botte")

    stage_id = fields.Selection([
        ("collected", "Raccolta"),
        ("pig_rasp", "Pigiata/diraspata"),
        ("closed", "Chiuso")],
        "Stato", required='True')

    collection_date = fields.Date('Data raccolta')
    svination_date = fields.Date('Data svinatura')
    transformation_date = fields.Date('Data trasformazione')

    wine_analysis_ids = fields.One2many(
        'wine.wine_analysis', 'grape_lot', 'Analysis', copy='True')
    wine_additions_ids = fields.One2many(
        'wine.additions', 'grape_lot', 'Additions', copy='True')
    grape_origin_ids = fields.One2many('wine.grape_origin','grape_lot_id','Origins', copy='True')

    comments = fields.Text("Comments")

    @api.onchange('collection_date')
    def _setDate(self):
        if self.collection_date:
            self.svination_date = self.collection_date


class GrapeOrigin(models.Model):
    _name = 'wine.grape_origin'

    product = fields.Many2one("product.product", "Prodotto")
    quantity = fields.Float('Quantity (Kg)')
    grape_lot_id = fields.Many2one("wine.grape_lot", "Grape Lot")


class WortLot (models.Model):
    _name = 'wine.wort_lot'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Wort Lot"

    name = fields.Char('Name')
    quantity = fields.Float("Quantity (Lt)")
    tank = fields.Many2one("wine.tank", "Vasca")

    stage_id = fields.Selection([
        ("ferm_alc", "Ferm. Alc."),
        ("ferm_mal", "Ferm. Malol."),
        ("svinatura", "Svinatura"),
        ("affinamento", "Affinamento"),
        ("bottling", "Imbottigliamento"),
        ("closed", "Chiuso"),
        ], "Stato")

    alc_ferm_begin = fields.Date('Inizio ferm. alcol.')
    alc_ferm_end = fields.Date('Fine ferm. alcol.')

    malol_ferm_begin = fields.Date('Inizio ferm. malol.')
    malol_ferm_end = fields.Date('Fine ferm. malol.')

    svin_date = fields.Date('Data svinatura')

    affin_begin = fields.Date('Inizio affinamento')
    affin_end = fields.Date('Fine affinamento')
    affin_type = fields.Selection([
        ("ferm_alc", "Legno grande"),
        ("ferm_mal", "Legno piccolo"),
        ("svinatura", "Acciaio"),
        ("affinamento", "Cemento"),
        ], "Tipo affinamento")

    bottling_date = fields.Date('Data imbottigliamento')

    wine_analysis_ids = fields.One2many('wine.wine_analysis', 'wort_lot', 'Analysis', copy='True')
    wine_additions_ids = fields.One2many('wine.additions', 'wort_lot', 'Additions', copy='True')
    wort_lot_origin_ids = fields.One2many('wine.wort_origin', 'wort_lot_id', 'Origins', copy='True')
    refill_ids = fields.One2many('wine.refill', 'wort_lot_id', 'Ricolmaggi', copy='True')

    comments = fields.Text("Comments")

    @api.multi
    def action_draft(self):
        self.stage_id = 'wort1'

    @api.multi
    def action_confirm(self):
        self.stage_id = 'closed'


class WortOrigin(models.Model):
    _name = 'wine.wort_origin'

    product = fields.Many2one("wine.grape_lot", "Lotto uva")
    quantity = fields.Float('Quantity (Kg)')
    wort_lot_id = fields.Many2one("wine.wort_lot", "Wort Lot")


class ReFill(models.Model):
    _name = 'wine.refill'

    name = fields.Char("Name")
    date = fields.Date('Data')
    description = fields.Text('Descrizione')
    wort_lot_id = fields.Many2one("wine.wort_lot", "Wort Lot")
