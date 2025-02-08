import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import logging
import json

# Import analysis functions
from films import (create_films_dataframe, analyze_runtime_distribution,
                  analyze_character_count, analyze_word_frequencies,
                  plot_release_timeline)
from people import (create_people_dataframe, analyze_gender_distribution,
                   analyze_physical_attributes, analyze_homeworld_statistics,
                   analyze_film_appearances, analyze_species_diversity_interactive,
                   analyze_numeric_correlations)
from planets import (create_planets_dataframe, analyze_climate_distribution,
                    analyze_terrain_distribution, analyze_population_metrics,
                    analyze_characteristics)
from species import (create_species_dataframe, analyze_classification_distribution,
                    analyze_lifespan_distribution, analyze_language_distribution,
                    analyze_physical_traits)
from vehicles import (create_vehicles_dataframe, analyze_vehicle_classes,
                     analyze_cost_metrics, analyze_capacity_metrics,
                     analyze_performance_metrics)
from starships import (create_starships_dataframe, analyze_starship_classes,
                      analyze_cost_metrics as analyze_starship_cost_metrics,
                      analyze_capacity_metrics as analyze_starship_capacity_metrics,
                      analyze_performance_metrics as analyze_starship_performance_metrics,
                      get_starship_stats)

# Import data manager for cached data
from data_manager import (get_films_data, get_people_data, get_planets_data,
                         get_species_data, get_vehicles_data, get_starships_data)

# Configure Streamlit page settings
st.set_page_config(
    page_title="Star Wars Universe Explorer",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure matplotlib for better rendering in Streamlit
plt.style.use('dark_background')
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['figure.dpi'] = 100

# Configure plotly for better rendering in dark theme
import plotly.io as pio
pio.templates.default = "plotly_dark"

# Set page config
st.markdown("""
<style>
    /* Main background and text colors */
    .stApp {
        background-color: rgba(0, 0, 0, 0.9);
        color: #ffffff;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        color: #FFE81F !important;
    }
</style>
""", unsafe_allow_html=True)

# Configure plot theme for all visualizations
plot_theme = {
    'template': 'plotly_dark',
    'layout': {
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': 'white'},
        'title': {'font': {'color': 'white'}}
    }
}

# Title with Star Wars style
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='font-size: 3rem; margin-bottom: 1rem;'>Star Wars Universe Explorer</h1>
    <p style='color: #FFE81F; font-size: 1.2rem; font-style: italic;'>
        A long time ago in a galaxy far, far away...
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem 0;'>
    <h3 style='color: #FFE81F; margin-bottom: 1rem;'>Navigation</h3>
</div>
""", unsafe_allow_html=True)

# Category selection
category = st.sidebar.selectbox(
    "Choose a category to explore",
    ["Home", "Films", "Characters", "Planets", "Species", "Vehicles", "Starships"],
    index=0
)

# Home Page
if category == "Home":
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h2>Welcome to the Star Wars Universe Explorer</h2>
        <p style='font-size: 1.2rem; margin: 2rem 0;'>
            Explore detailed analytics and insights about the Star Wars universe, including:
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='feature-card'>
            <h3 style='color: #FFE81F;'>Films</h3>
            <p>Analyze the Star Wars saga through data visualization and statistics</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='feature-card'>
            <h3 style='color: #FFE81F;'>Characters</h3>
            <p>Explore character relationships and demographics across the galaxy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='feature-card'>
            <h3 style='color: #FFE81F;'>Universe</h3>
            <p>Discover planets, species, vehicles, and starships in the Star Wars universe</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; padding: 2rem; margin-top: 2rem;'>
        <p style='font-style: italic; color: #FFE81F;'>
            "Do. Or do not. There is no try." - Yoda
        </p>
    </div>
    """, unsafe_allow_html=True)

