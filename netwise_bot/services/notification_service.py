from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .request_service import RequestService
from .user_service import UserService
from ..keyboards.interaction_keyboards import get_help_offer_keyboard

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, bot: Bot, request_service: RequestService, user_service: UserService):
        self.bot = bot
        self.request_service = request_service
        self.user_service = user_service

    async def generate_daily_digest_for_user(self, telegram_id: int) -> str:
        """Generate a daily digest message for a user containing relevant requests they can help with.
        
        Args:
            telegram_id: The user's Telegram ID
            
        Returns:
            str: The formatted digest message
        """
        try:
            # Get requests the user can help with
            relevant_requests = await self.request_service.get_requests_user_can_help_with(telegram_id)
            
            if not relevant_requests:
                return "На сегодня нет новых запросов, с которыми вы могли бы помочь. Загляните позже!"
            
            # Format the digest message
            message = "📬 Ваш ежедневный дайджест запросов:\n\n"
            
            for request in relevant_requests:
                requester = await self.user_service.get_profile(request['requester_id'])
                message += (
                    f"🔹 Запрос от {requester['name']}:\n"
                    f"{request['description_text'][:200]}...\n\n"
                )
            
            message += "Нажмите 'Готов помочь' под интересующим запросом, чтобы предложить свою помощь."
            return message
            
        except Exception as e:
            logger.error(f"Error generating digest for user {telegram_id}: {e}")
            return "Извините, произошла ошибка при формировании дайджеста. Попробуйте позже."

    async def send_daily_digest(self, telegram_id: int) -> bool:
        """Send the daily digest to a user.
        
        Args:
            telegram_id: The user's Telegram ID
            
        Returns:
            bool: True if the digest was sent successfully, False otherwise
        """
        try:
            # Check if user is active
            user = await self.user_service.get_profile(telegram_id)
            if not user or not user.get('is_active_in_search', True):
                logger.info(f"Skipping digest for inactive user {telegram_id}")
                return False
            
            # Generate and send the digest
            message = await self.generate_daily_digest_for_user(telegram_id)
            await self.bot.send_message(telegram_id, message)
            
            # Update last active timestamp
            await self.user_service.update_user_activity(telegram_id)
            
            logger.info(f"Successfully sent digest to user {telegram_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending digest to user {telegram_id}: {e}")
            return False

    async def notify_help_offer(self, helper_id: int, requester_id: int, request_id: str) -> None:
        """Notify a user that someone has offered to help with their request.
        
        Args:
            helper_id: The Telegram ID of the user offering help
            requester_id: The Telegram ID of the user who made the request
            request_id: The ID of the request
        """
        try:
            helper = await self.user_service.get_profile(helper_id)
            request = await self.request_service.get_request(request_id)
            
            if not helper or not request:
                logger.error(f"Could not find helper {helper_id} or request {request_id}")
                return
            
            message = (
                f"🎉 {helper['name']} готов помочь с вашим запросом!\n\n"
                f"Запрос: {request['description_text'][:200]}...\n\n"
                f"Вы можете связаться с {helper['name']} через Telegram."
            )
            
            await self.bot.send_message(requester_id, message)
            logger.info(f"Sent help offer notification to user {requester_id}")
            
        except Exception as e:
            logger.error(f"Error sending help offer notification: {e}")

    async def notify_help_accepted(self, helper_id: int, requester_id: int, request_id: str) -> None:
        """Notify a helper that their help offer was accepted.
        
        Args:
            helper_id: The Telegram ID of the user who offered help
            requester_id: The Telegram ID of the user who accepted the help
            request_id: The ID of the request
        """
        try:
            requester = await self.user_service.get_profile(requester_id)
            request = await self.request_service.get_request(request_id)
            
            if not requester or not request:
                logger.error(f"Could not find requester {requester_id} or request {request_id}")
                return
            
            message = (
                f"✅ {requester['name']} принял(а) ваше предложение помощи!\n\n"
                f"Запрос: {request['description_text'][:200]}...\n\n"
                f"Вы можете связаться с {requester['name']} через Telegram."
            )
            
            await self.bot.send_message(helper_id, message)
            logger.info(f"Sent help acceptance notification to user {helper_id}")
            
        except Exception as e:
            logger.error(f"Error sending help acceptance notification: {e}")

    async def send_inactive_reminders(self, days_threshold: int = 30, grace_period: int = 3) -> int:
        """Send reminder messages to users approaching inactivity threshold.
        
        Args:
            days_threshold: Number of days of inactivity before deactivation
            grace_period: Number of days before deactivation to send reminder
            
        Returns:
            int: Number of reminders sent
        """
        try:
            # Calculate the cutoff date for users approaching inactivity
            cutoff_date = datetime.utcnow() - timedelta(days=days_threshold - grace_period)
            
            # Find users approaching inactivity
            response = await self.user_service.supabase.table('users').select('id, telegram_id, name, last_active_at').lt('last_active_at', cutoff_date.isoformat()).eq('is_active_in_search', True).execute()
            
            users = response.data
            if not users:
                logger.info("No users approaching inactivity found")
                return 0
                
            # Send reminders
            reminders_sent = 0
            for user in users:
                try:
                    last_active = datetime.fromisoformat(user['last_active_at'])
                    days_inactive = (datetime.utcnow() - last_active).days
                    
                    message = (
                        f"👋 Привет, {user['name']}!\n\n"
                        f"Мы заметили, что вы не были активны в NetWise уже {days_inactive} дней. "
                        f"Если вы не проявите активность в течение следующих {grace_period} дней, "
                        f"ваш профиль будет временно деактивирован из поиска.\n\n"
                        f"Чтобы оставаться активным, просто отправьте любое сообщение боту или "
                        f"используйте команду /start."
                    )
                    
                    await self.bot.send_message(user['telegram_id'], message)
                    reminders_sent += 1
                    logger.info(f"Sent inactivity reminder to user {user['name']} (ID: {user['telegram_id']})")
                    
                except Exception as e:
                    logger.error(f"Error sending reminder to user {user['id']}: {e}")
                    
            logger.info(f"Sent {reminders_sent} inactivity reminders")
            return reminders_sent
            
        except Exception as e:
            logger.error(f"Error in send_inactive_reminders: {e}")
            return 0 