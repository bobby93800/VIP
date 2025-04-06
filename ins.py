from instagrapi import Client

from instagrapi.exceptions import LoginRequired, ChallengeRequired

import random

import time

from datetime import datetime

import json

import os

import logging



# Configuration

USERNAME = os.getenv('INSTA_USERNAME', "gaurav_lancer1")  # Use environment variables

PASSWORD = os.getenv('INSTA_PASSWORD', "anita1234@1") 

SESSION_FILE = "instagram_session.json"

LOG_FILE = "bot_activity.log"



# More natural-looking reply options

RANDOM_REPLIES = [

    " TUM TO WAHI HO NA JISE 6000 ME RUSSIAN CHAHIYE 🤭🤭@{username}! ",

    "I LOVE YOU JAANU ♥️ @{username}! 💖",

    "HAM LOGO KE MAMMY PAPA JANTE HAI 😆",

    """

🔥╔══════════════════════╗🔥

       EVERYONE FOLLOW THE GROUP RULES 

🔥╚══════════════════════╝🔥



⚡️ 𝟙. 𝐍𝐎 𝐒𝐄𝐋𝐅-𝐏𝐑𝐎𝐌𝐎!

   ▸ 𝗡𝗼 𝗮𝗱𝘀, 𝗻𝗼 𝗯𝘂𝘀𝗶𝗻𝗲𝘀𝘀 𝗱𝗺𝘀, 𝗻𝗼 𝗯𝗲𝗴𝗴𝗶𝗻𝗴

   ▸ 𝗩𝗶𝗼𝗹𝗮𝘁𝗼𝗿𝘀 𝘄𝗶𝗹𝗹 𝗯𝗲 𝗘𝗫𝗜𝗟𝗘𝗗



💢 𝟚. 𝐒𝐖𝐄𝐀𝐑 𝐈𝐍 𝐌𝐎𝐃𝐄𝐑𝐀𝐓𝐈𝐎𝐍

   ▸ 𝗚𝗮𝗹𝗶 𝗼𝗸, 𝗯𝘂𝘁 𝗻𝗼 𝗲𝘅𝘁𝗿𝗲𝗺𝗲 𝘁𝗼𝘅𝗶𝗰𝗶𝘁𝘆

   ▸ 𝗗𝗼𝗻'𝘁 𝗯𝗲 𝗮 𝗽𝗲𝘀𝘁



👑 𝟛. 𝐀𝐃𝐌𝐈𝐍𝐒 𝐀𝐑𝐄 𝐑𝐎𝐘𝐀𝐋𝐓𝐘

   ▸ 𝗡𝗼 𝗱𝗶𝘀𝗿𝗲𝘀𝗽𝗲𝗰𝘁, 𝗻𝗼 𝗽𝗲𝗿𝘀𝗼𝗻𝗮𝗹 𝗷𝗮𝗯𝘀

   ▸ 𝗠𝗨𝗦𝗧 𝗙𝗢𝗟𝗟𝗢𝗪:

      ✷ @usetname

      ✷ @username

      ✷ @username

      ✷ @username



💎 𝟜. 𝐑𝐄𝐒𝐏𝐄𝐂𝐓 𝐈𝐒 𝐌𝐀𝐍𝐃𝐀𝐓𝐎𝐑𝐘

   ▸ 𝗡𝗼 𝗿𝗮𝗰𝗶𝘀𝗺, 𝗻𝗼 𝗯𝘂𝗹𝗹𝘆𝗶𝗻𝗴

   ▸ 𝗪𝗲'𝗿𝗲 𝗮𝗹𝗹 𝗵𝗲𝗿𝗲 𝗳𝗼𝗿 𝗳𝘂𝗻



🎨 𝟝. 𝐓𝐇𝐄𝐌𝐄 𝐈𝐒 𝐒𝐀𝐂𝐑𝐄𝐃

   ▸ 𝗗𝗼𝗻'𝘁 𝘁𝗼𝘂𝗰𝗵 𝘁𝗵𝗲 𝗽𝗳𝗽/𝗯𝗶𝗼

   ▸ 𝗧𝗵𝗶𝘀 𝗶𝘀 𝗼𝘂𝗿 𝗶𝗱𝗲𝗻𝘁𝗶𝘁𝘆



⚡ 𝟞. 𝐀𝐃𝐌𝐈𝐍 𝐃𝐄𝐂𝐈𝐒𝐈𝐎𝐍𝐒 𝐀𝐑𝐄 𝐅𝐈𝐍𝐀𝐋

   ▸ 𝗡𝗼 𝗻𝗲𝗴𝗼𝘁𝗶𝗮𝘁𝗶𝗻𝗴, 𝗻𝗼 𝘄𝗵𝗶𝗻𝗶𝗻𝗴

   ▸ 𝗧𝗵𝗲𝗶𝗿 𝘄𝗼𝗿𝗱 𝗶𝘀 𝗹𝗮𝘄



⚠️╔══════════════════════╗⚠️

      𝐁𝐑𝐄𝐀𝐊 𝐑𝐔𝐋𝐄𝐒 = 𝐏𝐔𝐍𝐈𝐒𝐇𝐌𝐄𝐍𝐓

⚠️╚══════════════════════╝⚠️



💀 1st offense: Warning

💀 2nd offense: Mute

💀 3rd offense: Permanent Ban



🔥 𝐄𝐗𝐓𝐑𝐀 𝐍𝐎𝐓𝐄𝐒:

- 𝗔𝗱𝗺𝗶𝗻'𝘀 𝗴𝗳 𝘀𝘁𝗮𝘁𝘂𝘀 𝗶𝘀 𝗮 𝗺𝗲𝗻𝘀𝗶𝘁𝗶𝘃𝗲 𝘁𝗼𝗽𝗶𝗰 (𝗶𝗳 𝘁𝗵𝗲𝗿𝗲 𝗲𝘃𝗲𝗻 𝗶𝘀 𝗼𝗻𝗲) 😏

- 𝗧𝗵𝗶𝘀 𝗶𝘀 𝗮 𝗳𝘂𝗻 𝘇𝗼𝗻𝗲, 𝗯𝘂𝘁 𝘄𝗶𝘁𝗵 𝗼𝗿𝗱𝗲𝗿



    """

    "तुम्हारी मुस्कान देखकर मेरा Windows भी हैंग हो गया! 😂 @{username}",

    "तुम Google हो क्या? क्योंकि तुम्हारे बिना कुछ भी Search नहीं होता! 🔍 @{username}",

    "तुम WiFi हो? क्योंकि तुम्हारे बिना मेरा Signal Weak है! 📶 @{username}",

    "तुम Traffic हो क्या? क्योंकि तुम्हारे सामने मेरी Speed कम हो जाती है! 🚦😆 @{username}",

    

    # Romantic

    "तुम चाय हो क्या? क्योंकि सुबह-सुबह तुम्हारी याद आती है! ☕ @{username}",

    "मैं ATM नहीं हूँ, पर तुम मेरे दिल से प्यार निकाल सकती हो! 💖 @{username}",

    "तुम्हारी आँखों में इतने सपने हैं, मैं उन्हें पूरा कर दूँगा! ✨ @{username}",

    "तुम Starbucks हो क्या? क्योंकि तुम्हारे बिना मेरी सुबह Incomplete है! ☕❤️ @{username}",

    

    # Cheeky/Double Meaning

    "तुम UPS हो क्या? क्योंकि तुम्हारे आते ही मेरा Current बढ़ जाता है! ⚡😏 @{username}",

    "तुम Ola हो? क्योंकि तुम्हारे लिए मैं Cashless हो जाऊँगा! 💰😂 @{username}",

    "तुम Bluetooth हो? क्योंकि तुम्हारे साथ मेरा Connection Automatic है! 📲💙 @{username}",

    "तुम Gym हो क्या? क्योंकि तुम्हारे बिना मेरा Motivation ही नहीं रहता! 💪😏 @{username}",

    

    # Bollywood Style

    "तुम Mere Khwabon Mein Aao... वोह नहीं, Real Mein! 😍 @{username}",

    "तुम्हारे बिना मेरी Life वैसी ही है जैसे बिना गानों वाली Movie! 🎬 @{username}",

    "तुम्हारे लिए मैं Jio का Saal ka Plan भी ले आया! 📅❤️ @{username}",

    

    # Foodie

    "तुम Pizza हो क्या? क्योंकि तुम्हारे बिना मेरी Life Cheesy नहीं! 🍕❤️ @{username}",

    "तुम Chocolate हो? क्योंकि तुम्हारे बिना मेरा मूड Melt नहीं होता! 🍫🔥 @{username}",

    "तुम Cold Drink हो क्या? क्योंकि तुम्हारे साथ मेरा Temperature बढ़ जाता है! 🥤😉 @{username}",

    

    # Techy

    "तुम 5G हो क्या? क्योंकि तुम्हारे सामने मेरा दिल Loading हो जाता है! 📶😉 @{username}",

    "तुम Netflix हो? क्योंकि तुम्हारे साथ हर Moment बिना Buffering के चलता है! 🎬💖 @{username}",

    "तुम Password हो क्या? क्योंकि तुम्हारे बिना मैं Login नहीं हो पाता! 🔑💘 @{username}"

]



