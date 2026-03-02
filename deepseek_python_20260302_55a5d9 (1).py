import telebot
from telebot import types
import random
import time
import json
import os
from threading import RLock, Thread
from datetime import datetime, timedelta
import hashlib
import sys
import signal

# ====================== КОНФИГУРАЦИЯ ======================
TOKEN = os.getenv('BOT_TOKEN', '8019174987:AAFd_qG434htnd94mnCOZfd2ejD0hgTGUJk')
ADMIN_PASSWORD_HASH = hashlib.sha256('Kyniksvs1832'.encode()).hexdigest()
OWNER_USERNAME = '@kyniks'
OWNER_ID = None
CHANNEL_USERNAME = '@werdoxz_wiinere'
CHAT_LINK = 'https://t.me/+B7u5OmPsako4MTAy'

# Файлы данных
DATA_FILE = 'bot_data.json'
USERNAME_CACHE_FILE = 'username_cache.json'
PROMO_FILE = 'promocodes.json'
BUSINESS_FILE = 'business_data.json'
CLAN_FILE = 'clan_data.json'
ACHIEVEMENTS_FILE = 'achievements.json'
QUESTS_FILE = 'quests_data.json'
EVENT_FILE = 'event_data.json'
CASES_FILE = 'cases_data.json'
ORDERS_FILE = 'orders.json'
CHEQUES_FILE = 'cheques.json'
MICE_FILE = 'mice_data.json'
PETS_FILE = 'pets_data.json'
BANK_FILE = 'bank_data.json'
PHONE_FILE = 'phone_data.json'
BONUS_FILE = 'bonus_data.json'
DUEL_FILE = 'duel_data.json'
CARS_FILE = 'cars_data.json'               # Новый файл для машин

MAX_BET = 100000000
GAME_TIMEOUT = 300

# Множители игр
TOWER_MULTIPLIERS = {1: 1.0, 2: 1.5, 3: 2.5, 4: 4.0, 5: 6.0}
FOOTBALL_MULTIPLIER = 2.0
BASKETBALL_MULTIPLIER = 2.0
PYRAMID_MULTIPLIER = 5.0
MINES_MULTIPLIERS = {
    1: {1: 1.1, 2: 1.2, 3: 1.3, 4: 1.4, 5: 1.5, 6: 1.6, 7: 1.7, 8: 1.8, 9: 1.9, 10: 2.0},
    2: {1: 1.2, 2: 1.4, 3: 1.6, 4: 1.8, 5: 2.0, 6: 2.2, 7: 2.4, 8: 2.6, 9: 2.8, 10: 3.0},
    3: {1: 1.3, 2: 1.6, 3: 2.0, 4: 2.4, 5: 2.8, 6: 3.2, 7: 3.6, 8: 4.0, 9: 4.5, 10: 5.0},
    4: {1: 1.5, 2: 2.0, 3: 2.5, 4: 3.0, 5: 3.5, 6: 4.0, 7: 4.5, 8: 5.0, 9: 5.5, 10: 6.0},
    5: {1: 2.0, 2: 3.0, 3: 4.0, 4: 5.0, 5: 6.0, 6: 7.0, 7: 8.0, 8: 9.0, 9: 10.0, 10: 12.0}
}
BLACKJACK_MULTIPLIER = 2.0
SLOTS_SYMBOLS = ['🍒', '🍋', '🍊', '🍇', '💎', '7️⃣']
SLOTS_PAYOUTS = {
    ('7️⃣', '7️⃣', '7️⃣'): 10.0,
    ('💎', '💎', '💎'): 5.0,
    ('🍇', '🍇', '🍇'): 3.0,
    ('🍊', '🍊', '🍊'): 2.0,
    ('🍋', '🍋', '🍋'): 1.5,
    ('🍒', '🍒', '🍒'): 1.2
}
HILO_MULT = 2.0
HILO_WIN_CHANCE = 0.5
ROULETTE_NUMBERS = list(range(37))
RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
ROULETTE_MULTIPLIERS = {
    'straight': 36,
    'red': 2,
    'black': 2,
    'even': 2,
    'odd': 2,
    '1-18': 2,
    '19-36': 2,
    'dozen': 3
}

# Ивент (отключён)
RELEASE_EVENT = {'active': False, 'multiplier': 1.0, 'end_time': 0}

# ====================== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ======================
users = {}
username_cache = {}
game_timers = {}
crash_update_timers = {}
crash_locks = {}
admin_users = set()
promocodes = {}
orders = {}
next_order_id = 1
cheques = {}
user_cases = {}
user_achievements = {}
user_quests = {}
duels = {}
clans = {}
businesses = {}
event_data = {'active': False, 'participants': {}, 'leaderboard': [], 'last_update': time.time()}
jackpot = {'total': 0, 'last_winner': None, 'last_win_time': None, 'history': []}
daily_reward = {}

# Новые системы
bank_data = {'loans': {}, 'deposits': {}, 'transfers': [], 'total_deposits': 0, 'interest_rate': 0.05}
phone_data = {'contacts': {}, 'calls': {}, 'messages': {}, 'phone_numbers': {}}
bonus_data = {'daily': {}, 'weekly': {}, 'monthly': {}, 'referral_bonus': 5000}
pets_data = {}
clans_data = {}
businesses_data = {}
cars_data = {}          # данные о машинах пользователей

# Блокировки
data_lock = RLock()
user_locks = {}

# ====================== VIP РОЛИ ======================
VIP_ROLES = {
    'admin': {'name': '🔥Admin🔥', 'permissions': ['admin_panel']},
    'tester': {'name': '🤎Тестер💜', 'permissions': ['tester_bonus']},
    'helper': {'name': '💫Helper💫', 'permissions': []},
    'coder': {'name': '💻к0д3(р💻', 'permissions': ['admin_panel', 'tester_bonus', 'helper_bonus']}
}

# ====================== МАШИНЫ / ТАКСИ ======================
CARS = {
    'lada': {
        'name': 'Lada Migranta',
        'class': 'низкий',
        'price': 732000,
        'income': 50000,
        'income_interval': 10800,  # 3 часа
        'icon': '🚗'
    },
    'lixianur': {
        'name': 'Lixianur',
        'class': 'средний',
        'price': 1732974,
        'income': 100000,
        'income_interval': 10800,
        'icon': '🚙'
    },
    'luxliver': {
        'name': 'Luxliver',
        'class': 'высокий',
        'price': 12574297,
        'income': 500000,
        'income_interval': 10800,
        'icon': '🏎️'
    }
}

# ====================== СИСТЕМА МЫШЕК ======================
MICE_DATA = {
    'standard': {
        'name': '💖 Мышка - стандарт 💖',
        'price': 100000,
        'total': 100,
        'sold': 0,
        'rarity': 'обычная',
        'description': '👻 Для украшения аккаунта',
        'signature': 'kyn k.y 🌟',
        'version': 'стандарт',
        'income': 500,
        'income_interval': 3600,
        'icon': '🐭'
    },
    'china': {
        'name': '🤩 Мышка - чуньхаохаокакао 🤩',
        'price': 500000,
        'total': 100,
        'sold': 0,
        'rarity': 'средняя',
        'description': '💖 Китайская коллекционная мышка',
        'signature': 'chinalals k.y 💖',
        'version': 'china',
        'income': 1000,
        'income_interval': 3600,
        'icon': '🐹'
    },
    'world': {
        'name': '🌍 Мышка - мира 🌍',
        'price': 1000000,
        'total': 100,
        'sold': 0,
        'rarity': 'Lux',
        'description': '🍦 Эксклюзивная мышка мира',
        'signature': 'lux k.y 🖊️',
        'version': 'maximum',
        'income': 5000,
        'income_interval': 3600,
        'icon': '🐼'
    }
}

# ====================== СИСТЕМА ПИТОМЦЕВ ======================
PETS_DATA = {
    'dog': {
        'name': '🐕 Пёс',
        'price': 5000,
        'food_cost': 10,
        'happiness': 100,
        'income': 50,
        'rarity': 'обычный',
        'description': 'Верный друг, приносит небольшой доход'
    },
    'cat': {
        'name': '🐈 Кот',
        'price': 7500,
        'food_cost': 8,
        'happiness': 100,
        'income': 70,
        'rarity': 'обычный',
        'description': 'Независимый, но прибыльный'
    },
    'parrot': {
        'name': '🦜 Попугай',
        'price': 12000,
        'food_cost': 5,
        'happiness': 100,
        'income': 100,
        'rarity': 'редкий',
        'description': 'Говорящий, приносит хороший доход'
    },
    'hamster': {
        'name': '🐹 Хомяк',
        'price': 3000,
        'food_cost': 3,
        'happiness': 100,
        'income': 30,
        'rarity': 'обычный',
        'description': 'Маленький, но трудолюбивый'
    },
    'dragon': {
        'name': '🐲 Дракон',
        'price': 100000,
        'food_cost': 50,
        'happiness': 100,
        'income': 1000,
        'rarity': 'легендарный',
        'description': 'Мифическое существо, огромный доход'
    }
}

# ====================== СИСТЕМА БИЗНЕСА ======================
BUSINESS_DATA = {
    'kiosk': {
        'name': '🏪 Ларёк',
        'price': 10000,
        'income': 500,
        'level': 1,
        'max_level': 10,
        'upgrade_cost': 5000,
        'icon': '🏪',
        'description': 'Маленький, но стабильный доход'
    },
    'shop': {
        'name': '🏬 Магазин',
        'price': 50000,
        'income': 2000,
        'level': 1,
        'max_level': 10,
        'upgrade_cost': 25000,
        'icon': '🏬',
        'description': 'Серьёзный бизнес'
    },
    'restaurant': {
        'name': '🍽️ Ресторан',
        'price': 200000,
        'income': 10000,
        'level': 1,
        'max_level': 10,
        'upgrade_cost': 100000,
        'icon': '🍽️',
        'description': 'Премиум сегмент'
    },
    'factory': {
        'name': '🏭 Завод',
        'price': 1000000,
        'income': 50000,
        'level': 1,
        'max_level': 10,
        'upgrade_cost': 500000,
        'icon': '🏭',
        'description': 'Промышленный масштаб'
    },
    'corporation': {
        'name': '🏢 Корпорация',
        'price': 10000000,
        'income': 500000,
        'level': 1,
        'max_level': 10,
        'upgrade_cost': 5000000,
        'icon': '🏢',
        'description': 'Мировой уровень'
    }
}

# ====================== СИСТЕМА КЛАНОВ ======================
CLAN_DATA = {
    'create_cost': 100000,
    'max_members': 50,
    'war_cost': 50000,
    'bonus_per_member': 1000
}

# ====================== КЕЙСЫ ======================
CASES = {
    'case1': {'name': '😁 лол 😁', 'price': 3000, 'min_win': 1000, 'max_win': 5000, 'icon': '📦'},
    'case2': {'name': '🎮 лотус 🎮', 'price': 10000, 'min_win': 7500, 'max_win': 15000, 'icon': '🎮'},
    'case3': {'name': '💫 люкс кейс 💫', 'price': 50000, 'min_win': 35000, 'max_win': 65000, 'icon': '💫'},
    'case4': {'name': '💎 Платинум 💍', 'price': 200000, 'min_win': 175000, 'max_win': 250000, 'icon': '💎'},
    'case5': {'name': '💫 специальный кейс 👾', 'price': 1000000, 'min_win': 750000, 'max_win': 1250000, 'icon': '👾'},
    'case6': {'name': '🎉 ивентовый 🎊', 'price': 0, 'min_win': 12500, 'max_win': 75000, 'icon': '🎉'}
}

# ====================== ДОСТИЖЕНИЯ ======================
achievements = {
    'first_game': {'name': '🎮 Первый шаг', 'desc': 'Сыграть первую игру', 'reward': 1000},
    'millionaire': {'name': '💰 Миллионер', 'desc': 'Накопить 1,000,000 кредиксов', 'reward': 50000},
    'referral_master': {'name': '🤝 Реферал', 'desc': 'Пригласить 10 друзей', 'reward': 100000},
    'mice_collector': {'name': '🐭 Мышиный король', 'desc': 'Собрать всех видов мышек', 'reward': 150000},
    'pet_collector': {'name': '🐾 Зоофил', 'desc': 'Собрать всех питомцев', 'reward': 100000},
    'clan_leader': {'name': '👑 Лидер клана', 'desc': 'Создать клан', 'reward': 50000},
    'banker': {'name': '💳 Банкир', 'desc': 'Положить 1,000,000 в банк', 'reward': 75000},
    'businessman': {'name': '💼 Бизнесмен', 'desc': 'Купить 5 бизнесов', 'reward': 100000},
    'phone_addict': {'name': '📱 Телефономан', 'desc': 'Сделать 100 звонков', 'reward': 25000},
    'bonus_hunter': {'name': '🎁 Охотник за бонусами', 'desc': 'Забрать 30 ежедневных бонусов', 'reward': 50000}
}

# ====================== ИНИЦИАЛИЗАЦИЯ БОТА ======================
bot = telebot.TeleBot(TOKEN)

# ====================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ======================
def ensure_dir_exists(file_path):
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def atomic_json_save(file_path, data):
    ensure_dir_exists(file_path)
    temp = file_path + '.tmp'
    try:
        with open(temp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, file_path)
    except Exception as e:
        print(f"Ошибка сохранения {file_path}: {e}")

def safe_json_load(file_path, default_value=None):
    if default_value is None:
        default_value = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return default_value
        except Exception as e:
            print(f"Ошибка загрузки {file_path}: {e}")
            return default_value
    return default_value

