import requests
import json
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import re
from wordcloud import WordCloud
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import io
import base64

def fetch_films_data():
    """Fetch all films data from SWAPI."""
    url = "https://swapi.dev/api/films/"
    all_films = []
    
    while url:
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching films data: {e}")
            return []
        
        for film in data['results']:
            film_info = {
                'title': film['title'],
                'episode_id': film['episode_id'],
                'opening_crawl': film['opening_crawl'],
                'director': film['director'],
                'producer': film['producer'],
                'release_date': film['release_date'],
                'characters': film['characters'],
                'planets': film['planets'],
                'starships': film['starships'],
                'vehicles': film['vehicles'],
                'species': film['species'],
                'created': film['created'],
                'edited': film['edited'],
                'url': film['url']
            }
            all_films.append(film_info)
        
        url = data.get('next', None)

    with open('all_films_data.json', 'w') as file:
        json.dump(all_films, file, indent=4)
    
    return all_films

def load_films_data():
    try:
        with open('all_films_data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return fetch_films_data()

def count_films_by_director(films):
    director_counts = Counter(film['director'] for film in films)
    return dict(director_counts)

def plot_counts_per_film(films, data_key, title, color):
    df = pd.DataFrame(films)
    df[f'{data_key}_count'] = df[data_key].apply(len)

    plt.figure(figsize=(10, 5))  
    plt.bar(df['title'], df[f'{data_key}_count'], color=color, edgecolor='black')

    plt.xlabel("Film Title")
    plt.ylabel(f"Number of {title}")
    plt.title(f"Number of {title} per Film")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

def analyze_film_summary(films):
    crawls = []
    
    for film in films:
        crawl = film['opening_crawl']
        cleaned_crawl = re.sub(r'\s+', ' ', crawl.replace('\r', '').replace('\n', ' '))
        crawls.append(cleaned_crawl)
    
    all_crawls = ' '.join(crawls)
    
    words = re.findall(r'\b\w+\b', all_crawls.lower())  
    word_counts = Counter(words)
    
    return word_counts.most_common(10)

def plot_common_words(df):
    """Generate a word cloud from opening crawls."""
    if df.empty:
        return None
    
    # Combine all opening crawls
    text = ' '.join(df['opening_crawl'].fillna(''))
    
    # Generate word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='black').generate(text)
    
    # Convert to bytes for Streamlit
    img = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(img, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    
    return img.getvalue()

def analyze_character_appearance(films_data):
    character_appearance = {}

    for film in films_data:
        character_ids = film['characters']
        
        for character_url in character_ids:
            character_id = character_url.split('/')[-2]  
            if character_id not in character_appearance:
                character_appearance[character_id] = 1
            else:
                character_appearance[character_id] += 1

    return character_appearance

def analyze_runtime_distribution(df):
    """Analyze the runtime distribution of films."""
    if df.empty:
        return None

    # Runtime data mapping
    runtime_mapping = {
        1: 121,  # A New Hope
        2: 124,  # The Empire Strikes Back
        3: 131,  # Return of the Jedi
        4: 136,  # The Phantom Menace
        5: 142,  # Attack of the Clones
        6: 140,  # Revenge of the Sith
        7: 135,  # The Force Awakens
        8: 152,  # The Last Jedi
        9: 141   # The Rise of Skywalker
    }
    
    # Add runtime column based on episode_id mapping
    df = df.copy()
    df['runtime'] = df['episode_id'].map(runtime_mapping)
    
    # Create the figure
    fig = px.histogram(
        df,
        x='runtime',
        nbins=10,
        title='Distribution of Star Wars Film Runtimes',
        labels={'runtime': 'Runtime (minutes)', 'count': 'Number of Films'},
        color_discrete_sequence=['yellow']
    )
    
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        bargap=0.1
    )
    
    # Add mean line
    mean_runtime = df['runtime'].mean()
    fig.add_vline(
        x=mean_runtime,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: {mean_runtime:.0f} min",
        annotation_position="top"
    )
    
    return fig

def analyze_character_count(df):
    """Analyze the number of characters in each film."""
    if df.empty:
        return None

    # Calculate character counts
    df = df.copy()
    df['character_count'] = df['characters'].apply(len)
    
    # Create the visualization
    fig = px.bar(
        df,
        x='title',
        y='character_count',
        title='Number of Characters per Star Wars Film',
        labels={'character_count': 'Number of Characters', 'title': 'Film Title'},
        color='character_count',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def plot_release_timeline(df):
    """Plot the release timeline of Star Wars films."""
    if df.empty:
        return None
    
    df = df.copy()
    df['release_date'] = pd.to_datetime(df['release_date'])
    df = df.sort_values('release_date')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['release_date'],
        y=[1] * len(df),
        mode='markers+text',
        text=df['title'],
        textposition='top center',
        marker=dict(size=15, color='yellow'),
        name='Release Dates'
    ))
    
    fig.update_layout(
        title='Star Wars Film Release Timeline',
        showlegend=False,
        height=400,
        yaxis=dict(visible=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def analyze_word_frequencies(df):
    """Analyze word frequencies in opening crawls."""
    if df.empty:
        return go.Figure()
    
    # Combine all opening crawls
    all_text = ' '.join(df['opening_crawl'].fillna(''))
    
    # Clean and tokenize text
    words = re.findall(r'\b\w+\b', all_text.lower())
    
    # Remove common English stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'up', 'down', 'into', 'over', 'under',
        'again', 'once', 'is', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall',
        'should', 'may', 'might', 'must', 'can', 'could'
    }
    
    # Filter out stop words and count frequencies
    word_freq = Counter(word for word in words if word not in stop_words)
    
    # Get top 20 words
    top_words = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20])
    
    # Create bar chart
    fig = px.bar(
        x=list(top_words.keys()),
        y=list(top_words.values()),
        title='Most Common Words in Opening Crawls',
        labels={'x': 'Word', 'y': 'Frequency'}
    )
    
    # Update layout
    fig.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def create_films_dataframe(films_data):
    """Create a DataFrame from films data."""
    if not films_data:
        return pd.DataFrame()
        
    df = pd.DataFrame(films_data)
    
    # Ensure episode_id is properly formatted as integer
    if 'episode_id' in df.columns:
        df['episode_id'] = pd.to_numeric(df['episode_id'], errors='coerce')
    
    # Convert release_date to datetime
    df['release_date'] = pd.to_datetime(df['release_date'])
    
    # Sort by episode_id
    df = df.sort_values('episode_id')
    
    return df

