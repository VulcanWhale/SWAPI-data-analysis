import requests
import logging
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('people_analysis.log'),
        logging.StreamHandler()
    ]
)

def get_cached_people_data(cache_file='people_cache.json'):
    """Retrieve cached data if available."""
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return None

def cache_people_data(people_data, cache_file='people_cache.json'):
    """Cache data to a file."""
    with open(cache_file, 'w') as f:
        json.dump(people_data, f)

def fetch_people_data():
    """Fetch people data from local cache or SWAPI."""
    try:
        with open('people_cache.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        url = "https://swapi.dev/api/people/"
        all_people = []
        
        while url:
            response = requests.get(url)
            data = response.json()
            all_people.extend(data['results'])
            url = data.get('next')
        
        with open('people_cache.json', 'w') as f:
            json.dump(all_people, f)
        
        return all_people

def create_people_dataframe(people_data):
    """
    Create a Pandas DataFrame from the people data.
    Converts numeric fields and handles missing values.
    """
    try:
        if not people_data:
            raise ValueError("No data available to create DataFrame.")
        
        df = pd.DataFrame(people_data)
        
        # Convert numeric fields safely
        numeric_fields = ['height', 'mass']
        for field in numeric_fields:
            df[field] = pd.to_numeric(df[field], errors='coerce')
        
        return df
    except Exception as e:
        logging.error(f"Failed to create DataFrame: {e}")
        return pd.DataFrame()

def validate_people_dataframe(df):
    """
    Validate the structure and content of the DataFrame.
    """
    required_columns = ['name', 'height', 'mass', 'gender', 'homeworld']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        logging.error(f"Missing required columns: {missing_columns}")
        return False
    
    if df.empty:
        logging.warning("DataFrame is empty.")
        return False
    
    return True

def analyze_gender_distribution(df):
    """Create an optimized gender distribution visualization."""
    gender_counts = df['gender'].value_counts()
    
    fig = px.pie(
        values=gender_counts.values,
        names=gender_counts.index,
        title='Character Gender Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def analyze_physical_attributes(df):
    """Create an optimized physical attributes visualization."""
    # Convert height and mass to numeric, handling 'unknown' values
    df['height'] = pd.to_numeric(df['height'].replace('unknown', '0'), errors='coerce')
    df['mass'] = pd.to_numeric(df['mass'].replace('unknown', '0'), errors='coerce')
    
    # Filter out zero values
    df_filtered = df[(df['height'] > 0) & (df['mass'] > 0)]
    
    fig = px.scatter(
        df_filtered,
        x='height',
        y='mass',
        title='Character Physical Attributes',
        labels={'height': 'Height (cm)', 'mass': 'Mass (kg)'},
        color='gender',
        hover_data=['name'],
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def analyze_homeworld_statistics(df):
    """Create an optimized homeworld statistics visualization."""
    # Clean up homeworld URLs to show just "Planet X"
    df['homeworld_clean'] = df['homeworld'].apply(lambda x: f"Planet {x.split('/')[-2]}" if pd.notnull(x) and 'planets' in str(x) else 'Unknown')
    
    # Get top 10 homeworlds
    homeworld_counts = df['homeworld_clean'].value_counts().head(10)
    
    fig = px.bar(
        x=homeworld_counts.index,
        y=homeworld_counts.values,
        title='Top 10 Character Homeworlds',
        labels={'x': 'Homeworld', 'y': 'Number of Characters'},
        color=homeworld_counts.values,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        showlegend=False,
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def analyze_film_appearances(df):
    """
    Analyze and visualize the number of films each character appears in.
    """
    try:
        # Count the number of films per character
        df['film_count'] = df['films'].apply(lambda films: len(films) if isinstance(films, list) else 0)

        # Top 10 characters by film appearances
        top_characters = df.nlargest(10, 'film_count')

        logging.info("Top characters by film appearances:")
        logging.info(top_characters[['name', 'film_count']])

        # Visualization
        fig = px.bar(
            top_characters,
            x='name',
            y='film_count',
            title='Top 10 Characters by Film Appearances',
            labels={'name': 'Character', 'film_count': 'Number of Films'}
        )
        fig.show()
    except Exception as e:
        logging.error(f"Failed to analyze film appearances: {e}")

def analyze_species_diversity_interactive(df):
    """
    Analyze species diversity with an interactive option to view character details.
    """
    try:
        species_counts = df['species'].apply(lambda species: species[0] if isinstance(species, list) and species else 'Unknown')
        species_counts = species_counts.value_counts()

        # Generate custom labels
        custom_labels = {original: f"Species {i + 1}" for i, original in enumerate(species_counts.index)}
        species_counts.index = species_counts.index.map(custom_labels)

        logging.info("Species diversity with custom labels:")
        logging.info(species_counts)

        # Visualization
        fig = px.pie(
            values=species_counts.values,
            names=species_counts.index,
            title='Species Diversity',
            labels={'label': 'Species', 'value': 'Count'}
        )
        fig.show()

        # Drill-down details
        selected_species = input("Enter the species label to view details (e.g., 'Species 1'): ").strip()
        if selected_species in custom_labels.values():
            original_species = [key for key, val in custom_labels.items() if val == selected_species][0]
            species_df = df[df['species'].apply(lambda x: original_species in x if isinstance(x, list) else False)]
            logging.info(f"Characters in {selected_species}:")
            logging.info(species_df[['name', 'height', 'mass']])
        else:
            logging.warning("Invalid species selection.")
    except Exception as e:
        logging.error(f"Failed to analyze interactive species diversity: {e}")

def analyze_numeric_correlations(df):
    """Analyze and visualize correlations between numeric fields."""
    try:
        # Convert height and mass to numeric
        df['height'] = pd.to_numeric(df['height'].replace('unknown', '0'), errors='coerce')
        df['mass'] = pd.to_numeric(df['mass'].replace('unknown', '0'), errors='coerce')
        
        # Create correlation matrix
        numeric_df = df[['height', 'mass']].copy()
        correlation = numeric_df.corr()
        
        # Create heatmap
        fig = px.imshow(
            correlation,
            title='Correlation between Physical Attributes',
            labels=dict(color="Correlation"),
            color_continuous_scale='RdBu'
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        return fig
    except Exception as e:
        logging.error(f"Failed to analyze numeric correlations: {e}")
        return None

def calculate_popularity_index(df):
    """Calculate a custom popularity index for each character."""
    try:
        df['popularity_index'] = (
            df['films'].str.len() * 2 +  # Weight film appearances more heavily
            df['vehicles'].str.len() +
            df['starships'].str.len()
        )
        
        # Get top 10 most popular characters
        top_characters = df.nlargest(10, 'popularity_index')
        
        fig = px.bar(
            top_characters,
            x='name',
            y='popularity_index',
            title='Top 10 Most Popular Characters',
            labels={'name': 'Character', 'popularity_index': 'Popularity Index'}
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        return fig
    except Exception as e:
        logging.error(f"Failed to calculate popularity index: {e}")
        return None

def main():
    """Main function to fetch, clean, validate, and analyze people data."""
    try:
        # Fetch data
        people_data = fetch_people_data()
        
        # Create and validate DataFrame
        df = create_people_dataframe(people_data)
        if not validate_people_dataframe(df):
            raise ValueError("Invalid DataFrame structure")
        
        # Generate visualizations
        gender_fig = analyze_gender_distribution(df)
        physical_fig = analyze_physical_attributes(df)
        homeworld_fig = analyze_homeworld_statistics(df)
        film_fig = analyze_film_appearances(df)
        species_fig = analyze_species_diversity_interactive(df)
        correlation_fig = analyze_numeric_correlations(df)
        popularity_fig = calculate_popularity_index(df)
        
        # Return all figures for display
        return {
            'gender': gender_fig,
            'physical': physical_fig,
            'homeworld': homeworld_fig,
            'films': film_fig,
            'species': species_fig,
            'correlation': correlation_fig,
            'popularity': popularity_fig
        }
        
    except Exception as e:
        logging.error(f"Error in main function: {e}")
        return {}

if __name__ == "__main__":
    main()