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

def analyze_film_runtimes(films):
    runtimes = []
    for film in films:
        runtime_str = film.get('length')
        if runtime_str:
            try:
                runtime = int(runtime_str.split()[0])
                runtimes.append(runtime)
            except ValueError:
                print(f"Warning: Invalid runtime format: {runtime_str}")

    if runtimes:
        plt.figure(figsize=(8, 5))
        plt.hist(runtimes, bins=10, color='skyblue', edgecolor='black')
        plt.xlabel("Runtime (minutes)")
        plt.ylabel("Number of Films")
        plt.title("Distribution of Film Runtimes")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.show()

        runtimes_array = np.array(runtimes)
        mean_runtime = np.mean(runtimes)
        median_runtime = np.median(runtimes_array)
        std_dev_runtime = np.std(runtimes)

        print(f"Mean Runtime: {mean_runtime:.2f} minutes")
        print(f"Median Runtime: {median_runtime:.2f} minutes")
        print(f"Standard Deviation: {std_dev_runtime:.2f} minutes")
    else:
        print("No valid runtime data found for analysis.")

def analyze_producer_diversity(films):
    all_producers = []
    for film in films:
        producers_str = film.get('producer')
        if producers_str:
            producers = [p.strip() for p in producers_str.split(',')]
            all_producers.extend(producers)

    producer_counts = Counter(all_producers)
    num_producers = len(producer_counts)
    print(f"Number of unique producers: {num_producers}")

    films_per_producer = [count for count in producer_counts.values()]
    print(f"Average films per producer: {np.mean(films_per_producer):.2f}")
    print(f"Maximum films per producer: {max(films_per_producer)}")
    print(f"Minimum films per producer: {min(films_per_producer)}")

    plt.figure(figsize=(8, 5))
    plt.hist(films_per_producer, bins=10, color="lightcoral", edgecolor="black")
    plt.xlabel("Number of Films per Producer")
    plt.ylabel("Number of Producers")
    plt.title("Distribution of Films per Producer")
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.bar(producer_counts.keys(), producer_counts.values(), color='mediumvioletred', edgecolor='black')
    plt.xlabel("Producer")
    plt.ylabel("Number of Films")
    plt.title("Number of Films per Producer (Bar Chart)")
    plt.xticks(rotation=45, ha='right', fontsize=8)  
    plt.tight_layout() 
    plt.show()

def analyze_director_diversity(films):
    df = pd.DataFrame(films)
    director_counts = df['director'].value_counts()

    plt.figure(figsize=(10, 6))  
    director_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.xlabel("Director")
    plt.ylabel("Number of Films")
    plt.title("Film Count by Director")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    return director_counts  

def plot_film_release_timeline(films):
    df = pd.DataFrame(films)

    df['release_date'] = pd.to_datetime(df['release_date'])

    df = df.sort_values(by='release_date')

    plt.figure(figsize=(10, 5))
    plt.scatter(df['release_date'], df['episode_id'], color='red', label="Film Release")

    for i, row in df.iterrows():
        plt.text(row['release_date'], row['episode_id'], row['title'], fontsize=9, ha='right')

    plt.xlabel("Release Year")
    plt.ylabel("Episode ID")
    plt.title("Star Wars Film Release Timeline")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    plt.show()

