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

    # Initialize counters for morning and evening message counts
    morning_message_counts = {}
    evening_message_counts = {}

    # Define the start and end datetime for the specified year
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)

    # Store the printed output for each channel to print at the end
    channel_outputs = []

    print(f"Tallying messages...")
    for channel_id in channel_list:
        channel = client.get_channel(channel_id)
        if not channel:
            print(f"Channel with ID {channel_id} not found.")
            continue

        user_message_count = {}
        user_reaction_count = {}
        top_reactions = []
        message_count = 0  # Initialize message count for each channel

        # Initialize channel-specific output
        channel_output = []

        async for message in channel.history(limit=None, after=start_date, before=end_date):
            if message.author.bot:
                continue

            # Tally message counts
            user_message_count[message.author.name] = user_message_count.get(message.author.name, 0) + 1
            total_messages += 1
            message_count += 1  # Increment message count for print statements

            # Tally reaction counts
            reaction_count = sum(reaction.count for reaction in message.reactions)
            if reaction_count > 0:
                user_reaction_count[message.author.name] = user_reaction_count.get(message.author.name, 0) + reaction_count
                top_reactions.append((message, reaction_count))
                total_reactions += reaction_count

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

        # Sort messages by reaction count in descending order and get the top 5
        top_reactions.sort(key=lambda x: x[1], reverse=True)

        # Add the top 5 reactions to channel output
        channel_output.append(f"\n\nTOP 5 MESSAGES WITH THE MOST REACTIONS IN {channel.name}:")
        top_5_reactions = []
        used_users = set()
        for message, reaction_count in top_reactions:
            if message.author.name not in used_users:
                used_users.add(message.author.name)
                top_5_reactions.append((message, reaction_count))
                if len(top_5_reactions) == 5:
                    break

        for message, reaction_count in top_5_reactions:
            reactors = []
            for reaction in message.reactions:
                async for user in reaction.users():
                    reactors.append(user.name)
            reactors_list = ', '.join(reactors)

            channel_output.append(f"\nMessage ID: {message.id}\nAuthor: {message.author.name}\nReactions: {reaction_count}\nContent: {message.content}\nReacted by: {reactors_list}")

        # Print top 5 users who sent the most messages in the current channel
        sorted_message_counts = sorted(user_message_count.items(), key=lambda x: x[1], reverse=True)
        channel_output.append(f"\n\nTOP 5 USERS WHO SENT THE MOST MESSAGES IN {channel.name}:")
        used_users = set()  # Reset for users already listed
        top_5_messages = []
        for user, count in sorted_message_counts:
            if user not in used_users:
                used_users.add(user)
                top_5_messages.append((user, count))
                if len(top_5_messages) == 5:
                    break

        for user, count in top_5_messages:
            channel_output.append(f"{user}: {count} messages")

        # Append the channel-specific output to the list
        channel_outputs.append("\n".join(channel_output))

    # After processing all channels, print all the collected outputs
    for output in channel_outputs:
        print(output)

    # Find the user who sent the most messages in the morning
    most_messages_morning = max(morning_message_counts.items(), key=lambda x: x[1], default=None)
    if most_messages_morning:
        print(f"\nUSER WHO SENT MOST MESSAGES IN THE MORNING (3 AM to 7 AM EST): {most_messages_morning[0]} with {most_messages_morning[1]} messages")

    # Find the user who sent the most messages in the evening
    most_messages_evening = max(evening_message_counts.items(), key=lambda x: x[1], default=None)
    if most_messages_evening:
        print(f"USER WHO SENT MOST MESSAGES IN THE EVENING (10 PM to 2 AM EST): {most_messages_evening[0]} with {most_messages_evening[1]} messages")

    # Print final results as usual
    print("\n\nFINAL RESULTS FOR THE YEAR:")
    print(f"Total messages sent: {total_messages}")
    print(f"Total reactions given: {total_reactions}")
    print(f"New users who joined: {len(user_join_dates)}")

    # Print top 5 users who sent the most messages overall
    sorted_overall_message_counts = sorted(user_message_counts.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 5 users who sent the most messages overall:")
    for user, count in sorted_overall_message_counts[:5]:
        print(f"{user}: {count} messages")

    # Print top 5 users who gave the most reactions overall
    sorted_overall_reaction_counts = sorted(user_reaction_counts.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 5 users who gave the most reactions overall:")
    for user, count in sorted_overall_reaction_counts[:5]:
        print(f"{user}: {count} reactions")

client.run(bot_token)
