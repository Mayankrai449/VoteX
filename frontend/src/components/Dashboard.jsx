import React, { useState } from 'react';
import Layout from './layout';

const Dashboard = () => {
  const [flashMessage, setFlashMessage] = useState('');
  const [flashType, setFlashType] = useState('');

  const handleVote = (e) => {
    e.preventDefault();
    const pollId = e.target.poll_id.value;
    // Perform vote action with pollId
    setFlashMessage('Vote submitted successfully!');
    setFlashType('success');
    e.target.poll_id.value = '';
  };

  return (
    <Layout flashMessage={flashMessage} setFlashMessage={setFlashMessage} flashType={flashType} setFlashType={setFlashType}>
      <div>
        <style>
          {`
            body {
              overflow: hidden;
            }
          `}
        </style>
        <div className="container mx-auto px-4 py-8">
          <div className="heading">
            <h1>VoteX</h1>
            <h2>Create and Vote from Anywhere</h2>
            <div style={{ height: '50px' }}></div>
            <img src="/static/line.png" alt="line" />
          </div>

          <div className="clickcard max-w-sm bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700">
            <a href="/pollform">
              <img className="rounded-t-lg imgsize" src="/static/createpoll.jpg" alt="Create Poll" />
            </a>
            <div className="p-5">
              <a href="/pollform">
                <h5 className="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Create a New Poll</h5>
              </a>
              <p className="mb-3 font-normal text-gray-700 dark:text-gray-400">Customize a Decentralized Election secured by blockchain and share the poll</p>
              <a
                href="/pollform"
                className="inline-flex items-center px-3 py-2 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
              >
                Create Poll
                <svg className="rtl:rotate-180 w-3.5 h-3.5 ms-2" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 10">
                  <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 5h12m0 0L9 1m4 4L9 9" />
                </svg>
              </a>
            </div>
          </div>

          <div className="votecard max-w-sm bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700">
            <a onClick={() => document.querySelector('.myDropdown').classList.toggle('show')} href="#">
              <img className="rounded-t-lg imgsize" src="/static/vote.png" alt="Vote" />
            </a>
            <div className="p-5">
              <a onClick={() => document.querySelector('.myDropdown').classList.toggle('show')} href="#">
                <h5 className="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Cast Vote</h5>
              </a>
              <p className="mb-3 font-normal text-gray-700 dark:text-gray-400">Enter the Poll ID to verify voter and cast the vote</p>
              <a
                onClick={() => document.querySelector('.myDropdown').classList.toggle('show')}
                href="#"
                className="inline-flex items-center px-3 py-2 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
              >
                Vote
                <svg className="rtl:rotate-180 w-3.5 h-3.5 ms-2" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 10">
                  <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 5h12m0 0L9 1m4 4L9 9" />
                </svg>
              </a>
            </div>
          </div>

          <form method="post" action="/vote" onSubmit={handleVote} className="myDropdown voteverify w-full max-w-sm" style={{ bottom: '80px' }}>
            <div className="flex items-center border-b border-blue-500 py-2">
              <input
                className="appearance-none bg-transparent border-none w-full text-stone-50 mr-3 py-1 px-2 leading-tight focus:outline-none"
                type="text"
                name="poll_id"
                placeholder="Poll ID"
                aria-label="Poll ID"
              />
              <button className="flex-shrink-0 border-transparent border-4 text-blue-500 hover:text-teal-800 text-sm py-1 px-2 rounded" type="submit">
                Goto Poll
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
