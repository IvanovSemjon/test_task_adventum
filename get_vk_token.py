import webbrowser
import requests

def get_vk_token():
    """Простой способ получения токена VK для публичных данных"""
    
    print("=" * 60)
    print("ПОЛУЧЕНИЕ ТОКЕНА VK ДЛЯ ПУБЛИЧНЫХ ДАННЫХ")
    print("=" * 60)
    
    # Используем готовое приложение VK Admin
    app_id = "6121396"  # ID официального приложения VK Admin
    
    # Минимальные права для чтения публичных данных
    scopes = "wall,friends,groups"
    
    # URL для получения токена
    auth_url = (
        f"https://oauth.vk.com/authorize?"
        f"client_id={app_id}&"
        f"display=page&"
        f"redirect_uri=https://oauth.vk.com/blank.html&"
        f"scope={scopes}&"
        f"response_type=token&"
        f"v=5.131"
    )
    
    print("1. Открываю браузер для авторизации...")
    webbrowser.open(auth_url)
    
    print("\n2. В браузере:")
    print("   - Войдите в VK (если не авторизованы)")
    print("   - Нажмите 'Разрешить'")
    print("   - Скопируйте токен из адресной строки")
    
    print("\n3. Адрес будет выглядеть так:")
    print("   https://oauth.vk.com/blank.html#access_token=vk1.a.ABC123...")
    print("   Скопируйте только часть после access_token= до символа &")
    
    print("\n" + "=" * 60)
    
    # Получаем токен от пользователя
    token = input("Вставьте токен: ").strip()
    
    if not token:
        print("❌ Токен не введен")
        return None
    
    # Проверяем токен
    print("\n4. Проверяю токен...")
    if verify_token(token):
        save_token(token)
        return token
    else:
        print("❌ Токен недействителен")
        return None

def verify_token(token):
    """Проверка токена"""
    try:
        url = "https://api.vk.com/method/users.get"
        params = {
            'access_token': token,
            'v': '5.131'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'response' in data:
            user = data['response'][0]
            print(f"✅ Токен работает! Пользователь: {user['first_name']} {user['last_name']}")
            return True
        else:
            error = data.get('error', {})
            print(f"❌ Ошибка: {error.get('error_msg', 'Неизвестная ошибка')}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

def save_token(token):
    """Сохранение токена в config.py"""
    config_content = f'''# Конфигурация для VK API
VK_ACCESS_TOKEN = "{token}"'''
    
    try:
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f"✅ Токен сохранен в config.py")
        print(f"   Длина: {len(token)} символов")
        print(f"   Начало: {token[:30]}...")
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

if __name__ == "__main__":
    print("🚀 Получение токена VK для анализа публичных страниц")
    token = get_vk_token()
    
    if token:
        print("\n🎉 Готово! Теперь можете запускать анализ:")
        print("   cd src")
        print("   python give_me_statistics.py")
    else:
        print("\n❌ Не удалось получить токен. Попробуйте еще раз.")