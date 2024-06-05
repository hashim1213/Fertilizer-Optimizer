from flask import Flask, render_template, request
from pulp import LpMinimize, LpProblem, LpVariable, lpSum, value, GLPK

app = Flask(__name__)

#Defines the fertilizers, their nutrient contents and prices (This is just an example)
fertilizers = {
    'Ammonium_nitrate': {'N': 34, 'P2O5': 0, 'K2O': 0, 'Ca': 0, 'Mg': 0, 'S': 0, 'cost': 910},
    'Ammonium_sulfate': {'N': 21, 'P2O5': 0, 'K2O': 0, 'Ca': 0, 'Mg': 0, 'S': 24, 'cost': 1100},
    'Anhydrous_ammonia': {'N': 82, 'P2O5': 0, 'K2O': 0, 'Ca': 0, 'Mg': 0, 'S': 0, 'cost': 1480},
    'Urea': {'N': 46, 'P2O5': 0, 'K2O': 0, 'Ca': 0, 'Mg': 0, 'S': 0, 'cost': 820},
    'Diammonium_phosphate': {'N': 18, 'P2O5': 46, 'K2O': 0, 'Ca': 0, 'Mg': 1, 'S': 0, 'cost': 970},
    'MAP': {'N': 11, 'P2O5': 52, 'K2O': 0, 'Ca': 0, 'Mg': 1, 'S': 0, 'cost': 65},
    'Potassium_chloride': {'N': 0, 'P2O5': 0, 'K2O': 60, 'Ca': 0, 'Mg': 0, 'S': 0, 'cost': 90},
    'Potassium_sulfate': {'N': 0, 'P2O5': 0, 'K2O': 52, 'Ca': 0, 'Mg': 0, 'S': 16, 'cost': 70},
    'Gypsum': {'N': 0, 'P2O5': 0, 'K2O': 0, 'Ca': 22, 'Mg': 0, 'S': 18, 'cost': 80},
}

#nutrient removal rates per acre
removal_rates_per_bushel = {
    'N': 1.87,
    'P2O5': 0.78,
    'K2O': 0.38,
    'S': 0.22
}
# calc nutriant removal rates
def calculate_nutrient_removal(previous_yield):
    removal_rates = {nutrient: previous_yield * rate for nutrient, rate in removal_rates_per_bushel.items()}
    return removal_rates
# calculates the required fert 
def integrated_calculation(previous_yield, yield_goal, OM):
    soil_OM_contribution_N = OM * 14 * 0.8
    removal_rates = calculate_nutrient_removal(previous_yield)
    uptake_rates = calculate_nutrient_uptake(yield_goal)
    uptake_rates['N'] = uptake_rates['N'] + soil_OM_contribution_N
    return uptake_rates
# upatake calc
def calculate_nutrient_uptake(yield_goal):
    uptake_per_bushel = {
        'N': 2.38,
        'P2O5': 0.90,
        'K2O': 2.93,
        'S': 0.86
    }
    uptake_rates = {nutrient: yield_goal * rate for nutrient, rate in uptake_per_bushel.items()}
    return uptake_rates
# calc rates 
def calculate_fertilizer_rate(required_rate, fertilizer, nutrient):
    nutrient_percentage = fertilizer[nutrient]
    return (required_rate * 100) / nutrient_percentage

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        previous_yield = float(request.form['previous_yield'])
        yield_goal = float(request.form['yield_goal'])
        OM = float(request.form['OM'])
        use_soil_data = request.form.get('use_soil_data') == 'yes'
        
        if use_soil_data:
            soil_test = {
                'N': float(request.form['soil_N']),
                'P2O5': float(request.form['soil_P2O5']),
                'K2O': float(request.form['soil_K2O']),
                'S': float(request.form['soil_S'])
            }
            removal_rates = calculate_nutrient_removal(previous_yield)
            required_fertilizer = {nutrient: max(0, removal_rates[nutrient] - soil_test.get(nutrient, 0)) for nutrient in removal_rates}
        else:
            required_fertilizer = integrated_calculation(previous_yield, yield_goal, OM)
        
        prob = LpProblem("FertilizerBlendOptimization", LpMinimize)
        fertilizer_vars = {name: LpVariable(name, lowBound=0, upBound=1000) for name in fertilizers}
        
        prob += lpSum([fertilizers[name]['cost'] * var for name, var in fertilizer_vars.items()]), "TotalCost"
        prob += lpSum([fertilizers[name]['N'] * var for name, var in fertilizer_vars.items()]) >= required_fertilizer['N'], "NRequirement"
        prob += lpSum([fertilizers[name]['P2O5'] * var for name, var in fertilizer_vars.items()]) >= required_fertilizer['P2O5'], "PRequirement"
        prob += lpSum([fertilizers[name]['K2O'] * var for name, var in fertilizer_vars.items()]) >= required_fertilizer['K2O'], "KRequirement"
        prob += lpSum([fertilizers[name]['S'] * var for name, var in fertilizer_vars.items()]) >= required_fertilizer['S'], "SRequirement"

        print("Problem Definition:", prob)

        prob.solve(GLPK(msg=True))

        results = {v.name: v.varValue for v in prob.variables()}
        total_cost = value(prob.objective)

        print("Results:", results)
        print("Total Cost:", total_cost)

        # calc the application rate for each fertilizer
        area_sqft = 43560  # 1 acre in square feet
        rates = {}
        for name, var in fertilizer_vars.items():
            if results[name] > 0:
                for nutrient in required_fertilizer:
                    if fertilizers[name][nutrient] > 0:
                        rate = calculate_fertilizer_rate(required_fertilizer[nutrient], fertilizers[name], nutrient)
                        if rate > 0:
                            rates[name] = rate

        print("Application Rates (lb/acre):", rates)

        return render_template('index.html', results=results, total_cost=total_cost, rates=rates, required_fertilizer=required_fertilizer, use_soil_data=use_soil_data)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)