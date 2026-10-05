import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Navbar.css";

const Navbar = () => {
  const { isAuthenticated, username, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="navbar navbar-expand-lg sbd-navbar">
      <div className="container">
        <Link className="navbar-brand sbd-brand" to="/">
          Soweto Business Directory
        </Link>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav ms-auto align-items-lg-center">
            <li className="nav-item">
              <Link className="nav-link sbd-nav-link" to="/">
                Home
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link sbd-nav-link" to="/about">
                About
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link sbd-nav-link" to="/contact">
                Contact
              </Link>
            </li>
            {isAuthenticated ? (
              <>
                <li className="nav-item">
                  <span className="sbd-nav-link sbd-nav-username">
                    Hi, {username}
                  </span>
                </li>
                <li className="nav-item">
                  <button className="sbd-nav-logout-btn" onClick={handleLogout}>
                    Log Out
                  </button>
                </li>
              </>
            ) : (
              <>
                <li className="nav-item">
                  <Link className="nav-link sbd-nav-link" to="/login">
                    Log In
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className="sbd-nav-signup-btn" to="/signup">
                    Sign Up
                  </Link>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;