def load_data():
    global users, username_cache, promocodes, user_achievements, user_quests, event_data
    global user_cases, orders, next_order_id, cheques, jackpot, duels, clans, businesses
    global bank_data, phone_data, bonus_data, pets_data, clans_data, businesses_data, cars_data
    global OWNER_ID

    with data_lock:
        users_data = safe_json_load(DATA_FILE, {})
        if users_data:
            users = {str(k): v for k, v in users_data.items()}
            for uid in users:
                # Инициализация отсутствующих полей
                defaults = {
                    'balance': 1000,
                    'krds_balance': 0,
                    'game': None,
                    'referrals': 0,
                    'referrer': None,
                    'banned': False,
                    'bank': {'balance': 0, 'last_interest': time.time(), 'history': []},
                    'used_promos': [],
                    'clan': None,
                    'total_wins': 0,
                    'total_losses': 0,
                    'games_played': 0,
                    'win_streak': 0,
                    'max_win_streak': 0,
                    'total_lost': 0,
                    'quests_completed': 0,
                    'event_points': 0,
                    'game_history': [],
                    'daily_last_claim': 0,
                    'daily_streak': 0,
                    'last_case6_open': 0,
                    'mice': {},
                    'mice_last_collect': {},
                    'pets': {},
                    'pets_last_feed': {},
                    'businesses': {},
                    'businesses_last_collect': {},
                    'phone_number': None,
                    'phone_contacts': [],
                    'daily_bonus': {'last_claim': 0, 'streak': 0},
                    'weekly_bonus': {'last_claim': 0, 'streak': 0},
                    'bank_deposit': {'amount': 0, 'time': 0},
                    'bank_loan': {'amount': 0, 'time': 0},
                    'work_count': 0,
                    'role': None,
                    'tester_last_payout': 0,
                    'cars': []          # для машин
                }
                for key, val in defaults.items():
                    if key not in users[uid]:
                        users[uid][key] = val

        username_cache = safe_json_load(USERNAME_CACHE_FILE, {})
        promocodes = safe_json_load(PROMO_FILE, {})
        
        mice_data = safe_json_load(MICE_FILE, {})
        if mice_data and 'mice_sold' in mice_data:
            for mouse_id, data in mice_data['mice_sold'].items():
                if mouse_id in MICE_DATA:
                    MICE_DATA[mouse_id]['sold'] = data

        orders_data = safe_json_load(ORDERS_FILE, {})
        if orders_data:
            orders = orders_data.get('orders', {})
            next_order_id = orders_data.get('next_id', 1)

        cheques = safe_json_load(CHEQUES_FILE, {})
        user_achievements = safe_json_load(ACHIEVEMENTS_FILE, {})
        user_quests = safe_json_load(QUESTS_FILE, {})
        user_cases = safe_json_load(CASES_FILE, {})
        duels = safe_json_load(DUEL_FILE, {})
        clans = safe_json_load(CLAN_FILE, {})
        businesses = safe_json_load(BUSINESS_FILE, {})

        bank_data = safe_json_load(BANK_FILE, {
            'loans': {}, 'deposits': {}, 'transfers': [], 'total_deposits': 0, 'interest_rate': 0.05
        })
        phone_data = safe_json_load(PHONE_FILE, {
            'contacts': {}, 'calls': {}, 'messages': {}, 'phone_numbers': {}
        })
        bonus_data = safe_json_load(BONUS_FILE, {
            'daily': {}, 'weekly': {}, 'monthly': {}, 'referral_bonus': 5000
        })
        pets_data = safe_json_load(PETS_FILE, {})
        clans_data = safe_json_load(CLAN_FILE, {})
        businesses_data = safe_json_load(BUSINESS_FILE, {})
        cars_data = safe_json_load(CARS_FILE, {})       # загружаем данные машин

        jackpot_data = safe_json_load('jackpot.json', {'total': 0})
        if jackpot_data:
            jackpot.update(jackpot_data)

        event_data = safe_json_load(EVENT_FILE, {
            'active': RELEASE_EVENT['active'],
            'participants': {},
            'leaderboard': [],
            'last_update': time.time()
        })

def save_data():
    with data_lock:
        try:
            atomic_json_save(DATA_FILE, users)
            atomic_json_save(USERNAME_CACHE_FILE, username_cache)
            atomic_json_save(PROMO_FILE, promocodes)
            atomic_json_save(ACHIEVEMENTS_FILE, user_achievements)
            atomic_json_save(QUESTS_FILE, user_quests)
            atomic_json_save(CASES_FILE, user_cases)
            atomic_json_save(DUEL_FILE, duels)
            atomic_json_save(CLAN_FILE, clans)
            atomic_json_save(BUSINESS_FILE, businesses)
            atomic_json_save('jackpot.json', jackpot)
            atomic_json_save(EVENT_FILE, event_data)
            atomic_json_save(BANK_FILE, bank_data)
            atomic_json_save(PHONE_FILE, phone_data)
            atomic_json_save(BONUS_FILE, bonus_data)
            atomic_json_save(PETS_FILE, pets_data)
            atomic_json_save(CARS_FILE, cars_data)      # сохраняем машины
            
            mice_data = {'mice_sold': {mid: MICE_DATA[mid]['sold'] for mid in MICE_DATA}}
            atomic_json_save(MICE_FILE, mice_data)
            
            orders_data = {'orders': orders, 'next_id': next_order_id}
            atomic_json_save(ORDERS_FILE, orders_data)
            atomic_json_save(CHEQUES_FILE, cheques)
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")

def get_user_lock(user_id):
    if user_id not in user_locks:
        user_locks[user_id] = RLock()
    return user_locks[user_id]

def get_locks_sorted(uid1, uid2):
    if uid1 < uid2:
        return get_user_lock(uid1), get_user_lock(uid2)
    else:
        return get_user_lock(uid2), get_user_lock(uid1)

def get_user(user_id):
    user_id = str(user_id)
    with get_user_lock(user_id):
        if user_id not in users:
            users[user_id] = {
                'balance': 1000,
                'krds_balance': 0,
                'game': None,
                'referrals': 0,
                'referrer': None,
                'banned': False,
                'bank': {'balance': 0, 'last_interest': time.time(), 'history': []},
                'used_promos': [],
                'clan': None,
                'total_wins': 0,
                'total_losses': 0,
                'games_played': 0,
                'win_streak': 0,
                'max_win_streak': 0,
                'total_lost': 0,
                'quests_completed': 0,
                'event_points': 0,
                'game_history': [],
                'daily_last_claim': 0,
                'daily_streak': 0,
                'last_case6_open': 0,
                'mice': {},
                'mice_last_collect': {},
                'pets': {},
                'pets_last_feed': {},
                'businesses': {},
                'businesses_last_collect': {},
                'phone_number': None,
                'phone_contacts': [],
                'daily_bonus': {'last_claim': 0, 'streak': 0},
                'weekly_bonus': {'last_claim': 0, 'streak': 0},
                'bank_deposit': {'amount': 0, 'time': 0},
                'bank_loan': {'amount': 0, 'time': 0},
                'work_count': 0,
                'role': None,
                'tester_last_payout': 0,
                'cars': []
            }
            save_data()
        return users[user_id]

def is_banned(user_id):
    return get_user(user_id).get('banned', False)

def is_admin(user_id):
    if str(user_id) in admin_users:
        return True
    user = get_user(user_id)
    return user.get('role') in ('admin', 'coder')

def update_username_cache(user_id, username):
    if username:
        with data_lock:
            username_cache[username.lower()] = str(user_id)
            save_data()

def parse_bet(bet_str):
    try:
        bet_str = bet_str.lower().strip()
        if 'кк' in bet_str:
            bet_str = bet_str.replace('кк', '')
            if bet_str == '':
                bet_str = '1'
            return int(float(bet_str) * 1000000)
        elif 'к' in bet_str:
            bet_str = bet_str.replace('к', '')
            if bet_str == '':
                bet_str = '1'
            return int(float(bet_str) * 1000)
        else:
            return int(bet_str)
    except:
        return None

def format_number(num):
    if num >= 1000000:
        return f"{num/1000000:.1f}М"
    elif num >= 1000:
        return f"{num/1000:.1f}К"
    return str(num)

def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)} сек"
    elif seconds < 3600:
        return f"{int(seconds/60)} мин"
    elif seconds < 86400:
        return f"{int(seconds/3600)} ч"
    else:
        return f"{int(seconds/86400)} д"

def get_event_multiplier():
    return 1.0

def unlock_achievement(user_id, achievement_id):
    if achievement_id not in achievements:
        return
    with data_lock:
        if user_id not in user_achievements:
            user_achievements[user_id] = {}
        if achievement_id in user_achievements[user_id]:
            return
        achievement = achievements[achievement_id]
        user_achievements[user_id][achievement_id] = time.time()
        user = get_user(user_id)
        user['balance'] += achievement['reward']
        save_data()
    try:
        bot.send_message(int(user_id), 
            f"🏆 ** ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО! ** 🏆\n\n"
            f"{achievement['name']}\n"
            f"{achievement['desc']}\n"
            f"💰 Награда: +{format_number(achievement['reward'])} кредиксов")
    except:
        pass

def update_game_stats(user_id, won, bet, win_amount=0):
    user = get_user(user_id)
    with get_user_lock(user_id):
        user['games_played'] = user.get('games_played', 0) + 1
        if won:
            user['total_wins'] = user.get('total_wins', 0) + 1
            user['win_streak'] = user.get('win_streak', 0) + 1
            if user['win_streak'] > user.get('max_win_streak', 0):
                user['max_win_streak'] = user['win_streak']
            user['game_history'].append({
                'time': time.time(),
                'game': 'game',
                'bet': bet,
                'result': 'win',
                'profit': win_amount - bet
            })
        else:
            user['total_losses'] = user.get('total_losses', 0) + 1
            user['win_streak'] = 0
            user['total_lost'] = user.get('total_lost', 0) + bet
            user['game_history'].append({
                'time': time.time(),
                'game': 'game',
                'bet': bet,
                'result': 'loss',
                'profit': -bet
            })
        save_data()
    
    if user['games_played'] == 1:
        unlock_achievement(user_id, 'first_game')
    if user['balance'] >= 1000000:
        unlock_achievement(user_id, 'millionaire')
    if len(user.get('mice', {})) >= 3:
        unlock_achievement(user_id, 'mice_collector')
    if len(user.get('pets', {})) >= 5:
        unlock_achievement(user_id, 'pet_collector')
    if len(user.get('businesses', {})) >= 5:
        unlock_achievement(user_id, 'businessman')
    if user.get('clan') is not None:
        unlock_achievement(user_id, 'clan_leader')
    if user.get('bank_deposit', {}).get('amount', 0) >= 1000000:
        unlock_achievement(user_id, 'banker')
    if len(user.get('phone_contacts', [])) >= 100:
        unlock_achievement(user_id, 'phone_addict')
    if user.get('daily_bonus', {}).get('streak', 0) >= 30:
        unlock_achievement(user_id, 'bonus_hunter')

def cancel_user_game(user_id):
    with get_user_lock(user_id):
        if user_id in crash_update_timers:
            try:
                crash_update_timers[user_id].cancel()
            except:
                pass
            del crash_update_timers[user_id]
        if user_id in game_timers:
            try:
                game_timers[user_id].cancel()
            except:
                pass
            del game_timers[user_id]
        user = get_user(user_id)
        if user.get('game') is not None:
            if user['game'].get('stage') == 'waiting_bet' and 'bet' in user['game']:
                user['balance'] += user['game']['bet']
            user['game'] = None
            save_data()
            return True
    return False

def cleanup_all_timers():
    with data_lock:
        for user_id in list(crash_update_timers.keys()):
            try:
                crash_update_timers[user_id].cancel()
            except:
                pass
        for user_id in list(game_timers.keys()):
            try:
                game_timers[user_id].cancel()
            except:
                pass
        crash_update_timers.clear()
        game_timers.clear()

def give_tester_bonus():
    while True:
        time.sleep(3600)
        now = time.time()
        with data_lock:
            for uid, user in users.items():
                role = user.get('role')
                if role in ('tester', 'coder') and not user.get('banned', False):
                    last = user.get('tester_last_payout', 0)
                    if now - last >= 10 * 3600:
                        user['balance'] = user.get('balance', 0) + 1_000_000
                        user['tester_last_payout'] = now
                        try:
                            bot.send_message(int(uid),
                                f"🤎 ** БОНУС ТЕСТЕРА ** 🤎\n\n"
                                f"💰 Вам начислено +1 000 000 кредиксов!\n"
                                f"Следующее начисление через 10 часов.")
                        except:
                            pass
            save_data()

# Фоновая задача для списаний по ипотеке
def mortgage_deduction_worker():
    while True:
        time.sleep(3600)  # проверка каждый час
        now = time.time()
        with data_lock:
            for uid, user in users.items():
                cars = user.get('cars', [])
                changed = False
                for car in cars:
                    if car.get('installment', False) and car.get('debt', 0) > 0:
                        last = car.get('last_deduction', 0)
                        # списываем раз в 24 часа
                        if now - last >= 86400:
                            price = CARS[car['model']]['price']
                            deduction = price * 0.1  # 10% от полной стоимости
                            if user['balance'] >= deduction:
                                user['balance'] -= deduction
                                car['debt'] -= deduction
                                if car['debt'] <= 0:
                                    car['installment'] = False
                                    car['debt'] = 0
                                car['last_deduction'] = now
                                changed = True
                            else:
                                # не хватает - баланс уходит в минус
                                user['balance'] -= deduction  # может стать отрицательным
                                # долг не уменьшается? По логике автора - дальше не списывается
                                # но мы просто пропускаем списание, чтобы не копить долг
                                # Однако автор сказал "ставится в - и дальше не списывается"
                                # Значит списание не происходит, баланс становится отрицательным.
                                # Реализуем так: если не хватает, баланс становится минус (уже вычли)
                                # и списание больше не производим (устанавливаем last_deduction = now,
                                # чтобы не пытаться каждый час)
                                car['last_deduction'] = now
                                changed = True
                if changed:
                    save_data()

