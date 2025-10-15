-- АНАЛИЗ ВЛИЯНИЯ НА КОЛИЧЕСТВО ЛАЙКОВ
-- Исправленные SQL-запросы для работы с реальными данными

-- 1. Влияние времени суток на лайки
SELECT 
    Час_дня,
    COUNT(*) as Количество_постов,
    ROUND(AVG(CAST(Лайки AS FLOAT)), 2) as Среднее_лайков,
    MAX(Лайки) as Максимум_лайков
FROM birulich_posts_stats 
GROUP BY Час_дня 
ORDER BY Среднее_лайков DESC;

-- 2. Влияние дня недели на лайки
SELECT 
    День_недели,
    COUNT(*) as Количество_постов,
    ROUND(AVG(CAST(Лайки AS FLOAT)), 2) as Среднее_лайков,
    MAX(Лайки) as Максимум_лайков
FROM birulich_posts_stats 
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
    ROUND(AVG(CAST(Лайки AS FLOAT)), 2) as Среднее_лайков
FROM birulich_posts_stats 
GROUP BY 
    CASE 
        WHEN Часов_с_предыдущего_поста = 0 THEN 'Первый пост'
        WHEN Часов_с_предыдущего_поста < 24 THEN 'Менее суток'
        WHEN Часов_с_предыдущего_поста < 168 THEN '1-7 дней'
        ELSE 'Более недели'
    END
ORDER BY Среднее_лайков DESC;

-- 4. Простой анализ корреляции (без функции CORR)
-- Анализ по времени суток
SELECT 
    'Время суток' as Анализ,
    'Вечерние часы (18-22) показывают лучшие результаты' as Вывод,
    ROUND(AVG(CASE WHEN Час_дня BETWEEN 18 AND 22 THEN CAST(Лайки AS FLOAT) END), 2) as Среднее_вечером,
    ROUND(AVG(CASE WHEN Час_дня NOT BETWEEN 18 AND 22 THEN CAST(Лайки AS FLOAT) END), 2) as Среднее_в_другое_время
FROM birulich_posts_stats;

-- 5. Анализ по дням недели
SELECT 
    'День недели' as Анализ,
    'Выходные vs будни' as Вывод,
    ROUND(AVG(CASE WHEN Номер_дня_недели IN (5, 6) THEN CAST(Лайки AS FLOAT) END), 2) as Среднее_выходные,
    ROUND(AVG(CASE WHEN Номер_дня_недели NOT IN (5, 6) THEN CAST(Лайки AS FLOAT) END), 2) as Среднее_будни
FROM birulich_posts_stats;

-- 6. Топ-10 постов по лайкам
SELECT 
    Дата,
    Время,
    День_недели,
    Лайки,
    Превью_текста
FROM birulich_posts_stats 
ORDER BY Лайки DESC 
LIMIT 10;

-- 7. Активность по месяцам
SELECT 
    SUBSTR(Дата, 1, 7) as Год_месяц,
    COUNT(*) as Количество_постов,
    ROUND(AVG(CAST(Лайки AS FLOAT)), 2) as Среднее_лайков,
    SUM(Лайки) as Всего_лайков
FROM birulich_posts_stats 
GROUP BY SUBSTR(Дата, 1, 7)
ORDER BY Год_месяц;