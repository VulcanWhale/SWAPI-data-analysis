import requests
import json
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def fetch_starships_data(api_url="https://swapi.dev/api/starships/"):
    """
    Fetch all starships data from the SWAPI endpoint with pagination handling.

    Args:
        api_url (str): The URL of the SWAPI starships endpoint. Defaults to the base URL.

    Returns:
        list: A list of dictionaries containing starship data.
    """
    starships = []
    while api_url:
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            data = response.json()
            
            # Append results to the starships list
            starships.extend(data.get("results", []))

            # Update the URL for the next page
            api_url = data.get("next")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            break

    return starships

def try_float_conversion(value):
    """Helper function to safely convert a value to float."""
    try:
        if value in ["unknown", "n/a", None]:
            return None
        return float(str(value).replace(",", ""))
    except ValueError:
        return None

def try_int_conversion(value):
    """Helper function to safely convert a value to int."""
    try:
        if value in ["unknown", "n/a", None]:
            return None
        return int(str(value).replace(",", ""))
    except ValueError:
        return None

def try_numeric_conversion(value, dtype):
    """Helper function to safely convert a value to a numeric type."""
    try:
        if value in ["unknown", "n/a", None]:
            return None
        return dtype(str(value).replace(",", ""))
    except ValueError:
        return None

def create_starships_dataframe(starships_data):
    """Create a DataFrame from starships data with proper numeric conversions."""
    df = pd.DataFrame(starships_data)
    
    # Convert numeric columns
    numeric_columns = {
        'cost_in_credits': float,
        'length': float,
        'max_atmosphering_speed': float,
        'crew': int,
        'passengers': int,
        'cargo_capacity': float,
        'hyperdrive_rating': float,
        'MGLT': int
    }
    
    for col, dtype in numeric_columns.items():
        df[col] = df[col].apply(lambda x: try_numeric_conversion(x, dtype))
    
    # Calculate derived metrics
    df['total_capacity'] = df['crew'].fillna(0) + df['passengers'].fillna(0)
    df['cost_per_capacity'] = df.apply(
        lambda row: row['cost_in_credits'] / row['total_capacity'] 
        if row['total_capacity'] > 0 and row['cost_in_credits'] is not None 
        else None, axis=1
    )
    
    return df

def analyze_cost_efficiency(data):
    """
    Analyze the cost efficiency of the starships by calculating the cost per person.
    
    Args:
        data (DataFrame): The starship data.
    
    Returns:
        DataFrame: The updated starship data with cost per person.
    """
    # Ensure 'cost_per_person' column exists
    if 'cost_per_person' not in data.columns:
        data['cost_per_person'] = None
    
    # Calculate cost per person
    def calculate_cost_per_person(row):
        total_people = (row['crew'] or 0) + (row['passengers'] or 0)
        if total_people > 0 and row['cost_in_credits'] is not None:
            return row['cost_in_credits'] / total_people
        return None
    
    # Apply the calculation
    data['cost_per_person'] = data.apply(calculate_cost_per_person, axis=1)
    
    # Handle NaN and infinite values
    data['cost_per_person'] = data['cost_per_person'].replace([np.inf, -np.inf], np.nan)
    data['cost_per_person'] = data['cost_per_person'].fillna(0)
    
    return data