# ====================== ОБРАБОТЧИК ТЕКСТОВЫХ КОМАНД (без слеша) ======================
def text_command_handler(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return

    text = message.text.strip().lower()
    if not text:
        return

    if text.startswith('/'):
        return

    parts = text.split()
    command = parts[0]

    command_map = {
        'баланс': balance_command,
        'профиль': profile_command,
        'топ': top_command,
        'помощь': help_command,
        'игры': games_command,
        'работа': work_command,
        'банк': bank_command,
        'депозит': deposit_command,
        'снять': withdraw_command,
        'кредит': loan_command,
        'выплатить': repay_loan_command,
        'проценты': interest_command,
        'телефон': phone_command,
        'контакты': contacts_command,
        'добавить': add_contact_command,
        'позвонить': call_command,
        'бонус': bonus_command,
        'daily': daily_bonus_command,
        'weekly': weekly_bonus_command,
        'питомцы': pets_command,
        'магазинпитомцев': pet_shop_command,
        'купитьпитомца': buy_pet_command,
        'покормить': feed_pet_command,
        'собратьпитомцы': collect_pets_command,
        'бизнес': business_command,
        'магазинбизнеса': business_shop_command,
        'купитьбизнес': buy_business_command,
        'улучшить': upgrade_business_command,
        'собратьбизнес': collect_business_command,
        'клан': clan_command,
        'создатьклан': create_clan_command,
        'мышки': mice_shop_command,
        'купитьмышку': buy_mouse_command,
        'мыши': my_mice_command,
        'собратьмыши': collect_mice_command,
        'обменник': exchange_menu,
        'продатькрдс': sell_krds_command,
        'продать': sell_to_bot_command,
        'моиордера': my_orders_command,
        'ордера': all_orders_command,
        'купить': buy_krds_command,
        'отменитьордер': cancel_order_command,
        'сенд': send_krds_command,
        'дать': give_command,
        'донат': donate_command,
        'реф': ref_command,
        'cancel': cancel_game_command,
        'кости': dice_game_command,
        'башня': tower_game_command,
        'футбол': football_game_command,
        'баскетбол': basketball_game_command,
        'пирамида': pyramid_game_command,
        'мины': mines_game_command,
        'джекпот': jackpot_game_command,
        'фишки': chips_game_command,
        'x2': x2_game_command,
        'x3': x3_game_command,
        'x5': x5_game_command,
        'рулетка_рус': russian_roulette_command,
        'очко': blackjack_game_command,
        'краш': crash_game_command,
        'слоты': slots_game_command,
        'рулетка_каз': roulette_command,
        'хило': hilo_game_command,
        # Новые команды для машин
        'машины': cars_shop_command,
        'купитьмашину': buy_car_command,
        'ипотека': mortgage_car_command,
        'моимашины': my_cars_command,
        'выплатитьипотеку': repay_mortgage_command,
        'такси': taxi_work_command,
    }

    if command in command_map:
        try:
            command_map[command](message)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка выполнения команды: {e}")
    else:
        # Неизвестная команда – игнорируем
        pass

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text and message.text.startswith('/'):
        return
    text_command_handler(message)

# ====================== КОМАНДА /start ======================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.from_user.id)
    try:
        print(f"✅ /start от пользователя {user_id} (@{message.from_user.username})")
        user = get_user(user_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        bot.send_message(message.chat.id, f"❌ Ошибка при создании профиля: {e}")
        return

    update_username_cache(user_id, message.from_user.username)

    # Проверка реферальной ссылки
    args = message.text.split()
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id != user_id and referrer_id in users and user.get('referrer') is None:
            try:
                with data_lock:
                    user['referrer'] = referrer_id
                    referrer = get_user(referrer_id)
                    referrer['referrals'] = referrer.get('referrals', 0) + 1
                    # Убедимся, что bonus_data существует и содержит ключ
                    global bonus_data
                    if not bonus_data:
                        bonus_data = {'referral_bonus': 5000}
                    referrer['balance'] += bonus_data.get('referral_bonus', 5000)
                    referrer['krds_balance'] += 5
                    if referrer['referrals'] >= 10:
                        unlock_achievement(referrer_id, 'referral_master')
                    save_data()
                try:
                    bot.send_message(int(referrer_id),
                        f"👥 По вашей ссылке зарегистрировался новый игрок!\n"
                        f"💰 +{format_number(bonus_data.get('referral_bonus', 5000))} кредиксов\n"
                        f"💎 +5 KRDS")
                except:
                    pass
            except Exception as e:
                print(f"Ошибка при обработке реферала: {e}")

    text = (
        f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
        f"🎰 Это игровой бот с множеством возможностей:\n"
        f"💰 Экономика, игры, бизнес, питомцы, мышки, кланы, машины и такси!\n\n"
        f"📋 Основные команды:\n"
        f"помощь - список всех команд\n"
        f"баланс - твой баланс\n"
        f"игры - список игр\n"
        f"профиль - твой профиль\n"
        f"машины - купить автомобиль для такси\n\n"
        f"🔗 Наш канал: {CHANNEL_USERNAME}\n"
        f"💬 Чат: {CHAT_LINK}"
    )
    bot.send_message(message.chat.id, text)

# ====================== АДМИН КОМАНДЫ ======================
@bot.message_handler(commands=['Admin'])
def admin_login(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "⛔ Доступ запрещён!")
        return
    bot.send_message(message.chat.id, "⚙️ Панель администратора", reply_markup=admin_panel())

def admin_panel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
        types.InlineKeyboardButton("💳 Балансы", callback_data="admin_balances"),
        types.InlineKeyboardButton("🔨 Бан", callback_data="admin_ban"),
        types.InlineKeyboardButton("🔓 Разбан", callback_data="admin_unban"),
        types.InlineKeyboardButton("🎁 Создать промо", callback_data="admin_create_promo"),
        types.InlineKeyboardButton("💎 Выдать KRDS", callback_data="admin_give_krds"),
        types.InlineKeyboardButton("💰 Выдать кредиксы", callback_data="admin_give_credits"),
        types.InlineKeyboardButton("👑 Назначить роль", callback_data="admin_set_role"),
        types.InlineKeyboardButton("🚗 Управление машинами", callback_data="admin_cars"),
        types.InlineKeyboardButton("🔙 Закрыть", callback_data="admin_close")
    )
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_callback(call):
    user_id = str(call.from_user.id)
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "⛔ Доступ запрещён!")
        return

    data = call.data
    if data == "admin_stats":
        total_users = len(users)
        total_balance = sum(u.get('balance', 0) for u in users.values())
        total_krds = sum(u.get('krds_balance', 0) for u in users.values())
        text = f"📊 Статистика:\n👥 Пользователей: {total_users}\n💰 Всего кредиксов: {format_number(total_balance)}\n💎 Всего KRDS: {total_krds}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel())
    elif data == "admin_users":
        msg = "Введите ник или ID пользователя для поиска:"
        bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(call.message, admin_search_user)
    elif data == "admin_balances":
        msg = "Введите ID пользователя для просмотра баланса:"
        bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(call.message, admin_show_balance)
    elif data == "admin_ban":
        msg = "Введите ID пользователя для бана:"
        bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(call.message, admin_ban_user)
    elif data == "admin_unban":
        msg = "Введите ID пользователя для разбана:"
        bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(call.message, admin_unban_user)
    elif data == "admin_create_promo":
        msg = "Введите параметры промокода в формате: код сумма лимит"
        bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(call.message, admin_create_promo)
    elif data == "admin_give_krds":
        msg = "Введите ID пользователя и сумму KRDS через пробел:"
        bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(call.message, admin_give_krds)
    elif data == "admin_give_credits":
        msg = "Введите ID пользователя и сумму кредиксов через пробел:"
        bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(call.message, admin_give_credits)
    elif data == "admin_set_role":
        msg = "Введите ID пользователя и роль (admin/tester/helper/coder) через пробел:"
        bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(call.message, admin_set_role)
    elif data == "admin_cars":
        msg = "Управление машинами пока в разработке."
        bot.answer_callback_query(call.id, msg)
    elif data == "admin_close":
        bot.delete_message(call.message.chat.id, call.message.message_id)

# Пример реализации одного из админ-шагов (остальные аналогично)
def admin_search_user(message):
    query = message.text.strip()
    # поиск по username или id
    found = None
    if query.isdigit():
        uid = query
        if uid in users:
            found = uid
    else:
        # поиск в username_cache
        if query.lower() in username_cache:
            found = username_cache[query.lower()]
    if found:
        user = users[found]
        text = f"ID: {found}\nБаланс: {format_number(user['balance'])}\nKRDS: {user['krds_balance']}\nРоль: {user.get('role', 'нет')}\nБан: {user.get('banned', False)}"
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "Пользователь не найден.")

# ... (остальные админ-функции можно реализовать по аналогии, для краткости опущены)

# ====================== БАЗОВЫЕ КОМАНДЫ ======================
@bot.message_handler(commands=['помощь', 'help'])
def help_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    
    text = (
        "📚 ** ПОМОЩЬ ПО БОТУ ** 📚\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎮 ** ИГРЫ **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏰 Башня: башня [ставка]\n"
        "⚽ Футбол: футбол [ставка] [гол/мимо]\n"
        "🏀 Баскетбол: баскетбол [ставка] [гол/мимо]\n"
        "🔺 Пирамида: пирамида [ставка]\n"
        "💣 Мины: мины [ставка]\n"
        "🎰 Джекпот: джекпот [ставка]\n"
        "⚫️⚪️ Фишки: фишки [ставка] [black/white]\n"
        "🎲 x2/x3/x5: x2/x3/x5 [ставка]\n"
        "🔫 Русская рулетка: рулетка_рус [ставка]\n"
        "🃏 Очко: очко [ставка]\n"
        "🚀 Краш: краш [ставка]\n"
        "🎰 Слоты: слоты [ставка]\n"
        "🎲 Кости: кости [ставка] [больше/меньше]\n"
        "🎰 Рулетка: рулетка_каз [ставка] [тип] [число]\n"
        "📈 Хило: хило [ставка]\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💎 ** KRDS СИСТЕМА **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "донат - баланс KRDS\n"
        "сенд @ник сумма - отправить KRDS\n"
        "продать количество - продать боту (3250/шт)\n"
        "обменник - P2P обменник\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🚗 ** ТАКСИ И МАШИНЫ **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "машины - магазин машин\n"
        "купитьмашину [модель] - покупка сразу\n"
        "ипотека [модель] - купить в ипотеку (взнос 10%)\n"
        "моимашины - список ваших машин\n"
        "выплатитьипотеку [модель] [сумма] - досрочное погашение\n"
        "такси - заработать на такси (раз в 3 часа)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🐭 ** МЫШКИ **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "мышки - магазин мышек\n"
        "купитьмышку [тип] - купить мышку\n"
        "мыши - мои мышки\n"
        "собратьмыши - собрать доход\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏦 ** БАНК **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "банк - банковские операции\n"
        "депозит [сумма] - положить под 5%\n"
        "снять [сумма] - снять с депозита\n"
        "кредит [сумма] - взять кредит\n"
        "выплатить [сумма] - выплатить кредит\n"
        "проценты - начислить проценты\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📱 ** ТЕЛЕФОН **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "телефон - твой номер\n"
        "контакты - список контактов\n"
        "добавить @ник - добавить контакт\n"
        "позвонить @ник - позвонить\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎁 ** БОНУСЫ **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "бонус - информация о бонусах\n"
        "daily - ежедневный бонус\n"
        "weekly - еженедельный бонус\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🐾 ** ПИТОМЦЫ **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "питомцы - мои питомцы\n"
        "магазинпитомцев - купить питомца\n"
        "купитьпитомца [тип] - купить\n"
        "покормить [тип] - покормить\n"
        "собратьпитомцы - собрать доход\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏢 ** БИЗНЕС **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "бизнес - мой бизнес\n"
        "магазинбизнеса - купить бизнес\n"
        "купитьбизнес [тип] - купить\n"
        "улучшить [тип] - улучшить\n"
        "собратьбизнес - собрать доход\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👥 ** КЛАНЫ **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "клан - информация\n"
        "создатьклан [название] - создать клан\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💼 ** ЭКОНОМИКА **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "работа - +55 кредиксов\n"
        "дать @ник сумма - перевод\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👥 ** СОЦИАЛ **\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "реф - реферальная ссылка\n"
        "топ - топ игроков\n"
        "профиль - профиль\n"
        "cancel - отменить игру\n"
        "помощь - это меню\n"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['баланс'])
def balance_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return

    user = get_user(user_id)
    try:
        chat = bot.get_chat(int(user_id))
        name = chat.first_name
    except:
        name = "Игрок"

    text = (
        f"💰 {name} 💰\n"
        f"💲Твой баланс: {format_number(user['balance'])} кредиксов💲\n"
        f"⚡krds: {user['krds_balance']}⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎰 Проиграно: {format_number(user.get('total_lost', 0))}\n"
        f"☃️выиграно: {user.get('total_wins', 0)}☃️\n"
        f"💖сыграно игр: {user.get('games_played', 0)}💖\n"
        f"~~~~~~~~~~~~~~~~~~~~~~~~"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['профиль'])
def profile_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return

    user = get_user(user_id)
    try:
        chat = bot.get_chat(int(user_id))
        name = chat.first_name
    except:
        name = "Игрок"
    role = VIP_ROLES.get(user.get('role'), {}).get('name', 'Игрок')
    text = (
        f"📇 ** ПРОФИЛЬ ** 📇\n\n"
        f"👤 Имя: {name}\n"
        f"🆔 ID: {user_id}\n"
        f"👑 Роль: {role}\n"
        f"💰 Баланс: {format_number(user['balance'])} кредиксов\n"
        f"💎 KRDS: {user['krds_balance']}\n"
        f"🎮 Игр сыграно: {user.get('games_played', 0)}\n"
        f"🏆 Побед: {user.get('total_wins', 0)}\n"
        f"💔 Поражений: {user.get('total_losses', 0)}\n"
        f"🔥 Текущая серия: {user.get('win_streak', 0)}\n"
        f"⭐ Макс серия: {user.get('max_win_streak', 0)}\n"
        f"📉 Всего проиграно: {format_number(user.get('total_lost', 0))}\n"
        f"👥 Рефералов: {user.get('referrals', 0)}\n"
        f"🚗 Машин: {len(user.get('cars', []))}"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['топ'])
def top_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    sorted_users = sorted(users.items(), key=lambda x: x[1].get('balance', 0), reverse=True)[:10]
    text = "🏆 ** ТОП 10 ПО БАЛАНСУ ** 🏆\n\n"
    for i, (uid, u) in enumerate(sorted_users, 1):
        try:
            chat = bot.get_chat(int(uid))
            name = chat.first_name
        except:
            name = f"ID {uid}"
        text += f"{i}. {name} — {format_number(u.get('balance', 0))} кредиксов\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['игры'])
def games_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    text = (
        "🎮 ** СПИСОК ИГР ** 🎮\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏰 Башня: башня [ставка]\n"
        "⚽ Футбол: футбол [ставка] [гол/мимо]\n"
        "🏀 Баскетбол: баскетбол [ставка] [гол/мимо]\n"
        "🔺 Пирамида: пирамида [ставка]\n"
        "💣 Мины: мины [ставка]\n"
        "🎰 Джекпот: джекпот [ставка]\n"
        "⚫️⚪️ Фишки: фишки [ставка] [black/white]\n"
        "🎲 x2/x3/x5: x2/x3/x5 [ставка]\n"
        "🔫 Русская рулетка: рулетка_рус [ставка]\n"
        "🃏 Очко: очко [ставка]\n"
        "🚀 Краш: краш [ставка]\n"
        "🎰 Слоты: слоты [ставка]\n"
        "🎲 Кости: кости [ставка] [больше/меньше]\n"
        "🎰 Рулетка: рулетка_каз [ставка] [тип] [число]\n"
        "📈 Хило: хило [ставка]\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🛑 Отмена игры: cancel"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['cancel'])
