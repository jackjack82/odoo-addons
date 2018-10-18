from odoo import models, fields, api
from odoo import exceptions



class WineProduct(models.Model):
    _inherit ='product.template'

    # selecting the type
    is_bottle = fields.Boolean('Bottiglia?')
    is_chemical = fields.Boolean('Prodotto chimico?')

    # data required by a bottle of wine
    wort_lot_id = fields.Many2one("wine.wort_lot", "Lotto mosto")
    bottling_date = fields.Date('Data imbottigliamento')

    @api.onchange('wort_lot_id')
    def setBottlingDate (self):
        self.bottling_date = self.wort_lot_id.bottling_date

    # chemical product fields
    type_id = fields.Char('Tipologia')


class Vineyard (models.Model):
    _name = 'wine.vineyard'

    name = fields.Char('Name')
    surface = fields.Float("Surface (ha)")
    ref_vineyard = fields.Many2one("wine.terrain", "Terreno")
    responsible = fields.Many2one("res.partner", "Responsible")

    biological_phase = fields.Selection([("seed", "Semina"), ("transfer", "Trapianto"),
                                         ("flower", "Fioritura")], "Fase del ciclo biologico")

    event_ids = fields.One2many('wine.event', 'vineyard_id', 'Products', copy='True')

    comments = fields.Html("Description")

    treatment_ids = fields.Many2many('wine.treatment', compute='_compute_treatment_ids', string='Treatments', )

    @api.multi
    @api.depends('name')
    def _compute_treatment_ids(self):
        for order in self:
            order.treatment_ids = self.env['wine.treatment'].search(
                [('vineyard_id', '=', order.name)]) if order.name else []


class TerrEvents (models.Model):
    _name = 'wine.event'

    date = fields.Date('Data')
    event = fields.Char('Evento')
    vineyard_id = fields.Many2one("wine.vineyard","Terreno")


class WineTool (models.Model):
    _name = 'wine.wine_tool'

    name = fields.Char('Name')
    ref_asset = fields.Many2one("account.asset.asset", "Dati contabili")
    responsible = fields.Many2one("res.partner", "Responsible")

    comments = fields.Html("Description")


class Treatment (models.Model):
    _name = 'wine.treatment'

    name = fields.Char("Name")
    date_execution = fields.Date("Date execution")
    reason = fields.Text('Motivazione')
    executor = fields.Many2one("res.partner", "Esecutore")
    vineyard_phase = fields.Selection([
        ("seed", "Pianto"),
        ("germ", "Germogliamento"),
        ("flower", "Fioritura"),
        ("alleg", "Allegagione"),
        ("invaiatura", "Invaiatura"),
        ("maturity", "Maturazione"),
        ("fall", "Caduta foglie"),
        ("rest", "Riposo vegetativo"),
          ], "Fase fenologica")

    treat_prod_ids = fields.One2many('wine.treat_prod', 'treatment_id', 'Products', copy='True')
    type_id = fields.Char('Tipologia')
    comments = fields.Html("Description")
    #vineyard_ids = fields.Many2one("vineyard", "vineyard")

    vineyard_id = fields.Many2one('wine.vineyard', 'Vineyards')


class TreatmProduct(models.Model):
    _name ='wine.treat_prod'

    product = fields.Many2one("product.product", "Prodotto")
    quantity = fields.Float('Quantita\'')
    treatment_id = fields.Many2one("wine.treatment", "Treatment")


class Tanks (models.Model):
    _name = 'wine.tank'

    name = fields.Char('Name')
    functioning = fields.Boolean("Attivo")
    related_tank = fields.Many2one("product.template", "Prodotto assoc.",
                                   attrs="{'required':[('active','!=','False')]}")
    tank_image = fields.Binary('Image')
    dimensions = fields.Float('Dimension')
    content = fields.Float('Content', compute="_setTotalAmount")

    wort_lot_ids = fields.One2many('wine.wort_lot', 'tank', 'Wort lots', copy='True')
    grape_lot_ids = fields.One2many('wine.grape_lot', 'tank', 'Grape lots', copy='True')
    repairment_ids = fields.One2many('wine.repairment', 'tank', 'Riparazioni', copy='True')

    @api.one
    def _setTotalAmount (self):
        if self.grape_lot_ids or self.wort_lot_ids:
            grape_lot_amount = 0
            for grape in self.grape_lot_ids:
                    if grape.stage_id != "closed":
                        grape_lot_amount += grape.quantity

            wort_lot_amount = 0
            for wort in self.wort_lot_ids:
                    if wort.stage_id != "closed":
                        wort_lot_amount += wort.quantity

            self.content = grape_lot_amount + wort_lot_amount

            return True


