# Bioreactor-model Python package

## Installation

`pip install bioreactor-model`

## Cell Composition functionality

Use `calc.CellComposition` class to obtain biomass formula and biomass formula weight.

`CellComposition(C_dry_weight, H_dry_weight, N_dry_weight, O_dry_weight, ash_fraction)` object requires as input:
1. `C_dry_weight`: dry weight percentage of carbon (between 0 and 100)
2. `H_dry_weight`: dry weight percentage of hydrogen (between 0 and 100)
3. `N_dry_weight`: dry weight percentage of nitrogen (between 0 and 100)
4. `O_dry_weight`: dry weight percentage of oxygen (between 0 and 100)
5. `ash_fraction`: dry weight percentage of ash (between 0 and 100)

These percentages must be between 0 and 100, not between 0 and 1. These are not absolute fractions but percentages.

### Estimating biomass formula

Function `CellComposition.biomass_formula()` returns dictionary with molecular formula of biomass. Dictionary keys are carbon, hydrogen, nitrogen and oxygen. Dictionary values are numbers corresponding to subscript value of each element in the biomass formula.

### Estimating biomass formula weight

Function `CellComposition.biomass_formula_weight()` returns molecular weight of biomass.

## Future development

Scale up parameters, fed-batch yield estimation, yield coefficient calculation, gas transfer estimation, oxygen transport and uptake rates will be added soon.