# Films Analysis
elif category == "Films":
    st.header("Films Analysis")
    
    # Load film data
    films_data = get_films_data()
    if not films_data:
        st.error("Failed to load film data. Please try again.")
        st.stop()
        
    df_films = create_films_dataframe(films_data)
    
    # Runtime Distribution
    st.subheader("Film Runtime Distribution")
    runtime_fig = analyze_runtime_distribution(df_films)
    st.plotly_chart(runtime_fig, use_container_width=True)
    
    # Character Count Analysis
    st.subheader("Character Count Analysis")
    char_count_fig = analyze_character_count(df_films)
    st.plotly_chart(char_count_fig, use_container_width=True)
    
    # Word Frequency Analysis
    st.subheader("Word Frequency Analysis")
    word_freq_fig = analyze_word_frequencies(df_films)
    st.plotly_chart(word_freq_fig, use_container_width=True)
    
    # Release Timeline
    st.subheader("Film Release Timeline")
    timeline_fig = plot_release_timeline(df_films)
    st.plotly_chart(timeline_fig, use_container_width=True)

# Characters Analysis
elif category == "Characters":
    st.header("Character Analysis")
    
    try:
        people_data = get_people_data()
        df = create_people_dataframe(people_data)
        
        # Create three columns for better organization
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Gender Distribution")
            gender_fig = analyze_gender_distribution(df)
            gender_fig.update_layout(**plot_theme['layout'])
            st.plotly_chart(gender_fig, use_container_width=True)
        
        with col2:
            st.subheader("Physical Attributes")
            attr_fig = analyze_physical_attributes(df)
            attr_fig.update_layout(**plot_theme['layout'])
            st.plotly_chart(attr_fig, use_container_width=True)
        
        # Full width for homeworld statistics
        st.subheader("Character Origins")
        homeworld_fig = analyze_homeworld_statistics(df)
        homeworld_fig.update_layout(**plot_theme['layout'])
        st.plotly_chart(homeworld_fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading character data: {str(e)}")
        st.info("Please check the data source and try again.")

# Planets Analysis
elif category == "Planets":
    st.header("Planets Analysis")
    
    # Load planet data
    planets_data = get_planets_data()
    if not planets_data:
        st.error("No planet data available. Please check the data source.")
        st.stop()
        
    df = create_planets_dataframe(planets_data)
    if df.empty:
        st.error("Could not process planet data.")
        st.stop()
    
    tabs = st.tabs(["Climate", "Population", "Terrain", "Characteristics"])
    
    # Climate Tab
    with tabs[0]:
        st.subheader("Climate Analysis")
        try:
            climate_figs = analyze_climate_distribution(df)
            
            col1, col2 = st.columns(2)
            with col1:
                climate_figs['pie'].update_layout(**plot_theme['layout'])
                st.plotly_chart(climate_figs['pie'], use_container_width=True)
            with col2:
                climate_figs['bar'].update_layout(**plot_theme['layout'])
                st.plotly_chart(climate_figs['bar'], use_container_width=True)
            
            # Display some climate stats
            total_climates = df['climate'].str.split(',').explode().str.strip().nunique()
            st.metric("Total Unique Climates", total_climates)
            
            st.markdown("""
            **Climate Distribution Insights:**
            - Star Wars planets feature diverse climate types
            - Some planets have multiple climate zones
            - Temperate and arid climates are common
            """)
        except Exception as e:
            st.error(f"Error analyzing climate data: {str(e)}")
    
    # Population Tab
    with tabs[1]:
        st.subheader("Population Analysis")
        try:
            pop_figs = analyze_population_metrics(df)
            pop_figs['bar'].update_layout(**plot_theme['layout'])
            st.plotly_chart(pop_figs['bar'], use_container_width=True)
            
            st.markdown("""
            **Population Insights:**
            - Population sizes vary dramatically across planets
            - Some planets are heavily populated urban centers
            - Others are sparsely populated or uninhabited
            """)
        except Exception as e:
            st.error(f"Error analyzing population data: {str(e)}")
    
    # Terrain Tab
    with tabs[2]:
        st.subheader("Terrain Analysis")
        try:
            terrain_figs = analyze_terrain_distribution(df)
            
            col1, col2 = st.columns(2)
            with col1:
                terrain_figs['bar'].update_layout(**plot_theme['layout'])
                st.plotly_chart(terrain_figs['bar'], use_container_width=True)
            with col2:
                terrain_figs['pie'].update_layout(**plot_theme['layout'])
                st.plotly_chart(terrain_figs['pie'], use_container_width=True)
            
            st.markdown("""
            **Terrain Insights:**
            - Planets show diverse geographical features
            - Many planets have multiple terrain types
            - Common terrains include mountains, forests, and deserts
            - Terrain affects habitability and development
            """)
        except Exception as e:
            st.error(f"Error analyzing terrain data: {str(e)}")
    
    # Characteristics Tab
    with tabs[3]:
        st.subheader("Planet Characteristics")
        try:
            char_figs = analyze_characteristics(df)
            char_figs['scatter1'].update_layout(**plot_theme['layout'])
            char_figs['scatter2'].update_layout(**plot_theme['layout'])
            st.plotly_chart(char_figs['scatter1'], use_container_width=True)
            st.plotly_chart(char_figs['scatter2'], use_container_width=True)
            
            # Display some interesting stats
            avg_diameter = df[df['diameter'] > 0]['diameter'].mean()
            avg_rotation = df[df['rotation_period'] > 0]['rotation_period'].mean()
            avg_orbital = df[df['orbital_period'] > 0]['orbital_period'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Diameter", f"{avg_diameter:,.0f} km")
            with col2:
                st.metric("Average Rotation", f"{avg_rotation:,.0f} hours")
            with col3:
                st.metric("Average Orbit", f"{avg_orbital:,.0f} days")
            
            st.markdown("""
            **Physical Characteristics Insights:**
            - Planet sizes vary greatly across the galaxy
            - Rotation and orbital periods show interesting patterns
            - Surface water affects climate and habitability
            - Larger planets tend to have longer rotation periods
            """)
        except Exception as e:
            st.error(f"Error analyzing characteristics data: {str(e)}")

# Species Analysis
elif category == "Species":
    st.header("Species Analysis")
    
    try:
        # Load species data
        species_data = get_species_data()
        df = create_species_dataframe(species_data)
        
        if not df.empty:
            tabs = st.tabs(["Classification", "Lifespan", "Language", "Physical Traits"])
            
            # Classification Tab
            with tabs[0]:
                st.subheader("Species Classification")
                class_figs = analyze_classification_distribution(df)
                
                col1, col2 = st.columns(2)
                with col1:
                    class_figs['pie'].update_layout(**plot_theme['layout'])
                    st.plotly_chart(class_figs['pie'], use_container_width=True)
                with col2:
                    class_figs['bar'].update_layout(**plot_theme['layout'])
                    st.plotly_chart(class_figs['bar'], use_container_width=True)
                
                # Display classification stats
                total_classifications = df['classification'].nunique()
                st.metric("Total Classifications", total_classifications)
            
            # Lifespan Tab
            with tabs[1]:
                st.subheader("Lifespan Analysis")
                lifespan_figs = analyze_lifespan_distribution(df)
                
                lifespan_figs['bar'].update_layout(**plot_theme['layout'])
                lifespan_figs['scatter'].update_layout(**plot_theme['layout'])
                st.plotly_chart(lifespan_figs['bar'], use_container_width=True)
                st.plotly_chart(lifespan_figs['scatter'], use_container_width=True)
                
                # Display lifespan stats
                avg_lifespan = df[df['average_lifespan'] > 0]['average_lifespan'].mean()
                st.metric("Average Lifespan", f"{avg_lifespan:.0f} years")
            
            # Language Tab
            with tabs[2]:
                st.subheader("Language Distribution")
                lang_figs = analyze_language_distribution(df)
                
                col1, col2 = st.columns(2)
                with col1:
                    lang_figs['pie'].update_layout(**plot_theme['layout'])
                    st.plotly_chart(lang_figs['pie'], use_container_width=True)
                with col2:
                    lang_figs['bar'].update_layout(**plot_theme['layout'])
                    st.plotly_chart(lang_figs['bar'], use_container_width=True)
                
                # Display language stats
                total_languages = df['language'].nunique()
                st.metric("Total Languages", total_languages)
            
            # Physical Traits Tab
            with tabs[3]:
                st.subheader("Physical Characteristics")
                traits_figs = analyze_physical_traits(df)
                
                traits_figs['bar'].update_layout(**plot_theme['layout'])
                traits_figs['color_bar'].update_layout(**plot_theme['layout'])
                st.plotly_chart(traits_figs['bar'], use_container_width=True)
                st.plotly_chart(traits_figs['color_bar'], use_container_width=True)
                
                # Display physical trait stats
                avg_height = df[df['average_height'] > 0]['average_height'].mean()
                st.metric("Average Height", f"{avg_height:.0f} cm")
        
        else:
            st.error("No species data available.")
            
    except Exception as e:
        st.error(f"Error analyzing species data: {str(e)}")
        st.info("Please check the data source and try again.")

# Vehicles Analysis
elif category == "Vehicles":
    st.title("Star Wars Vehicles Analysis")
    
    # Load and process vehicles data
    vehicles_data = get_vehicles_data()
    if not vehicles_data:
        st.error("Failed to load vehicles data. Please try again.")
        st.stop()
        
    df_vehicles = create_vehicles_dataframe(vehicles_data)
    
    # Class Distribution
    st.subheader("Vehicle Classes")
    class_fig1, class_fig2 = analyze_vehicle_classes(df_vehicles)
    st.plotly_chart(class_fig1, use_container_width=True)
    st.plotly_chart(class_fig2, use_container_width=True)
    
    # Cost Analysis
    st.subheader("Cost Analysis")
    cost_fig1, cost_fig2 = analyze_cost_metrics(df_vehicles)
    st.plotly_chart(cost_fig1, use_container_width=True)
    st.plotly_chart(cost_fig2, use_container_width=True)
    
    # Capacity Analysis
    st.subheader("Capacity Analysis")
    capacity_fig1, capacity_fig2 = analyze_capacity_metrics(df_vehicles)
    st.plotly_chart(capacity_fig1, use_container_width=True)
    st.plotly_chart(capacity_fig2, use_container_width=True)
    
    # Performance Analysis
    st.subheader("Performance Analysis")
    perf_fig1, perf_fig2 = analyze_performance_metrics(df_vehicles)
    st.plotly_chart(perf_fig1, use_container_width=True)
    st.plotly_chart(perf_fig2, use_container_width=True)

# Starships Analysis
elif category == "Starships":
    st.title("Star Wars Starships Analysis")
    
    # Load and process starships data
    starships_data = get_starships_data()
    if not starships_data:
        st.error("Failed to load starships data. Please try again.")
        st.stop()
        
    df_starships = create_starships_dataframe(starships_data)
    
    # Class Distribution
    st.subheader("Starship Classes")
    class_fig = analyze_starship_classes(df_starships)
    st.plotly_chart(class_fig, use_container_width=True)
    
    # Cost Analysis
    st.subheader("Cost Analysis")
    cost_fig1, cost_fig2 = analyze_starship_cost_metrics(df_starships)
    st.plotly_chart(cost_fig1, use_container_width=True)
    st.plotly_chart(cost_fig2, use_container_width=True)
    
    # Capacity Analysis
    st.subheader("Capacity Analysis")
    capacity_fig1, capacity_fig2 = analyze_starship_capacity_metrics(df_starships)
    st.plotly_chart(capacity_fig1, use_container_width=True)
    st.plotly_chart(capacity_fig2, use_container_width=True)
    
    # Performance Analysis
    st.subheader("Performance Analysis")
    perf_fig1, perf_fig2 = analyze_starship_performance_metrics(df_starships)
    st.plotly_chart(perf_fig1, use_container_width=True)
    st.plotly_chart(perf_fig2, use_container_width=True)
    
    # Summary Statistics
    st.subheader("Summary Statistics")
    stats = get_starship_stats(df_starships)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Starships", stats['total_starships'])
    with col2:
        st.metric("Unique Classes", stats['unique_classes'])
    with col3:
        st.metric("Average Cost", f"{stats['avg_cost']:,.0f} credits")

# Footer
st.markdown("---")
st.markdown("### About")
st.write("This dashboard provides comprehensive analysis of the Star Wars universe using data from various sources.")