import React, { useState, useEffect } from 'react';

// The base URL for your Flask API.
const API_URL = "http://localhost:5000";

// --- Helper Component: Loading Spinner ---
const Spinner = () => (
  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
);

// --- Dashboard Component ---
// This is the new, multi-tab dashboard with all fixes applied.
const Dashboard = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState("overview");
  const [dashboardData, setDashboardData] = useState(null);
  const [trips, setTrips] = useState([]);
  const [destinations, setDestinations] = useState([]);
  const [weather, setWeather] = useState(null);
  const [selectedCity, setSelectedCity] = useState("Paris");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // --- Data Loading Effect ---
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        setError("");

        // ***FIXED***: Added '/api' prefix to all fetch calls.
        const [dashRes, tripsRes, destRes] = await Promise.all([
          fetch(`${API_URL}/api/dashboard`),
          fetch(`${API_URL}/api/trips`),
          fetch(`${API_URL}/api/destinations`),
        ]);

        if (!dashRes.ok || !tripsRes.ok || !destRes.ok) {
          throw new Error("Failed to load initial dashboard data.");
        }

        const dashData = await dashRes.json();
        const tripsData = await tripsRes.json();
        const destData = await destRes.json();

        setDashboardData(dashData);
        setTrips(tripsData.trips);
        setDestinations(destData.destinations);
        
      } catch (err) {
        console.error("Dashboard load error:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, []); // Runs once on component mount

  // --- Weather Loading Effect ---
  useEffect(() => {
    const loadWeather = async () => {
      if (activeTab !== 'weather') return;
      try {
        // ***FIXED***: Added '/api' prefix.
        const response = await fetch(`${API_URL}/api/weather/${selectedCity}`);
        if (!response.ok) throw new Error(`Failed to load weather for ${selectedCity}`);
        const weatherData = await response.json();
        setWeather(weatherData);
      } catch (err) {
        console.error("Weather load error:", err);
        setError(err.message);
      }
    };
    
    loadWeather();
  }, [activeTab, selectedCity]); // Runs when tab or city changes

  // --- Render Functions for Tabs ---
  const renderOverview = () => (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Welcome back, {user.email}! 👋</h2>
      {dashboardData && (
        <div className="space-y-8">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-blue-100 p-6 rounded-xl text-center"><h3 className="font-semibold text-blue-800">🧳 Total Trips</h3><p className="text-4xl font-bold text-blue-600 mt-2">{dashboardData.user_stats.total_trips}</p></div>
            <div className="bg-green-100 p-6 rounded-xl text-center"><h3 className="font-semibold text-green-800">⏰ Upcoming</h3><p className="text-4xl font-bold text-green-600 mt-2">{dashboardData.user_stats.upcoming_trips}</p></div>
            <div className="bg-purple-100 p-6 rounded-xl text-center"><h3 className="font-semibold text-purple-800">✅ Completed</h3><p className="text-4xl font-bold text-purple-600 mt-2">{dashboardData.user_stats.completed_trips}</p></div>
          </div>
          {/* Recent Trips */}
          <div>
            <h3 className="text-xl font-bold text-gray-700 mb-4">🌟 Recent Trips</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {dashboardData.recent_trips.map(trip => (
                <div key={trip.id} className="bg-white p-4 rounded-xl shadow-sm flex items-center gap-4">
                  <div className="text-4xl">{trip.image}</div>
                  <div>
                    <h4 className="font-bold">{trip.destination}</h4>
                    <p className="text-sm text-gray-500">📅 {trip.date}</p>
                    <span className={`text-xs font-bold px-2 py-1 rounded-full text-white ${trip.status === 'upcoming' ? 'bg-blue-500' : 'bg-green-500'}`}>{trip.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderTrips = () => (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">My Trips 🧳</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {trips.map(trip => (
          <div key={trip.id} className="bg-white p-6 rounded-xl shadow-sm">
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-4">
                <div className="text-5xl">{trip.image}</div>
                <div>
                  <h3 className="text-xl font-bold">{trip.destination}</h3>
                  <p className="text-sm text-gray-500">📅 {trip.date} • ⏱️ {trip.duration}</p>
                </div>
              </div>
              <span className={`text-xs font-bold px-3 py-1 rounded-full text-white ${trip.status === 'upcoming' ? 'bg-blue-500' : 'bg-green-500'}`}>{trip.status}</span>
            </div>
            <div className="mt-4 pt-4 border-t">
              <p><strong>💰 Budget:</strong> {trip.budget}</p>
              <p className="mt-2"><strong>🎯 Activities:</strong></p>
              <ul className="list-disc list-inside text-gray-600 mt-1">
                {trip.activities.map((activity, index) => <li key={index}>{activity}</li>)}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
  
  // --- Main Return ---
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">Travel Planner</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600 hidden sm:block">Welcome, {user.email}!</span>
            <button onClick={onLogout} className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg transition duration-300">Logout</button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center items-center h-64"><Spinner /></div>
        ) : error ? (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg text-center">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline ml-2">{error}</span>
          </div>
        ) : (
          <div>
            <div className="mb-6 border-b border-gray-200">
              <nav className="-mb-px flex space-x-6">
                <button onClick={() => setActiveTab('overview')} className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'overview' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>📊 Overview</button>
                <button onClick={() => setActiveTab('trips')} className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'trips' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>🧳 My Trips</button>
              </nav>
            </div>
            <div className="bg-gray-50 p-6 rounded-xl">
              {activeTab === 'overview' && renderOverview()}
              {activeTab === 'trips' && renderTrips()}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};


// --- Main App Component (Login Page) ---
export default function App() {
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState("admin@travel.com");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Login failed.");
      }
      setUser({ id: data.user.id, email: data.user.email });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    setUser(null);
    setError("");
  };

  if (user) {
    return <Dashboard user={user} onLogout={handleLogout} />;
  }

  return (
    <div className="bg-gray-100 flex items-center justify-center min-h-screen">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-extrabold text-gray-900">AI Itinerary Planner</h1>
          <p className="mt-2 text-gray-600">Sign in to continue</p>
        </div>
        <form onSubmit={handleLogin} className="space-y-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg text-center">
              <span className="font-medium">{error}</span>
            </div>
          )}
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <input id="email-address" name="email" type="email" required className="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" placeholder="Email address (admin@travel.com)" value={email} onChange={(e) => setEmail(e.target.value)} disabled={isLoading} />
            </div>
            <div>
              <input id="password" name="password" type="password" required className="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" placeholder="Password (admin123)" value={password} onChange={(e) => setPassword(e.target.value)} disabled={isLoading} />
            </div>
          </div>
          <div>
            <button type="submit" className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-400" disabled={isLoading}>
              {isLoading ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div> : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
