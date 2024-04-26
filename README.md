# VoteX

## Introduction
Welcome to the Voting System VoteX! This document provides an overview of the features, setup instructions, and usage guidelines for the Voting System application.

## Features
1. **Poll Creation**: Users can create polls with titles, descriptions, and options for voting.
2. **Real-Time Voting**: Users can vote on the available options in a poll.
3. **Poll Results**: Users can view the results of a poll, including the number of votes for each option.
4. **Authentication**: JWT Authentication is implemented to ensure that only authorized users can create and vote on polls.

## Setup Instructions
Follow these steps to set up the Voting System locally:

1. **Clone Repository**: Clone the repository to your local machine using Git.

 git clone https://github.com/Mayankrai449/Blockchain-voting-system

2. **Navigate to Directory**: Change your directory to the cloned repository.


3. **Install Dependencies**: Install the required Python dependencies using pip.

pip install -r requirements.txt

4. **Set Environment Variables**: Configure any necessary environment variables, such as database connection strings or authentication tokens, in a `.env` file.

5. **Run the Application**: Start the FastAPI server to run the application.

uvicorn main:app --reload

or

Run the main.py file

6. **Access the Application**: Access the Voting System application in your web browser at `http://localhost:8000`.

## Usage Guidelines
1. **Creating a Poll**:
- Navigate to the application's homepage.
- Click on the "Create Poll" button.
- Fill in the required details such as title, description, options, etc.
- Submit the form to create the poll.

2. **Voting on a Poll**:
- Browse the list of available polls on the homepage.
- Click on a poll to view its details.
- Select an option and submit your vote.

3. **Viewing Poll Results**:
- After voting, or at any time, you can view the results of a poll.
- Navigate to the poll's details page.
- The results, including the number of votes for each option, will be displayed.

4. **Authentication**:
- To create a poll or vote on a poll, users need to authenticate.
- Use the provided authentication mechanism to log in or register as a new user.

5. **Flash Messages**:
- Flash messages are displayed to provide feedback to users after performing actions such as creating a poll or voting.
- These messages convey success or failure information and are visible for a short duration.

## Contributors
- John Doe (@johndoe) - Project Lead
- Jane Smith (@janesmith) - Frontend Developer
- Alex Johnson (@alexjohnson) - Backend Developer

## Support
For any inquiries or assistance, please contact mayankraivns@gmail.com

Thank you for using the Votex!
