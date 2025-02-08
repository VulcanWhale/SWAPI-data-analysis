import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

def fetch_vehicles_data():
    """Fetch vehicles data from local cache or SWAPI."""
    try:
        with open('vehicles_cache.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        url = "https://swapi.dev/api/vehicles/"
        all_vehicles = []
        
        while url:
            response = requests.get(url)
            data = response.json()
            all_vehicles.extend(data['results'])
            url = data.get('next')
        
        with open('vehicles_cache.json', 'w') as f:
            json.dump(all_vehicles, f)
        
        return all_vehicles

def create_vehicles_dataframe(vehicles_data):
    """Create and clean the vehicles DataFrame."""
    if not vehicles_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(vehicles_data)
    
    # Convert numeric fields with proper type handling
    numeric_fields = {
        'cost_in_credits': float,
        'length': float,
        'max_atmosphering_speed': float,
        'crew': int,
        'passengers': int,
        'cargo_capacity': float
    }
    
    for field, dtype in numeric_fields.items():
        df[field] = df[field].replace(['unknown', 'n/a'], None)
        df[field] = pd.to_numeric(df[field], errors='coerce')
        if dtype == int:
            df[field] = df[field].fillna(0).astype('Int64')  # Use Int64 to handle NaN
        else:
            df[field] = df[field].fillna(0.0)
    
    return df

def analyze_vehicle_classes(df):
    """Create visualizations for vehicle classes."""
    if df.empty:
        return go.Figure(), go.Figure()
    
    # Vehicle class distribution
    class_counts = df['vehicle_class'].value_counts()
    
    fig1 = px.pie(
        values=class_counts.values,
        names=class_counts.index,
        title='Vehicle Class Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig1.update_layout(
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Average speed by class
    avg_speed = df.groupby('vehicle_class')['max_atmosphering_speed'].mean().sort_values(ascending=False)
    
    fig2 = px.bar(
        x=avg_speed.index,
        y=avg_speed.values,
        title='Average Speed by Vehicle Class',
        labels={'x': 'Vehicle Class', 'y': 'Average Speed'},
        color=avg_speed.values,
        color_continuous_scale='Viridis'
    )
    
    fig2.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig1, fig2

def analyze_cost_metrics(df):
    """Create visualizations for cost analysis."""
    if df.empty:
        return go.Figure(), go.Figure()
    
    # Cost vs Speed
    fig1 = px.scatter(
        df[df['cost_in_credits'] > 0],
        x='cost_in_credits',
        y='max_atmosphering_speed',
        color='vehicle_class',
        title='Cost vs Speed by Vehicle Class',
        labels={
            'cost_in_credits': 'Cost (credits)',
            'max_atmosphering_speed': 'Maximum Speed',
            'vehicle_class': 'Vehicle Class'
        },
        hover_data=['name']
    )
    
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Top 10 most expensive vehicles
    top_10_cost = df[df['cost_in_credits'] > 0].nlargest(10, 'cost_in_credits')
    
    fig2 = px.bar(
        top_10_cost,
        x='name',
        y='cost_in_credits',
        title='Top 10 Most Expensive Vehicles',
        labels={'name': 'Vehicle Name', 'cost_in_credits': 'Cost (credits)'},
        color='vehicle_class'
    )
    
    fig2.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig1, fig2

def analyze_capacity_metrics(df):
    """Create visualizations for capacity analysis."""
    if df.empty:
        return go.Figure(), go.Figure()
    
    # Passenger vs Cargo capacity
    fig1 = px.scatter(
        df[df['cargo_capacity'] > 0],
        x='passengers',
        y='cargo_capacity',
        color='vehicle_class',
        title='Passenger vs Cargo Capacity',
        labels={
            'passengers': 'Number of Passengers',
            'cargo_capacity': 'Cargo Capacity',
            'vehicle_class': 'Vehicle Class'
        },
        hover_data=['name']
    )
    
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Top 10 vehicles by total capacity
    df['total_capacity'] = df['passengers'] + df['crew']
    top_10_capacity = df.nlargest(10, 'total_capacity')
    
    fig2 = px.bar(
        top_10_capacity,
        x='name',
        y=['passengers', 'crew'],
        title='Top 10 Vehicles by Total Capacity',
        labels={'name': 'Vehicle Name', 'value': 'Number of People'},
        barmode='stack'
    )
    
    fig2.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig1, fig2

def analyze_performance_metrics(df):
    """Create visualizations for vehicle performance."""
    if df.empty:
        return go.Figure(), go.Figure()
    
    # Speed vs Length
    fig1 = px.scatter(
        df[df['length'] > 0],
        x='length',
        y='max_atmosphering_speed',
        color='vehicle_class',
        title='Speed vs Length by Vehicle Class',
        labels={
            'length': 'Length (m)',
            'max_atmosphering_speed': 'Maximum Speed',
            'vehicle_class': 'Vehicle Class'
        },
        hover_data=['name']
    )
    
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Top 10 fastest vehicles
    top_10_speed = df.nlargest(10, 'max_atmosphering_speed')
    
    fig2 = px.bar(
        top_10_speed,
        x='name',
        y='max_atmosphering_speed',
        title='Top 10 Fastest Vehicles',
        labels={'name': 'Vehicle Name', 'max_atmosphering_speed': 'Maximum Speed'},
        color='vehicle_class'
    )
    
    fig2.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig1, fig2

def main():
    try:
        print("Fetching Vehicles data...")
        vehicles = fetch_vehicles_data()

        print("Cleaning data...")
        df = create_vehicles_dataframe(vehicles)

        # Call new analysis functions here
        print("Analyzing vehicle classes...")
        vehicle_class_figures = analyze_vehicle_classes(df)

        print("Analyzing cost metrics...")
        cost_figures = analyze_cost_metrics(df)

        print("Analyzing capacity metrics...")
        capacity_figures = analyze_capacity_metrics(df)

        print("Analyzing performance metrics...")
        performance_figures = analyze_performance_metrics(df)

        # Show the figures
        for figure in vehicle_class_figures:
            figure.show()

        for figure in cost_figures:
            figure.show()

        for figure in capacity_figures:
            figure.show()

        for figure in performance_figures:
            figure.show()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