IGNORE_USERS = ["user1", "user2"]  # Users to never reply to

MIN_REPLY_DELAY = 300  # Minimum seconds between replies (to appear human)

MAX_REPLY_DELAY = 301  # Maximum seconds between replies



class InstantGroupReplyBot:

    def __init__(self):

        self.client = Client()

        self.replied_messages = set()  # Track individual messages instead of threads

        self.setup_logging()

        self.setup_client()

        

    def setup_logging(self):

        """Configure logging to file and console"""

        logging.basicConfig(

            level=logging.INFO,

            format='%(asctime)s - %(levelname)s - %(message)s',

            handlers=[

                logging.FileHandler(LOG_FILE),

                logging.StreamHandler()

            ]

        )

        self.log = logging.getLogger(__name__)

        

    def setup_client(self):

        """Configure client with updated settings"""

        settings = {

            "user_agent": "Instagram 275.0.0.27.98 Android (28/9.0; 480dpi; 1080x2260; OnePlus; ONEPLUS A6013; OnePlus6T; qcom; en_US; 314665256)",

            "device_settings": {

                "manufacturer": "OnePlus",

                "model": "ONEPLUS A6013",

                "android_version": 28,

                "android_release": "9.0",

                "chipset": "qualcomm"

            },

            "app_version": "275.0.0.27.98",

            "android_version": 28,

            "android_release": "9.0",

            "locale": "en_US",

            "country": "US",

            "timezone_offset": 19800,

            "request_timeout": 10  # Faster timeout for quicker checks

        }

        self.client.set_settings(settings)



    def load_session(self):

        """Load saved session if exists"""

        if os.path.exists(SESSION_FILE):

            try:

                self.client.load_settings(SESSION_FILE)

                return True

            except Exception as e:

                self.log.error(f"Failed to load session: {e}")

        return False



    def save_session(self):

        """Save current session"""

        try:

            self.client.dump_settings(SESSION_FILE)

            return True

        except Exception as e:

            self.log.error(f"Failed to save session: {e}")

            return False



    def login(self):

        """Handle login with session management"""

        try:

            # Try loading existing session first

            if self.load_session():

                try:

                    # Lightweight check instead of full timeline fetch

                    self.client.account_info()

                    self.log.info("Logged in via existing session")

                    return True

                except (LoginRequired, ChallengeRequired):

                    self.log.info("Session expired, relogging in...")

            

            # Full login required

            time.sleep(3)  # Reduced delay for faster startup

            login_result = self.client.login(USERNAME, PASSWORD)

            

            if login_result:

                self.log.info("Login successful!")

                self.save_session()

                return True

            return False

            

        except Exception as e:

            self.log.error(f"Login failed: {e}")

            if "challenge_required" in str(e):

                self.log.error("Please check your Instagram app for verification")

            return False



    def get_random_reply(self, username):

        """Select a random reply template"""

        return random.choice(RANDOM_REPLIES).format(username=username)



    def process_group_messages(self):

        """Find and reply to unread group messages instantly"""

        try:

            # Get only unread threads for faster processing

            threads = self.client.direct_threads(selected_filter="unread")

            

            for thread in threads:

                if not thread.is_group:

                    continue

                    

                if not thread.messages:

                    continue

                    

                # Process all unread messages, not just the last one

                for message in thread.messages:

                    if message.id in self.replied_messages:

                        continue

                        

                    sender_id = message.user_id

                    

                    if sender_id == self.client.user_id:

                        continue

                        

                    try:

                        user_info = self.client.user_info(sender_id)

                        username = user_info.username

                    except Exception as e:

                        self.log.error(f"Couldn't get user info: {e}")

                        continue

                    

                    if username in IGNORE_USERS:

                        continue

                    

                    # Generate reply with random delay

                    reply = self.get_random_reply(username)

                    delay = random.uniform(MIN_REPLY_DELAY, MAX_REPLY_DELAY)

                    time.sleep(delay)

                    

                    try:

                        self.client.direct_send(reply, thread_ids=[thread.id])

                        self.log.info(f"Replied to @{username} in group (after {delay:.1f}s): {reply}")

                        self.replied_messages.add(message.id)

                        

                        # Mark as read after replying

                        self.client.direct_thread_mark_read(thread.id)

                        

                    except Exception as e:

                        self.log.error(f"Failed to send reply: {e}")



        except Exception as e:

            self.log.error(f"Error processing messages: {e}")

            time.sleep(30)  # Shorter delay on errors for faster recovery



    def run(self):

        """Main bot execution loop with faster checks"""

        if not self.login():

            self.log.error("Cannot continue without login")

            return

            

        self.log.info("Instant group message reply bot started! Press Ctrl+C to stop")

        self.log.info(f"Loaded {len(RANDOM_REPLIES)} reply options")

        

        try:

            while True:

                start_time = time.time()

                self.log.info("Checking for new group messages...")

                self.process_group_messages()

                

                # Dynamic sleep based on processing time

                processing_time = time.time() - start_time

                sleep_time = max(5, 15 - processing_time)  # Minimum 5s between checks

                time.sleep(sleep_time)

                

        except KeyboardInterrupt:

            self.log.info("\nBot stopped by user")

            self.save_session()



if __name__ == "__main__":

    # Clear console for cleaner output

    os.system('cls' if os.name == 'nt' else 'clear')

    

    bot = InstantGroupReplyBot()

    bot.run()

