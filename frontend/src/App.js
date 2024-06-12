import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Layout from './components/layout';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import ErrorBoundary from './components/ErrorBoundary';

const App = () => {
  const [flashMessage, setFlashMessage] = useState('');
  const [flashType, setFlashType] = useState('');

  const handleSetFlashMessage = (message, type) => {
    setFlashMessage(message);
    setFlashType(type);
  };

  const clearFlashMessage = () => {
    setFlashMessage('');
    setFlashType('');
  };

  return (
    <Router>
      <ErrorBoundary>
      <Layout flashMessage={flashMessage} flashType={flashType} clearFlashMessage={clearFlashMessage}>
        <Switch>
          <Route path="/dashboard">
            <Dashboard setFlashMessage={handleSetFlashMessage} />
          </Route>
          <Route path="/login">
            <Login setFlashMessage={handleSetFlashMessage} />
          </Route>
        </Switch>
      </Layout>
      </ErrorBoundary>
    </Router>
  );
};

export default App;
