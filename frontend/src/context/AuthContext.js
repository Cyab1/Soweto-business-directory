import React, { createContext, useContext, useState } from "react";
import { loginUser, registerUser } from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [username, setUsername] = useState(
    localStorage.getItem("sbd_username"),
  );

  const login = async (usernameInput, password) => {
    const data = await loginUser(usernameInput, password);
    localStorage.setItem("sbd_access_token", data.access);
    localStorage.setItem("sbd_refresh_token", data.refresh);
    localStorage.setItem("sbd_username", usernameInput);
    setUsername(usernameInput);
  };

  const register = async (usernameInput, email, password) => {
    await registerUser(usernameInput, email, password);
    await login(usernameInput, password);
  };

  const logout = () => {
    localStorage.removeItem("sbd_access_token");
    localStorage.removeItem("sbd_refresh_token");
    localStorage.removeItem("sbd_username");
    setUsername(null);
  };

  return (
    <AuthContext.Provider
      value={{ username, isAuthenticated: !!username, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
