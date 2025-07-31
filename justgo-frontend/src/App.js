import React, { useState, useEffect } from 'react';

const API_URL = "http://localhost:5000";

const authenticatedFetch = async (url, options = {}) => {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const response = await fetch(url, { ...options, headers });
  if (response.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.reload();
  }
  return response;
};

const Spinner = () => <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>;

const Dashboard = ({ user, onLogout }) => {
  const [overviewData, setOverviewData] = useState(null);
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        setError("");
        const [overviewRes, tripsRes] = await Promise.all([
          authenticatedFetch(`${API_URL}/api/trips/dashboard-overview`),
          authenticatedFetch(`${API_URL}/api/trips/`),
        ]);

        if (!overviewRes.ok || !tripsRes.ok) {
          throw new Error("Failed to load dashboard data. Is the server running?");
        }

        const overview = await overviewRes.json();
        const tripsData = await tripsRes.json();

        setOverviewData(overview);
        setTrips(tripsData.data.trips || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    loadDashboardData();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">Travel Planner</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600 hidden sm:block">Welcome, {user.email}!</span>
            <button onClick={onLogout} className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg">Logout</button>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? <div className="flex justify-center pt-16"><Spinner /></div> : 
         error ? <div className="bg-red-100 text-red-700 p-4 rounded-lg text-center">{error}</div> :
        (
          <div className="space-y-8">
            {overviewData && (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                <div className="bg-blue-100 p-6 rounded-xl text-center"><h3 className="font-semibold text-blue-800">Total Trips</h3><p className="text-4xl font-bold text-blue-600 mt-2">{overviewData.user_stats.total_trips}</p></div>
                <div className="bg-green-100 p-6 rounded-xl text-center"><h3 className="font-semibold text-green-800">Upcoming</h3><p className="text-4xl font-bold text-green-600 mt-2">{overviewData.user_stats.upcoming_trips}</p></div>
                <div className="bg-purple-100 p-6 rounded-xl text-center"><h3 className="font-semibold text-purple-800">Completed</h3><p className="text-4xl font-bold text-purple-600 mt-2">{overviewData.user_stats.completed_trips}</p></div>
              </div>
            )}
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">My Trips</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {trips.length > 0 ? trips.map(trip => (
                  <div key={trip.id} className="bg-white p-6 rounded-xl shadow-sm">
                    <h3 className="text-xl font-bold">{trip.title}</h3>
                    <p className="text-gray-600">{trip.destination_city}, {trip.destination_country}</p>
                  </div>
                )) : <p>No trips found. Plan your first adventure!</p>}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default function App() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoginLoading, setIsLoginLoading] = useState(false);
  const [isRegister, setIsRegister] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false);
  }, []);

  const handleAuthAction = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoginLoading(true);
    
    const url = isRegister ? `${API_URL}/api/auth/register` : `${API_URL}/api/auth/login`;

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.message || "An error occurred.");
      }
      
      if (isRegister) {
        setIsRegister(false);
        setError("Registration successful! Please log in.");
      } else {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        setUser(data.user);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoginLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  if (isLoading) {
    return <div className="min-h-screen bg-gray-100 flex justify-center items-center"><Spinner /></div>;
  }

  if (user) {
    return <Dashboard user={user} onLogout={handleLogout} />;
  }

  return (
    <div className="bg-gray-100 flex items-center justify-center min-h-screen">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-extrabold text-gray-900">AI Itinerary Planner</h1>
          <p className="mt-2 text-gray-600">{isRegister ? "Create an account" : "Sign in to continue"}</p>
        </div>
        <form onSubmit={handleAuthAction} className="space-y-6">
          {error && <div className={`p-3 rounded-lg text-center ${error.includes("successful") ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{error}</div>}
          <div className="rounded-md shadow-sm -space-y-px">
            <input type="email" required className="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" placeholder="Email address" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input type="password" required className="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <button type="submit" className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400" disabled={isLoginLoading}>
            {isLoginLoading ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div> : (isRegister ? 'Register' : 'Sign in')}
          </button>
        </form>
        <div className="text-center">
          <button onClick={() => { setIsRegister(!isRegister); setError(""); }} className="font-medium text-sm text-indigo-600 hover:text-indigo-500">
            {isRegister ? "Already have an account? Sign In" : "Don't have an account? Register"}
          </button>
        </div>
      </div>
    </div>
  );
}
