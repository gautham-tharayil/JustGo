import React, { useState, useEffect } from 'react';

// The base URL for your Flask API.
const API_URL = "http://localhost:5000";

// --- Helper Component: Loading Spinner ---
// A simple spinner to show during network requests.
const Spinner = () => (
  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
);

// --- Dashboard Component ---
// This component is shown after a user successfully logs in.
// I've created it here to make the example fully runnable.
const Dashboard = ({ user, onLogout }) => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch dashboard data when the component loads.
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Corrected the endpoint to /api/dashboard
        const response = await fetch(`${API_URL}/api/dashboard`);
        if (!response.ok) {
          throw new Error('Failed to fetch dashboard data.');
        }
        const dashboardData = await response.json();
        setData(dashboardData);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-4 sm:p-6 lg:p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <header className="flex justify-between items-center bg-white p-4 rounded-xl shadow-md mb-8">
          <h1 className="text-2xl font-bold text-gray-800">Travel Planner</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600 hidden sm:block">Welcome, {user.email}!</span>
            <button
              onClick={onLogout}
              className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg transition duration-300"
            >
              Logout
            </button>
          </div>
        </header>

        {/* Main Content */}
        {isLoading && <p className="text-center text-gray-500">Loading dashboard...</p>}
        {error && <p className="text-center text-red-500 bg-red-100 p-3 rounded-lg">{error}</p>}
        {data && (
          <div className="bg-white p-6 rounded-xl shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">{data.welcome}</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div className="bg-blue-100 p-4 rounded-lg">
                <p className="text-3xl font-bold text-blue-600">{data.user_stats.total_trips}</p>
                <p className="text-blue-800">Total Trips</p>
              </div>
              <div className="bg-green-100 p-4 rounded-lg">
                <p className="text-3xl font-bold text-green-600">{data.user_stats.upcoming_trips}</p>
                <p className="text-green-800">Upcoming</p>
              </div>
              <div className="bg-purple-100 p-4 rounded-lg">
                <p className="text-3xl font-bold text-purple-600">{data.user_stats.completed_trips}</p>
                <p className="text-purple-800">Completed</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};


// --- Main App Component ---
// This is the main component that handles login logic.
export default function App() {
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState("admin@travel.com"); // Pre-filled for convenience
  const [password, setPassword] = useState("admin123"); // Pre-filled for convenience
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // --- Login Handler ---
  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      // ***FIXED***: Changed endpoint from `/login` to `/api/login` to match the Flask server.
      const response = await fetch(`${API_URL}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      // Check if the response was not successful (e.g., 401 Unauthorized)
      if (!response.ok) {
        // Use the error message from the server, or a default message.
        throw new Error(data.error || "Login failed. Please check your credentials.");
      }
      
      // ***FIXED***: Correctly accessed user data from `data.user.id` and `data.user.email`.
      setUser({ id: data.user.id, email: data.user.email });
      
    } catch (err) {
      // Set the error message to be displayed to the user.
      setError(err.message);
    } finally {
      // Always stop loading, whether success or failure.
      setIsLoading(false);
    }
  };

  // --- Logout Handler ---
  const handleLogout = () => {
    setUser(null);
    setError("");
  };

  // If the user is logged in, show the Dashboard.
  if (user) {
    return <Dashboard user={user} onLogout={handleLogout} />;
  }

  // Otherwise, show the Login form.
  return (
    <div className="bg-gray-100 flex items-center justify-center min-h-screen">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-extrabold text-gray-900">
            AI Itinerary Planner
          </h1>
          <p className="mt-2 text-gray-600">
            Sign in to continue to your dashboard
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          {/* Display error message if it exists */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg text-center">
              <span className="font-medium">{error}</span>
            </div>
          )}

          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address (e.g., admin@travel.com)"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <div>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password (e.g., admin123)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-400"
              disabled={isLoading}
            >
              {/* Show spinner when loading, otherwise show text */}
              {isLoading ? <Spinner /> : 'Sign in'}
            </button>
          </div>
        </form>
        <p className="text-center text-sm text-gray-500">
          Use admin@travel.com / admin123 to log in.
        </p>
      </div>
    </div>
  );
}