def analyze_characters_distribution(films_data):
    character_appearances = {}

    for film in films_data:
        for character_url in film['characters']:
            character_id = character_url.split('/')[-2]
            if character_id not in character_appearances:
                character_appearances[character_id] = {'film_count': 0, 'films': []}
            character_appearances[character_id]['films'].append(film['title'])
            character_appearances[character_id]['film_count'] = len(character_appearances[character_id]['films'])

    df_characters = pd.DataFrame.from_dict(character_appearances, orient='index')
    df_characters['Character_ID'] = df_characters.index

    character_ids = df_characters.index.tolist()
    character_names = get_character_names(character_ids)
    df_characters['Character_Name'] = df_characters['Character_ID'].map(character_names)

    df_characters = df_characters.sort_values('film_count', ascending=False).head(20)

    fig = px.bar(
        df_characters, 
        x='Character_Name', 
        y='film_count',
        title='Top 20 Characters by Film Appearances',
        labels={'film_count': 'Number of Film Appearances', 'Character_Name': 'Character'},
        color='film_count',
        color_continuous_scale='Viridis'
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    return fig

def analyze_film_runtimes(films_data):
    runtime_data = {
        'A New Hope': 121,
        'The Empire Strikes Back': 124,
        'Return of the Jedi': 131,
        'The Phantom Menace': 136,
        'Attack of the Clones': 142,
        'Revenge of the Sith': 140,
        'The Force Awakens': 135,
        'The Last Jedi': 152,
        'The Rise of Skywalker': 141
    }
    
    df_runtimes = pd.DataFrame(list(runtime_data.items()), columns=['Title', 'Runtime'])
    
    fig = px.bar(
        df_runtimes,
        x='Title',
        y='Runtime',
        title='Star Wars Film Runtimes',
        labels={'Runtime': 'Runtime (minutes)', 'Title': 'Film Title'},
        color='Runtime',
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

def plot_film_release_timeline(films_data):
    df_releases = pd.DataFrame([
        {'title': film['title'], 'release_date': film['release_date']}
        for film in films_data
    ])
    
    df_releases['release_date'] = pd.to_datetime(df_releases['release_date'])
    df_releases = df_releases.sort_values('release_date')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_releases['release_date'],
        y=[1] * len(df_releases),
        mode='markers+text',
        text=df_releases['title'],
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

def analyze_genre_distribution(films_data):
    genre_data = {
        'Science Fiction': 9,
        'Action': 9,
        'Adventure': 9,
        'Fantasy': 7,
        'Space Opera': 9,
        'Epic': 6
    }
    
    df_genres = pd.DataFrame(list(genre_data.items()), columns=['Genre', 'Count'])
    
    fig = px.bar(
        df_genres,
        x='Genre',
        y='Count',
        title='Genre Distribution in Star Wars Films',
        color='Count',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_tickangle=0,
        showlegend=False,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def get_character_names(character_ids):
    names = {}
    for char_id in character_ids:
        names[char_id] = f"Character {char_id}"
    return names

def create_films_dataframe(films_data):
    """Create a DataFrame from films data."""
    if not films_data:
        return pd.DataFrame()
        
    df = pd.DataFrame(films_data)
    
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

def analyze_word_frequencies(films_data):
    """Analyze word frequencies in opening crawls."""
    if not films_data:
        return {}
    
    # Combine all opening crawls
    text = ' '.join([film['opening_crawl'] for film in films_data])
    
    # Split into words and clean
    words = text.lower().split()
    words = [word.strip('.,!?()[]{}":;') for word in words]
    
    # Count word frequencies
    word_freq = {}
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    
    for word in words:
        if word and word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    return word_freq

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

def analyze_character_count(df):
    """Analyze the number of characters in each film."""
    if df.empty:
        return go.Figure(), go.Figure()
    
    # Count characters per film
    df['character_count'] = df['characters'].apply(len)
    
    # Sort by episode_id for chronological order
    df = df.sort_values('episode_id')
    
    # Create bar chart
    fig1 = px.bar(
        df,
        x='title',
        y='character_count',
        title='Number of Characters per Film',
        labels={
            'title': 'Film Title',
            'character_count': 'Number of Characters'
        },
        template='plotly_dark'
    )
    
    fig1.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Create line chart for character count over time
    fig2 = px.line(
        df,
        x='release_date',
        y='character_count',
        title='Character Count Evolution Over Time',
        labels={
            'release_date': 'Release Date',
            'character_count': 'Number of Characters'
        },
        template='plotly_dark'
    )
    
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig1, fig2

def plot_character_count(films_data):
    """Plot detailed character analysis."""
    if not films_data:
        return go.Figure()
    
    df = pd.DataFrame(films_data)
    df['character_count'] = df['characters'].apply(len)
    df = df.sort_values('episode_id')
    
    fig = px.line(df,
                  x='episode_id',
                  y='character_count',
                  title='Character Count Evolution',
                  labels={'character_count': 'Number of Characters',
                         'episode_id': 'Episode Number'},
                  template='plotly_dark',
                  markers=True)
    
    fig.update_traces(line_color='#00ff00')
    return fig

def analyze_runtime_distribution(df):
    """Analyze the runtime distribution of films."""
    if df.empty:
        return go.Figure(), go.Figure()
    
    # Sort by episode_id for chronological order
    df = df.sort_values('episode_id')
    
    # Create bar chart
    fig1 = px.bar(
        df,
        x='title',
        y='episode_id',
        title='Film Episodes',
        labels={
            'title': 'Film Title',
            'episode_id': 'Episode ID'
        },
        template='plotly_dark'
    )
    
    fig1.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Create histogram
    fig2 = px.histogram(
        df,
        x='episode_id',
        nbins=10,
        title='Episode Distribution',
        labels={
            'episode_id': 'Episode ID',
            'count': 'Number of Films'
        },
        template='plotly_dark'
    )
    
    fig2.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig1, fig2

def plot_runtime_distribution(films_data):
    """Plot runtime distribution visualization."""
    df = pd.DataFrame(films_data)
    
    fig = px.box(df, y='episode_id', title='Film Runtime Distribution')
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True
    )
    
    return fig

def plot_release_timeline(films_data):
    """Plot release timeline visualization."""
    df = pd.DataFrame(films_data)
    
    fig = px.scatter(df, x='release_date', y='episode_id', 
                    title='Star Wars Films Release Timeline',
                    text='title')
    
    fig.update_traces(
        textposition='top center',
        marker=dict(size=12, symbol='star')
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False
    )
    
    return fig

def analyze_character_count(films_data):
    """Analyze the number of characters in each film."""
    df = pd.DataFrame(films_data)
    
    fig = px.bar(df, x='title', y=df['characters'].str.len(),
                title='Number of Characters per Film')
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        xaxis_tickangle=-45
    )
    
    return fig

def analyze_runtime_distribution(films_data):
    """Analyze the runtime distribution of films."""
    df = pd.DataFrame(films_data)
    
    fig = px.histogram(df, x='runtime',
                      title='Runtime Distribution',
                      labels={'runtime': 'Runtime (minutes)',
                             'count': 'Number of Films'})
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False
    )
    
    return fig

