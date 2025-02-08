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
    # Class distribution
    class_dist = df['starship_class'].value_counts()
    fig1 = px.pie(
        values=class_dist.values,
        names=class_dist.index,
        title='Distribution of Starship Classes',
        template='plotly_dark'
    )
    
    # Average cost by class
    avg_cost_by_class = df.groupby('starship_class')['cost_in_credits'].mean().sort_values(ascending=True)
    fig2 = px.bar(
        x=avg_cost_by_class.values,
        y=avg_cost_by_class.index,
        title='Average Cost by Starship Class',
        labels={'x': 'Average Cost (credits)', 'y': 'Starship Class'},
        template='plotly_dark'
    )
    
    return fig1, fig2

def analyze_cost_metrics(df):
    """Analyze cost-related metrics of starships."""
    if df.empty:
        return go.Figure(), go.Figure()

    # Cost vs Speed
    fig1 = px.scatter(
        df[df['cost_in_credits'] > 0],
        x='max_atmosphering_speed',
        y='cost_in_credits',
        title='Cost vs Speed',
        hover_data=['name'],
        template='plotly_dark',
        labels={
            'max_atmosphering_speed': 'Maximum Speed',
            'cost_in_credits': 'Cost (credits)',
            'name': 'Name'
        }
    )
    
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Top 10 most expensive starships
    top_expensive = df[df['cost_in_credits'] > 0].nlargest(10, 'cost_in_credits')
    fig2 = px.bar(
        top_expensive,
        x='name',
        y='cost_in_credits',
        title='Top 10 Most Expensive Starships',
        template='plotly_dark',
        labels={
            'name': 'Name',
            'cost_in_credits': 'Cost (credits)'
        }
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
        title='Passenger vs Cargo Capacity',
        hover_data=['name'],
        template='plotly_dark',
        labels={
            'passengers': 'Number of Passengers',
            'cargo_capacity': 'Cargo Capacity',
            'name': 'Name'
        }
    )
    
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Top 10 by total capacity
    df['total_capacity'] = df['passengers'].fillna(0) + df['crew'].fillna(0)
    top_capacity = df[df['total_capacity'] > 0].nlargest(10, 'total_capacity')
    
    fig2 = px.bar(
        top_capacity,
        x='name',
        y=['passengers', 'crew'],
        title='Top 10 by Total Capacity',
        template='plotly_dark',
        labels={
            'name': 'Name',
            'value': 'Number of People',
            'variable': 'Type'
        },
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
        title='Speed vs Length',
        hover_data=['name'],
        template='plotly_dark',
        labels={
            'length': 'Length (m)',
            'max_atmosphering_speed': 'Maximum Speed',
            'name': 'Name'
        }
    )
    
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Top 10 fastest
    top_speed = df[df['max_atmosphering_speed'] > 0].nlargest(10, 'max_atmosphering_speed')
    fig2 = px.bar(
        top_speed,
        x='name',
        y='max_atmosphering_speed',
        title='Top 10 Fastest',
        template='plotly_dark',
        labels={
            'name': 'Name',
            'max_atmosphering_speed': 'Maximum Speed'
        }
    )
    
    fig2.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig1, fig2

def get_starship_stats(df):
    """Get summary statistics for starships."""
    stats = {
        'Total Starships': len(df),
        'Average Cost': f"{df['cost_in_credits'].mean():,.0f} credits",
        'Average Speed': f"{df['MGLT'].mean():.1f} MGLT",
        'Total Passenger Capacity': f"{df['passengers'].sum():,.0f}",
        'Most Common Class': df['starship_class'].mode().iloc[0]
    }
    return stats

def main():
    # Fetch and clean the starship data
    starships_data = fetch_starships_data()
    starships_df = create_starships_dataframe(starships_data)
    
    # Cost Efficiency Analysis and Visualization
    starships_df = analyze_cost_efficiency(starships_df)
    visualize_cost_efficiency(starships_df)
    
    # Cargo Utilization Analysis and Visualization
    starships_df = analyze_cargo_utilization(starships_df)
    visualize_cargo_utilization(starships_df)
    
    # Custom Scoring and Visualization
    starships_df = calculate_custom_score(starships_df)
    visualize_starship_scores(starships_df)
    
    # Additional Analysis and Visualization
    fig1, fig2 = analyze_starship_classes(starships_df)
    fig1.show()
    fig2.show()
    
    fig1, fig2 = analyze_cost_metrics(starships_df)
    fig1.show()
    fig2.show()
    
    fig1, fig2 = analyze_capacity_metrics(starships_df)
    fig1.show()
    fig2.show()
    
    fig1, fig2 = analyze_performance_metrics(starships_df)
    fig1.show()
    fig2.show()
    
    stats = get_starship_stats(starships_df)
    for key, value in stats.items():
        print(f"{key}: {value}")

# Run the main function
if __name__ == "__main__":
    main()