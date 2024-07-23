# MovieRadar Bot

MovieRadar is a Discord bot that notifies users about trending movies. It can send trending movie information to a specified channel and monitor for new trending movies at regular intervals.

## Features

- Set a channel for movie notifications
- Fetch and display the list of trending movies
- Display the current settings for the server
- Start and stop monitoring for new movies
- Check if the bot is live with a ping command

## Requirements

- Python 3.8+
- Discord account and server
- Discord bot token

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/whistle-dev/MovieRadar.git
   cd MovieRadar
   ```

2. Create a virtual environment and activate it:

   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project directory and add your bot token and application ID:
   ```env
   BOT_TOKEN=your_discord_bot_token
   APPLICATION_ID=your_application_id
   ```

## Usage

1. Register the bot commands:

   ```sh
   python register_commands.py
   ```

2. Start the bot:
   ```sh
   python main.py
   ```

## Commands

- `/setchannel`: Sets the channel for movie notifications.
- `/trending`: Fetches and sends the list of trending movies.
- `/status`: Displays the current settings for the server.
- `/ping`: Check if the bot is live.
- `/startmonitoring`: Starts monitoring for new movies.
- `/stopmonitoring`: Stops monitoring for new movies.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