def analyze_film_summary(df):
    """Analyze and create summary statistics for films."""
    if df.empty:
        return {
            'Total Films': 0,
            'Date Range': 'N/A',
            'Total Episodes': 0
        }
    
    print("DataFrame columns:", df.columns.tolist())  # Debug print
    
    # Convert release_date to datetime if not already
    if not pd.api.types.is_datetime64_any_dtype(df['release_date']):
        df['release_date'] = pd.to_datetime(df['release_date'])
    
    summary = {
        'Total Films': len(df),
        'Date Range': f"{df['release_date'].min().year} - {df['release_date'].max().year}",
        'Total Episodes': len(df['episode_id'].unique())
    }
    
    return summary

def main():
    films = load_films_data()
    if not films:
        return

    word_freq = analyze_word_frequencies(create_films_dataframe(films))
    print("Word Frequencies in Film Opening Crawls:")
    word_freq.show()

    common_words = analyze_film_summary(films)
    print("\nMost Common Words/Phrases in Film Opening Crawls:")
    for word, count in common_words:
        print(f"{word}: {count}")

    df = create_films_dataframe(films)
    common_words_img = plot_common_words(df)
    print(common_words_img)

    character_appearance = analyze_character_appearance(films)
    character_ids = list(character_appearance.keys())
    character_names = {char_id: f"Character {char_id}" for char_id in character_ids}

    print("\nCharacter Appearances in Films:")
    for char_id, count in character_appearance.items():
        name = character_names.get(char_id, "Unknown Character")
        print(f"{name}: {count} appearances")

    plot_counts_per_film(films, 'planets', 'Planets', 'mediumseagreen')
    plot_counts_per_film(films, 'starships', 'Starships', 'dodgerblue')
    plot_counts_per_film(films, 'vehicles', 'Vehicles', 'orange')
    plot_counts_per_film(films, 'species', 'Species', 'green')
    plot_counts_per_film(films, 'characters', 'Characters', 'goldenrod')

    director_counts = count_films_by_director(films)
    df = pd.DataFrame(list(director_counts.items()), columns=['Director', 'Count'])
    plt.figure(figsize=(8, 5))
    plt.bar(df['Director'], df['Count'], color='skyblue', edgecolor='black')
    plt.xlabel("Director")
    plt.ylabel("Number of Films")
    plt.title("Film Count by Director")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    producer_list = [film['producer'] for film in films]
    producer_counts = Counter([p.strip() for producers in producer_list for p in producers.split(',')])
    plt.figure(figsize=(10, 5))
    plt.bar(producer_counts.keys(), producer_counts.values(), color='lightcoral', edgecolor='black')
    plt.xlabel("Producer")
    plt.ylabel("Number of Films")
    plt.title("Film Count by Producer")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    plot_release_timeline(df)

    analyze_runtime_distribution(df)
    analyze_character_count(df)

    summary = analyze_film_summary(df)
    print(summary)

    word_freq_fig, wordcloud = analyze_word_frequencies(df)
    word_freq_fig.show()

if __name__ == "__main__":
    main()