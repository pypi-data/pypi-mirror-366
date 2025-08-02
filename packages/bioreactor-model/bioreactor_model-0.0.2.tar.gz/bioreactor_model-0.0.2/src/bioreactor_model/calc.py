class CellComposition:
    def __init__(self, c_dry_wt, h_dry_wt, n_dry_wt, o_dry_wt, ash_fraction):
        self.percentage_dry_weights = {
            "carbon": c_dry_wt,
            "hydrogen": h_dry_wt,
            "nitrogen": n_dry_wt,
            "oxygen":   o_dry_wt
        }
        self.ash_fraction = ash_fraction
        self.atomic_weights = {
            "carbon": 12,
            "hydrogen": 1,
            "nitrogen": 14,
            "oxygen":   16
        }
    def biomass_formula (self):
        n_moles_100g = {
            "carbon": self.percentage_dry_weights['carbon']/self.atomic_weights['carbon'],
            "hydrogen": self.percentage_dry_weights['hydrogen']/self.atomic_weights['hydrogen'],
            "nitrogen": self.percentage_dry_weights['nitrogen']/self.atomic_weights['nitrogen'],
            "oxygen":   self.percentage_dry_weights['oxygen']/self.atomic_weights['oxygen']
        }
        moles_100g_norm = {
            "carbon": 1,
            "hydrogen": n_moles_100g["hydrogen"]/n_moles_100g["carbon"],
            "nitrogen": n_moles_100g["nitrogen"]/n_moles_100g["carbon"],
            "oxygen":   n_moles_100g["oxygen"]/n_moles_100g["carbon"]
        }
        return moles_100g_norm
    def biomass_formula_weight (self):
        bf = self.biomass_formula()
        formula_weight = (self.atomic_weights["carbon"]*bf["carbon"] + self.atomic_weights["nitrogen"]*bf["nitrogen"] + self.atomic_weights["oxygen"]*bf["oxygen"] + self.atomic_weights["hydrogen"]*bf["hydrogen"])
        p = 1 - (self.ash_fraction/100)
        formula_weight = formula_weight / p
        return formula_weight