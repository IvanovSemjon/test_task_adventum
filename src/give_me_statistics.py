import requests
import pandas as pd
from datetime import datetime


class VKPublicStats:
    def __init__(self, access_token=None):
        self.api_version = "5.131"
        self.access_token = access_token
        print(f"Класс инициализирован с токеном: {access_token[:20] if access_token else 'None'}...")
    
    def get_posts_stats_by_date(self, user_id):
        """Статистика постов по датам и лайкам"""
        print(f"Сбор статистики постов для: {user_id}")
        
        wall_data = self._get_wall_stats(user_id)
        return self._analyze_posts_by_date(wall_data)
    
    def _api_call(self, method, params):
        """API вызов с токеном"""
        params['v'] = self.api_version
        if self.access_token:
            params['access_token'] = self.access_token
            print(f"Используем токен: {self.access_token[:20]}...")
        else:
            print("Токен не передан в API-запрос")
        url = f"https://api.vk.com/method/{method}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def _get_basic_info(self, user_id):
        """Базовая информация"""
        data = self._api_call('users.get', {
            'user_ids': user_id,
            'fields': 'counters,sex,bdate,city,country,photo_max,last_seen,career,education'
        })
        return data.get('response', [{}])[0] if 'response' in data else {}
    
    def _get_wall_stats(self, user_id):
        """Статистика стены"""
        # Пробуем без фильтра owner
        data = self._api_call('wall.get', {
            'owner_id': user_id,
            'count': 100
        })
        
        if 'error' in data:
            print(f"Ошибка API: {data['error']}")
        elif 'response' in data:
            items_count = len(data['response'].get('items', []))
            print(f"Получено {items_count} постов")
        else:
            print(f"Неожиданный ответ: {data}")
            
        return data.get('response', {})
    
    def _analyze_posts_by_date(self, wall_data):
        """Анализ постов по датам и лайкам"""
        if 'items' not in wall_data:
            return {'error': 'Нет доступа к постам или посты отсутствуют'}
        
        posts = wall_data['items']
        posts_stats = []
        
        # Сортировка по времени для расчета промежутков
        posts.sort(key=lambda x: x.get('date', 0))
        
        for i, post in enumerate(posts):
            post_date = datetime.fromtimestamp(post.get('date', 0))
            likes_count = post.get('likes', {}).get('count', 0)
            
            # Промежуток до предыдущего поста в часах
            hours_since_prev = 0
            if i > 0:
                prev_date = datetime.fromtimestamp(posts[i-1].get('date', 0))
                hours_since_prev = (post_date - prev_date).total_seconds() / 3600
            
            posts_stats.append({
                'Дата': post_date.strftime('%Y-%m-%d'),
                'Время': post_date.strftime('%H:%M:%S'),
                'Час_дня': post_date.hour,
                'День_недели': post_date.strftime('%A'),
                'Номер_дня_недели': post_date.weekday(),
                'Лайки': likes_count,
                'Часов_с_предыдущего_поста': round(hours_since_prev, 2),
                'Превью_текста': post.get('text', '')[:50] + '...' if post.get('text') else 'Без текста'
            })
        
        return {
            'total_posts': len(posts_stats),
            'posts_by_date': posts_stats,
            'total_likes': sum(p['Лайки'] for p in posts_stats),
            'avg_likes': sum(p['Лайки'] for p in posts_stats) / max(len(posts_stats), 1)
        }
    
    def _create_test_data(self):
        """Создание тестовых данных"""
        import random
        from datetime import timedelta
        
        posts_stats = []
        base_date = datetime.now() - timedelta(days=365)  # Начинаем с прошлого года
        
        for i in range(50):
            hours_gap = random.randint(6, 168)
            post_date = base_date + timedelta(hours=hours_gap * i)
            
            hour_bonus = 1.5 if 18 <= post_date.hour <= 22 else 1.0
            weekday_bonus = 1.3 if post_date.weekday() in [5, 6] else 1.0
            
            base_likes = random.randint(10, 50)
            likes = int(base_likes * hour_bonus * weekday_bonus)
            
            hours_since_prev = hours_gap if i > 0 else 0
            
            posts_stats.append({
                'Дата': post_date.strftime('%Y-%m-%d'),
                'Время': post_date.strftime('%H:%M:%S'),
                'Час_дня': post_date.hour,
                'День_недели': post_date.strftime('%A'),
                'Номер_дня_недели': post_date.weekday(),
                'Лайки': likes,
                'Часов_с_предыдущего_поста': hours_since_prev,
                'Превью_текста': f'Тестовый пост #{i+1} с длинным текстом для демонстрации'[:50] + '...'
            })
        
        return {
            'total_posts': len(posts_stats),
            'posts_by_date': posts_stats,
            'total_likes': sum(p['Лайки'] for p in posts_stats),
            'avg_likes': sum(p['Лайки'] for p in posts_stats) / len(posts_stats)
        }