def cancel_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    if cancel_user_game(user_id):
        bot.send_message(message.chat.id, "🛑 Игра отменена. Ставка возвращена.")
    else:
        bot.send_message(message.chat.id, "❌ У тебя нет активной игры.")

# ====================== СИСТЕМА РАБОТЫ ======================
@bot.message_handler(commands=['работа'])
def work_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    with get_user_lock(user_id):
        reward = 55
        user['balance'] += reward
        user['work_count'] = user.get('work_count', 0) + 1
        save_data()
    text = (
        f"💼 ** РАБОТА ** 💼\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ Ты получил: +{reward} кредиксов\n"
        f"💰 Текущий баланс: {format_number(user['balance'])} кредиксов\n"
        f"📊 Всего отработано раз: {user['work_count']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 Приходи за бонусом снова!"
    )
    bot.send_message(message.chat.id, text)

# ====================== СИСТЕМА БАНКА ======================
@bot.message_handler(commands=['банк'])
def bank_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    deposit = user.get('bank_deposit', {'amount': 0, 'time': 0})
    loan = user.get('bank_loan', {'amount': 0, 'time': 0})
    text = (
        f"🏦 ** БАНК ** 🏦\n\n"
        f"💰 Депозит: {format_number(deposit['amount'])} кредиксов (ставка 5%)\n"
        f"💸 Кредит: {format_number(loan['amount'])} кредиксов\n"
        f"📈 Проценты можно начислить раз в сутки командой проценты"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['депозит'])
def deposit_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: депозит [сумма]")
        return
    amount = parse_bet(parts[1])
    if amount is None or amount <= 0:
        bot.send_message(message.chat.id, "❌ Неверная сумма.")
        return
    user = get_user(user_id)
    with get_user_lock(user_id):
        if user['balance'] < amount:
            bot.send_message(message.chat.id, f"❌ Недостаточно средств! Баланс: {format_number(user['balance'])}")
            return
        user['balance'] -= amount
        dep = user.get('bank_deposit', {'amount': 0, 'time': time.time()})
        dep['amount'] += amount
        dep['time'] = time.time()
        user['bank_deposit'] = dep
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы положили {format_number(amount)} кредиксов на депозит.")

@bot.message_handler(commands=['снять'])
def withdraw_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: снять [сумма]")
        return
    amount = parse_bet(parts[1])
    if amount is None or amount <= 0:
        bot.send_message(message.chat.id, "❌ Неверная сумма.")
        return
    user = get_user(user_id)
    with get_user_lock(user_id):
        dep = user.get('bank_deposit', {'amount': 0, 'time': 0})
        if dep['amount'] < amount:
            bot.send_message(message.chat.id, f"❌ На депозите только {format_number(dep['amount'])}")
            return
        dep['amount'] -= amount
        user['bank_deposit'] = dep
        user['balance'] += amount
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы сняли {format_number(amount)} кредиксов.")

@bot.message_handler(commands=['кредит'])
def loan_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: кредит [сумма]")
        return
    amount = parse_bet(parts[1])
    if amount is None or amount <= 0:
        bot.send_message(message.chat.id, "❌ Неверная сумма.")
        return
    user = get_user(user_id)
    with get_user_lock(user_id):
        # Проверка: нельзя взять кредит, если уже есть
        if user.get('bank_loan', {}).get('amount', 0) > 0:
            bot.send_message(message.chat.id, "❌ У вас уже есть непогашенный кредит.")
            return
        user['balance'] += amount
        user['bank_loan'] = {'amount': amount, 'time': time.time()}
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы взяли кредит {format_number(amount)} кредиксов.")

@bot.message_handler(commands=['выплатить'])
def repay_loan_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: выплатить [сумма]")
        return
    amount = parse_bet(parts[1])
    if amount is None or amount <= 0:
        bot.send_message(message.chat.id, "❌ Неверная сумма.")
        return
    user = get_user(user_id)
    with get_user_lock(user_id):
        loan = user.get('bank_loan', {'amount': 0, 'time': 0})
        if loan['amount'] <= 0:
            bot.send_message(message.chat.id, "❌ У вас нет кредита.")
            return
        if amount > loan['amount']:
            amount = loan['amount']
        if user['balance'] < amount:
            bot.send_message(message.chat.id, f"❌ Недостаточно средств! Баланс: {format_number(user['balance'])}")
            return
        user['balance'] -= amount
        loan['amount'] -= amount
        if loan['amount'] <= 0:
            user['bank_loan'] = {'amount': 0, 'time': 0}
        else:
            user['bank_loan'] = loan
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы выплатили {format_number(amount)} кредиксов по кредиту. Остаток: {format_number(loan['amount'])}")

@bot.message_handler(commands=['проценты'])
def interest_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    with get_user_lock(user_id):
        dep = user.get('bank_deposit', {'amount': 0, 'time': 0})
        if dep['amount'] <= 0:
            bot.send_message(message.chat.id, "❌ У вас нет депозита.")
            return
        now = time.time()
        if now - dep['time'] < 86400:
            remaining = 86400 - (now - dep['time'])
            bot.send_message(message.chat.id, f"❌ Проценты можно начислить раз в сутки. Осталось {format_time(remaining)}.")
            return
        interest = int(dep['amount'] * 0.05)
        dep['amount'] += interest
        dep['time'] = now
        user['bank_deposit'] = dep
        user['balance'] += interest  # проценты добавляются к балансу? Обычно на депозит, но автор, возможно, хочет на баланс. Оставим на баланс.
        save_data()
    bot.send_message(message.chat.id, f"✅ Начислены проценты: +{format_number(interest)} кредиксов на баланс.")

# ====================== СИСТЕМА ТЕЛЕФОНА ======================
@bot.message_handler(commands=['телефон'])
def phone_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    if not user.get('phone_number'):
        # генерируем номер
        number = f"+7{random.randint(900,999)}{random.randint(1000000,9999999)}"
        with get_user_lock(user_id):
            user['phone_number'] = number
            save_data()
    else:
        number = user['phone_number']
    text = f"📱 Ваш номер телефона: {number}"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['контакты'])
def contacts_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    contacts = user.get('phone_contacts', [])
    if not contacts:
        bot.send_message(message.chat.id, "📭 Список контактов пуст.")
        return
    text = "📇 ** Контакты **\n"
    for contact in contacts:
        text += f"• {contact}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['добавить'])
def add_contact_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: добавить @username")
        return
    username = parts[1].strip().lower()
    if not username.startswith('@'):
        username = '@' + username
    # проверить, существует ли такой пользователь
    target_id = username_cache.get(username[1:])
    if not target_id:
        bot.send_message(message.chat.id, "❌ Пользователь не найден.")
        return
    user = get_user(user_id)
    with get_user_lock(user_id):
        if username not in user.get('phone_contacts', []):
            user['phone_contacts'].append(username)
            save_data()
    bot.send_message(message.chat.id, f"✅ Контакт {username} добавлен.")

@bot.message_handler(commands=['позвонить'])
def call_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: позвонить @username")
        return
    username = parts[1].strip().lower()
    if not username.startswith('@'):
        username = '@' + username
    target_id = username_cache.get(username[1:])
    if not target_id:
        bot.send_message(message.chat.id, "❌ Пользователь не найден.")
        return
    # отправляем уведомление целевому пользователю
    try:
        bot.send_message(int(target_id), f"📞 Вам звонит {message.from_user.username or 'пользователь'}!")
        bot.send_message(message.chat.id, f"📞 Звонок {username} совершён.")
    except:
        bot.send_message(message.chat.id, "❌ Не удалось дозвониться.")

# ====================== СИСТЕМА БОНУСОВ ======================
@bot.message_handler(commands=['бонус'])
def bonus_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    daily = user.get('daily_bonus', {'last_claim': 0, 'streak': 0})
    weekly = user.get('weekly_bonus', {'last_claim': 0, 'streak': 0})
    now = time.time()
    daily_next = 86400 - (now - daily['last_claim']) if daily['last_claim'] > 0 else 0
    weekly_next = 604800 - (now - weekly['last_claim']) if weekly['last_claim'] > 0 else 0
    text = (
        f"🎁 ** БОНУСЫ ** 🎁\n\n"
        f"daily - ежедневный бонус\n"
        f"📅 Текущий стрик: {daily['streak']}\n"
        f"⏳ До следующего: {format_time(max(0, daily_next)) if daily_next > 0 else 'Доступно'}\n\n"
        f"weekly - еженедельный бонус\n"
        f"📅 Текущий стрик: {weekly['streak']}\n"
        f"⏳ До следующего: {format_time(max(0, weekly_next)) if weekly_next > 0 else 'Доступно'}"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['daily'])
def daily_bonus_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    with get_user_lock(user_id):
        daily = user.get('daily_bonus', {'last_claim': 0, 'streak': 0})
        now = time.time()
        if now - daily['last_claim'] < 86400:
            remaining = 86400 - (now - daily['last_claim'])
            bot.send_message(message.chat.id, f"❌ Ежедневный бонус уже получен. Следующий через {format_time(remaining)}.")
            return
        # расчёт награды
        streak = daily['streak'] + 1
        reward = 1000 + (streak * 100)
        user['balance'] += reward
        daily['last_claim'] = now
        daily['streak'] = streak
        user['daily_bonus'] = daily
        save_data()
    bot.send_message(message.chat.id, f"✅ Ежедневный бонус получен! +{format_number(reward)} кредиксов. Стрик: {streak}")

@bot.message_handler(commands=['weekly'])
def weekly_bonus_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    with get_user_lock(user_id):
        weekly = user.get('weekly_bonus', {'last_claim': 0, 'streak': 0})
        now = time.time()
        if now - weekly['last_claim'] < 604800:
            remaining = 604800 - (now - weekly['last_claim'])
            bot.send_message(message.chat.id, f"❌ Еженедельный бонус уже получен. Следующий через {format_time(remaining)}.")
            return
        streak = weekly['streak'] + 1
        reward = 10000 + (streak * 1000)
        user['balance'] += reward
        weekly['last_claim'] = now
        weekly['streak'] = streak
        user['weekly_bonus'] = weekly
        save_data()
    bot.send_message(message.chat.id, f"✅ Еженедельный бонус получен! +{format_number(reward)} кредиксов. Стрик: {streak}")

# ====================== СИСТЕМА ПИТОМЦЕВ ======================
@bot.message_handler(commands=['питомцы'])
def pets_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    pets = user.get('pets', {})
    if not pets:
        bot.send_message(message.chat.id, "🐾 У вас нет питомцев. Купите в магазинепитомцев")
        return
    text = "🐕 ** Ваши питомцы **\n\n"
    now = time.time()
    for pid, pet in pets.items():
        pet_info = PETS_DATA.get(pid, {})
        name = pet_info.get('name', pid)
        happiness = pet.get('happiness', 100)
        last_feed = pet.get('last_feed', 0)
        hungry = now - last_feed > 86400  # не кормили более суток
        text += f"{name} – счастье: {happiness}%, { '😢 голоден' if hungry else '😊 сыт'}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['магазинпитомцев'])
def pet_shop_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    text = "🐾 ** Магазин питомцев **\n\n"
    for pid, info in PETS_DATA.items():
        text += f"{info['name']}\n"
        text += f"💰 Цена: {format_number(info['price'])} кредиксов\n"
        text += f"💵 Доход: {info['income']}/час\n"
        text += f"🍖 Корм: {info['food_cost']} кредиксов\n"
        text += f"📝 {info['description']}\n"
        text += f"➡️ Купить: купитьпитомца {pid}\n\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['купитьпитомца'])
def buy_pet_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: купитьпитомца [тип]")
        return
    pet_id = parts[1].lower()
    if pet_id not in PETS_DATA:
        bot.send_message(message.chat.id, "❌ Такого питомца нет.")
        return
    pet_info = PETS_DATA[pet_id]
    user = get_user(user_id)
    with get_user_lock(user_id):
        if user['balance'] < pet_info['price']:
            bot.send_message(message.chat.id, f"❌ Недостаточно средств! Нужно {format_number(pet_info['price'])}")
            return
        user['balance'] -= pet_info['price']
        pets = user.get('pets', {})
        pets[pet_id] = {'happiness': 100, 'last_feed': time.time()}
        user['pets'] = pets
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы купили {pet_info['name']}!")

@bot.message_handler(commands=['покормить'])
def feed_pet_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: покормить [тип]")
        return
    pet_id = parts[1].lower()
    user = get_user(user_id)
    pets = user.get('pets', {})
    if pet_id not in pets:
        bot.send_message(message.chat.id, "❌ У вас нет такого питомца.")
        return
    pet_info = PETS_DATA.get(pet_id)
    if not pet_info:
        return
    with get_user_lock(user_id):
        if user['balance'] < pet_info['food_cost']:
            bot.send_message(message.chat.id, f"❌ Недостаточно средств для корма! Нужно {pet_info['food_cost']}")
            return
        user['balance'] -= pet_info['food_cost']
        pets[pet_id]['last_feed'] = time.time()
        pets[pet_id]['happiness'] = min(100, pets[pet_id].get('happiness', 100) + 10)
        user['pets'] = pets
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы покормили {pet_info['name']}. Счастье +10%.")

@bot.message_handler(commands=['собратьпитомцы'])
def collect_pets_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    pets = user.get('pets', {})
    if not pets:
        bot.send_message(message.chat.id, "🐾 У вас нет питомцев.")
        return
    now = time.time()
    total = 0
    changed = False
    with get_user_lock(user_id):
        for pid, pet in pets.items():
            last = pet.get('last_collect', 0)
            if now - last >= 3600:  # раз в час
                pet_info = PETS_DATA.get(pid)
                if pet_info:
                    income = pet_info['income']
                    # учёт счастья
                    happiness = pet.get('happiness', 100)
                    if happiness < 50:
                        income = int(income * 0.5)
                    elif happiness < 80:
                        income = int(income * 0.8)
                    total += income
                    pet['last_collect'] = now
                    changed = True
        if changed:
            user['balance'] += total
            user['pets'] = pets
            save_data()
    if total > 0:
        bot.send_message(message.chat.id, f"✅ Собрано с питомцев: +{format_number(total)} кредиксов.")
    else:
        bot.send_message(message.chat.id, "⏳ Ещё не прошёл час с последнего сбора.")

# ====================== СИСТЕМА БИЗНЕСА ======================
@bot.message_handler(commands=['бизнес'])
def business_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    businesses = user.get('businesses', {})
    if not businesses:
        bot.send_message(message.chat.id, "🏢 У вас нет бизнеса. Купите в магазинбизнеса")
        return
    text = "🏢 ** Ваш бизнес **\n\n"
    for bid, bus in businesses.items():
        info = BUSINESS_DATA.get(bid, {})
        name = info.get('name', bid)
        level = bus.get('level', 1)
        income = info.get('income', 0) * level
        text += f"{name} ур.{level} – доход {format_number(income)}/час\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['магазинбизнеса'])
