import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import logging
import streamlit as st

def fetch_planets_data():
    """Fetch planets data from local cache or SWAPI."""
    try:
        with open('planets_cache.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        url = "https://swapi.dev/api/planets/"
        all_planets = []
        
        while url:
            response = requests.get(url)
            data = response.json()
            all_planets.extend(data['results'])
            url = data.get('next')
        
        with open('planets_cache.json', 'w') as f:
            json.dump(all_planets, f)
        
        return all_planets

def safe_numeric_conversion(value):
    """Safely convert string values to numeric, handling 'unknown' values."""
    try:
        if value in ['unknown', '', None]:
            return 0
        return float(str(value).replace(',', ''))
    except (ValueError, TypeError):
        return 0

def create_planets_dataframe(planets_data):
    """Create and clean the planets DataFrame."""
    if not planets_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(planets_data)
    
    # Convert numeric columns
    numeric_columns = ['population', 'diameter', 'surface_water', 'orbital_period', 'rotation_period']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].apply(safe_numeric_conversion)
    
    return df

def analyze_climate_distribution(df):
    """Create visualizations for climate analysis."""
    figures = {}
    
    # Pie chart of climate distribution
    climate_series = df['climate'].str.split(',').explode().str.strip()
    climate_counts = climate_series.value_counts().head(8)
    
    figures['pie'] = px.pie(
        values=climate_counts.values,
        names=climate_counts.index,
        title='Planet Climate Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    figures['pie'].update_layout(
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Bar chart of climate vs average surface water
    climate_water = df.groupby('climate')['surface_water'].mean().sort_values(ascending=False).head(8)
    
    figures['bar'] = px.bar(
        x=climate_water.index,
        y=climate_water.values,
        title='Average Surface Water by Climate',
        labels={'x': 'Climate', 'y': 'Average Surface Water (%)'},
        color=climate_water.values,
        color_continuous_scale='Viridis'
    )
    
    figures['bar'].update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return figures

def analyze_population_metrics(df):
    """Create visualizations for population analysis."""
    figures = {}
    
    # Bar chart of most populated planets
    top_planets = df[df['population'] > 0].nlargest(10, 'population')
    
    figures['bar'] = px.bar(
        top_planets,
        x='name',
        y='population',
        title='Top 10 Most Populated Planets',
        color='population',
        color_continuous_scale='Viridis',
        labels={'name': 'Planet Name', 'population': 'Population'}
    )
    
    figures['bar'].update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Scatter plot of population vs diameter
    figures['scatter'] = px.scatter(
        df[df['population'] > 0],
        x='diameter',
        y='population',
        title='Population vs Planet Size',
        color='surface_water',
        hover_data=['name'],
        labels={
            'diameter': 'Diameter (km)',
            'population': 'Population',
            'surface_water': 'Surface Water (%)'
        },
        color_continuous_scale='Viridis'
    )
    
    figures['scatter'].update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return figures

def analyze_terrain_distribution(df):
    """Create visualizations for terrain analysis."""
    figures = {}
    
    # Process terrain data
    terrain_series = df['terrain'].str.split(',').explode().str.strip()
    terrain_counts = terrain_series.value_counts().head(10)
    
    # Bar chart of terrain types
    figures['bar'] = px.bar(
        x=terrain_counts.index,
        y=terrain_counts.values,
        title='Most Common Terrain Types',
        color=terrain_counts.values,
        color_continuous_scale='Viridis',
        labels={'x': 'Terrain Type', 'y': 'Number of Planets'}
    )
    
    figures['bar'].update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Pie chart of terrain diversity
    figures['pie'] = px.pie(
        values=terrain_counts.values,
        names=terrain_counts.index,
        title='Terrain Type Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    figures['pie'].update_layout(
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Create a copy of bar chart for treemap key to maintain compatibility
    figures['treemap'] = figures['bar']
    
    return figures

def analyze_characteristics(df):
    """Create visualizations for planet characteristics."""
    figures = {}
    
    # Scatter plot of diameter vs rotation period
    filtered_df = df[
        (df['diameter'] > 0) & 
        (df['rotation_period'] > 0) & 
        (df['rotation_period'] < 1000)
    ]
    
    figures['scatter1'] = px.scatter(
        filtered_df,
        x='diameter',
        y='rotation_period',
        title='Planet Size vs Rotation Period',
        color='surface_water',
        hover_data=['name'],
        labels={
            'diameter': 'Diameter (km)',
            'rotation_period': 'Rotation Period (hours)',
            'surface_water': 'Surface Water (%)'
        },
        color_continuous_scale='Viridis'
    )
    
    figures['scatter1'].update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Scatter plot of orbital period vs rotation period
    filtered_df = df[
        (df['orbital_period'] > 0) & 
        (df['rotation_period'] > 0) & 
        (df['orbital_period'] < 2000) & 
        (df['rotation_period'] < 1000)
    ]
    
    figures['scatter2'] = px.scatter(
        filtered_df,
        x='orbital_period',
        y='rotation_period',
        title='Orbital Period vs Rotation Period',
        color='surface_water',
        hover_data=['name'],
        labels={
            'orbital_period': 'Orbital Period (days)',
            'rotation_period': 'Rotation Period (hours)',
            'surface_water': 'Surface Water (%)'
        },
        color_continuous_scale='Viridis'
    )
    
    figures['scatter2'].update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Create a copy of scatter1 for scatter key to maintain compatibility
    figures['scatter'] = figures['scatter1']
    
    return figures

def main():
    planets_data = fetch_planets_data()
    df = create_planets_dataframe(planets_data)

    st.title("Planets Analysis")
    st.write("This app analyzes the characteristics of planets in the Star Wars universe.")

    st.header("Climate Distribution")
    climate_figures = analyze_climate_distribution(df)
    st.plotly_chart(climate_figures['pie'], use_container_width=True)
    st.plotly_chart(climate_figures['bar'], use_container_width=True)

    st.header("Population Metrics")
    population_figures = analyze_population_metrics(df)
    st.plotly_chart(population_figures['bar'], use_container_width=True)
    st.plotly_chart(population_figures['scatter'], use_container_width=True)

    st.header("Terrain Distribution")
    terrain_figures = analyze_terrain_distribution(df)
    st.plotly_chart(terrain_figures['treemap'], use_container_width=True)
    st.plotly_chart(terrain_figures['bar'], use_container_width=True)
    st.plotly_chart(terrain_figures['pie'], use_container_width=True)

    st.header("Planet Characteristics")
    planet_figures = analyze_characteristics(df)
    st.plotly_chart(planet_figures['scatter'], use_container_width=True)

if __name__ == "__main__":
    main()