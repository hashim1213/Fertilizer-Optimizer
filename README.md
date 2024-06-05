# Fertilizer Optimization for Canola

This project is a web application designed to optimize fertilizer blends for canola crops based on crop yield goals and soil data. Users can input information such as previous yield, yield goal, soil organic matter, and optionally soil test data to calculate the optimal fertilizer blend, application rates, and fertilizer requirements.

## Features

- Input previous yield, yield goal, and soil organic matter percentage.
- Option to include soil test data for N, P2O5, K2O, and S.
- Calculate optimal fertilizer blend and application rates.
- Display total cost, application rates, and fertilizer requirements.

## Prerequisites

- Python 3.6 or higher
- Flask
- PuLP (Linear Programming library)

## Installation

1. **Clone the repository to your local machine:**
   ```bash
   git clone https://github.com/your-username/fertilizer-optimization.git
   ```
2. Navigate to the project directory:
```bash
cd fertilizer-optimization
```
3. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   #Windows 
   `venv\Scripts\activate`
   ```
4. Install PuLp, GLPK and Flask
   
#Run the App
```bash
python app.py
```
#open your browser and navigate to 
```bash
http://127.0.0.1:5000/
```
#Fill out the form with the required information:
- Previous Yield (bushels/acre)
- Yield Goal (bushels/acre)
- Soil Organic Matter (%)
- Use Soil Test Data? (Yes/No)
- If "Yes" selected, input Soil Test Data (lb/acre) for N, P2O5, K2O, and S.
- Click on the "Calculate" button to get the optimal fertilizer blend, application rates, and fertilizer requirements.
#File Structure
-  app.py - Main application file that runs the Flask server.
-  templates/index.html - HTML template for the web page.

