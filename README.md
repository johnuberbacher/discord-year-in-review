# Discord Year in Review

This bot tallies user activity on a Discord server, counting messages, reactions, emojis, and more, all while providing a summary of the year. It tracks activity in specified channels and offers detailed breakdowns such as message counts, top emoji usage, and the most active users.

## Features

- Count total messages and reactions
- Track custom and default emoji usage
- Track activity during specific hours (morning and evening)
- Identify top message senders and reaction givers
- Filter and count George Costanza's messages
- Provides a summary for the year with detailed outputs for each channel

## Setup

### Prerequisites
- Python 3.x
- Required Python libraries: `discord`, `asyncio`, `pytz`
- A Discord bot token

### Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/discord-activity-tally-bot.git
    ```

2. Install the required libraries:
    ```bash
    pip install discord pytz
    ```

3. Create a `config.py` file and include your bot token and channel list:
    ```python
    # config.py
    bot_token = "YOUR_BOT_TOKEN"
    channel_list = [123456789012345678, 987654321098765432]  # List of channel IDs
    ```

4. Run the bot:
    ```bash
    python bot.py
    ```

### Customization

- Modify the `MORNING_START`, `MORNING_END`, `EVENING_START`, and `EVENING_END` variables to adjust the time ranges for tracking morning and evening activity.
- Add additional logic or channels to the `channel_list` in `config.py` to track more channels.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
