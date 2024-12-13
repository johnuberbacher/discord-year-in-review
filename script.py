import discord
import asyncio
import os
from datetime import datetime
import pytz

from config import channel_list, bot_token

# Set up the Discord client
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.reactions = True

# Create a Discord client
client = discord.Client(intents=intents)

# Define the time range for morning and evening (in EST)
EST = pytz.timezone('US/Eastern')
MORNING_START = 3  # 3 AM EST
MORNING_END = 7    # 7 AM EST
EVENING_START = 22  # 10 PM EST
EVENING_END = 2    # 2 AM EST (next day)

@client.event
async def on_ready():
    print(f"{client.user.name} is ready.")
    await tally_messages(year=2024)
    await client.close()  # Close the client when done

async def tally_messages(year):
    total_messages = 0
    total_reactions = 0
    user_join_dates = {}
    user_message_counts = {}
    user_reaction_counts = {}
    daily_activity = {}

    youtube_link_counts = {}
    discord_link_counts = {}
    non_youtube_discord_counts = {}
    george_message_count = 0

    custom_emoji_counts = {}
    default_emoji_counts = {}

    # Initialize counters for morning and evening message counts
    morning_message_counts = {}
    evening_message_counts = {}

    # Define the start and end datetime for the specified year
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)

    # Store the printed output for each channel to print at the end
    channel_outputs = []

    print(f"Tallying messages...")

    # Initialize a dictionary for top reactions per channel
    top_reactions_per_channel = {channel_id: [] for channel_id in channel_list}
    top_messages_per_channel = {channel_id: [] for channel_id in channel_list}  # Added for top 5 message senders per channel

    for channel_id in channel_list:
        channel = client.get_channel(channel_id)
        
        if not channel:
            continue
        
        user_message_count = {}
        user_reaction_count = {}
        top_reactions = []
        message_count = 0  # Initialize message count for each channel

        # Initialize channel-specific output
        channel_output = []

        async for message in channel.history(limit=None, after=start_date, before=end_date):
            if message.author.bot:
                if message.author.name == "George Costanza" and message.author.discriminator == "7488":
                    george_message_count += 1
                continue

            # Tally message counts
            user_message_count[message.author.name] = user_message_count.get(message.author.name, 0) + 1
            total_messages += 1
            message_count += 1  # Increment message count for print statements

            # Tally reaction counts
            reaction_count = sum(reaction.count for reaction in message.reactions)
            if reaction_count > 0:
                user_reaction_count[message.author.name] = user_reaction_count.get(message.author.name, 0) + reaction_count

                # Store additional metadata for top reactions in the channel
                top_reactions.append({
                    'message_content': message.content,
                    'reaction_count': reaction_count,
                    'author': message.author.name,
                    'timestamp': message.created_at,
                    'link': message.jump_url
                })
                total_reactions += reaction_count

                # Tally custom and default emojis
                for reaction in message.reactions:
                    if reaction.is_custom_emoji():
                        custom_emoji_counts[str(reaction.emoji)] = custom_emoji_counts.get(str(reaction.emoji), 0) + reaction.count
                    else:
                        default_emoji_counts[str(reaction.emoji)] = default_emoji_counts.get(str(reaction.emoji), 0) + reaction.count

            # Track daily activity
            message_date = message.created_at.strftime('%Y-%m-%d')
            if message_date not in daily_activity:
                daily_activity[message_date] = {'messages': 0, 'reactions': 0}
            daily_activity[message_date]['messages'] += 1
            daily_activity[message_date]['reactions'] += reaction_count 

            # Convert message timestamp to EST
            message_time_est = message.created_at.astimezone(EST)
            message_hour = message_time_est.hour

            # Check if message is in the morning (3 AM to 7 AM)
            if MORNING_START <= message_hour < MORNING_END:
                morning_message_counts[message.author.name] = morning_message_counts.get(message.author.name, 0) + 1

            # Check if message is in the evening (10 PM to 2 AM)
            elif EVENING_START <= message_hour or message_hour < EVENING_END:
                evening_message_counts[message.author.name] = evening_message_counts.get(message.author.name, 0) + 1

            await asyncio.sleep(0.1)  # Sleep to avoid hitting rate limits

        # Add user message and reaction counts to the overall tally
        for user, count in user_message_count.items():
            user_message_counts[user] = user_message_counts.get(user, 0) + count
        for user, count in user_reaction_count.items():
            user_reaction_counts[user] = user_reaction_counts.get(user, 0) + count

        # Fix: Ensure that even if there were no messages, the channel's total is set to 0
        if message_count == 0:
            message_count = 0
        
        # Print the total messages for this channel
        print(f"Total messages in channel {channel.name}: {message_count}")

        # Add channel's top reactions to the overall tally
        top_reactions_per_channel[channel_id] = top_reactions

        # Collect top 5 users who sent the most messages in the channel
        sorted_channel_message_counts = sorted(user_message_count.items(), key=lambda x: x[1], reverse=True)
        top_messages_per_channel[channel_id] = sorted_channel_message_counts[:5]  # Store the top 5 senders

    # After processing all channels, print all the collected outputs
    print("\n\nFINAL RESULTS FOR THE YEAR:")
    print(f"Total messages sent: {total_messages}")
    print(f"Total reactions given: {total_reactions}")
    print(f"Messages sent by George Costanza: {george_message_count}")

    # Print top 5 custom emojis
    sorted_custom_emojis = sorted(custom_emoji_counts.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 5 custom emojis used:")
    for emoji, count in sorted_custom_emojis[:5]:
        print(f"{emoji}: {count} uses")

    # Print top 5 default emojis
    sorted_default_emojis = sorted(default_emoji_counts.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 5 default emojis used:")
    for emoji, count in sorted_default_emojis[:5]:
        print(f"{emoji}: {count} uses")

    # Print top 5 users who sent the most messages overall
    sorted_overall_message_counts = sorted(user_message_counts.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 5 users who sent the most messages overall:")
    for user, count in sorted_overall_message_counts[:11]:
        print(f"{user}: {count} messages")

    # Print top 5 users who gave the most reactions overall
    sorted_overall_reaction_counts = sorted(user_reaction_counts.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 5 users who gave the most reactions overall:")
    for user, count in sorted_overall_reaction_counts[:11]:
        print(f"{user}: {count} reactions")

    # Top 5 message senders per channel
    for channel_id in channel_list:
        channel = client.get_channel(channel_id)
        if channel:
            # Print top 5 message senders in the channel
            print(f"\nTop 5 message senders in channel {channel.name}:")
            sorted_channel_message_counts = sorted(top_messages_per_channel[channel_id], key=lambda x: x[1], reverse=True)
            for user, count in sorted_channel_message_counts:
                print(f"{user}: {count} messages")

            # Top 5 reaction senders per channel
            print(f"\nTop 5 reaction senders in channel {channel.name}:")
            sorted_user_reaction_counts = sorted(top_reactions_per_channel[channel_id], key=lambda x: x['reaction_count'], reverse=True)[:5]
            for reaction in sorted_user_reaction_counts:
                print(f"{reaction['author']}: {reaction['reaction_count']} reactions on message: {reaction['message_content']}")

    print(f"\nSummary: George message count: {george_message_count}")
    print(f"Custom emoji counts: {custom_emoji_counts}")
    print(f"Default emoji counts: {default_emoji_counts}")

client.run(bot_token)