class Repairments (models.Model):
    _name = 'wine.repairment'

    name = fields.Char('Name', required=True)
    tank = fields.Many2one('wine.tank', 'Botte', required=True)
    date_repar= fields.Date('Date', required=True)


class vineyardAnalysis (models.Model):
    _name = 'wine.vineyard_analysis'

    name = fields.Char('Name', required=True)
    vineyard_id = fields.Many2one('wine.vineyard', 'vineyard', required=True)
    date_analysis= fields.Date('Date', required=True)

    sand = fields.Float("Sabbia (%)")
    lime = fields.Float("Limo (%)")
    clay = fields.Float("Argilla (%)")
    clay_method = fields.Many2one("wine.terr_method", "Metodo")

    ph = fields.Float("PH in acqua (U.pH)")
    ph_method = fields.Many2one("wine.terr_method", "Metodo")

    limestone_active = fields.Float("Calcare attivo (g/kg)")
    lim_act_method = fields.Many2one("wine.terr_method", "Metodo")

    limestone_total = fields.Float("Calcare totale (g/kg)")
    lim_tot_method = fields.Many2one("wine.terr_method", "Metodo")

    organ_carbon = fields.Float("Carbonio organico (g/kg)")
    organ_substance = fields.Float("Sostanza organica (g/kg)")
    org_sub_method = fields.Many2one("wine.terr_method", "Metodo")

    nitrogen = fields.Float("Azoto (g/kg)")
    nit_method = fields.Many2one("wine.terr_method", "Metodo")
    c_n_rel = fields.Float("Rapporto C/N")

    cationic_exch = fields.Float("Scambio cationico(meq/100g)")
    calcium_mg_kg = fields.Float("Calcio scamb. (mg/kg)")
    calcium_meq_hg = fields.Float("Calcio scamb.(meq/100g)")
    magnesium_mg_kg = fields.Float("Magnesio scamb. (mg/kg)")
    magnesium_meq_hg= fields.Float("Magnesio scamb. (meq/100g)")
    potassium_mg_kg = fields.Float("Potassio scamb. (mg/kg)")
    potassium_meq_hg = fields.Float("Potassio scamb. (meq/100g)")

    ca_mg = fields.Float("Ca/Mg")
    ca_kg = fields.Float("Ca/K")
    mg_kg = fields.Float("Mg/K")

    phosphorus = fields.Float("Fosforo assim. (mg/kg)")
    phosph_anhydride = fields.Float("Anidride Fosforica assim. (mg/kg)")
    ph_anhy_method = fields.Many2one("wine.terr_method", "Metodo")

    comments = fields.Html("Description")

class vineyardAnalysMeth (models.Model):
    _name = 'wine.terr_method'

    name = fields.Char('Name')