def create_film_summary_charts(films_data):
    """Create complementary summary pie charts."""
    df = pd.DataFrame(films_data)
    
    # Create pie chart for director distribution
    director_counts = df['director'].value_counts()
    director_fig = px.pie(
        values=director_counts.values,
        names=director_counts.index,
        title='Films by Director'
    )
    director_fig.update_layout(
        height=400,  # Slightly larger for better visibility
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(size=12)
    )
    
    # Create pie chart for release year distribution
    df['year'] = pd.to_datetime(df['release_date']).dt.year
    year_counts = df['year'].value_counts()
    year_fig = px.pie(
        values=year_counts.values,
        names=year_counts.index,
        title='Films by Release Year'
    )
    year_fig.update_layout(
        height=400,  # Slightly larger for better visibility
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(size=12)
    )
    
    return [director_fig, year_fig]

def create_character_count_chart(films_data):
    """Create a full-width character count chart."""
    df = pd.DataFrame(films_data)
    
    # Characters per film bar chart
    fig = px.bar(
        df,
        x='title',
        y=df['characters'].str.len(),
        title='Number of Characters per Film',
        height=500  # Taller for better readability
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=14),
        showlegend=False,
        margin=dict(l=80, r=80, t=100, b=100),  # Large margins for rotated labels
        title=dict(
            font=dict(size=24)
        ),
        xaxis=dict(
            title='Film Title',
            title_font=dict(size=16),
            tickfont=dict(size=14),
            tickangle=-45  # Angled labels for better readability
        ),
        yaxis=dict(
            title='Number of Characters',
            title_font=dict(size=16),
            tickfont=dict(size=14)
        )
    )
    
    return fig