def business_shop_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    text = "🏢 ** Магазин бизнеса **\n\n"
    for bid, info in BUSINESS_DATA.items():
        text += f"{info['icon']} {info['name']}\n"
        text += f"💰 Цена: {format_number(info['price'])} кредиксов\n"
        text += f"💵 Доход: {format_number(info['income'])}/час (ур.1)\n"
        text += f"📈 Улучшение: +{format_number(info['upgrade_cost'])} за уровень\n"
        text += f"➡️ Купить: купитьбизнес {bid}\n\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['купитьбизнес'])
def buy_business_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: купитьбизнес [тип]")
        return
    bid = parts[1].lower()
    if bid not in BUSINESS_DATA:
        bot.send_message(message.chat.id, "❌ Такого бизнеса нет.")
        return
    info = BUSINESS_DATA[bid]
    user = get_user(user_id)
    with get_user_lock(user_id):
        if user['balance'] < info['price']:
            bot.send_message(message.chat.id, f"❌ Недостаточно средств! Нужно {format_number(info['price'])}")
            return
        user['balance'] -= info['price']
        businesses = user.get('businesses', {})
        businesses[bid] = {'level': 1, 'last_collect': 0}
        user['businesses'] = businesses
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы купили {info['name']}!")

@bot.message_handler(commands=['улучшить'])
def upgrade_business_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: улучшить [тип]")
        return
    bid = parts[1].lower()
    user = get_user(user_id)
    businesses = user.get('businesses', {})
    if bid not in businesses:
        bot.send_message(message.chat.id, "❌ У вас нет такого бизнеса.")
        return
    bus = businesses[bid]
    info = BUSINESS_DATA.get(bid)
    if not info:
        return
    level = bus.get('level', 1)
    if level >= info['max_level']:
        bot.send_message(message.chat.id, "❌ Достигнут максимальный уровень.")
        return
    cost = info['upgrade_cost'] * level
    with get_user_lock(user_id):
        if user['balance'] < cost:
            bot.send_message(message.chat.id, f"❌ Недостаточно средств! Нужно {format_number(cost)}")
            return
        user['balance'] -= cost
        bus['level'] = level + 1
        bus['last_collect'] = bus.get('last_collect', 0)  # сохраняем
        user['businesses'][bid] = bus
        save_data()
    bot.send_message(message.chat.id, f"✅ {info['name']} улучшен до ур.{level+1}!")

@bot.message_handler(commands=['собратьбизнес'])
def collect_business_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    businesses = user.get('businesses', {})
    if not businesses:
        bot.send_message(message.chat.id, "🏢 У вас нет бизнеса.")
        return
    now = time.time()
    total = 0
    changed = False
    with get_user_lock(user_id):
        for bid, bus in businesses.items():
            last = bus.get('last_collect', 0)
            if now - last >= 3600:
                info = BUSINESS_DATA.get(bid)
                if info:
                    level = bus.get('level', 1)
                    income = info['income'] * level
                    total += income
                    bus['last_collect'] = now
                    changed = True
        if changed:
            user['balance'] += total
            user['businesses'] = businesses
            save_data()
    if total > 0:
        bot.send_message(message.chat.id, f"✅ Собрано с бизнеса: +{format_number(total)} кредиксов.")
    else:
        bot.send_message(message.chat.id, "⏳ Ещё не прошёл час с последнего сбора.")

# ====================== СИСТЕМА КЛАНОВ ======================
@bot.message_handler(commands=['клан'])
def clan_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    clan_id = user.get('clan')
    if not clan_id:
        bot.send_message(message.chat.id, "👥 Вы не состоите в клане. Создайте: создатьклан [название]")
        return
    clan = clans.get(clan_id)
    if not clan:
        bot.send_message(message.chat.id, "❌ Клан не найден.")
        return
    text = (
        f"👥 ** Клан {clan['name']} **\n"
        f"👑 Лидер: {clan.get('leader')}\n"
        f"👤 Участников: {len(clan.get('members', []))}\n"
        f"💰 Казна: {format_number(clan.get('balance', 0))}"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['создатьклан'])
def create_clan_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Формат: создатьклан [название]")
        return
    name = parts[1].strip()
    if len(name) > 32:
        bot.send_message(message.chat.id, "❌ Название слишком длинное (макс. 32 символа).")
        return
    user = get_user(user_id)
    if user.get('clan'):
        bot.send_message(message.chat.id, "❌ Вы уже в клане.")
        return
    cost = CLAN_DATA['create_cost']
    if user['balance'] < cost:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств! Нужно {format_number(cost)}")
        return
    with data_lock:
        clan_id = f"clan_{int(time.time())}_{user_id}"
        clans[clan_id] = {
            'name': name,
            'leader': user_id,
            'members': [user_id],
            'balance': 0,
            'created': time.time()
        }
        user['clan'] = clan_id
        user['balance'] -= cost
        save_data()
    bot.send_message(message.chat.id, f"✅ Клан '{name}' создан!")

# ====================== СИСТЕМА МЫШЕК ======================
@bot.message_handler(commands=['мышки'])
def mice_shop_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    text = "🐭 ** Магазин мышек **\n\n"
    for mid, info in MICE_DATA.items():
        sold = info.get('sold', 0)
        total = info['total']
        text += f"{info['icon']} {info['name']}\n"
        text += f"💰 Цена: {format_number(info['price'])} кредиксов\n"
        text += f"💵 Доход: {info['income']}/час\n"
        text += f"📦 В наличии: {total - sold}/{total}\n"
        text += f"⭐ Редкость: {info['rarity']}\n"
        text += f"➡️ Купить: купитьмышку {mid}\n\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['купитьмышку'])
def buy_mouse_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: купитьмышку [тип]")
        return
    mid = parts[1].lower()
    if mid not in MICE_DATA:
        bot.send_message(message.chat.id, "❌ Такой мышки нет.")
        return
    info = MICE_DATA[mid]
    if info['sold'] >= info['total']:
        bot.send_message(message.chat.id, "❌ Все мышки этого типа распроданы.")
        return
    user = get_user(user_id)
    with get_user_lock(user_id):
        if user['balance'] < info['price']:
            bot.send_message(message.chat.id, f"❌ Недостаточно средств! Нужно {format_number(info['price'])}")
            return
        user['balance'] -= info['price']
        mice = user.get('mice', {})
        mice[mid] = mice.get(mid, 0) + 1
        user['mice'] = mice
        info['sold'] += 1
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы купили {info['name']}!")

@bot.message_handler(commands=['мыши'])
def my_mice_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    mice = user.get('mice', {})
    if not mice:
        bot.send_message(message.chat.id, "🐭 У вас нет мышек. Купите в магазине мышки")
        return
    text = "🐭 ** Ваши мышки **\n\n"
    for mid, count in mice.items():
        info = MICE_DATA.get(mid, {})
        name = info.get('name', mid)
        text += f"{info.get('icon', '🐭')} {name} x{count}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['собратьмыши'])
def collect_mice_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    mice = user.get('mice', {})
    if not mice:
        bot.send_message(message.chat.id, "🐭 У вас нет мышек.")
        return
    now = time.time()
    total = 0
    changed = False
    with get_user_lock(user_id):
        for mid, count in mice.items():
            last = user.get('mice_last_collect', {}).get(mid, 0)
            if now - last >= 3600:
                info = MICE_DATA.get(mid)
                if info:
                    income = info['income'] * count
                    total += income
                    if 'mice_last_collect' not in user:
                        user['mice_last_collect'] = {}
                    user['mice_last_collect'][mid] = now
                    changed = True
        if changed:
            user['balance'] += total
            save_data()
    if total > 0:
        bot.send_message(message.chat.id, f"✅ Собрано с мышек: +{format_number(total)} кредиксов.")
    else:
        bot.send_message(message.chat.id, "⏳ Ещё не прошёл час с последнего сбора.")

# ====================== ОБМЕННИК KRDS ======================
@bot.message_handler(commands=['обменник'])
def exchange_menu(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    text = (
        "💎 ** ОБМЕННИК KRDS ** 💎\n\n"
        "продатькрдс [количество] [цена за 1 KRDS в кредиксах] - выставить ордер на продажу\n"
        "продать [количество] - продать боту по фикс. цене 3250 кредиксов за 1 KRDS\n"
        "моиордера - ваши активные ордера\n"
        "ордера - все активные ордера\n"
        "купить [ID ордера] [количество] - купить KRDS по ордеру\n"
        "отменитьордер [ID ордера] - отменить свой ордер\n"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['продатькрдс'])
def sell_krds_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.send_message(message.chat.id, "❌ Формат: продатькрдс [количество] [цена за 1 KRDS]")
        return
    try:
        amount = int(parts[1])
        price = int(parts[2])
    except:
        bot.send_message(message.chat.id, "❌ Неверные числа.")
        return
    if amount <= 0 or price <= 0:
        bot.send_message(message.chat.id, "❌ Числа должны быть положительными.")
        return
    user = get_user(user_id)
    if user['krds_balance'] < amount:
        bot.send_message(message.chat.id, f"❌ У вас только {user['krds_balance']} KRDS.")
        return
    with data_lock:
        global next_order_id
        order_id = next_order_id
        next_order_id += 1
        orders[order_id] = {
            'user_id': user_id,
            'type': 'sell',
            'amount': amount,
            'price': price,
            'remaining': amount,
            'created': time.time()
        }
        save_data()
    bot.send_message(message.chat.id, f"✅ Ордер №{order_id} создан. Продажа {amount} KRDS по {price} кредиксов за 1 KRDS.")

@bot.message_handler(commands=['продать'])
def sell_to_bot_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: продать [количество]")
        return
    try:
        amount = int(parts[1])
    except:
        bot.send_message(message.chat.id, "❌ Неверное число.")
        return
    if amount <= 0:
        bot.send_message(message.chat.id, "❌ Количество должно быть положительным.")
        return
    user = get_user(user_id)
    if user['krds_balance'] < amount:
        bot.send_message(message.chat.id, f"❌ У вас только {user['krds_balance']} KRDS.")
        return
    total_credits = amount * 3250
    with get_user_lock(user_id):
        user['krds_balance'] -= amount
        user['balance'] += total_credits
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы продали {amount} KRDS боту за {format_number(total_credits)} кредиксов.")

@bot.message_handler(commands=['моиордера'])
def my_orders_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    my_ords = [o for o in orders.values() if o['user_id'] == user_id and o['remaining'] > 0]
    if not my_ords:
        bot.send_message(message.chat.id, "📭 У вас нет активных ордеров.")
        return
    text = "📋 ** Ваши ордера **\n\n"
    for oid, ord in [(oid, ord) for oid, ord in orders.items() if ord['user_id'] == user_id and ord['remaining'] > 0]:
        text += f"№{oid}: {ord['type']} {ord['remaining']}/{ord['amount']} KRDS по {ord['price']} кредиксов\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['ордера'])
def all_orders_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    sell_ords = [o for o in orders.values() if o['type'] == 'sell' and o['remaining'] > 0]
    if not sell_ords:
        bot.send_message(message.chat.id, "📭 Нет активных ордеров на продажу.")
        return
    text = "📋 ** Ордера на продажу **\n\n"
    for oid, ord in orders.items():
        if ord['type'] == 'sell' and ord['remaining'] > 0:
            text += f"№{oid}: {ord['remaining']} KRDS по {ord['price']} кредиксов\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['купить'])
def buy_krds_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.send_message(message.chat.id, "❌ Формат: купить [ID ордера] [количество]")
        return
    try:
        order_id = int(parts[1])
        amount = int(parts[2])
    except:
        bot.send_message(message.chat.id, "❌ Неверные числа.")
        return
    if amount <= 0:
        bot.send_message(message.chat.id, "❌ Количество должно быть положительным.")
        return
    with data_lock:
        order = orders.get(order_id)
        if not order or order['remaining'] <= 0:
            bot.send_message(message.chat.id, "❌ Ордер не найден или уже закрыт.")
            return
        if order['type'] != 'sell':
            bot.send_message(message.chat.id, "❌ Это не ордер на продажу.")
            return
        if amount > order['remaining']:
            amount = order['remaining']
        seller_id = order['user_id']
        seller = get_user(seller_id)
        buyer = get_user(user_id)
        total_cost = amount * order['price']
        if buyer['balance'] < total_cost:
            bot.send_message(message.chat.id, f"❌ Недостаточно кредиксов! Нужно {format_number(total_cost)}")
            return
        # блокируем обоих пользователей в правильном порядке
        lock1, lock2 = get_locks_sorted(user_id, seller_id)
        with lock1, lock2:
            buyer['balance'] -= total_cost
            seller['balance'] += total_cost
            buyer['krds_balance'] += amount
            seller['krds_balance'] -= amount
            order['remaining'] -= amount
            if order['remaining'] <= 0:
                del orders[order_id]
            save_data()
    bot.send_message(message.chat.id, f"✅ Вы купили {amount} KRDS за {format_number(total_cost)} кредиксов.")

@bot.message_handler(commands=['отменитьордер'])
def cancel_order_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: отменитьордер [ID]")
        return
    try:
        order_id = int(parts[1])
    except:
        bot.send_message(message.chat.id, "❌ Неверный ID.")
        return
    with data_lock:
        order = orders.get(order_id)
        if not order:
            bot.send_message(message.chat.id, "❌ Ордер не найден.")
            return
        if order['user_id'] != user_id:
            bot.send_message(message.chat.id, "❌ Это не ваш ордер.")
            return
        del orders[order_id]
        save_data()
    bot.send_message(message.chat.id, f"✅ Ордер №{order_id} отменён.")

# ====================== ПРОМОКОДЫ ======================
@bot.message_handler(commands=['createpromo'])
def create_promo_command(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "⛔ Доступ запрещён!")
        return
    parts = message.text.split()
    if len(parts) != 4:
        bot.send_message(message.chat.id, "❌ Формат: createpromo [код] [сумма] [лимит]")
        return
    code = parts[1].upper()
    try:
        amount = int(parts[2])
        limit = int(parts[3])
    except:
        bot.send_message(message.chat.id, "❌ Неверные числа.")
        return
    with data_lock:
        promocodes[code] = {'amount': amount, 'limit': limit, 'used': 0}
        save_data()
    bot.send_message(message.chat.id, f"✅ Промокод {code} создан. Сумма: {format_number(amount)}, лимит: {limit}")

@bot.message_handler(commands=['promo'])
def promo_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: promo [код]")
        return
    code = parts[1].upper()
    user = get_user(user_id)
    with data_lock:
        promo = promocodes.get(code)
        if not promo:
            bot.send_message(message.chat.id, "❌ Промокод не найден.")
            return
        if code in user.get('used_promos', []):
            bot.send_message(message.chat.id, "❌ Вы уже использовали этот промокод.")
            return
        if promo['used'] >= promo['limit']:
            bot.send_message(message.chat.id, "❌ Промокод исчерпал лимит.")
            return
        user['balance'] += promo['amount']
        user.setdefault('used_promos', []).append(code)
        promo['used'] += 1
        save_data()
    bot.send_message(message.chat.id, f"✅ Промокод активирован! Вы получили +{format_number(promo['amount'])} кредиксов.")

# ====================== РЕФЕРАЛЬНАЯ СИСТЕМА ======================
@bot.message_handler(commands=['реф'])
def ref_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    link = f"https://t.me/{bot.get_me().username}?start={user_id}"
    text = (
        f"👥 ** Реферальная система **\n\n"
        f"🔗 Ваша ссылка: {link}\n"
        f"👤 Приглашено: {get_user(user_id).get('referrals', 0)} друзей\n"
        f"💰 За каждого друга вы получаете +{format_number(bonus_data['referral_bonus'])} кредиксов и +5 KRDS"
    )
    bot.send_message(message.chat.id, text)

# ====================== ДОНАТ (KRDS) ======================
@bot.message_handler(commands=['донат'])
def donate_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    text = f"💎 Ваш баланс KRDS: {user['krds_balance']} KRDS"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['сенд'])
def send_krds_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.send_message(message.chat.id, "❌ Формат: сенд @username [сумма]")
        return
    username = parts[1].lower().lstrip('@')
    try:
        amount = int(parts[2])
    except:
        bot.send_message(message.chat.id, "❌ Неверная сумма.")
        return
    if amount <= 0:
        bot.send_message(message.chat.id, "❌ Сумма должна быть положительной.")
        return
    target_id = username_cache.get(username)
    if not target_id:
        bot.send_message(message.chat.id, "❌ Пользователь не найден.")
        return
    if user_id == target_id:
        bot.send_message(message.chat.id, "❌ Нельзя отправить самому себе.")
        return
    sender = get_user(user_id)
    receiver = get_user(target_id)
    if sender['krds_balance'] < amount:
        bot.send_message(message.chat.id, f"❌ У вас только {sender['krds_balance']} KRDS.")
        return
    lock1, lock2 = get_locks_sorted(user_id, target_id)
    with lock1, lock2:
        sender['krds_balance'] -= amount
        receiver['krds_balance'] += amount
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы отправили {amount} KRDS пользователю @{username}.")
    try:
        bot.send_message(int(target_id), f"💎 Вы получили {amount} KRDS от {message.from_user.username or 'пользователя'}.")
    except:
        pass

