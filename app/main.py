# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlmodel import Session, select

from .db_config import get_db_session
from . import database_queries as db_queries
from . import calculations as calc
# Import the new indicators module
from . import indicators as ind 
from app.modelsarch import StockDetailResponse, StockQuote, PriceChartResponseAPI, IndicatorSignal 
from app.models.fundamentals.masters import CompanyMaster
from app.models.stockprice.base import BSEAdjustedPrice 


app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://fundamental-frontend-demo.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/stocks", response_model=List[StockQuote])
async def get_all_stocks_summary(db: Session = Depends(get_db_session)):
    statement = select(CompanyMaster).limit(100) 
    companies_db = db.exec(statement).all()
    
    results = []
    for company_db in companies_db:
        if not company_db.fincode:
            continue

        latest_eod = db_queries.get_latest_eod_price_data(db, company_db.fincode)
        current_price_val = calc.get_current_price_val(latest_eod)
        
        outstanding_shares = db_queries.get_latest_outstanding_shares(db, company_db.fincode)
        market_cap_fmt = calc.calculate_market_cap_formatted(current_price_val, outstanding_shares)

        tech_signals_data = None
        debug_score = None
        price_history_db: List[BSEAdjustedPrice] = db_queries.get_price_history_for_chart(db, company_db.fincode, days_limit=252*1) 

        if price_history_db and len(price_history_db) > 60: 
            
            # Prepare data for indicators
            # Create a list of dicts to ensure alignment and handle Nones properly before passing
            ohlcv_data = []
            for p_item in price_history_db:
                # Ensure all required fields are present for a data point
                if p_item.open is not None and \
                   p_item.high is not None and \
                   p_item.low is not None and \
                   p_item.close is not None and \
                   p_item.volume is not None:
                    ohlcv_data.append({
                        "open": p_item.open, "high": p_item.high, "low": p_item.low,
                        "close": p_item.close, "volume": float(p_item.volume)
                    })
                else: # If any crucial part is missing, append Nones or skip
                      # For simplicity, indicators.py should handle internal Nones if passed as lists
                      # Here, we'll filter out incomplete daily data before creating separate lists
                      pass # Or append a structure with Nones if indicators can handle it robustly

            # Recreate individual lists ONLY from ohlcv_data to ensure they are aligned
            if len(ohlcv_data) > 60 : # Check if we still have enough complete data
                opens = [d['open'] for d in ohlcv_data]
                highs = [d['high'] for d in ohlcv_data]
                lows = [d['low'] for d in ohlcv_data]
                closes = [d['close'] for d in ohlcv_data]
                volumes = [d['volume'] for d in ohlcv_data]
                
                try:
                    tech_signals_data = ind.get_technical_analysis_summary(
                        opens=opens, highs=highs, lows=lows, closes=closes, volumes=volumes
                    )
                    debug_score = tech_signals_data.get("raw_score_debug")
                except Exception as e:
                    print(f"Error calculating indicators for {company_db.fincode}: {e}")
            else:
                print(f"Skipping indicators for {company_db.fincode} due to insufficient complete price data points after filtering Nones.")

        signals_to_send = None
        overall_signal_to_send = "Neutral"

        if tech_signals_data and tech_signals_data.get("signals"):
            signals_to_send = [IndicatorSignal(**s) for s in tech_signals_data["signals"]]
            overall_signal_to_send = tech_signals_data.get("overallSignal", "Neutral")

        results.append(
            StockQuote(
                id=str(company_db.fincode),
                name=company_db.compname or company_db.s_name or "N/A",
                symbol=company_db.symbol or company_db.scrip_name or "N/A",
                currentPrice=current_price_val,
                marketCapFormatted=market_cap_fmt,
                signals=signals_to_send,
                overallSignal=overall_signal_to_send,
                debug_score=debug_score 
            )
        )
    return results


