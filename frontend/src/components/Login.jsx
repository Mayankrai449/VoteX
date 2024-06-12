import React, { useState, useEffect } from 'react';
import api from '../api';
import { useHistory } from 'react-router-dom';
import Layout from './layout';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [flashMessage, setFlashMessage] = useState('');
  const [flashType, setFlashType] = useState('');
  const history = useHistory();

  useEffect(() => {
    const flashMessage = document.cookie
      .split('; ')
      .find((row) => row.startsWith('flash_message='))
      ?.split('=')[1];
    const flashType = document.cookie
      .split('; ')
      .find((row) => row.startsWith('flash_type='))
      ?.split('=')[1];

    setFlashMessage(flashMessage);
    setFlashType(flashType);

    document.cookie = 'flash_message=; Max-Age=0';
    document.cookie = 'flash_type=; Max-Age=0';
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/user/login', {
        username,
        password,
      });
      if (response.status === 200) {
        history.push('/dashboard');
      }
    } catch (error) {
      setFlashMessage('Incorrect username or password');
      setFlashType('failure');
    }
  };

  const handleDismiss = () => {
    setFlashMessage('');
    setFlashType('');
  };

  return (
    <Layout flashMessage={flashMessage} setFlashMessage={setFlashMessage} flashType={flashType} setFlashType={setFlashType}>
      <div>
        {flashMessage && (
          <div
            className={`flex items-center p-4 mb-4 border-t-4 ${
              flashType === 'neutral'
                ? 'text-blue-800 border-blue-300 bg-blue-50'
                : flashType === 'failure'
                ? 'text-red-800 border-red-300 bg-red-50'
                : 'text-green-800 border-green-300 bg-green-50'
            }`}
            role="alert"
          >
            <svg
              className="flex-shrink-0 w-4 h-4"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0Z" />
            </svg>
            <div className="ms-3 text-sm font-medium">{flashMessage}</div>
            <button
              type="button"
              className="close-button ms-auto -mx-1.5 -my-1.5 rounded-lg p-1.5 inline-flex items-center justify-center h-8 w-8"
              onClick={handleDismiss}
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
        <section>
          <div className="flex flex-col items-center justify-center px-6 py-8 mx-auto md:h-screen lg:py-0">
            <h1 style={{ marginBottom: '40px', fontStyle: 'bold', fontSize: '70px', color: 'white' }}>VoteX</h1>
            <div
              className="w-full bg-white rounded-lg shadow dark:border md:mt-0 sm:max-w-md xl:p-0 dark:bg-gray-800 dark:border-gray-700"
              style={{ marginBottom: '30px' }}
            >
              <div className="p-6 space-y-4 md:space-y-6 sm:p-8">
                <h1 className="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white">
                  Sign in to your account
                </h1>
                <form className="space-y-4 md:space-y-6" onSubmit={handleSubmit}>
                  <div>
                    <label htmlFor="username" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                      Your Username
                    </label>
                    <input
                      type="text"
                      name="username"
                      id="username"
                      className="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                      placeholder="username"
                      required
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                    />
                  </div>
                  <div>
                    <label htmlFor="password" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                      Password
                    </label>
                    <input
                      type="password"
                      name="password"
                      id="password"
                      placeholder="••••••••"
                      className="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <a
                      href="/password"
                      className="text-sm font-medium text-primary-600 hover:underline dark:text-primary-500"
                      style={{ color: '#7CB9E8' }}
                    >
                      Forgot password?
                    </a>
                  </div>
                  <button
                    type="submit"
                    className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800"
                  >
                    Sign In
                  </button>
                  <p className="text-sm font-light text-gray-500 dark:text-gray-400">
                    Don't have an account yet?{' '}
                    <a
                      href="/register"
                      className="font-medium text-primary-600 hover:underline dark:text-primary-500"
                      style={{ color: '#7CB9E8' }}
                    >
                      Register
                    </a>
                  </p>
                </form>
              </div>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
};

export default LoginPage;
