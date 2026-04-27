import pandas as pd

def calculate_surplus_deficit(supply_mw, demand_mw):
    """
    Computes surplus or deficit.
    Positive -> Surplus
    Negative -> Deficit
    """
    return supply_mw - demand_mw

def get_state_analysis(df, state=None):
    """
    Analyzes supply vs demand for states.
    Returns a list of dictionaries with analysis.
    """
    if state:
        df = df[df['state'].str.lower() == state.lower()]
    
    analysis_results = []
    
    for _, row in df.iterrows():
        surplus = calculate_surplus_deficit(row['supply_mw'], row['demand_mw'])
        status = 'Surplus' if surplus > 0 else 'Deficit' if surplus < 0 else 'Balanced'
        
        analysis_results.append({
            'state': row['state'],
            'year': row['year'],
            'month': row['month'],
            'demand_mw': row['demand_mw'],
            'supply_mw': row['supply_mw'],
            'surplus_mw': surplus,
            'status': status,
            'timestamp': row['timestamp']
        })
        
    return analysis_results

def get_seasonal_trends(df):
    """
    Analyzes historical data to determine in which phase of the year usage increases/decreases.
    Returns aggregated data by month.
    """
    if df.empty:
        return {}
    # Group by month and calculate average demand
    monthly_avg = df.groupby('month')['demand_mw'].mean().reset_index()
    monthly_avg = monthly_avg.sort_values('month')
    
    # Identify phases
    max_month = monthly_avg.loc[monthly_avg['demand_mw'].idxmax()]['month']
    min_month = monthly_avg.loc[monthly_avg['demand_mw'].idxmin()]['month']
    
    trend_summary = {
        'peak_month': int(max_month),
        'lowest_month': int(min_month),
        'monthly_data': monthly_avg.to_dict(orient='records')
    }
    
    return trend_summary
