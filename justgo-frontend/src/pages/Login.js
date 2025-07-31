import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser, registerUser } from "../api";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    let response;
    if (isRegister) {
      response = await registerUser(email, password);
    } else {
      response = await loginUser(email, password);
      if (response.success) {
        localStorage.setItem("token", response.token);
        navigate("/dashboard");
      }
    }
    setMessage(response.message || "Action completed");
  };

  return (
    <div className="container">
      <h2>{isRegister ? "Register" : "Login"}</h2>
      <form onSubmit={handleSubmit}>
        <input type="email" value={email} placeholder="Email"
               onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" value={password} placeholder="Password"
               onChange={(e) => setPassword(e.target.value)} required />
        <button type="submit">{isRegister ? "Register" : "Login"}</button>
      </form>
      <p>{message}</p>
      <button onClick={() => setIsRegister(!isRegister)}>
        {isRegister ? "Already have an account? Login" : "No account? Register"}
      </button>
    </div>
  );
};

export default Login;