def visualize_cost_efficiency(data):
    """
    Visualize cost per person for starships.
    """
    filtered_data = data[data['cost_per_person'].notna()].sort_values('cost_per_person')
    fig = px.bar(
        x=filtered_data['name'],
        y=filtered_data['cost_per_person'],
        title='Cost Efficiency of Starships',
        labels={'x': 'Starship', 'y': 'Cost per Person (Credits)'},
        template='plotly_dark'
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

def analyze_cargo_utilization(data):
    """
    Analyze cargo utilization of starships based on cargo capacity.

    Args:
        data (DataFrame): The starship data.

    Returns:
        DataFrame: The updated data with additional analysis results.
    """
    # Fill missing cargo_capacity with 0
    data['cargo_capacity'] = data['cargo_capacity'].fillna(0)

    # Calculate cargo to person ratio
    data['cargo_to_person_ratio'] = data.apply(
        lambda row: row['cargo_capacity'] / (row['crew'] + row['passengers']) 
        if (row['crew'] + row['passengers']) > 0 else 0, 
        axis=1
    )

    return data

def visualize_cargo_utilization(data):
    """
    Visualize cargo-to-person ratios of starships.
    """
    filtered_data = data[data['cargo_to_person_ratio'] > 0].sort_values('cargo_to_person_ratio')
    fig = px.bar(
        x=filtered_data['name'],
        y=filtered_data['cargo_to_person_ratio'],
        title='Cargo Utilization of Starships',
        labels={'x': 'Starship', 'y': 'Cargo to Person Ratio'},
        template='plotly_dark'
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

def calculate_custom_score(data):
    """
    Create a scoring index combining multiple metrics.

    Args:
        data (DataFrame): A DataFrame containing starship data.

    Returns:
        DataFrame: The updated data with the custom score for each starship.
    """
    # Fill missing values
    columns_to_fill = ['MGLT', 'hyperdrive_rating', 'crew', 'passengers', 'cargo_capacity']
    data[columns_to_fill] = data[columns_to_fill].fillna(0)

    # Calculate custom score with weights for each attribute
    data['custom_score'] = (
        (data['MGLT'] * 0.4) +                    # Weight of 0.4 for speed (MGLT)
        (data['hyperdrive_rating'] * 0.3) +       # Weight of 0.3 for hyperdrive rating
        ((data['crew'] + data['passengers']) * 0.2) +  # Weight of 0.2 for crew + passengers
        (data['cargo_capacity'] * 0.1)            # Weight of 0.1 for cargo capacity
    )
    
    return data

def visualize_starship_scores(data):
    """
    Visualize starships based on their custom scores.
    """
    sorted_data = data.sort_values('custom_score', ascending=False)
    fig = px.bar(
        x=sorted_data['name'],
        y=sorted_data['custom_score'],
        title='Starship Utility Scoring',
        labels={'x': 'Starship', 'y': 'Custom Score'},
        template='plotly_dark'
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

def analyze_starship_classes(df):
    """Analyze starship classes distribution and characteristics."""
    if df.empty:
        return go.Figure(), go.Figure()
    
    # Class distribution
    class_counts = df['starship_class'].value_counts()
    
    fig1 = px.pie(
        values=class_counts.values,
        names=class_counts.index,
        title='Starship Class Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig1.update_layout(
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig1

def analyze_cost_metrics(df):
    """Analyze cost-related metrics of starships."""
    if df.empty:
        return go.Figure(), go.Figure()
    
    # Cost vs Speed
    fig1 = px.scatter(
        df[df['cost_in_credits'] > 0],
        x='cost_in_credits',
        y='max_atmosphering_speed',
        color='starship_class',
        title='Cost vs Speed by Starship Class',
        labels={
            'cost_in_credits': 'Cost (credits)',
            'max_atmosphering_speed': 'Maximum Speed',
            'starship_class': 'Starship Class'
        },
        hover_data=['name']
    )
    
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Top 10 most expensive starships
    top_10_cost = df[df['cost_in_credits'] > 0].nlargest(10, 'cost_in_credits')
    
    fig2 = px.bar(
        top_10_cost,
        x='name',
        y='cost_in_credits',
        title='Top 10 Most Expensive Starships',
        labels={'name': 'Starship Name', 'cost_in_credits': 'Cost (credits)'},
        color='starship_class'
    )
    
    fig2.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig1, fig2

def analyze_capacity_metrics(df):
    """Analyze capacity-related metrics of starships."""
    if df.empty:
        return go.Figure(), go.Figure()
    
    # Passenger vs Cargo capacity
    fig1 = px.scatter(
        df[df['cargo_capacity'] > 0],
        x='passengers',
        y='cargo_capacity',
        color='starship_class',
        title='Passenger vs Cargo Capacity',
        labels={
            'passengers': 'Number of Passengers',
            'cargo_capacity': 'Cargo Capacity',
            'starship_class': 'Starship Class'
        },
        hover_data=['name']
    )
    
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Top 10 starships by total capacity
    df['total_capacity'] = df['passengers'] + df['crew']
    top_10_capacity = df.nlargest(10, 'total_capacity')
    
    fig2 = px.bar(
        top_10_capacity,
        x='name',
        y=['passengers', 'crew'],
        title='Top 10 Starships by Total Capacity',
        labels={'name': 'Starship Name', 'value': 'Number of People'},
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
    """Analyze performance-related metrics of starships."""
    if df.empty:
        return go.Figure(), go.Figure()
    
    # Speed vs Length
    fig1 = px.scatter(
        df[df['length'] > 0],
        x='length',
        y='max_atmosphering_speed',
        color='starship_class',
        title='Speed vs Length by Starship Class',
        labels={
            'length': 'Length (m)',
            'max_atmosphering_speed': 'Maximum Speed',
            'starship_class': 'Starship Class'
        },
        hover_data=['name']
    )
    
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Hyperdrive rating distribution
    fig2 = px.histogram(
        df[df['hyperdrive_rating'] > 0],
        x='hyperdrive_rating',
        title='Distribution of Hyperdrive Ratings',
        labels={'hyperdrive_rating': 'Hyperdrive Rating'},
        color='starship_class'
    )
    
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig1, fig2

def get_starship_stats(df):
    """Get summary statistics for starships."""
    if df.empty:
        return {}
    
    stats = {
        'total_starships': len(df),
        'unique_classes': df['starship_class'].nunique(),
        'avg_cost': df['cost_in_credits'].mean(),
        'avg_speed': df['max_atmosphering_speed'].mean(),
        'avg_capacity': df['total_capacity'].mean()
    }
    
    return stats

def main():
    """Main function to load and analyze starship data."""
    try:
        # Load data
        starships_data = fetch_starships_data()
        df = create_starships_dataframe(starships_data)
        
        if df.empty:
            print("No starship data available.")
            return
        
        # Perform analysis
        df = analyze_cost_efficiency(df)
        df = analyze_cargo_utilization(df)
        df = calculate_custom_score(df)
        
        # Generate visualizations
        class_fig = analyze_starship_classes(df)
        cost_fig1, cost_fig2 = analyze_cost_metrics(df)
        capacity_fig1, capacity_fig2 = analyze_capacity_metrics(df)
        perf_fig1, perf_fig2 = analyze_performance_metrics(df)
        
        # Get summary statistics
        stats = get_starship_stats(df)
        
        return {
            'dataframe': df,
            'class_distribution': class_fig,
            'cost_analysis': (cost_fig1, cost_fig2),
            'capacity_analysis': (capacity_fig1, capacity_fig2),
            'performance_analysis': (perf_fig1, perf_fig2),
            'summary_stats': stats
        }
        
    except Exception as e:
        print(f"Error in main function: {e}")
        return None

# Run the main function
if __name__ == "__main__":
    main()