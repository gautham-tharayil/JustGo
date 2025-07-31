import React, { useState, useEffect } from "react";

const API_URL = "http://localhost:5000";

export default function Dashboard({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [dashboardData, setDashboardData] = useState(null);
  const [trips, setTrips] = useState([]);
  const [destinations, setDestinations] = useState([]);
  const [weather, setWeather] = useState(null);
  const [selectedCity, setSelectedCity] = useState("Paris");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDashboardData();
  }, []);

  useEffect(() => {
    if (activeTab === "weather") {
      loadWeather(selectedCity);
    }
  }, [activeTab, selectedCity]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError("");

      // Load dashboard overview
      const dashboardResponse = await fetch(`${API_URL}/dashboard`);
      if (!dashboardResponse.ok) throw new Error("Failed to load dashboard");
      const dashboardData = await dashboardResponse.json();
      setDashboardData(dashboardData);

      // Load trips
      const tripsResponse = await fetch(`${API_URL}/trips`);
      if (!tripsResponse.ok) throw new Error("Failed to load trips");
      const tripsData = await tripsResponse.json();
      setTrips(tripsData.trips);

      // Load destinations
      const destinationsResponse = await fetch(`${API_URL}/destinations`);
      if (!destinationsResponse.ok) throw new Error("Failed to load destinations");
      const destinationsData = await destinationsResponse.json();
      setDestinations(destinationsData.destinations);

    } catch (error) {
      console.error("Dashboard load error:", error);
      setError(`Failed to load dashboard: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadWeather = async (city) => {
    try {
      const response = await fetch(`${API_URL}/weather/${city}`);
      if (!response.ok) throw new Error("Failed to load weather");
      const weatherData = await response.json();
      setWeather(weatherData);
    } catch (error) {
      console.error("Weather load error:", error);
      setError(`Failed to load weather: ${error.message}`);
    }
  };

  const renderOverview = () => (
    <div style={styles.tabContent}>
      <h2>Welcome back, {user.email}! 👋</h2>
      
      {dashboardData && (
        <>
          <div style={styles.statsGrid}>
            <div style={styles.statCard}>
              <h3>🧳 Total Trips</h3>
              <p style={styles.statNumber}>{dashboardData.user_stats.total_trips}</p>
            </div>
            <div style={styles.statCard}>
              <h3>⏰ Upcoming</h3>
              <p style={styles.statNumber}>{dashboardData.user_stats.upcoming_trips}</p>
            </div>
            <div style={styles.statCard}>
              <h3>✅ Completed</h3>
              <p style={styles.statNumber}>{dashboardData.user_stats.completed_trips}</p>
            </div>
          </div>

          <div style={styles.section}>
            <h3>🌟 Recent Trips</h3>
            <div style={styles.tripsGrid}>
              {dashboardData.recent_trips.map(trip => (
                <div key={trip.id} style={styles.tripCard}>
                  <div style={styles.tripImage}>{trip.image}</div>
                  <div style={styles.tripInfo}>
                    <h4>{trip.destination}</h4>
                    <p>📅 {trip.date}</p>
                    <p>⏱️ {trip.duration}</p>
                    <span style={{
                      ...styles.statusBadge,
                      backgroundColor: trip.status === 'upcoming' ? '#007BFF' : '#28a745'
                    }}>
                      {trip.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div style={styles.section}>
            <h3>🌤️ Current Weather</h3>
            <div style={styles.weatherCard}>
              <h4>{dashboardData.weather_info.current_location}</h4>
              <p>🌡️ {dashboardData.weather_info.temperature}</p>
              <p>☀️ {dashboardData.weather_info.condition}</p>
              <p>💧 Humidity: {dashboardData.weather_info.humidity}</p>
            </div>
          </div>
        </>
      )}
    </div>
  );

  const renderTrips = () => (
    <div style={styles.tabContent}>
      <h2>My Trips 🧳</h2>
      <div style={styles.tripsGrid}>
        {trips.map(trip => (
          <div key={trip.id} style={styles.expandedTripCard}>
            <div style={styles.tripHeader}>
              <span style={styles.tripImage}>{trip.image}</span>
              <div>
                <h3>{trip.destination}</h3>
                <p>📅 {trip.date} • ⏱️ {trip.duration}</p>
              </div>
              <span style={{
                ...styles.statusBadge,
                backgroundColor: trip.status === 'upcoming' ? '#007BFF' : '#28a745'
              }}>
                {trip.status}
              </span>
            </div>
            <div style={styles.tripDetails}>
              <p><strong>💰 Budget:</strong> {trip.budget}</p>
              <p><strong>🎯 Activities:</strong></p>
              <ul style={styles.activitiesList}>
                {trip.activities.map((activity, index) => (
                  <li key={index}>{activity}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderDestinations = () => (
    <div style={styles.tabContent}>
      <h2>Recommended Destinations 🌍</h2>
      <div style={styles.destinationsGrid}>
        {destinations.map(destination => (
          <div key={destination.id} style={styles.destinationCard}>
            <div style={styles.destinationImage}>{destination.image}</div>
            <div style={styles.destinationInfo}>
              <h3>{destination.name}</h3>
              <p>{destination.description}</p>
              <div style={styles.destinationMeta}>
                <p>⭐ {destination.rating}/5</p>
                <p>💰 {destination.price_range}</p>
                <p>📅 Best: {destination.best_time}</p>
              </div>
              <button style={styles.exploreButton}>
                Explore Destination
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderWeather = () => (
    <div style={styles.tabContent}>
      <h2>Weather Forecast 🌤️</h2>
      
      <div style={styles.weatherControls}>
        <select 
          value={selectedCity} 
          onChange={(e) => setSelectedCity(e.target.value)}
          style={styles.citySelect}
        >
          <option value="Paris">Paris</option>
          <option value="Tokyo">Tokyo</option>
          <option value="New York">New York</option>
          <option value="London">London</option>
          <option value="Bali">Bali</option>
          <option value="Rome">Rome</option>
          <option value="Dubai">Dubai</option>
          <option value="Iceland">Iceland</option>
        </select>
      </div>

      {weather && (
        <div style={styles.weatherSection}>
          <div style={styles.currentWeatherCard}>
            <h3>Current Weather in {weather.city}</h3>
            <div style={styles.weatherMain}>
              <span style={styles.temperature}>{weather.weather.temp}</span>
              <div>
                <p>☀️ {weather.weather.condition}</p>
                <p>💧 Humidity: {weather.weather.humidity}</p>
              </div>
            </div>
          </div>

          <div style={styles.forecastSection}>
            <h4>3-Day Forecast</h4>
            <div style={styles.forecastGrid}>
              {weather.forecast.map((day, index) => (
                <div key={index} style={styles.forecastCard}>
                  <h5>{day.day}</h5>
                  <p>{day.temp}</p>
                  <p>{day.condition}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>
          <h2>Loading your dashboard... ✈️</h2>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1>Travel Planner Dashboard</h1>
        <div style={styles.userInfo}>
          <span>👤 {user.email}</span>
          <button onClick={onLogout} style={styles.logoutButton}>
            Logout
          </button>
        </div>
      </header>

      {error && (
        <div style={styles.errorMessage}>
          ❌ {error}
          <button onClick={loadDashboardData} style={styles.retryButton}>
            Retry
          </button>
        </div>
      )}

      <nav style={styles.tabNav}>
        {[
          { id: "overview", label: "📊 Overview" },
          { id: "trips", label: "🧳 My Trips" },
          { id: "destinations", label: "🌍 Destinations" },
          { id: "weather", label: "🌤️ Weather" }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              ...styles.tabButton,
              backgroundColor: activeTab === tab.id ? "#007BFF" : "#f8f9fa",
              color: activeTab === tab.id ? "white" : "#333"
            }}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main style={styles.main}>
        {activeTab === "overview" && renderOverview()}
        {activeTab === "trips" && renderTrips()}
        {activeTab === "destinations" && renderDestinations()}
        {activeTab === "weather" && renderWeather()}
      </main>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    backgroundColor: "#f5f5f5",
    fontFamily: "Arial, sans-serif",
  },
  header: {
    backgroundColor: "#007BFF",
    color: "white",
    padding: "20px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  userInfo: {
    display: "flex",
    alignItems: "center",
    gap: "15px",
  },
  logoutButton: {
    padding: "8px 16px",
    backgroundColor: "#dc3545",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
  loading: {
    textAlign: "center",
    padding: "50px",
  },
  errorMessage: {
    backgroundColor: "#f8d7da",
    color: "#721c24",
    padding: "15px",
    margin: "20px",
    borderRadius: "5px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  retryButton: {
    padding: "5px 10px",
    backgroundColor: "#007BFF",
    color: "white",
    border: "none",
    borderRadius: "3px",
    cursor: "pointer",
  },
  tabNav: {
    backgroundColor: "white",
    padding: "0 20px",
    display: "flex",
    gap: "10px",
    borderBottom: "1px solid #ddd",
  },
  tabButton: {
    padding: "15px 20px",
    border: "none",
    borderRadius: "5px 5px 0 0",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "bold",
  },
  main: {
    padding: "20px",
  },
  tabContent: {
    backgroundColor: "white",
    padding: "30px",
    borderRadius: "10px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
  },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: "20px",
    marginBottom: "30px",
  },
  statCard: {
    backgroundColor: "#f8f9fa",
    padding: "20px",
    borderRadius: "10px",
    textAlign: "center",
  },
  statNumber: {
    fontSize: "2em",
    fontWeight: "bold",
    color: "#007BFF",
    margin: "10px 0",
  },
  section: {
    marginBottom: "30px",
  },
  tripsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
    gap: "20px",
  },
  tripCard: {
    backgroundColor: "#f8f9fa",
    padding: "15px",
    borderRadius: "10px",
    display: "flex",
    alignItems: "center",
    gap: "15px",
  },
  expandedTripCard: {
    backgroundColor: "#f8f9fa",
    padding: "20px",
    borderRadius: "10px",
  },
  tripHeader: {
    display: "flex",
    alignItems: "center",
    gap: "15px",
    marginBottom: "15px",
  },
  tripImage: {
    fontSize: "2em",
    minWidth: "50px",
  },
  tripInfo: {
    flex: 1,
  },
  tripDetails: {
    paddingTop: "15px",
    borderTop: "1px solid #ddd",
  },
  statusBadge: {
    padding: "5px 10px",
    borderRadius: "15px",
    color: "white",
    fontSize: "12px",
    fontWeight: "bold",
    textTransform: "uppercase",
  },
  activitiesList: {
    margin: "10px 0",
    paddingLeft: "20px",
  },
  weatherCard: {
    backgroundColor: "#f8f9fa",
    padding: "20px",
    borderRadius: "10px",
    maxWidth: "300px",
  },
  destinationsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))",
    gap: "20px",
  },
  destinationCard: {
    backgroundColor: "#f8f9fa",
    borderRadius: "10px",
    overflow: "hidden",
  },
  destinationImage: {
    fontSize: "4em",
    textAlign: "center",
    padding: "20px",
    backgroundColor: "#e9ecef",
  },
  destinationInfo: {
    padding: "20px",
  },
  destinationMeta: {
    display: "flex",
    justifyContent: "space-between",
    margin: "15px 0",
    fontSize: "14px",
  },
  exploreButton: {
    width: "100%",
    padding: "10px",
    backgroundColor: "#007BFF",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    fontWeight: "bold",
  },
  weatherControls: {
    marginBottom: "20px",
  },
  citySelect: {
    padding: "10px",
    fontSize: "16px",
    borderRadius: "5px",
    border: "1px solid #ddd",
    minWidth: "200px",
  },
  weatherSection: {
    display: "grid",
    gap: "20px",
  },
  currentWeatherCard: {
    backgroundColor: "#f8f9fa",
    padding: "20px",
    borderRadius: "10px",
  },
  weatherMain: {
    display: "flex",
    alignItems: "center",
    gap: "20px",
    marginTop: "15px",
  },
  temperature: {
    fontSize: "3em",
    fontWeight: "bold",
    color: "#007BFF",
  },
  forecastSection: {
    backgroundColor: "#f8f9fa",
    padding: "20px",
    borderRadius: "10px",
  },
  forecastGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
    gap: "15px",
    marginTop: "15px",
  },
  forecastCard: {
    backgroundColor: "white",
    padding: "15px",
    borderRadius: "8px",
    textAlign: "center",
  },
};