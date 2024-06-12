// Layout.js
import React, { useState, useEffect, useRef } from 'react';
import api from '../api';
import blocklogo from '../images/blocklogo.png';
import userlogo from '../images/user.webp';
import '../index.css';
import './Layout.css';

const Layout = ({ children, flashMessage, flashType, clearFlashMessage }) => {
  const [user, setUser] = useState('');
  const [email, setEmail] = useState('');
  const dropdownRef = useRef(null);
  const userMenuButtonRef = useRef(null);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await api.get('/userdata');
        setUser(response.data.user);
        setEmail(response.data.email);
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };

    fetchUserData();
  }, []);

  const handleLogout = (event) => {
    event.preventDefault();
    window.location.href = '/logout';
  };

  const handleCloseAlert = () => {
    clearFlashMessage();
  };

  const handleClickOutside = (event) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
      setShowDropdown(false);
    }
  };

  const toggleDropdown = () => {
    setShowDropdown(!showDropdown);
    if (!showDropdown && userMenuButtonRef.current && dropdownRef.current) {
      const rect = userMenuButtonRef.current.getBoundingClientRect();
      dropdownRef.current.style.top = `${rect.bottom + window.scrollY}px`;
      dropdownRef.current.style.left = `${rect.left + window.scrollX}px`;
    }
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div>
      <header>
        <nav className="border-gray-200 bg-gray-900">
          <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
            <a href="/dashboard" className="flex items-center space-x-3 rtl:space-x-reverse">
              <img src={blocklogo} className="h-8" alt="Flowbite Logo" />
              <span className="self-center text-2xl font-semibold whitespace-nowrap text-white">Votex</span>
            </a>
            <div className="flex items-center md:order-2 space-x-3 md:space-x-0 rtl:space-x-reverse">
              <button
                type="button"
                ref={userMenuButtonRef}
                className="flex text-sm bg-gray-800 rounded-full md:me-0 focus:ring-4 focus:ring-gray-600"
                id="user-menu-button"
                aria-expanded={showDropdown}
                onClick={toggleDropdown}
              >
                <span className="sr-only">Open user menu</span>
                <img className="w-8 h-8 rounded-full" src={userlogo} alt="user photo" />
              </button>
            </div>
            <div className="items-center justify-between hidden w-full md:flex md:w-auto md:order-1" id="navbar-user">
              <ul class="flex flex-col font-medium p-4 md:p-0 mt-4 border rounded-lg md:space-x-8 rtl:space-x-reverse md:flex-row md:mt-0 md:border-0 bg-gray-800 md:bg-gray-900 border-gray-700">
                <li>
                  <a
                    href="/about"
                    className="block py-2 px-3 text-lg rounded md:hover:bg-transparent md:p-0 text-white md:hover:text-blue-500 hover:bg-gray-700 hover:text-white md:dark:hover:bg-transparent border-gray-700"
                  >
                    About
                  </a>
                </li>
                <li>
                  <a
                    href="/polls"
                    className="block py-2 px-3 text-lg rounded md:p-0 text-white md:hover:text-blue-500 hover:bg-gray-700 hover:text-white md:hover:bg-transparent border-gray-700"
                  >
                    Polls
                  </a>
                </li>
                <li>
                  <a
                    href="/history"
                    className="block py-2 px-3 text-lg rounded md:p-0 text-white md:hover:text-blue-500 hover:bg-gray-700 hover:text-white md:hover:bg-transparent border-gray-700"
                  >
                    History
                  </a>
                </li>
                <li>
                  <a
                    href="/results"
                    className="block py-2 px-3 text-lg rounded md:p-0 text-white md:hover:text-blue-500 hover:bg-gray-700 hover:text-white md:hover:bg-transparent border-gray-700"
                  >
                    Results
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </nav>

        {/* Dropdown menu */}
        <div
          ref={dropdownRef}
          className={`z-50 ${
            showDropdown ? '' : 'hidden'
          } my-4 text-base list-none divide-y rounded-lg shadow bg-gray-700 divide-gray-600`}
          id="user-dropdown"
        >
          <div className="px-4 py-3">
            <span className="block text-sm text-white">{user}</span>
            <span className="block text-sm truncate text-gray-400">{email}</span>
          </div>
          <ul className="py-2" aria-labelledby="user-menu-button">
            <li>
              <a href="#" className="block px-4 py-2 text-sm hover:bg-gray-600 text-gray-200 hover:text-white">
                Profile
              </a>
            </li>
            <li>
              <a
                href="#"
                onClick={handleLogout}
                className="block px-4 py-2 text-sm hover:bg-gray-600 text-gray-200 hover:text-white"
              >
                Log out
              </a>
            </li>
          </ul>
        </div>
      </header>

      <div style={{ position: 'fixed', top: '65px', left: 0, width: '100%', zIndex: 1001 }}>
        {flashType === 'neutral' && (
          <div
            id="alert-border-1"
            className="flex items-center p-4 mb-4 border-t-4 text-blue-400 bg-gray-800 border-blue-800"
            role="alert"
          >
            <svg
              className="flex-shrink-0 w-4 h-4"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z" />
            </svg>
            <div className="ms-3 text-sm font-medium">{flashMessage}</div>
            <button
              type="button"
              className="close-button ms-auto -mx-1.5 -my-1.5 rounded-lg focus:ring-2 focus:ring-blue-400 p-1.5 inline-flex items-center justify-center h-8 w-8 bg-gray-800 text-blue-400 hover:bg-gray-700"
              onClick={handleCloseAlert}
              aria-label="Close"
            >
              <span className="sr-only">Dismiss</span>
              <svg
                className="w-3 h-3"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 14 14"
              >
                <path
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"
                />
              </svg>
            </button>
          </div>
        )}
        {flashType === 'failure' && (
          <div
            id="alert-border-2"
            className="flex items-center p-4 mb-4 border-t-4 text-red-400 bg-gray-800 border-red-800"
            role="alert"
          >
            <svg
              className="flex-shrink-0 w-4 h-4"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z" />
            </svg>
            <div className="ms-3 text-sm font-medium">{flashMessage}</div>
            <button
              type="button"
              className="close-button ms-auto -mx-1.5 -my-1.5 rounded-lg focus:ring-2 focus:ring-red-400 p-1.5 inline-flex items-center justify-center h-8 w-8 bg-gray-800 text-red-400 hover:bg-gray-700"
              onClick={handleCloseAlert}
              aria-label="Close"
            >
              <span className="sr-only">Dismiss</span>
              <svg
                className="w-3 h-3"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 14 14"
              >
                <path
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"
                />
              </svg>
            </button>
          </div>
        )}
        {flashType === 'success' && (
          <div
            id="alert-border-3"
            className="flex items-center p-4 mb-4 border-t-4 text-green-400 bg-gray-800 border-green-800"
            role="alert"
          >
            <svg
              className="flex-shrink-0 w-4 h-4"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z" />
            </svg>
            <div className="ms-3 text-sm font-medium">{flashMessage}</div>
            <button
              type="button"
              className="close-button ms-auto -mx-1.5 -my-1.5 rounded-lg focus:ring-2 focus:ring-green-400 p-1.5 inline-flex items-center justify-center h-8 w-8 bg-gray-800 text-green-400 hover:bg-gray-700"
              onClick={handleCloseAlert}
              aria-label="Close"
            >
              <span className="sr-only">Dismiss</span>
              <svg
                className="w-3 h-3"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 14 14"
              >
                <path
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"
                />
              </svg>
            </button>
          </div>
        )}
      </div>

      <main>{children}</main>
      <footer>
        <div style={{ position: 'fixed', left: 0, bottom: 10, width: '100%', zIndex: 9999, color: 'white', textAlign: 'center' }}>
          <p>&copy; BlockChainVotingSystem2024-mayankraivns@gmail.com</p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