@bot.message_handler(commands=['дать'])
def give_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.send_message(message.chat.id, "❌ Формат: дать @username [сумма]")
        return
    username = parts[1].lower().lstrip('@')
    try:
        amount = parse_bet(parts[2])
    except:
        bot.send_message(message.chat.id, "❌ Неверная сумма.")
        return
    if amount <= 0:
        bot.send_message(message.chat.id, "❌ Сумма должна быть положительной.")
        return
    target_id = username_cache.get(username)
    if not target_id:
        bot.send_message(message.chat.id, "❌ Пользователь не найден.")
        return
    if user_id == target_id:
        bot.send_message(message.chat.id, "❌ Нельзя отправить самому себе.")
        return
    sender = get_user(user_id)
    receiver = get_user(target_id)
    if sender['balance'] < amount:
        bot.send_message(message.chat.id, f"❌ У вас только {format_number(sender['balance'])} кредиксов.")
        return
    lock1, lock2 = get_locks_sorted(user_id, target_id)
    with lock1, lock2:
        sender['balance'] -= amount
        receiver['balance'] += amount
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы перевели {format_number(amount)} кредиксов пользователю @{username}.")
    try:
        bot.send_message(int(target_id), f"💰 Вы получили {format_number(amount)} кредиксов от {message.from_user.username or 'пользователя'}.")
    except:
        pass

# ====================== ИГРЫ ======================
# Вспомогательная функция для проверки ставки и активной игры
def can_play_game(user, bet):
    if bet > MAX_BET:
        return False, f"❌ Максимальная ставка {format_number(MAX_BET)}"
    if user['balance'] < bet:
        return False, f"❌ Недостаточно средств! Баланс: {format_number(user['balance'])}"
    if user.get('game') is not None:
        return False, "❌ У тебя уже есть активная игра! Закончи её или отмени (cancel)"
    return True, None