if __name__ == "__main__":
    # Загрузка токена из отдельного файла
    try:
        import os
        import sys
        # Добавляем корневую папку проекта в sys.path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        from config import VK_ACCESS_TOKEN
        token = VK_ACCESS_TOKEN if VK_ACCESS_TOKEN != "YOUR_TOKEN_HERE" else None
        print(f"Токен загружен: {token[:20]}..." if token else "Токен не найден")
    except ImportError as e:
        print(f"Ошибка загрузки config.py: {e}")
        token = None
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        token = None
    print(f"Передаем токен в класс: {token[:20] if token else 'None'}...")
    vk_stats = VKPublicStats(access_token=token)
    
    if token:
        print("Используем токен VK API")
    else:
        print("Работаем без токена (ограниченные возможности)")
    
    # С токеном можно получать данные любых открытых профилей
    test_users = ['birulich']
    
    for user_identifier in test_users:
        print(f"\nПроверяем: {user_identifier}")
        stats = vk_stats.get_posts_stats_by_date(user_identifier)
        
        if 'error' not in stats:
            print(f"Успех! Найдено {stats['total_posts']} постов")
            break
        else:
            print(f"Ошибка: {stats['error']}")
    
    if 'error' in stats:
        print("\nСоздаем тестовые данные...")
        stats = vk_stats._create_test_data()
        user_identifier = 'test_data'
    
    if 'error' not in stats:
        # Создание папок если они не существуют
        import os
        os.makedirs('../data', exist_ok=True)
        os.makedirs('../sql', exist_ok=True)
        
        # Создание расширенной таблицы для анализа
        df = pd.DataFrame(stats['posts_by_date'])
        
        print(f"Всего постов: {stats['total_posts']}")
        print(f"Всего лайков: {stats['total_likes']}")
        print(f"Среднее лайков: {stats['avg_likes']:.1f}\n")
        
        # Сохранение в CSV
        try:
            filename_csv = f'../data/{user_identifier}_posts_stats.csv'
            df.to_csv(filename_csv, index=False, encoding='utf-8')
            print(f"CSV сохранен: {filename_csv}")
        except Exception as e:
            print(f"Ошибка сохранения CSV: {e}")
        
        # Сохранение в TXT
        try:
            filename_txt = f'../data/{user_identifier}_posts_stats.txt'
            with open(filename_txt, 'w', encoding='utf-8') as f:
                f.write(df.to_string(index=False))
            print(f"TXT сохранен: {filename_txt}")
        except Exception as e:
            print(f"Ошибка сохранения TXT: {e}")
        if user_identifier != 'test_data':
            print(f"Страница: https://vk.com/{user_identifier}")
        
        # SQL-запросы для анализа
        sql_queries = '''
-- АНАЛИЗ ВЛИЯНИЯ НА КОЛИЧЕСТВО ЛАЙКОВ

-- 1. Влияние времени суток на лайки
SELECT 
    Час_дня,
    COUNT(*) as Количество_постов,
    AVG(Лайки) as Среднее_лайков,
    MAX(Лайки) as Максимум_лайков
FROM posts_stats 
GROUP BY Час_дня 
ORDER BY Среднее_лайков DESC;

-- 2. Влияние дня недели на лайки
SELECT 
    День_недели,
    COUNT(*) as Количество_постов,
    AVG(Лайки) as Среднее_лайков,
    MAX(Лайки) as Максимум_лайков
FROM posts_stats 
GROUP BY День_недели, Номер_дня_недели 
ORDER BY Номер_дня_недели;

-- 3. Влияние промежутка между постами на лайки
SELECT 
    CASE 
        WHEN Часов_с_предыдущего_поста = 0 THEN 'Первый пост'
        WHEN Часов_с_предыдущего_поста < 24 THEN 'Менее суток'
        WHEN Часов_с_предыдущего_поста < 168 THEN '1-7 дней'
        ELSE 'Более недели'
    END as Категория_интервала,
    COUNT(*) as Количество_постов,
    AVG(Лайки) as Среднее_лайков
FROM posts_stats 
GROUP BY Категория_интервала 
ORDER BY Среднее_лайков DESC;

-- 4. Корреляционный анализ
SELECT 
    'Час_дня' as Фактор,
    CORR(Час_дня, Лайки) as Корреляция
FROM posts_stats
UNION ALL
SELECT 
    'Номер_дня_недели' as Фактор,
    CORR(Номер_дня_недели, Лайки) as Корреляция
FROM posts_stats
UNION ALL
SELECT 
    'Часов_с_предыдущего_поста' as Фактор,
    CORR(Часов_с_предыдущего_поста, Лайки) as Корреляция
FROM posts_stats
WHERE Часов_с_предыдущего_поста > 0;
        '''
        
        try:
            with open('../sql/analysis_queries.sql', 'w', encoding='utf-8') as f:
                f.write(sql_queries)
            print(f"SQL-запросы сохранены: ../sql/analysis_queries.sql")
        except Exception as e:
            print(f"Ошибка сохранения SQL: {e}")
        try:
            print("\nСтруктура таблицы:")
            print(df.head().to_string(index=False))
        except Exception as e:
            print(f"Ошибка вывода таблицы: {e}")
        
        print(f"\nАнализ завершен! Проверьте папку data/")