@app.get("/api/stock/{fincode_str}", response_model=StockDetailResponse)
async def get_stock_details(fincode_str: str, db: Session = Depends(get_db_session)):
    try:
        fincode = int(fincode_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Fincode format.")

    company_master = db_queries.get_company_master_info(db, fincode)
    if not company_master:
        raise HTTPException(status_code=404, detail=f"Company with fincode {fincode} not found")

    industry_info = db_queries.get_industry_info(db, company_master.ind_code)
    profile_text = db_queries.get_company_profile_text(db, fincode)
    latest_eod = db_queries.get_latest_eod_price_data(db, fincode)
    prev_eod = db_queries.get_previous_eod_price_data(db, fincode)
    current_price = calc.get_current_price_val(latest_eod)
    price_change_obj = calc.get_price_change_details(latest_eod, prev_eod)
    day_hl_str = calc.get_day_high_low_val(latest_eod)
    high_52w, low_52w = db_queries.get_52_week_high_low(db, fincode)
    year_hl_str = calc.get_year_high_low_val(high_52w, low_52w)
    
    price_history_db_for_rsi_chart = db_queries.get_price_history_for_chart(db, fincode, days_limit=90) # Shorter history for RSI calc
    rsi_from_calc = calc.calculate_rsi_value(price_history_db_for_rsi_chart)

    latest_ratios = db_queries.get_latest_annual_ratios(db, fincode)
    ttm_eps_from_ratios = calc.get_safe_attr(latest_ratios, 'reported_eps', None)
    ttm_eps = ttm_eps_from_ratios if ttm_eps_from_ratios is not None else db_queries.get_ttm_eps_from_quarterly(db, fincode)
    
    stock_pe = calc.calculate_stock_pe_val(current_price, ttm_eps)
    book_value = calc.get_book_value_formatted_val(latest_ratios)
    annual_dps = calc.get_safe_attr(latest_ratios, 'dps', None)
    div_yield = calc.calculate_dividend_yield_formatted_val(current_price, annual_dps)
    roce = calc.get_roce_formatted_val(latest_ratios)
    roe = calc.get_roe_formatted_val(latest_ratios)
    face_value = calc.get_face_value_val(company_master)
    outstanding_shares = db_queries.get_latest_outstanding_shares(db, fincode)
    market_cap_fmt = calc.calculate_market_cap_formatted(current_price, outstanding_shares)

    quarterly_results_db = db_queries.get_quarterly_financial_results(db, fincode)
    annual_pl_db = db_queries.get_annual_profit_loss(db, fincode)
    # Fetch balance sheet data
    annual_bs_db = db_queries.get_annual_balance_sheet(db, fincode)
    annual_cf_db = db_queries.get_annual_cash_flow(db, fincode)
    shp_history_db = db_queries.get_shareholding_pattern_history(db, fincode, num_periods=8) # Fetch more periods for trend
    latest_shp_summary = shp_history_db[-1] if shp_history_db else db_queries.get_latest_shareholding_pattern(db,fincode) # Fallback if history is short

    annual_cf_db_cons = db_queries.get_annual_cash_flow(db, fincode, num_years=12) # Fetch consolidated

    cash_flows_table_data = calc.get_annual_cash_flow_table_data(annual_cf_db_cons)
    # For Cash Flow Chart (e.g., Operating CF and Net CF)
    cash_flows_chart_data_list = calc.format_annual_financials_for_chart(
        annual_cf_db_cons, # Pass the consolidated cash flow data
        {"cashFromOperating": "cash_from_operation", "netCashFlow": "net_cash_inflow_outflow"}
    )

    # For Ratios Section (Table and Charts)
    annual_ratios_history_db = db_queries.get_annual_ratios_history_consolidated(db, fincode, num_years=12) # Fetch more years for trend
    
    ratios_table_data = calc.get_annual_ratios_table_data(annual_ratios_history_db)
    
    # Chart for Debtor, Inventory, Payable Days
    efficiency_days_chart_data = calc.format_annual_ratios_for_chart(
        annual_ratios_history_db,
        {
            "Debtor Days": "receivable_days",
            "Inventory Days": "inventory_days",
            "Payable Days": "payable_days"
        }
    )
    # Chart for ROCE % Trend
    roce_trend_chart_data = calc.format_annual_ratios_for_chart(
        annual_ratios_history_db,
        {"ROCE %": "roce"}
    )

    
    raw_peer_masters = db_queries.get_peer_companies_basic(db, fincode, limit=10) # Increase peer limit
    peer_data_for_api = calc.format_peer_comparison_data_for_api(db, fincode, raw_peer_masters)

    annual_pl_db_cons = db_queries.get_annual_profit_loss(db, fincode, num_years=12) # Use CompanyProfitLossCons
    # Fetch all available annual consolidated ratios to look up dividend payout
    all_annual_ratios_db_cons = db_queries.get_all_annual_ratios_consolidated(db, fincode) # NEW FUNCTION NEEDED

    # ...
    # For the P&L table data:
    profit_and_loss_table_data = calc.get_annual_profit_loss_table_data(annual_pl_db_cons, all_annual_ratios_db_cons)

    annual_bs_db_cons = db_queries.get_annual_balance_sheet(db, fincode, num_years=12) 
    
    balance_sheet_table_data = calc.get_annual_balance_sheet_table_data(annual_bs_db_cons)
    balance_sheet_chart_data_map = calc.format_annual_balance_sheet_for_chart(annual_bs_db_cons) # New call

    # MODIFIED CALLS for chart data
    quarterly_financials_chart_data_list = calc.format_quarterly_financials_for_chart(
        quarterly_results_db, 
        {"sales": "net_sales", "netProfit": "net_profit"} # Target Key: Source Attribute from FinancialResultCons
    )
    quarterly_eps_chart_data_list = calc.format_quarterly_financials_for_chart(
        quarterly_results_db, 
        {"eps": "eps_basic"} # Target Key: Source Attribute
    )
    
    annual_financials_chart_data_list = calc.format_annual_financials_for_chart(
        annual_pl_db,
        {"sales": "net_sales", "netProfit": "profit_after_tax"} # Target: Source from CompanyProfitLoss
    )
    cash_flows_chart_data_list = calc.format_annual_financials_for_chart(
        annual_cf_db,
        {"cashFromOperating": "cash_from_operation", "netCashFlow": "net_cash_inflow_outflow"} # Target: Source from CompanyCashflow
    )
    
    # Price history for the main price chart (distinct from RSI calculation history)
    # Let get_daily_price_history_for_range in price-chart endpoint handle its own data needs.
    # For the embedded price chart on detail page, use a default range like 1 year from price_history_db_for_rsi_chart
    # or fetch separately if different range/granularity is needed.
    # Assuming priceVolumeChartData is for a general overview, using the 2-year data.
    price_history_for_main_chart = db_queries.get_price_history_for_chart(db, fincode, days_limit=365*2)

    print(f"---- RAW Quarterly Results for Fincode {fincode} ----")
    for r in quarterly_results_db:
        print(f"Date: {r.date_end}, Sales: {r.net_sales}, NP: {r.net_profit}, EPS: {r.eps_basic}, Type: {r.result_type}")
    print("----------------------------------------------------")


    return StockDetailResponse(
        id=str(fincode),
        name=company_master.compname or company_master.s_name or "N/A",
        symbol=company_master.symbol or company_master.scrip_name or "N/A",
        bseCode=str(company_master.scripcode) if company_master.scripcode else None,
        nseCode=company_master.symbol,
        sector=calc.get_safe_attr(industry_info, 'sector', "N/A"),
        industry=calc.get_safe_attr(industry_info, 'industry', "N/A"),
        marketCapFormatted=market_cap_fmt,
        currentPrice=current_price,
        priceChange=price_change_obj,
        yearHighLow=year_hl_str,
        dayHighLow=day_hl_str,
        stockPE=stock_pe,
        bookValueFormatted=book_value,
        dividendYieldFormatted=div_yield,
        roceFormatted=roce,
        roeFormatted=roe,
        faceValue=face_value,
        rsiValue=rsi_from_calc, 
        aboutInfo=profile_text or "Company profile not available.",
        keyPoints=[], 
        pros=[],
        cons=[],
        priceVolumeChartData=calc.format_price_volume_data_for_chart(price_history_for_main_chart),
        peerCmpChart={"data": [{"name": p["name"], "cmp": p.get("cmp")} for p in peer_data_for_api if p.get("cmp") not in [None, "N/A"]], "title": "Current Market Price (₹)", "dataKey": "cmp"},
        peerPeChart={"data": [{"name": p["name"], "pe": p.get("pe")} for p in peer_data_for_api if p.get("pe") not in [None, "N/A"]], "title": "Price-to-Earnings Ratio", "dataKey": "pe"},
        
        quarterlyFinancialsChartData=quarterly_financials_chart_data_list,
        quarterlyEPSChartData=quarterly_eps_chart_data_list,
        annualFinancialsChartData=annual_financials_chart_data_list,
      
        shareholdingPieData=calc.format_shareholding_for_pie_chart(latest_shp_summary),
        shareholdingTrendData=calc.format_shareholding_trend_for_chart(shp_history_db),
        
        peerComparison=peer_data_for_api,
        quarterlyResults=calc.get_quarterly_results_table_data(quarterly_results_db),
        profitAndLoss=profit_and_loss_table_data,
        # Add balance sheet table data
        balanceSheet=balance_sheet_table_data, 
        balanceSheetLiabilitiesChartData=balance_sheet_chart_data_map.get("liabilitiesChart", []), # New field
        balanceSheetAssetsChartData=balance_sheet_chart_data_map.get("assetsChart", []),         # New field
        cashFlows=cash_flows_table_data, # For the table
        cashFlowsChartData=cash_flows_chart_data_list, # For the chart
        shareholdingHistory=calc.get_shareholding_history_table_data(shp_history_db),

        ratiosTableData=ratios_table_data,                 # New
        efficiencyDaysChartData=efficiency_days_chart_data, # New
        roceTrendChartData=roce_trend_chart_data,           # New
    )


@app.get("/api/stock/{fincode_str}/price-chart", response_model=PriceChartResponseAPI)
async def get_stock_price_chart_data(
    fincode_str: str,
    time_range: str = "1y", # Default to 1 year
    db: Session = Depends(get_db_session)
):
    try:
        fincode = int(fincode_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Fincode format.")

    # Fetch appropriate amount of data. For a 200 DMA on a 1Y chart, you need 1Y + 200 trading days.
    # Let's adjust days_to_fetch based on time_range and max DMA period.
    # Max DMA is 200. A trading year is ~252 days.
    days_offset_for_dma = 200 * (365/252) # ~280 calendar days for 200 trading days
    
    # This part is handled by get_daily_price_history_for_range now.
    # That function should fetch enough preceding data if possible based on its internal logic.
    # The main thing is that `get_daily_price_history_for_range` returns enough data
    # *before* the start of the visible chart range to calculate the initial DMAs.

    price_history_db = db_queries.get_daily_price_history_for_range(
        db, fincode, time_range # This function should internally handle fetching sufficient data
    )
    
    if not price_history_db:
        return PriceChartResponseAPI(priceData=[]) # Return empty list if no data
        
    chart_data_points = calc.prepare_price_chart_data_with_dma(
        price_history_db, dma_periods=[50, 200] # Pass desired DMA periods
    )
    return PriceChartResponseAPI(priceData=chart_data_points)