def create_species_chart(films_data):
    """Create a compact species distribution pie chart."""
    df = pd.DataFrame(films_data)
    
    # Get top 5 species for clarity
    species_counts = df['species'].explode().value_counts().head(5)
    
    fig = px.pie(
        values=species_counts.values,
        names=species_counts.index,
        title='Top 5 Species Distribution'
    )
    
    fig.update_layout(
        height=400,
        width=600,  # Fixed width for centered display
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(color='white', size=12),
        title=dict(
            font=dict(size=20)
        )
    )
    
    return fig

def analyze_word_frequencies(films_data):
    """Analyze word frequencies in opening crawls."""
    df = pd.DataFrame(films_data)
    
    # Create word frequency analysis
    fig = px.bar(df, x='title', y='word_count',
                 title='Word Frequencies in Opening Crawls')
    
    fig.update_layout(
        height=600,  # Fixed height
        autosize=True,  # Enable autosize for width
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=14),
        showlegend=False,
        margin=dict(l=80, r=80, t=100, b=80),  # Increased margins
        title=dict(
            font=dict(size=24)  # Larger title
        ),
        yaxis=dict(
            title='Word Count',
            title_font=dict(size=16),
            tickfont=dict(size=14)
        ),
        xaxis=dict(
            title='Film Title',
            title_font=dict(size=16),
            tickfont=dict(size=14)
        )
    )
    
    return fig

def analyze_release_timeline(df):
    """Analyze the release timeline of films."""
    if df.empty:
        return go.Figure()
    
    # Sort by release date
    df = df.sort_values('release_date')
    
    # Create timeline plot
    fig = px.scatter(
        df,
        x='release_date',
        y=[1] * len(df),  # All points at same y-level
        text='title',
        title='Star Wars Film Release Timeline',
        labels={
            'release_date': 'Release Date',
            'y': ''
        },
        template='plotly_dark'
    )
    
    # Update layout for better visibility
    fig.update_traces(
        marker=dict(size=12, color='yellow'),
        textposition='top center'
    )
    
    fig.update_layout(
        showlegend=False,
        yaxis_visible=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def main():
    films = load_films_data()
    if not films:
        return

    word_freq = analyze_word_frequencies(films)
    print("Word Frequencies in Film Opening Crawls:")
    for word, count in word_freq.items():
        print(f"{word}: {count}")

    common_words = analyze_film_summary(films)
    print("\nMost Common Words/Phrases in Film Opening Crawls:")
    for word, count in common_words:
        print(f"{word}: {count}")

    df = create_films_dataframe(films)
    common_words_img = plot_common_words(df)
    print(common_words_img)

    character_appearance = analyze_character_appearance(films)
    character_ids = list(character_appearance.keys())
    character_names = get_character_names(character_ids)

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

    plot_film_release_timeline(films)

    analyze_film_runtimes(films)
    analyze_producer_diversity(films)
    analyze_director_diversity(films)

    character_appearances_by_film = analyze_characters_distribution(films)
    character_names_dict = get_character_names(list(character_appearances_by_film.index))
    # display_character_appearances(character_appearances_by_film, character_names_dict)

    try:
        genre_fig = analyze_genre_distribution(films)
        genre_fig.show()  

        char_fig = analyze_characters_distribution(films)
        char_fig.show()  

    except Exception as e:
        print(f"Error in genre or character distribution analysis: {e}")

    df = create_films_dataframe(films)
    summary = analyze_film_summary(df)
    print(summary)

    char_count_fig, char_count_over_time_fig = analyze_character_count(df)
    char_count_fig.show()
    char_count_over_time_fig.show()

    runtime_dist_fig = plot_runtime_distribution(df)
    runtime_dist_fig.show()

    release_timeline_fig = plot_release_timeline(df)
    release_timeline_fig.show()

if __name__ == "__main__":
    main()