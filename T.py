import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import instaloader

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class InstagramBot:
    def __init__(self, token: str):
        self.token = token
        self.app = Application.builder().token(token).build()
        self.L = instaloader.Instaloader()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when command /start is issued."""
        user = update.effective_user
        await update.message.reply_text(
            f"नमस्ते {user.first_name}! 👋\n\n"
            "मैं Instagram Info Bot हूँ!\n\n"
            "बस मुझे Instagram username भेजें और मैं उसकी पूरी जानकारी दूंगा।\n\n"
            "Commands:\n"
            "/start - बॉट शुरू करें\n"
            "/help - मदद प्राप्त करें"
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message when command /help is issued."""
        help_text = """
🤖 **Instagram Info Bot Help**

📝 **Usage:**
बस किसी भी Instagram username को मुझे भेजें (बिना @ के)

📊 **मैं क्या जानकारी दूंगा:**
✅ Profile information
✅ Followers count
✅ Following count
✅ Posts count
✅ Bio
✅ Profile picture
✅ Private/Public status

⚠️ **Note:** यह बॉट सिर्फ public accounts की जानकारी दे सकता है।
        """
        await update.message.reply_text(help_text)
    
    def get_instagram_info(self, username: str):
        """Get Instagram profile information."""
        try:
            # Remove @ symbol if present
            username = username.replace('@', '').strip()
            
            # Get profile info
            profile = instaloader.Profile.from_username(self.L.context, username)
            
            info = {
                'success': True,
                'username': profile.username,
                'user_id': profile.userid,
                'full_name': profile.full_name,
                'followers': profile.followers,
                'following': profile.followees,
                'posts': profile.mediacount,
                'bio': profile.biography,
                'is_private': profile.is_private,
                'is_verified': profile.is_verified,
                'profile_pic_url': profile.profile_pic_url,
                'external_url': profile.external_url
            }
            return info
            
        except instaloader.exceptions.ProfileNotExistsException:
            return {'success': False, 'error': 'Profile does not exist'}
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            return {'success': False, 'error': 'Private profile - cannot access'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages."""
        username = update.message.text.strip()
        
        # Show typing action
        await update.message.chat.send_action(action="typing")
        
        # Get Instagram info
        info = self.get_instagram_info(username)
        
        if not info['success']:
            await update.message.reply_text(
                f"❌ Error: {info['error']}\n\n"
                "कृपया सही username दें और सुनिश्चित करें कि account public है।"
            )
            return
        
        # Format response
        response = f"""
📱 **Instagram Profile Info**

👤 **Username:** @{info['username']}
🆔 **User ID:** {info['user_id']}
👨‍💼 **Full Name:** {info['full_name'] or 'N/A'}

📊 **Statistics:**
👥 **Followers:** {info['followers']:,}
👥 **Following:** {info['following']:,}
📸 **Posts:** {info['posts']:,}

📝 **Bio:**
{info['bio'] or 'No bio'}

🔗 **External URL:** {info['external_url'] or 'N/A'}

🔒 **Account Type:** {'Private 🔐' if info['is_private'] else 'Public 🌐'}
✅ **Verified:** {'Yes ✅' if info['is_verified'] else 'No ❌'}

        """
        
        # Send profile picture if available
        if info['profile_pic_url']:
            try:
                await update.message.reply_photo(
                    photo=info['profile_pic_url'],
                    caption=response
                )
                return
            except:
                pass
        
        # If photo couldn't be sent, send text only
        await update.message.reply_text(response)
    
    def run(self):
        """Start the bot."""
        print("🤖 Bot is running...")
        self.app.run_polling()

# Bot Configuration
BOT_TOKEN = "8288719212:AAHfmlschKmtJWo5zor4YV3lkKImRffW1aQ"

if __name__ == "__main__":
    bot = InstagramBot(BOT_TOKEN)
    bot.run()