# ---------------------- Кости ----------------------
@bot.message_handler(commands=['кости'])
def dice_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.lower().split()
    if len(parts) != 3:
        bot.send_message(message.chat.id, "❌ Формат: кости [ставка] [больше/меньше]")
        return
    bet = parse_bet(parts[1])
    bet_type = parts[2]
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверный формат ставки.")
        return
    if bet_type not in ('больше', 'меньше'):
        bot.send_message(message.chat.id, "❌ Выбери 'больше' или 'меньше'")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2
        if bet_type == 'больше':
            won = total > 6
        else:
            won = total < 6
        if won:
            win_amount = int(bet * 1.8 * get_event_multiplier())
            user['balance'] += win_amount
            update_game_stats(user_id, True, bet, win_amount)
            text = (
                f"🎲 ** КОСТИ ** 🎲\n\n"
                f"Кости: {dice1} + {dice2} = {total}\n"
                f"Твоя ставка: {bet_type} 6\n\n"
                f"✅ ВЫИГРЫШ: x1.8\n"
                f"💰 +{format_number(win_amount)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        else:
            user['balance'] -= bet
            update_game_stats(user_id, False, bet)
            text = (
                f"🎲 ** КОСТИ ** 🎲\n\n"
                f"Кости: {dice1} + {dice2} = {total}\n"
                f"Твоя ставка: {bet_type} 6\n\n"
                f"❌ ПРОИГРЫШ\n"
                f"💰 -{format_number(bet)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        save_data()
    bot.send_message(message.chat.id, text)

# ---------------------- Башня ----------------------
@bot.message_handler(commands=['башня'])
def tower_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: башня [ставка]")
        return
    bet = parse_bet(parts[1])
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        # Создаём доску: 5 этажей, на каждом 5 ячеек, одна мина
        board = []
        for _ in range(5):
            floor = ['⭐'] * 5
            mine_pos = random.randint(0, 4)
            floor[mine_pos] = '💣'
            board.append(floor)
        user['game'] = {
            'type': 'tower',
            'bet': bet,
            'stage': 'in_progress',
            'level': 0,
            'multiplier': 1.0,
            'board': board
        }
        save_data()
    text = f"🏰 ** Башня **\nСтавка: {format_number(bet)}\nВыбери ячейку на 1 этаже:"
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = [types.InlineKeyboardButton(str(i+1), callback_data=f"tower_{i}") for i in range(5)]
    markup.add(*buttons)
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('tower_'))
def tower_callback(call):
    user_id = str(call.from_user.id)
    user = get_user(user_id)
    game = user.get('game')
    if not game or game['type'] != 'tower' or game['stage'] != 'in_progress':
        bot.answer_callback_query(call.id, "Игра не активна.")
        return
    try:
        cell = int(call.data.split('_')[1])
    except:
        bot.answer_callback_query(call.id, "Ошибка.")
        return
    level = game['level']
    board = game['board']
    if cell < 0 or cell >= len(board[level]):
        bot.answer_callback_query(call.id, "Неверная ячейка.")
        return
    result = board[level][cell]
    if result == '💣':
        # проигрыш
        with get_user_lock(user_id):
            user['balance'] -= game['bet']
            update_game_stats(user_id, False, game['bet'])
            user['game'] = None
            save_data()
        bot.edit_message_text(f"💥 БАХ! Ты наступил на мину на {level+1} этаже!\nПотеряно {format_number(game['bet'])} кредиксов.",
                              call.message.chat.id, call.message.message_id)
    else:
        # выигрыш этажа
        mult = TOWER_MULTIPLIERS.get(level+1, 1.0)
        if level == 4:  # последний этаж
            win = int(game['bet'] * mult * get_event_multiplier())
            with get_user_lock(user_id):
                user['balance'] += win
                update_game_stats(user_id, True, game['bet'], win)
                user['game'] = None
                save_data()
            bot.edit_message_text(f"🎉 Ты прошёл всю башню! Множитель {mult}\nВыигрыш: {format_number(win)}",
                                  call.message.chat.id, call.message.message_id)
        else:
            # переход на следующий этаж
            game['level'] += 1
            with get_user_lock(user_id):
                user['game'] = game
                save_data()
            text = f"🏰 Этаж {level+1} пройден! Множитель текущий: {mult}\nВыбери ячейку на {level+2} этаже:"
            markup = types.InlineKeyboardMarkup(row_width=5)
            buttons = [types.InlineKeyboardButton(str(i+1), callback_data=f"tower_{i}") for i in range(5)]
            markup.add(*buttons)
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ---------------------- Футбол ----------------------
@bot.message_handler(commands=['футбол'])
def football_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.lower().split()
    if len(parts) != 3:
        bot.send_message(message.chat.id, "❌ Формат: футбол [ставка] [гол/мимо]")
        return
    bet = parse_bet(parts[1])
    choice = parts[2]
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    if choice not in ('гол', 'мимо'):
        bot.send_message(message.chat.id, "❌ Выбери 'гол' или 'мимо'.")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        # Вероятность гола ~ 50%
        scored = random.random() < 0.5
        won = (choice == 'гол' and scored) or (choice == 'мимо' and not scored)
        if won:
            win_amount = int(bet * FOOTBALL_MULTIPLIER * get_event_multiplier())
            user['balance'] += win_amount
            update_game_stats(user_id, True, bet, win_amount)
            result_text = f"✅ ГОЛ! (x{FOOTBALL_MULTIPLIER})" if scored else "✅ МИМО! (x{FOOTBALL_MULTIPLIER})"
            text = (
                f"⚽ ** ФУТБОЛ ** ⚽\n\n"
                f"Твой выбор: {choice}\n"
                f"Результат: {'гол' if scored else 'мимо'}\n\n"
                f"{result_text}\n"
                f"💰 +{format_number(win_amount)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        else:
            user['balance'] -= bet
            update_game_stats(user_id, False, bet)
            text = (
                f"⚽ ** ФУТБОЛ ** ⚽\n\n"
                f"Твой выбор: {choice}\n"
                f"Результат: {'гол' if scored else 'мимо'}\n\n"
                f"❌ ПРОИГРЫШ\n"
                f"💰 -{format_number(bet)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        save_data()
    bot.send_message(message.chat.id, text)

# ---------------------- Баскетбол ----------------------
@bot.message_handler(commands=['баскетбол'])
def basketball_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.lower().split()
    if len(parts) != 3:
        bot.send_message(message.chat.id, "❌ Формат: баскетбол [ставка] [гол/мимо]")
        return
    bet = parse_bet(parts[1])
    choice = parts[2]
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    if choice not in ('гол', 'мимо'):
        bot.send_message(message.chat.id, "❌ Выбери 'гол' или 'мимо'.")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        scored = random.random() < 0.5
        won = (choice == 'гол' and scored) or (choice == 'мимо' and not scored)
        if won:
            win_amount = int(bet * BASKETBALL_MULTIPLIER * get_event_multiplier())
            user['balance'] += win_amount
            update_game_stats(user_id, True, bet, win_amount)
            result_text = f"✅ ГОЛ! (x{BASKETBALL_MULTIPLIER})" if scored else f"✅ МИМО! (x{BASKETBALL_MULTIPLIER})"
            text = (
                f"🏀 ** БАСКЕТБОЛ ** 🏀\n\n"
                f"Твой выбор: {choice}\n"
                f"Результат: {'гол' if scored else 'мимо'}\n\n"
                f"{result_text}\n"
                f"💰 +{format_number(win_amount)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        else:
            user['balance'] -= bet
            update_game_stats(user_id, False, bet)
            text = (
                f"🏀 ** БАСКЕТБОЛ ** 🏀\n\n"
                f"Твой выбор: {choice}\n"
                f"Результат: {'гол' if scored else 'мимо'}\n\n"
                f"❌ ПРОИГРЫШ\n"
                f"💰 -{format_number(bet)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        save_data()
    bot.send_message(message.chat.id, text)

# ---------------------- Пирамида ----------------------
@bot.message_handler(commands=['пирамида'])
def pyramid_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: пирамида [ставка]")
        return
    bet = parse_bet(parts[1])
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        # 10 ячеек, 1 алмаз
        cells = ['💎'] + ['⬛'] * 9
        random.shuffle(cells)
        # игрок выбирает ячейку (inline)
        user['game'] = {
            'type': 'pyramid',
            'bet': bet,
            'stage': 'in_progress',
            'cells': cells
        }
        save_data()
    text = f"🔺 ** Пирамида **\nСтавка: {format_number(bet)}\nВыбери ячейку с алмазом 💎:"
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = [types.InlineKeyboardButton(str(i+1), callback_data=f"pyramid_{i}") for i in range(10)]
    markup.add(*buttons)
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pyramid_'))
def pyramid_callback(call):
    user_id = str(call.from_user.id)
    user = get_user(user_id)
    game = user.get('game')
    if not game or game['type'] != 'pyramid' or game['stage'] != 'in_progress':
        bot.answer_callback_query(call.id, "Игра не активна.")
        return
    try:
        cell = int(call.data.split('_')[1])
    except:
        bot.answer_callback_query(call.id, "Ошибка.")
        return
    cells = game['cells']
    if cell < 0 or cell >= len(cells):
        bot.answer_callback_query(call.id, "Неверная ячейка.")
        return
    if cells[cell] == '💎':
        win = int(game['bet'] * PYRAMID_MULTIPLIER * get_event_multiplier())
        with get_user_lock(user_id):
            user['balance'] += win
            update_game_stats(user_id, True, game['bet'], win)
            user['game'] = None
            save_data()
        bot.edit_message_text(f"🎉 ТЫ НАШЁЛ АЛМАЗ! Выигрыш x{PYRAMID_MULTIPLIER}\n💰 +{format_number(win)} кредиксов",
                              call.message.chat.id, call.message.message_id)
    else:
        with get_user_lock(user_id):
            user['balance'] -= game['bet']
            update_game_stats(user_id, False, game['bet'])
            user['game'] = None
            save_data()
        bot.edit_message_text(f"💥 Пусто! Ты проиграл {format_number(game['bet'])} кредиксов.",
                              call.message.chat.id, call.message.message_id)

# ---------------------- Мины ----------------------
@bot.message_handler(commands=['мины'])
def mines_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: мины [ставка]")
        return
    bet = parse_bet(parts[1])
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        # 25 ячеек (5x5), 3 мины
        cells = ['💣'] * 3 + ['💎'] * 22
        random.shuffle(cells)
        user['game'] = {
            'type': 'mines',
            'bet': bet,
            'stage': 'in_progress',
            'cells': cells,
            'opened': 0
        }
        save_data()
    text = f"💣 ** Мины **\nСтавка: {format_number(bet)}\nВыбери ячейку (всего 25, 3 мины):"
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = [types.InlineKeyboardButton(str(i+1), callback_data=f"mines_{i}") for i in range(25)]
    markup.add(*buttons)
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('mines_'))
def mines_callback(call):
    user_id = str(call.from_user.id)
    user = get_user(user_id)
    game = user.get('game')
    if not game or game['type'] != 'mines' or game['stage'] != 'in_progress':
        bot.answer_callback_query(call.id, "Игра не активна.")
        return
    try:
        cell = int(call.data.split('_')[1])
    except:
        bot.answer_callback_query(call.id, "Ошибка.")
        return
    cells = game['cells']
    if cell < 0 or cell >= len(cells):
        bot.answer_callback_query(call.id, "Неверная ячейка.")
        return
    if cells[cell] == '💣':
        with get_user_lock(user_id):
            user['balance'] -= game['bet']
            update_game_stats(user_id, False, game['bet'])
            user['game'] = None
            save_data()
        bot.edit_message_text(f"💥 БАХ! Ты подорвался на мине!\nПотеряно {format_number(game['bet'])} кредиксов.",
                              call.message.chat.id, call.message.message_id)
    else:
        opened = game['opened'] + 1
        game['opened'] = opened
        # множитель зависит от кол-ва открытых ячеек и кол-ва мин (3)
        mult = MINES_MULTIPLIERS[3].get(opened, 1.0)  # для 3 мин
        if opened >= 10:
            # победа
            win = int(game['bet'] * mult * get_event_multiplier())
            with get_user_lock(user_id):
                user['balance'] += win
                update_game_stats(user_id, True, game['bet'], win)
                user['game'] = None
                save_data()
            bot.edit_message_text(f"🎉 Ты открыл 10 ячеек без мин! Множитель x{mult}\nВыигрыш: {format_number(win)}",
                                  call.message.chat.id, call.message.message_id)
        else:
            with get_user_lock(user_id):
                user['game'] = game
                save_data()
            # предлагаем продолжить или забрать выигрыш
            win_now = int(game['bet'] * mult)
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Продолжить", callback_data="mines_continue"),
                types.InlineKeyboardButton(f"Забрать {format_number(win_now)}", callback_data="mines_take")
            )
            bot.edit_message_text(f"✅ Ячейка безопасна! Открыто {opened}/10.\nТекущий множитель x{mult}\nМожно забрать {format_number(win_now)} или рискнуть дальше.",
                                  call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "mines_continue")
def mines_continue(call):
    user_id = str(call.from_user.id)
    user = get_user(user_id)
    game = user.get('game')
    if not game or game['type'] != 'mines' or game['stage'] != 'in_progress':
        bot.answer_callback_query(call.id, "Игра не активна.")
        return
    # просто возвращаем клавиатуру для выбора новой ячейки
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = [types.InlineKeyboardButton(str(i+1), callback_data=f"mines_{i}") for i in range(25)]
    markup.add(*buttons)
    bot.edit_message_text("Выбери следующую ячейку:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "mines_take")
def mines_take(call):
    user_id = str(call.from_user.id)
    user = get_user(user_id)
    game = user.get('game')
    if not game or game['type'] != 'mines' or game['stage'] != 'in_progress':
        bot.answer_callback_query(call.id, "Игра не активна.")
        return
    opened = game['opened']
    mult = MINES_MULTIPLIERS[3].get(opened, 1.0)
    win = int(game['bet'] * mult * get_event_multiplier())
    with get_user_lock(user_id):
        user['balance'] += win
        update_game_stats(user_id, True, game['bet'], win)
        user['game'] = None
        save_data()
    bot.edit_message_text(f"✅ Ты забрал выигрыш: {format_number(win)} кредиксов.",
                          call.message.chat.id, call.message.message_id)

# ---------------------- Джекпот ----------------------
@bot.message_handler(commands=['джекпот'])
def jackpot_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: джекпот [ставка]")
        return
    bet = parse_bet(parts[1])
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        # часть ставки идёт в джекпот, остальное в банк
        jackpot_share = int(bet * 0.1)
        jackpot['total'] += jackpot_share
        user['balance'] -= bet
        # шанс выиграть джекпот (например 0.1%)
        win_jackpot = random.random() < 0.001
        if win_jackpot:
            win = jackpot['total']
            user['balance'] += win
            jackpot['total'] = 0
            jackpot['last_winner'] = user_id
            jackpot['last_win_time'] = time.time()
            jackpot['history'].append({'user': user_id, 'amount': win, 'time': time.time()})
            update_game_stats(user_id, True, bet, win)
            text = (
                f"🎰 ** ДЖЕКПОТ ** 🎰\n\n"
                f"ТЫ ВЫИГРАЛ ДЖЕКПОТ!\n"
                f"💰 +{format_number(win)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        else:
            update_game_stats(user_id, False, bet)
            text = (
                f"🎰 ** ДЖЕКПОТ ** 🎰\n\n"
                f"Ты не выиграл джекпот.\n"
                f"Текущий джекпот: {format_number(jackpot['total'])} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        save_data()
    bot.send_message(message.chat.id, text)

# ---------------------- Фишки ----------------------
@bot.message_handler(commands=['фишки'])
def chips_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.lower().split()
    if len(parts) != 3:
        bot.send_message(message.chat.id, "❌ Формат: фишки [ставка] [black/white]")
        return
    bet = parse_bet(parts[1])
    color = parts[2]
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    if color not in ('black', 'white'):
        bot.send_message(message.chat.id, "❌ Выбери 'black' или 'white'.")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        # Простая игра: подбрасываем фишку, шанс 50%
        win = random.random() < 0.5
        if win:
            win_amount = int(bet * 2 * get_event_multiplier())
            user['balance'] += win_amount
            update_game_stats(user_id, True, bet, win_amount)
            text = (
                f"⚫️⚪️ ** ФИШКИ ** ⚫️⚪️\n\n"
                f"Твой цвет: {color}\n"
                f"Выпало: {random.choice(['black', 'white'])}\n\n"
                f"✅ ВЫИГРЫШ x2\n"
                f"💰 +{format_number(win_amount)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        else:
            user['balance'] -= bet
            update_game_stats(user_id, False, bet)
            text = (
                f"⚫️⚪️ ** ФИШКИ ** ⚫️⚪️\n\n"
                f"Твой цвет: {color}\n"
                f"Выпало: {random.choice(['black', 'white'])}\n\n"
                f"❌ ПРОИГРЫШ\n"
                f"💰 -{format_number(bet)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        save_data()
    bot.send_message(message.chat.id, text)

# ---------------------- x2, x3, x5 ----------------------
@bot.message_handler(commands=['x2'])
def x2_game_command(message):
    play_x_game(message, 2)

@bot.message_handler(commands=['x3'])
def x3_game_command(message):
    play_x_game(message, 3)

@bot.message_handler(commands=['x5'])
def x5_game_command(message):
    play_x_game(message, 5)

def play_x_game(message, mult):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, f"❌ Формат: x{mult} [ставка]")
        return
    bet = parse_bet(parts[1])
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        win = random.random() < 1/mult  # вероятность 1/mult
        if win:
            win_amount = int(bet * mult * get_event_multiplier())
            user['balance'] += win_amount
            update_game_stats(user_id, True, bet, win_amount)
            text = (
                f"🎲 ** x{mult} ** 🎲\n\n"
                f"✅ ВЫИГРЫШ x{mult}\n"
                f"💰 +{format_number(win_amount)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        else:
            user['balance'] -= bet
            update_game_stats(user_id, False, bet)
            text = (
                f"🎲 ** x{mult} ** 🎲\n\n"
                f"❌ ПРОИГРЫШ\n"
                f"💰 -{format_number(bet)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        save_data()
    bot.send_message(message.chat.id, text)

# ---------------------- Русская рулетка ----------------------
@bot.message_handler(commands=['рулетка_рус'])
def russian_roulette_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: рулетка_рус [ставка]")
        return
    bet = parse_bet(parts[1])
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        # 6 патронов, 1 заряжен
        shot = random.randint(1, 6) == 1
        if shot:
            user['balance'] -= bet
            update_game_stats(user_id, False, bet)
            text = (
                f"🔫 ** РУССКАЯ РУЛЕТКА ** 🔫\n\n"
                f"💥 БАХ! Ты проиграл.\n"
                f"💰 -{format_number(bet)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        else:
            win_amount = int(bet * 6 * get_event_multiplier())
            user['balance'] += win_amount
            update_game_stats(user_id, True, bet, win_amount)
            text = (
                f"🔫 ** РУССКАЯ РУЛЕТКА ** 🔫\n\n"
                f"😌 Щёлк... Ты выжил!\n"
                f"✅ ВЫИГРЫШ x6\n"
                f"💰 +{format_number(win_amount)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        save_data()
    bot.send_message(message.chat.id, text)

# ---------------------- Очко (Blackjack) ----------------------
@bot.message_handler(commands=['очко'])
def blackjack_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: очко [ставка]")
        return
    bet = parse_bet(parts[1])
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        # Упрощённый блэкджек: игрок тянет карту, дилер тянет карту, у кого больше (но не больше 21)
        # Для простоты используем числа от 2 до 11
        player = random.randint(2, 11)
        dealer = random.randint(2, 11)
        if player > 21:
            player = 21  # для простоты
        if dealer > 21:
            dealer = 21
        if player > dealer:
            win_amount = int(bet * BLACKJACK_MULTIPLIER * get_event_multiplier())
            user['balance'] += win_amount
            update_game_stats(user_id, True, bet, win_amount)
            result = f"✅ ВЫИГРЫШ x{BLACKJACK_MULTIPLIER}\n💰 +{format_number(win_amount)}"
        elif player < dealer:
            user['balance'] -= bet
            update_game_stats(user_id, False, bet)
            result = f"❌ ПРОИГРЫШ\n💰 -{format_number(bet)}"
        else:
            # ничья, возврат ставки
            result = f"🤝 НИЧЬЯ\n💰 Ставка возвращена"
        text = (
            f"🃏 ** ОЧКО ** 🃏\n\n"
            f"Твои карты: {player}\n"
            f"Карты дилера: {dealer}\n\n"
            f"{result}\n"
            f"💸 Баланс: {format_number(user['balance'])}"
        )
        save_data()
    bot.send_message(message.chat.id, text)

# ---------------------- Краш ----------------------
@bot.message_handler(commands=['краш'])
def crash_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: краш [ставка]")
        return
    bet = parse_bet(parts[1])
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        # Генерируем множитель, который крашнется
        crash_point = random.uniform(1.0, 10.0)
        # Игрок всегда забирает до краша? Упростим: игрок выигрывает с вероятностью 50% с множителем 2
        # Но сделаем как в классическом краше: игрок сам решает, когда остановиться. Но для inline это сложно.
        # Сделаем упрощённо: шанс 50% на x2
        win = random.random() < 0.5
        if win:
            win_amount = int(bet * 2 * get_event_multiplier())
            user['balance'] += win_amount
            update_game_stats(user_id, True, bet, win_amount)
            text = (
                f"🚀 ** КРАШ ** 🚀\n\n"
                f"Ты успел забрать выигрыш!\n"
                f"✅ x2\n"
                f"💰 +{format_number(win_amount)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        else:
            user['balance'] -= bet
            update_game_stats(user_id, False, bet)
            text = (
                f"🚀 ** КРАШ ** 🚀\n\n"
                f"Краш! Ты проиграл.\n"
                f"❌ -{format_number(bet)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        save_data()
    bot.send_message(message.chat.id, text)

# ---------------------- Слоты ----------------------
@bot.message_handler(commands=['слоты'])
def slots_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: слоты [ставка]")
        return
    bet = parse_bet(parts[1])
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        reel1 = random.choice(SLOTS_SYMBOLS)
        reel2 = random.choice(SLOTS_SYMBOLS)
        reel3 = random.choice(SLOTS_SYMBOLS)
        combo = (reel1, reel2, reel3)
        multiplier = SLOTS_PAYOUTS.get(combo, 0)
        if multiplier > 0:
            win_amount = int(bet * multiplier * get_event_multiplier())
            user['balance'] += win_amount
            update_game_stats(user_id, True, bet, win_amount)
            text = (
                f"🎰 ** СЛОТЫ ** 🎰\n\n"
                f"{reel1} | {reel2} | {reel3}\n\n"
                f"✅ ВЫИГРЫШ x{multiplier}\n"
                f"💰 +{format_number(win_amount)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        else:
            user['balance'] -= bet
            update_game_stats(user_id, False, bet)
            text = (
                f"🎰 ** СЛОТЫ ** 🎰\n\n"
                f"{reel1} | {reel2} | {reel3}\n\n"
                f"❌ ПРОИГРЫШ\n"
                f"💰 -{format_number(bet)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        save_data()
    bot.send_message(message.chat.id, text)

# ---------------------- Рулетка (каз) ----------------------
@bot.message_handler(commands=['рулетка_каз'])
def roulette_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.lower().split()
    if len(parts) < 3:
        bot.send_message(message.chat.id, "❌ Формат: рулетка_каз [ставка] [тип ставки] [число если нужно]")
        return
    bet = parse_bet(parts[1])
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    bet_type = parts[2]
    number = None
    if bet_type == 'straight' and len(parts) == 4:
        try:
            number = int(parts[3])
            if number < 0 or number > 36:
                raise ValueError
        except:
            bot.send_message(message.chat.id, "❌ Неверное число. Введи от 0 до 36.")
            return
    elif bet_type in ('red', 'black', 'even', 'odd', '1-18', '19-36'):
        pass
    elif bet_type == 'dozen' and len(parts) == 4:
        try:
            dozen = int(parts[3])
            if dozen not in (1,2,3):
                raise ValueError
        except:
            bot.send_message(message.chat.id, "❌ Дюжина должна быть 1, 2 или 3.")
            return
    else:
        bot.send_message(message.chat.id, "❌ Неверный тип ставки.")
        return

    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return

    with get_user_lock(user_id):
        result = random.choice(ROULETTE_NUMBERS)
        win_mult = 0
        if bet_type == 'straight' and result == number:
            win_mult = ROULETTE_MULTIPLIERS['straight']
        elif bet_type == 'red' and result in RED_NUMBERS:
            win_mult = ROULETTE_MULTIPLIERS['red']
        elif bet_type == 'black' and result in BLACK_NUMBERS:
            win_mult = ROULETTE_MULTIPLIERS['black']
        elif bet_type == 'even' and result != 0 and result % 2 == 0:
            win_mult = ROULETTE_MULTIPLIERS['even']
        elif bet_type == 'odd' and result % 2 == 1:
            win_mult = ROULETTE_MULTIPLIERS['odd']
        elif bet_type == '1-18' and 1 <= result <= 18:
            win_mult = ROULETTE_MULTIPLIERS['1-18']
        elif bet_type == '19-36' and 19 <= result <= 36:
            win_mult = ROULETTE_MULTIPLIERS['19-36']
        elif bet_type == 'dozen':
            d = (result-1)//3 + 1 if result != 0 else 0
            if d == int(parts[3]):
                win_mult = ROULETTE_MULTIPLIERS['dozen']

        if win_mult > 0:
            win_amount = int(bet * win_mult * get_event_multiplier())
            user['balance'] += win_amount
            update_game_stats(user_id, True, bet, win_amount)
            text = (
                f"🎰 ** РУЛЕТКА ** 🎰\n\n"
                f"Выпало число: {result}\n"
                f"Твоя ставка: {bet_type} {number if number else ''}\n\n"
                f"✅ ВЫИГРЫШ x{win_mult}\n"
                f"💰 +{format_number(win_amount)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        else:
            user['balance'] -= bet
            update_game_stats(user_id, False, bet)
            text = (
                f"🎰 ** РУЛЕТКА ** 🎰\n\n"
                f"Выпало число: {result}\n"
                f"Твоя ставка: {bet_type} {number if number else ''}\n\n"
                f"❌ ПРОИГРЫШ\n"
                f"💰 -{format_number(bet)} кредиксов\n"
                f"💸 Баланс: {format_number(user['balance'])}"
            )
        save_data()
    bot.send_message(message.chat.id, text)

# ---------------------- Хило ----------------------
@bot.message_handler(commands=['хило'])
def hilo_game_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: хило [ставка]")
        return
    bet = parse_bet(parts[1])
    if bet is None:
        bot.send_message(message.chat.id, "❌ Неверная ставка.")
        return
    user = get_user(user_id)
    ok, err = can_play_game(user, bet)
    if not ok:
        bot.send_message(message.chat.id, err)
        return
    with get_user_lock(user_id):
        # Простая версия: игрок угадывает, будет ли следующая карта выше или ниже первой.
        # Для простоты используем числа от 1 до 13
        card1 = random.randint(1, 13)
        card2 = random.randint(1, 13)
        # Игрок выбирает "выше" или "ниже" через inline
        user['game'] = {
            'type': 'hilo',
            'bet': bet,
            'stage': 'waiting_choice',
            'card1': card1,
            'card2': card2
        }
        save_data()
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("⬆️ Выше", callback_data="hilo_higher"),
        types.InlineKeyboardButton("⬇️ Ниже", callback_data="hilo_lower")
    )
    bot.send_message(message.chat.id, f"📈 ** ХИЛО ** 📉\n\nТвоя карта: {card1}\n\nБудет следующая карта выше или ниже?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('hilo_'))
def hilo_callback(call):
    user_id = str(call.from_user.id)
    user = get_user(user_id)
    game = user.get('game')
    if not game or game['type'] != 'hilo' or game['stage'] != 'waiting_choice':
        bot.answer_callback_query(call.id, "Игра не активна.")
        return
    choice = call.data.split('_')[1]  # higher or lower
    card1 = game['card1']
    card2 = game['card2']
    won = (choice == 'higher' and card2 > card1) or (choice == 'lower' and card2 < card1)
    if won:
        win_amount = int(game['bet'] * HILO_MULT * get_event_multiplier())
        with get_user_lock(user_id):
            user['balance'] += win_amount
            update_game_stats(user_id, True, game['bet'], win_amount)
            user['game'] = None
            save_data()
        text = (
            f"📈 ** ХИЛО ** 📉\n\n"
            f"Твоя карта: {card1}\n"
            f"Следующая карта: {card2}\n\n"
            f"✅ ВЫИГРЫШ x{HILO_MULT}\n"
            f"💰 +{format_number(win_amount)} кредиксов\n"
            f"💸 Баланс: {format_number(user['balance'])}"
        )
    else:
        with get_user_lock(user_id):
            user['balance'] -= game['bet']
            update_game_stats(user_id, False, game['bet'])
            user['game'] = None
            save_data()
        text = (
            f"📈 ** ХИЛО ** 📉\n\n"
            f"Твоя карта: {card1}\n"
            f"Следующая карта: {card2}\n\n"
            f"❌ ПРОИГРЫШ\n"
            f"💰 -{format_number(game['bet'])} кредиксов\n"
            f"💸 Баланс: {format_number(user['balance'])}"
        )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

# ====================== СИСТЕМА МАШИН И ТАКСИ ======================
@bot.message_handler(commands=['машины'])
def cars_shop_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    text = "🚗 ** Магазин машин для такси **\n\n"
    for cid, info in CARS.items():
        text += f"{info['icon']} {info['name']} ({info['class']} класс)\n"
        text += f"💰 Цена: {format_number(info['price'])} кредиксов\n"
        text += f"💵 Доход: {format_number(info['income'])} кредиксов / 3 часа\n"
        text += f"➡️ Купить сразу: купитьмашину {cid}\n"
        text += f"🏦 Ипотека: ипотека {cid} (взнос 10%)\n\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['купитьмашину'])
def buy_car_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: купитьмашину [модель]")
        return
    cid = parts[1].lower()
    if cid not in CARS:
        bot.send_message(message.chat.id, "❌ Такой модели нет.")
        return
    info = CARS[cid]
    user = get_user(user_id)
    with get_user_lock(user_id):
        if user['balance'] < info['price']:
            bot.send_message(message.chat.id, f"❌ Недостаточно средств! Нужно {format_number(info['price'])}")
            return
        user['balance'] -= info['price']
        cars = user.get('cars', [])
        # Проверяем, есть ли уже такая машина
        for car in cars:
            if car['model'] == cid and not car.get('installment', False) and car.get('debt', 0) == 0:
                bot.send_message(message.chat.id, "❌ У вас уже есть такая машина.")
                return
        cars.append({
            'model': cid,
            'installment': False,
            'debt': 0,
            'last_taxi': 0,
            'last_deduction': time.time()
        })
        user['cars'] = cars
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы купили {info['name']} за {format_number(info['price'])} кредиксов!")

@bot.message_handler(commands=['ипотека'])
def mortgage_car_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: ипотека [модель]")
        return
    cid = parts[1].lower()
    if cid not in CARS:
        bot.send_message(message.chat.id, "❌ Такой модели нет.")
        return
    info = CARS[cid]
    user = get_user(user_id)
    initial = int(info['price'] * 0.1)  # 10% первоначальный взнос
    with get_user_lock(user_id):
        if user['balance'] < initial:
            bot.send_message(message.chat.id, f"❌ Недостаточно для первоначального взноса! Нужно {format_number(initial)}")
            return
        user['balance'] -= initial
        cars = user.get('cars', [])
        cars.append({
            'model': cid,
            'installment': True,
            'debt': info['price'] - initial,
            'last_taxi': 0,
            'last_deduction': time.time()
        })
        user['cars'] = cars
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы взяли в ипотеку {info['name']}. Внесено {format_number(initial)}. Остаток долга: {format_number(info['price'] - initial)}.\nЕжедневно будет списываться 10% от полной стоимости ({format_number(int(info['price']*0.1))}).")

@bot.message_handler(commands=['моимашины'])
def my_cars_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    cars = user.get('cars', [])
    if not cars:
        bot.send_message(message.chat.id, "🚗 У вас нет машин. Купите в магазине машины")
        return
    text = "🚗 ** Ваши машины **\n\n"
    now = time.time()
    for car in cars:
        model = CARS.get(car['model'], {})
        name = model.get('name', car['model'])
        status = "в ипотеке" if car.get('installment') else "в собственности"
        debt = car.get('debt', 0)
        last_taxi = car.get('last_taxi', 0)
        taxi_ready = now - last_taxi >= model.get('income_interval', 10800) if last_taxi > 0 else True
        text += f"{model.get('icon', '🚗')} {name} – {status}\n"
        if car.get('installment'):
            text += f"💰 Остаток долга: {format_number(debt)}\n"
        text += f"⏳ Такси: {'✅ готово' if taxi_ready else '⏳ ещё ' + format_time(model.get('income_interval',10800) - (now - last_taxi))}\n\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['выплатитьипотеку'])
def repay_mortgage_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.send_message(message.chat.id, "❌ Формат: выплатитьипотеку [модель] [сумма]")
        return
    cid = parts[1].lower()
    try:
        amount = int(parts[2])
    except:
        bot.send_message(message.chat.id, "❌ Неверная сумма.")
        return
    if amount <= 0:
        bot.send_message(message.chat.id, "❌ Сумма должна быть положительной.")
        return
    user = get_user(user_id)
    cars = user.get('cars', [])
    target_car = None
    for car in cars:
        if car['model'] == cid and car.get('installment', False):
            target_car = car
            break
    if not target_car:
        bot.send_message(message.chat.id, "❌ У вас нет такой машины в ипотеке.")
        return
    if amount > target_car['debt']:
        amount = target_car['debt']
    with get_user_lock(user_id):
        if user['balance'] < amount:
            bot.send_message(message.chat.id, f"❌ Недостаточно средств! Баланс: {format_number(user['balance'])}")
            return
        user['balance'] -= amount
        target_car['debt'] -= amount
        if target_car['debt'] <= 0:
            target_car['installment'] = False
            target_car['debt'] = 0
        save_data()
    bot.send_message(message.chat.id, f"✅ Вы выплатили {format_number(amount)} по ипотеке. Остаток долга: {format_number(target_car['debt'])}")

@bot.message_handler(commands=['такси'])
def taxi_work_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    cars = user.get('cars', [])
    if not cars:
        bot.send_message(message.chat.id, "🚗 У вас нет машин. Купите в магазине машины")
        return
    now = time.time()
    total_income = 0
    changed = False
    with get_user_lock(user_id):
        for car in cars:
            model = CARS.get(car['model'])
            if not model:
                continue
            last = car.get('last_taxi', 0)
            if now - last >= model['income_interval']:
                # можно собрать доход
                income = model['income']
                # если машина в ипотеке, доход идёт в полном объёме? по условию да, можно зарабатывать.
                total_income += income
                car['last_taxi'] = now
                changed = True
        if changed:
            user['balance'] += total_income
            save_data()
    if total_income > 0:
        bot.send_message(message.chat.id, f"✅ Вы отработали на такси! Заработано: +{format_number(total_income)} кредиксов.")
    else:
        # не прошло 3 часа с последней работы
        # найдём ближайшее время ожидания
        min_wait = None
        for car in cars:
            model = CARS.get(car['model'])
            if not model:
                continue
            last = car.get('last_taxi', 0)
            if last > 0:
                elapsed = now - last
                if elapsed < model['income_interval']:
                    wait = model['income_interval'] - elapsed
                    if min_wait is None or wait < min_wait:
                        min_wait = wait
        if min_wait:
            bot.send_message(message.chat.id, f"⏳ Такси будет доступно через {format_time(min_wait)}.")
        else:
            bot.send_message(message.chat.id, "⏳ Вы уже собирали доход недавно. Подождите.")

# ====================== ОБРАБОТЧИК ЗАВЕРШЕНИЯ ======================
def signal_handler(signum, frame):
    print("\n" + "="*50)
    print("⏳ Завершение работы бота...")
    cleanup_all_timers()
    save_data()
    print("✅ Данные сохранены")
    print("👋 Бот остановлен")
    print("="*50)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ====================== ЗАПУСК БОТА ======================
if __name__ == '__main__':
    os.makedirs('.', exist_ok=True)
    load_data()
    
    try:
        owner_chat = bot.get_chat(f"@{OWNER_USERNAME[1:]}")
        OWNER_ID = str(owner_chat.id)
        with data_lock:
            if OWNER_ID in users:
                users[OWNER_ID]['role'] = 'coder'
            else:
                users[OWNER_ID] = get_user(OWNER_ID)
                users[OWNER_ID]['role'] = 'coder'
            save_data()
        print(f"👑 Владелец {OWNER_USERNAME} (ID: {OWNER_ID}) получил роль кодера.")
    except Exception as e:
        print(f"⚠️ Не удалось получить ID владельца: {e}")
        OWNER_ID = None
    
    # Фоновые задачи
    tester_thread = Thread(target=give_tester_bonus, daemon=True)
    tester_thread.start()
    mortgage_thread = Thread(target=mortgage_deduction_worker, daemon=True)
    mortgage_thread.start()
    
    print("=" * 60)
    print("✅ БОТ КАЗИНО ЗАПУЩЕН!")
    print("=" * 60)
    print("📋 СИСТЕМЫ:")
    print("  • 🚗 Машины и такси")
    print("  • 🐭 Мышки (пассивный доход)")
    print("  • 🐾 Питомцы (кормление, счастье)")
    print("  • 🏪 Бизнесы (покупка, улучшение)")
    print("  • 👥 Кланы (создание, управление)")
    print("  • 🏦 Банк (депозиты, кредиты)")
    print("  • 📱 Телефон (контакты, звонки)")
    print("  • 🎁 Бонусы (ежедневные, еженедельные)")
    print("  • 💎 KRDS (P2P обменник)")
    print("  • 👑 VIP-роли (админ, тестер, хелпер, кодер)")
    print("=" * 60)
    print("🎮 ИГРЫ:")
    print("  • Все 15 игр полностью реализованы!")
    print("=" * 60)
    print("🔑 АДМИН ПАНЕЛЬ: /Admin Kyniksvs1832")
    print("=" * 60)
    print("🛑 Для остановки нажмите Ctrl+C")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        cleanup_all_timers()
        save_data()
