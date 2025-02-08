# SWAPI Data Analysis and Streamlit MVP

## 📌 Project Overview

This project explores, analyzes, and visualizes data from the **Star Wars API (SWAPI)** endpoints. The data is processed using Python, analyzed using Pandas, and visualized using Matplotlib, Seaborn, and Plotly. The results are integrated into an interactive **Streamlit** dashboard.

## 🚀 Features

- **Fetch and store SWAPI data** locally for faster processing.
- **Analyze key Star Wars elements** including films, characters, planets, starships, vehicles, and species.
- **Generate insightful visualizations** using bar charts, scatter plots, pie charts, and word clouds.
- **Efficient data caching** using `data_manager.py` to reduce redundant API calls.
- **Interactive Streamlit app** for real-time exploration of Star Wars data.

## 📂 Project Structure

```bash
.
├── app.py         # Streamlit dashboard for visualization
├── data_manager.py # Handles data caching and retrieval
├── films.py       # Analysis of Star Wars films
├── people.py      # Analysis of characters
├── planets.py     # Analysis of planets
├── species.py     # Analysis of species
├── starships.py   # Analysis of starships
├── vehicles.py    # Analysis of vehicles
├── README.md      # Project documentation
```

## 🔧 Setup and Installation

### Prerequisites

Ensure you have Python 3.8+ installed. Required libraries:

```bash
pip install requests pandas matplotlib seaborn plotly streamlit wordcloud
```

### Running the Project

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/swapi-analysis.git
   cd swapi-analysis
   ```
2. **Run the data manager to fetch and cache data**
   ```bash
   python data_manager.py
   ```
3. **Run the analysis scripts**
   ```bash
   python films.py
   python people.py
   python planets.py
   python species.py
   python starships.py
   python vehicles.py
   ```
4. **Launch the Streamlit dashboard**
   ```bash
   streamlit run app.py
   ```

## 📊 Data Analysis & Visualizations

### **1️⃣ Data Caching with `data_manager.py`**

- Ensures efficient data retrieval by caching API responses for **7 days**.
- Prevents redundant API requests, improving performance.
- Stores cached data in JSON format inside a `data/` directory.
- Functions available:
  - `get_films_data()`
  - `get_people_data()`
  - `get_planets_data()`
  - `get_species_data()`
  - `get_vehicles_data()`
  - `get_starships_data()`
  - `fetch_all_data()` (fetches and caches everything at once)

### **2️⃣ Films Analysis (films.py)**

- Fetches and stores film data from SWAPI.
- **Visualizations:**
  - Film release timeline
  - Number of characters, planets, starships, vehicles, and species per film
  - Word cloud of the opening crawl text

### **3️⃣ Characters Analysis (people.py)**

- Fetches and analyzes Star Wars characters.
- **Visualizations:**
  - Gender distribution
  - Height and mass comparison
  - Character appearances across films

### **4️⃣ Planets Analysis (planets.py)**

- Fetches and analyzes planetary data.
- **Visualizations:**
  - Population distribution
  - Terrain and climate classification
  - Largest and smallest planets by diameter

### **5️⃣ Species Analysis (species.py)**

- Fetches and categorizes species data.
- **Visualizations:**
  - Species classification breakdown
  - Average lifespan and height comparisons
  - Language distribution

### **6️⃣ Starships Analysis (starships.py)**

- Fetches and evaluates starships.
- **Visualizations:**
  - Cost vs speed analysis
  - Top starships by cargo capacity
  - Most frequently appearing starships

### **7️⃣ Vehicles Analysis (vehicles.py)**

- Fetches and compares vehicles.
- **Visualizations:**
  - Vehicle class distribution
  - Speed vs length analysis
  - Top 10 most expensive vehicles

## 🎯 Future Improvements

- Implement real-time API data fetching in the Streamlit app.
- Add more interactive filters for deeper exploration.
- Expand analysis to include Star Wars trivia and lesser-known facts.

## 📝 License

This project is licensed under the **MIT License**.

## 🙌 Acknowledgments

- **SWAPI (Star Wars API)** for providing the dataset.
- **Python & Streamlit Community** for libraries and inspiration.

---

!https://github.com/VulcanWhale/SWAPI-data-analysis/blob/eb59a55def3fbf718233ef6e64aa1b48ce585078/characters.png

📌 **Contributions & Feedback:** Feel free to open an issue or submit a pull request!