class WineAnalysis (models.Model):
    _name = 'wine.wine_analysis'

    name = fields.Char('Name', required=True)
    prod_sample = fields.Selection([("wine.bottle", "Bottiglia"), ("wort", "Mosto"),
                                    ("grape", "Lotto uva")], "Oggetto dell'analisi")
    sampling_date = fields.Date('Data')
    sampling_partner = fields.Many2one('res.partner', 'Da')

    # in case of bottle sampling, additional fields are required.
    bottle_lot = fields.Char("Bottiglia")

    # this field is to link the lab analysis to a GRAPE LOT >> Change it!
    sample_bottle = fields.Many2one('product.product', 'Bott. campione')
    grape_lot = fields.Many2one('wine.grape_lot', 'Grape Lot')
    wort_lot = fields.Many2one('wine.wort_lot', 'Mosto')

    package_sample = fields.Char('Partita')
    gross_weight = fields.Float("Peso lordo")
    net_weight = fields.Float("Peso netto")
    client_id = fields.Many2one('res.partner', 'Cliente')
    client_country = fields.Char('Paese dest.')

    result=fields.Boolean('Idoneita\'')

    @api.onchange('client_id')
    def setCountry (self):
        self.client_country = self.client_id.country_id


    # analysisi fields

    relative_density = fields.Float("Densita\' 20*C")
    relative_density_meth = fields.Many2one('wine.wine_method', 'M.')
    relative_density_uncert = fields.Float('I.')

    alcohol_devel = fields.Float("Titolo alcolometrico volumico (%)")
    alcohol_devel_meth = fields.Many2one('wine.wine_method', 'M.')
    alcohol_devel_uncert = fields.Float('I.')

    sugars = fields.Float("Zuccheri (glucosio + fruttosio)")
    sugars_meth = fields.Many2one('wine.wine_method', 'M.')
    sugars_uncert = fields.Float('I.')

    alcohol_degree = fields.Float("Titolo alcolometrico volumico totale (%)")
    alcohol_degree_meth = fields.Many2one('wine.wine_method', 'M.')
    alcohol_degree_uncert = fields.Float('I.')

    tot_acidity = fields.Float("Acidita\' totale (%)")
    tot_acidity_meth = fields.Many2one('wine.wine_method', 'M.')
    tot_acidity_uncert = fields.Float('I.')

    volat_acidity = fields.Float("Acidita\' volatile (%)")
    volat_acidity_meth = fields.Many2one('wine.wine_method', 'M.')
    volat_acidity_uncert = fields.Float('I.')

    tot_dry = fields.Float("Estratto secco totale (%)")
    tot_dry_meth = fields.Many2one('wine.wine_method', 'M.')
    tot_dry_uncert = fields.Float('I.')

    extr_no_sugar = fields.Float("Estratto non riduttore (%)")
    extr_no_sugar_meth = fields.Many2one('wine.wine_method', 'M.')
    extr_no_sugar_uncert = fields.Float('I.')

    tot_ashes = fields.Float("Ceneri (%)")
    tot_ashes_meth = fields.Many2one('wine.wine_method', 'M.')
    tot_ashes_uncert = fields.Float('I.')

    chlorides = fields.Float("Cloruri (%)")
    chlorides_meth = fields.Many2one('wine.wine_method', 'M.')
    chlorides_uncert = fields.Float('I.')

    sulphates = fields.Float("Solfati (%)")
    sulphates_meth = fields.Many2one('wine.wine_method', 'M.')
    sulphates_uncert = fields.Float('I.')

    tot_sulph_diox = fields.Float("Anidride solforosa totale (%)")
    tot_sulph_diox_meth = fields.Many2one('wine.wine_method', 'M.')
    tot_sulph_diox_uncert = fields.Float('I.')

    overpressure = fields.Float("Sovrappressione CO2")
    overpressure_meth = fields.Many2one('wine.wine_method', 'M.')
    overpressure_uncert = fields.Float('I.')

    comments = fields.Html("Description")


class WineAnalysMeth (models.Model):
    _name = 'wine.wine_method'

    name = fields.Char('Name')


class Additions (models.Model):
    _name = 'wine.additions'
    _description = "Additions to wort or wine"

    name = fields.Char('Name', required=True)

    date_exec = fields.Date('Data', required=True)
    additive = fields.Many2one("product.product", "Aggiunta", required=True)
    quantity = fields.Float("Quantita\' (Kg)", required=True)

    grape_lot = fields.Many2one("wine.grape_lot", "Uva")
    wort_lot = fields.Many2one("wine.wort_lot", "Mosto")

    comments = fields.Text('Description')


class Meteo (models.Model):
    _name = 'wine.meteo'
    _description = "Data from meteo"

    date = fields.Date('Data', required=True)
    description = fields.Char('Descrizione', required=True)
    umidity = fields.Float('Umidity')


class Terrain (models.Model):
    _name = 'wine.terrain'

    name = fields.Char('Name')
    surface = fields.Float("Surface (ha)")
    description = fields.Text('Description?')
