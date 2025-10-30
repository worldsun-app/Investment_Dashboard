import os
import sys
from flask import Flask, jsonify, abort
from flask_cors import CORS
import plotly.io as pio
import plotly.express as px
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from InvestmentDashboard.models.fund_data import FundData
from InvestmentDashboard.utils import charts

base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

FUND_DATA_CACHE = {}

def get_fund_data(strategy_name):
    if strategy_name not in FUND_DATA_CACHE:
        try:
            FUND_DATA_CACHE[strategy_name] = FundData(strategy=strategy_name)
        except KeyError:
            return None
    return FUND_DATA_CACHE[strategy_name]

@app.route("/")
def health_check():
    """
    提供給雲端平台的健康檢查端點。
    """
    return jsonify({"status": "healthy", "message": "Investment Dashboard API is running."})

@app.route("/api/strategies/<strategy_name>/intro")
def get_strategy_intro(strategy_name):
    formatted_strategy_name = strategy_name.replace('-', ' ')
    fund_data = get_fund_data(formatted_strategy_name)
    if not fund_data:
        abort(404, description=f"Strategy '{formatted_strategy_name}' not found.")

    description, info_table, philosophy = fund_data.get_fund_intro_content()
    asset_allocation = fund_data.get_asset_allocation()
    sector_allocation = fund_data.get_sector_allocation()
    
    date, acc_ret = fund_data.get_components_acc_ret()
    risk_framework_list = fund_data.risk_framework_list
    
    asset_pie_fig = charts.make_asset_pie_figure(asset_allocation)
    sector_pie_fig = charts.make_sector_pie_figure(sector_allocation)
    components_bar_fig = charts.make_components_bar_figure(date, acc_ret)
    
    response_data = {
        "strategy_name": strategy_name,
        "description": description,
        "info_table": info_table,
        "philosophy": philosophy,
        "asset_allocation_chart": pio.to_json(asset_pie_fig),
        "sector_allocation_chart": pio.to_json(sector_pie_fig),
        "components_bar_chart": pio.to_json(components_bar_fig),
        "risk_framework": risk_framework_list
    }
    
    return jsonify(response_data)

@app.route("/api/strategies/<strategy_name>/performance")
def get_strategy_performance(strategy_name):
    formatted_strategy_name = strategy_name.replace('-', ' ')
    fund_data = get_fund_data(formatted_strategy_name)
    if not fund_data:
        abort(404, description=f"Strategy '{formatted_strategy_name}' not found.")

    metrics = fund_data.get_performance_metrics()
    performance_df = fund_data.get_performance_data()
    
    start_date = performance_df['date'].min()
    end_date = performance_df['date'].max()
    
    perf_fig = charts.make_performance_figure(performance_df, start_date, end_date)
    heatmap_fig = charts.make_heatmap_figure(fund_data.performance_df)

    response_data = {
        "strategy_name": strategy_name,
        "performance_metrics": metrics,
        "performance_chart": pio.to_json(perf_fig),
        "heatmap_chart": pio.to_json(heatmap_fig)
    }
    
    return jsonify(response_data)

@app.route("/api/test")
def test_endpoint():
    return jsonify({"message": "Hello from Investment Dashboard API!"})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
