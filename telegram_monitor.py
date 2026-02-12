"""

from telethon import TelegramClient
from telethon.tl.types import UserStatusOnline, UserStatusOffline, UserStatusRecently
from telethon.errors import FloodWaitError, SessionPasswordNeededError
from datetime import datetime
import asyncio
import pytz
import json
import os
from pathlib import Path

# ========== تنظیمات ==========
CONFIG_FILE = 'config.json'
LOG_FILE = 'online_log.txt'
STATS_FILE = 'statistics.json'
SESSION_NAME = 'monitoring_session'

# تایم‌زون تهران
TEHRAN_TZ = pytz.timezone('Asia/Tehran')


class TelegramMonitor:
    """کلاس اصلی نظارت بر تلگرام"""
    
    def __init__(self):
        """مقداردهی اولیه"""
        self.config = self.load_config()
        self.client = TelegramClient(
            SESSION_NAME,
            self.config['API_ID'],
            self.config['API_HASH']
        )
        self.stats = self.load_statistics()
    
    def load_config(self):
        """بارگذاری تنظیمات از فایل"""
        if not os.path.exists(CONFIG_FILE):
            self.create_default_config()
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_default_config(self):
        """ایجاد فایل تنظیمات پیش‌فرض"""
        default_config = {
            "API_ID": "YOUR_API_ID",
            "API_HASH": "YOUR_API_HASH",
            "TARGET_PHONE": "+989123456789",
            "CHECK_INTERVAL": 10,
            "ENABLE_SOUND": False,
            "ENABLE_DESKTOP_NOTIFICATION": False
        }
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        
        print(f"✅ فایل {CONFIG_FILE} ایجاد شد. لطفاً آن را ویرای�� کنید.")
        print("📝 برای دریافت API_ID و API_HASH به https://my.telegram.org/apps مراجعه کنید")
        exit(0)
    
    def load_statistics(self):
        """بارگذاری آمار از فایل"""
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'online_count': 0,
            'offline_count': 0,
            'total_checks': 0,
            'errors_count': 0,
            'start_time': None
        }
    
    def save_statistics(self):
        """ذخیره آمار در فایل"""
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def get_current_time():
        """زمان فعلی به تایم‌زون تهران"""
        return datetime.now(TEHRAN_TZ).strftime('%Y-%m-%d %H:%M:%S')
    
    def log_to_file(self, message):
        """ذخیره لاگ در فایل"""
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")
        except Exception as e:
            print(f"⚠️ خطا در ذخیره فایل: {e}")
    
    def print_header(self):
        """چاپ هدر برنامه"""
        print("=" * 70)
        print("🚀 سیستم نظارت پیشرفته تلگرام - Telegram Online Monitor")
        print("=" * 70)
        print(f"📅 تاریخ شروع: {self.get_current_time()}")
        print(f"📱 شماره هدف: {self.config['TARGET_PHONE']}")
        print(f"⏱️ فاصله چک: {self.config['CHECK_INTERVAL']} ثانیه")
        print("=" * 70)
        print("💡 برای توقف برنامه: Ctrl+C")
        print(f"📁 لاگ‌ها در فایل {LOG_FILE} ذخیره می‌شوند")
        print("=" * 70)
    
    def print_statistics(self):
        """نمایش آمار نهایی"""
        print("\n" + "=" * 70)
        print("📊 آمار نهایی:")
        print(f" ✅ تعداد دفعات آنلاین: {self.stats['online_count']}")
        print(f" ❌ تعداد دفعات آفلاین: {self.stats['offline_count']}")
        print(f" 🔍 تعداد کل چک‌ها: {self.stats['total_checks']}")
        print(f" ⚠️ تعداد خطاها: {self.stats['errors_count']}")
        if self.stats['start_time']:
            start = datetime.fromisoformat(self.stats['start_time'])
            duration = datetime.now(TEHRAN_TZ) - start
            hours = duration.total_seconds() / 3600
            print(f" ⏱️ مدت زمان نظارت: {hours:.2f} ساعت")
        print("=" * 70)
    
    async def get_user_info(self):
        """دریافت اطلاعات کاربر هدف"""
        try:
            user = await self.client.get_entity(self.config['TARGET_PHONE'])
            
            user_info = (
                f"\n📊 اطلاعات کاربر:\n"
                f" 👤 نام: {user.first_name} {user.last_name or ''}\n"
                f" 🆔 آیدی: {user.id}\n"
                f" 📱 شماره: {self.config['TARGET_PHONE']}\n"
                f" 🔗 یوزرنیم: @{user.username or 'بدون یوزرنیم'}\n"
            )
            print(user_info)
            
            # ذخیره header در فایل
            self.log_to_file(f"\n{'=' * 70}")
            self.log_to_file(f"🚀 شروع نظارت: {self.get_current_time()}")
            self.log_to_file(f"👤 کاربر: {user.first_name} {user.last_name or ''} (@{user.username or 'بدون یوزرنیم'})")
            self.log_to_file(f"{'=' * 70}\n")
            
            return user
            
        except Exception as e:
            print(f"\n❌ خطا در دریافت اطلاعات کاربر: {e}")
            print("\n💡 راهنما:")
            print(" • شماره را با فرمت +98... وارد کنید")
            print(" • مطمئن شوید API_ID و API_HASH صحیح است")
            print(" • کاربر باید در مخاطبین شما باشد یا قبلاً با او چت کرده باشید")
            print(" • اتصال اینترنت را بررسی کنید")
            return None
    
    async def monitor_status(self):
        """حلقه اصلی نظارت"""
        print("🔄 در حال اتصال به تلگرام...")
        
        try:
            await self.client.start()
            print("✅ اتصال برقرار شد!\n")
        except SessionPasswordNeededError:
            print("🔐 حساب شما دارای تأیید دو مرحله‌ای است")
            password = input("🔑 رمز عبور خود را وارد کنید: ")
            await self.client.start(password=password)
            print("✅ اتصال برقرار شد!\n")
        
        # دریافت اطلاعات کاربر
        user = await self.get_user_info()
        if not user:
            return
        
        # مقداردهی آمار
        if not self.stats['start_time']:
            self.stats['start_time'] = datetime.now(TEHRAN_TZ).isoformat()
        
        # متغیرهای نظارت
        last_status = None
        last_was_online = None
        consecutive_errors = 0
        
        print(f"\n{'=' * 70}")
        print("🔍 شروع نظارت...")
        print(f"{'=' * 70}\n")
        
        while True:
            try:
                # دریافت وضعیت فعلی
                user_entity = await self.client.get_entity(user.id)
                status = user_entity.status
                current_time = self.get_current_time()
                
                self.stats['total_checks'] += 1
                
                # بررسی UserStatusOnline
                if isinstance(status, UserStatusOnline):
                    if last_status != "online":
                        message = f"✅ [{current_time}] کاربر آنلاین شد 🟢"
                        print(message)
                        self.log_to_file(f"[{current_time}] آنلاین شد")
                        last_status = "online"
                        self.stats['online_count'] += 1
                        self.save_statistics()
                
                # بررسی UserStatusOffline
                elif isinstance(status, UserStatusOffline):
                    if not hasattr(status, 'was_online') or status.was_online is None:
                        if last_status != "offline_unknown":
                            message = f"❌ [{current_time}] کاربر آفلاین است (زمان نامشخص) 🔴"
                            print(message)
                            self.log_to_file(f"[{current_time}] آفلاین - زمان نامشخص")
                            last_status = "offline_unknown"
                            self.stats['offline_count'] += 1
                            self.save_statistics()
                    else:
                        was_online_utc = status.was_online
                        was_online_local = was_online_utc.astimezone(TEHRAN_TZ)
                        was_online_time = was_online_local.strftime('%Y-%m-%d %H:%M:%S')
                        
                        if last_status != "offline" or last_was_online != was_online_time:
                            message = (
                                f"❌ [{current_time}] کاربر آفلاین شد 🔴\n"
                                f" ⏰ آخرین بازدید: {was_online_time}"
                            )
                            print(message)
                            self.log_to_file(f"[{current_time}] آفلاین شد - آخرین بازدید: {was_online_time}")
                            last_status = "offline"
                            last_was_online = was_online_time
                            self.stats['offline_count'] += 1
                            self.save_statistics()
                
                # بررسی UserStatusRecently
                elif isinstance(status, UserStatusRecently):
                    if last_status != "recently":
                        message = f"🟡 [{current_time}] اخیراً آنلاین بوده (چند دقیقه پیش)"
                        print(message)
                        self.log_to_file(f"[{current_time}] اخیراً آنلاین بوده")
                        last_status = "recently"
                
                # حالت مخفی
                else:
                    if last_status != "hidden":
                        message = f"❓ [{current_time}] وضعیت مخفی یا نامشخص (Last Seen غیرفعال)"
                        print(message)
                        self.log_to_file(f"[{current_time}] وضعیت مخفی/نامشخص")
                        last_status = "hidden"
                
                # ریست کردن شمارنده خطا
                consecutive_errors = 0
                
                # صبر کردن
                await asyncio.sleep(self.config['CHECK_INTERVAL'])
            
            # مدیریت FloodWaitError
            except FloodWaitError as e:
                wait_time = e.seconds + 10
                message = (
                    f"⏳ [{self.get_current_time()}] محدودیت تلگرام فعال شد!\n"
                    f" ⏰ صبر کنید: {wait_time} ثانیه ({wait_time // 60} دقیقه و {wait_time % 60} ثانیه)"
                )
                print(message)
                self.log_to_file(f"[{self.get_current_time()}] FloodWait: {wait_time}s")
                await asyncio.sleep(wait_time)
            
            # توقف توسط کاربر
            except KeyboardInterrupt:
                print("\n\n⛔ نظارت متوقف شد توسط کاربر")
                self.log_to_file(f"\n[{self.get_current_time()}] نظارت متوقف شد\n{'=' * 70}")
                break
            
            # سایر خطاها
            except Exception as e:
                consecutive_errors += 1
                self.stats['errors_count'] += 1
                error_msg = f"⚠️ [{self.get_current_time()}] خطا (شماره {consecutive_errors}): {e}"
                print(error_msg)
                self.log_to_file(f"[{self.get_current_time()}] خطا: {str(e)}")
                
                if consecutive_errors >= 5:
                    print("\n❌ خطاهای متوالی زیاد! برنامه متوقف می‌شود.")
                    self.log_to_file(f"[{self.get_current_time()}] خطاهای متوالی زیاد - توقف برنامه")
                    break
                
                await asyncio.sleep(self.config['CHECK_INTERVAL'] * 2)
    
    async def run(self):
        """اجرای برنامه"""
        self.print_header()
        await self.monitor_status()
        self.print_statistics()


def main():
    """تابع اصلی"""
    monitor = TelegramMonitor()
    
    try:
        monitor.client.loop.run_until_complete(monitor.run())
    except KeyboardInterrupt:
        print("\n\n👋 خداحافظ!")
    finally:
        print("\n🔌 در حال قطع اتصال...")
        monitor.client.disconnect()
        monitor.save_statistics()
        print("✅ اتصال قطع شد")


if __name__ == "__main__":
    main()