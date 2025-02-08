import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import plotly.express as px
import json

# Configure logging
logging.basicConfig(
    level=logging.ERROR,  # Set the logging level to ERROR
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)


# Global variables
API_URL = "https://swapi.dev/api/species/"
CSV_FILE = "species_data.csv"

# SECTION 1: Data Fetching
def fetch_species_data():
    """
    Fetch all species data from the SWAPI API.
    
    Returns:
        list: A list of species data.
    """
    try:
        with open('species_cache.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        url = "https://swapi.dev/api/species/"
        all_species = []
        
        while url:
            response = requests.get(url)
            data = response.json()
            all_species.extend(data['results'])
            url = data.get('next')
        
        with open('species_cache.json', 'w') as f:
            json.dump(all_species, f)
        
        return all_species

# SECTION 2: Data Cleaning
def create_species_dataframe(species_data):
    """
    Create and clean the species DataFrame.
    
    Args:
        species_data (list): List of species data from SWAPI.
    
    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    if not species_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(species_data)
    
    # Fill missing values
    df['homeworld'].fillna('Unknown', inplace=True)
    df['language'].fillna('Unknown', inplace=True)
    df['classification'].fillna('Unknown', inplace=True)
    df['designation'].fillna('Unknown', inplace=True)
    
    # Convert numeric columns
    numeric_columns = ['average_height', 'average_lifespan']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col].replace('unknown', '0'), errors='coerce')
    
    return df

# SECTION 3: Data Storage and Loading
def load_or_fetch_species_data():
    """
    Load species data from a CSV file if it exists, otherwise fetch it from the API.
    
    Returns:
        pd.DataFrame: Cleaned DataFrame containing species data.
    """
    if os.path.exists(CSV_FILE):
        print(f"Loading species data from {CSV_FILE}...")
        df = pd.read_csv(CSV_FILE)
    else:
        print("Fetching species data from API...")
        raw_data = fetch_species_data()
        print("Cleaning data...")
        df = create_species_dataframe(raw_data)
        print(f"Saving cleaned data to {CSV_FILE}...")
        df.to_csv(CSV_FILE, index=False)
    return df

# SECTION 4: Data Analysis
def count_species(df):
    """
    Count the total number of species available in the dataset.
    
    Args:
        df (pd.DataFrame): DataFrame containing species data.
    
    Returns:
        int: Total number of species.
    """
    total_species = df.shape[0]  # Count the number of rows, which corresponds to the number of species
    print(f"Total number of species: {total_species}")
    return total_species

def analyze_classification_distribution(df):
    """
    Analyze and visualize the distribution of species classifications.
    
    Args:
        df (pd.DataFrame): DataFrame containing species data.
    """
    figures = {}
    
    # Normalize classifications
    df['classification'] = df['classification'].str.lower().replace({
        'mammals': 'mammal',
        'reptilian': 'reptile'
    })
    
    # Classification pie chart
    class_counts = df['classification'].value_counts()
    
    figures['pie'] = px.pie(
        values=class_counts.values,
        names=class_counts.index,
        title='Species Classification Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    figures['pie'].update_layout(
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Classification vs average height
    avg_height = df.groupby('classification')['average_height'].mean().sort_values(ascending=False)
    
    figures['bar'] = px.bar(
        x=avg_height.index,
        y=avg_height.values,
        title='Average Height by Classification',
        labels={'x': 'Classification', 'y': 'Average Height (cm)'},
        color=avg_height.values,
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

def analyze_lifespan_distribution(df):
    """
    Analyze and visualize the lifespan trends of species.
    
    Args:
        df (pd.DataFrame): DataFrame containing species data.
    """
    figures = {}
    
    # Filter valid lifespan data
    lifespan_df = df[df['average_lifespan'] > 0].copy()
    
    # Top 10 longest-living species
    top_lifespan = lifespan_df.nlargest(10, 'average_lifespan')
    
    figures['bar'] = px.bar(
        top_lifespan,
        x='name',
        y='average_lifespan',
        title='Top 10 Longest-Living Species',
        labels={'name': 'Species', 'average_lifespan': 'Average Lifespan (years)'},
        color='average_lifespan',
        color_continuous_scale='Viridis'
    )
    
    figures['bar'].update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Lifespan vs height scatter plot
    figures['scatter'] = px.scatter(
        df[df['average_lifespan'] > 0],
        x='average_height',
        y='average_lifespan',
        title='Species Lifespan vs Height',
        color='classification',
        hover_data=['name'],
        labels={
            'average_height': 'Average Height (cm)',
            'average_lifespan': 'Average Lifespan (years)',
            'classification': 'Classification'
        }
    )
    
    figures['scatter'].update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return figures

def analyze_language_distribution(df):
    """
    Analyze and visualize the distribution of species languages.
    
    Args:
        df (pd.DataFrame): DataFrame containing species data.
    """
    figures = {}
    
    # Count language frequencies
    language_counts = df['language'].value_counts().head(10)
    
    figures['bar'] = px.bar(
        x=language_counts.index,
        y=language_counts.values,
        title='Most Common Languages',
        labels={'x': 'Language', 'y': 'Number of Species'},
        color=language_counts.values,
        color_continuous_scale='Viridis'
    )
    
    figures['bar'].update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Language distribution pie chart
    figures['pie'] = px.pie(
        values=language_counts.values,
        names=language_counts.index,
        title='Language Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    figures['pie'].update_layout(
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return figures

def analyze_physical_traits(df):
    """
    Analyze and visualize the physical traits of species.
    
    Args:
        df (pd.DataFrame): DataFrame containing species data.
    """
    figures = {}
    
    # Height distribution by designation
    height_by_designation = df.groupby('designation')['average_height'].mean().sort_values(ascending=False)
    
    figures['bar'] = px.bar(
        x=height_by_designation.index,
        y=height_by_designation.values,
        title='Average Height by Designation',
        labels={'x': 'Designation', 'y': 'Average Height (cm)'},
        color=height_by_designation.values,
        color_continuous_scale='Viridis'
    )
    
    figures['bar'].update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Create a color characteristics summary
    color_data = []
    for col in ['skin_colors', 'hair_colors', 'eye_colors']:
        colors = df[col].str.split(',').explode().str.strip()
        top_colors = colors.value_counts().head(5)
        for color, count in top_colors.items():
            color_data.append({
                'feature': col.replace('_colors', '').title(),
                'color': color,
                'count': count
            })
    
    color_df = pd.DataFrame(color_data)
    
    figures['color_bar'] = px.bar(
        color_df,
        x='color',
        y='count',
        color='feature',
        title='Most Common Colors by Feature',
        barmode='group',
        labels={'color': 'Color', 'count': 'Number of Species', 'feature': 'Feature'}
    )
    
    figures['color_bar'].update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return figures

# SECTION 5: Main Function
def main():
    """
    Main function to load data and perform analysis.
    """
    # Load species data
    species_df = load_or_fetch_species_data()

    # Analyze classification distribution
    classification_figs = analyze_classification_distribution(species_df)
    classification_figs['pie'].show()
    classification_figs['bar'].show()

    # Analyze designation distribution
    designation_counts = species_df['designation'].value_counts()
    print("Designation Distribution:")
    print(designation_counts)

    # Count total species
    count_species(species_df)

    # Analyze lifespan distribution
    lifespan_figs = analyze_lifespan_distribution(species_df)
    lifespan_figs['bar'].show()
    lifespan_figs['scatter'].show()

    # Analyze language distribution
    language_figs = analyze_language_distribution(species_df)
    language_figs['bar'].show()
    language_figs['pie'].show()

    # Analyze physical traits
    physical_traits_figs = analyze_physical_traits(species_df)
    physical_traits_figs['bar'].show()
    physical_traits_figs['color_bar'].show()

if __name__ == "__main__":
    main()