# Подробное описание всех столбцов представления
COLUMN_DESCRIPTIONS = {
    "user_id": {
        "name": "user_id",
        "type": "text",
        "description": "Уникальный идентификатор зарегистрированного пользователя на платформе Atlantix. Представляет собой электронную почту, которую указал пользователь при регистрации. Для незарегистрированных посетителей используется device_id.",
        "example": "user@example.com",
        "usage": "Используется как первичный ключ и для соединения с другими таблицами данных пользователей."
    },
    
    "cohort_month": {
        "name": "cohort_month",
        "type": "timestamp",
        "description": "Месяц, когда пользователь впервые посетил платформу. Используется для когортного анализа, позволяет группировать пользователей по периоду их первого взаимодействия с платформой.",
        "example": "2025-01-01 00:00:00",
        "usage": "Для группировки используйте DATE_TRUNC('month', cohort_month) или DATE_TRUNC('week', cohort_month)."
    },
    
    "user_type": {
        "name": "user_type",
        "type": "text",
        "description": "Категория пользователя, определяющая его статус на платформе. Включает три возможных значения: 'Подписчик' (платящий клиент), 'Активированный' (пользователь, который активно использует функционал, но не платит), 'Заинтересованный' (пользователь, который только просматривает информацию).",
        "example": "Подписчик, Активированный, Заинтересованный",
        "usage": "Используется для сегментации пользователей и анализа конверсии между разными категориями."
    },
    
    "technology_views": {
        "name": "technology_views",
        "type": "bigint",
        "description": "Общее количество просмотров страниц 'технологий' пользователем. Технологии - это основной контент платформы Atlantix, представляющий различные инновационные решения и разработки.",
        "example": "42",
        "usage": "Показатель интереса пользователя к технологическому контенту платформы."
    },
    
    "technology_sessions": {
        "name": "technology_sessions",
        "type": "bigint",
        "description": "Количество уникальных сессий, в которых пользователь просматривал страницы 'технологий'. Отличается от technology_views тем, что учитывает не каждый просмотр, а каждую сессию с просмотрами.",
        "example": "15",
        "usage": "Показывает частоту возвращения пользователя к технологическому контенту."
    },
    
    "business_plan_clicks": {
        "name": "business_plan_clicks",
        "type": "bigint",
        "description": "Количество просмотров страницы 'бизнес-планов'. Бизнес-планы - это страницы, содержащие детальную информацию о возможностях коммерциализации технологий.",
        "example": "8",
        "usage": "Индикатор заинтересованности пользователя в коммерческих аспектах технологий."
    },
    
    "custom_business_plan_views": {
        "name": "custom_business_plan_views",
        "type": "bigint",
        "description": "Количество просмотров страницы 'Custom Business Plans'. Это специальная страница, где пользователи могут создавать персонализированные бизнес-планы для технологий.",
        "example": "3",
        "usage": "Показатель глубокой заинтересованности в коммерциализации технологий."
    },
    
    "discovery_views": {
        "name": "discovery_views",
        "type": "bigint",
        "description": "Количество просмотров страницы 'Discover'. Это основная страница для поиска и обнаружения новых технологий на платформе.",
        "example": "25",
        "usage": "Индикатор исследовательской активности пользователя на платформе."
    },
    
    "collection_views": {
        "name": "collection_views",
        "type": "bigint",
        "description": "Количество просмотров 'Коллекций'. Коллекции - это подборки технологий, объединенные по определенной теме или области применения.",
        "example": "12",
        "usage": "Показывает интерес пользователя к тематическим группам технологий."
    },
    
    "search_queries": {
        "name": "search_queries",
        "type": "bigint",
        "description": "Количество поисковых запросов, выполненных пользователем на платформе. Учитывает все запросы пользователя в поисковой строке.",
        "example": "18",
        "usage": "Показатель активности пользователя в поиске определенных технологий или информации."
    },
    
    "total_sessions": {
        "name": "total_sessions",
        "type": "bigint",
        "description": "Общее количество сессий пользователя на платформе. Сессия - это период активности пользователя на сайте без длительных перерывов.",
        "example": "30",
        "usage": "Базовый показатель вовлеченности, отражающий частоту возвращения пользователя на платформу."
    },
    
    "active_days": {
        "name": "active_days",
        "type": "bigint",
        "description": "Количество уникальных дней, в которые пользователь был активен на платформе. Показывает регулярность использования платформы.",
        "example": "14",
        "usage": "Индикатор регулярности взаимодействия с платформой."
    },
    
    "avg_session_minutes": {
        "name": "avg_session_minutes",
        "type": "numeric",
        "description": "Средняя продолжительность сессии пользователя в минутах. Измеряется как среднее время между первым и последним действием в рамках одной сессии.",
        "example": "12.5",
        "usage": "Показатель глубины вовлеченности пользователя в каждое посещение платформы."
    },
    
    "total_platform_minutes": {
        "name": "total_platform_minutes",
        "type": "numeric",
        "description": "Общее время в минутах, проведенное пользователем на платформе за все время. Сумма продолжительностей всех сессий пользователя.",
        "example": "375.0",
        "usage": "Комплексный показатель общей вовлеченности пользователя."
    },
    
    "total_discover_minutes": {
        "name": "total_discover_minutes",
        "type": "numeric",
        "description": "Общее время в минутах, проведенное пользователем на странице 'Discover'. Показывает, сколько времени пользователь потратил на поиск и изучение технологий.",
        "example": "120.0",
        "usage": "Индикатор интереса к исследованию доступных технологий."
    },
    
    "minutes_to_first_tech_view": {
        "name": "minutes_to_first_tech_view",
        "type": "numeric",
        "description": "Время в минутах от первого визита пользователя на платформу до первого просмотра страницы 'технологии'. Показывает, как быстро пользователь находит интересующий его контент.",
        "example": "8.5",
        "usage": "Используется для анализа эффективности навигации и UX платформы."
    },
    
    "minutes_to_first_favorites": {
        "name": "minutes_to_first_favorites",
        "type": "numeric",
        "description": "Время в минутах от первого визита пользователя на платформу до первого добавления технологии в избранное. Показывает скорость нахождения релевантного контента.",
        "example": "35.2",
        "usage": "Индикатор скорости принятия решения пользователем о ценности контента."
    },
    
    "avg_discover_minutes_per_session": {
        "name": "avg_discover_minutes_per_session",
        "type": "numeric",
        "description": "Среднее время в минутах, проведенное на странице 'Discover' за одну сессию. Показывает глубину исследования технологий в рамках одного посещения.",
        "example": "5.3",
        "usage": "Используется для оценки качества взаимодействия с поисковым функционалом."
    },
    
    "avg_discover_minutes_per_month": {
        "name": "avg_discover_minutes_per_month",
        "type": "numeric",
        "description": "Среднее время в минутах, проведенное на странице 'Discover' в месяц. Нормализует показатель avg_discover_minutes_per_session с учетом активности в разные месяцы.",
        "example": "42.1",
        "usage": "Показатель регулярности и интенсивности исследования технологий."
    },
    
    "avg_tech_views_per_session": {
        "name": "avg_tech_views_per_session",
        "type": "numeric",
        "description": "Среднее количество просмотров страниц 'технологий' за одну сессию. Рассчитывается как отношение technology_views к total_sessions.",
        "example": "1.4",
        "usage": "Показатель интенсивности исследования технологического контента за одно посещение."
    },
    
    "avg_business_plan_clicks_per_session": {
        "name": "avg_business_plan_clicks_per_session",
        "type": "numeric",
        "description": "Среднее количество кликов на страницы 'бизнес-планов' за одну сессию. Рассчитывается как отношение business_plan_clicks к total_sessions.",
        "example": "0.3",
        "usage": "Индикатор заинтересованности в коммерческой информации в каждом посещении."
    },
    
    "avg_search_queries_per_session": {
        "name": "avg_search_queries_per_session",
        "type": "numeric",
        "description": "Среднее количество поисковых запросов за одну сессию. Рассчитывается как отношение search_queries к total_sessions.",
        "example": "0.6",
        "usage": "Показатель интенсивности использования поиска во время посещения платформы."
    },
    
    "is_interested_user": {
        "name": "is_interested_user",
        "type": "integer",
        "description": "Флаг (1/null), указывающий, является ли пользователь 'заинтересованным'. Заинтересованный пользователь - это тот, кто просматривал страницы технологий, но не добавлял их в избранное и не оформлял подписку.",
        "example": "1",
        "usage": "Используется для фильтрации и подсчета пользователей на первом уровне вовлеченности."
    },
    
    "is_activated_user": {
        "name": "is_activated_user",
        "type": "integer",
        "description": "Флаг (1/null), указывающий, является ли пользователь 'активированным'. Активированный пользователь - это тот, кто просматривал технологии и добавлял их в избранное, но не оформлял подписку.",
        "example": "1",
        "usage": "Используется для фильтрации и подсчета пользователей на втором уровне вовлеченности."
    },
    
    "is_subscriber": {
        "name": "is_subscriber",
        "type": "integer",
        "description": "Флаг (1/null), указывающий, является ли пользователь подписчиком. Подписчик - это пользователь с активной платной подпиской на платформе.",
        "example": "1",
        "usage": "Используется для фильтрации и подсчета платящих пользователей, высший уровень вовлеченности."
    }
}

# Описание представления для использования в промптах
VIEW_DESCRIPTION = """
Представление test_staging.user_metrics_dashboard_optimized содержит детальную информацию о пользовательской активности на платформе Atlantix (https://platform.atlantix.cc). 
Оно объединяет данные о первом посещении пользователей, их типе, метриках активности и вовлеченности.
"""

# Типовые шаблоны запросов
COMMON_QUERIES = [
    {
        "name": "Активные пользователи по месяцам",
        "sql": """
            SELECT DATE_TRUNC('month', cohort_month) AS month,
                   COUNT(DISTINCT user_id) AS active_users
            FROM test_staging.user_metrics_dashboard_optimized
            WHERE cohort_month BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY month
            ORDER BY month
        """,
        "visualization_type": "line",
        "keywords": ["активные пользователи", "месяц", "динамика", "количество"]
    },
    {
        "name": "Распределение пользователей по типам",
        "sql": """
            SELECT user_type, COUNT(DISTINCT user_id) AS user_count
            FROM test_staging.user_metrics_dashboard_optimized
            WHERE cohort_month BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY user_type
            ORDER BY user_count DESC
        """,
        "visualization_type": "pie",
        "keywords": ["тип", "пользователи", "распределение", "доля"]
    },
    {
        "name": "Среднее время сессии по месяцам",
        "sql": """
            SELECT DATE_TRUNC('month', cohort_month) AS month,
                   AVG(avg_session_minutes) AS avg_time
            FROM test_staging.user_metrics_dashboard_optimized
            WHERE cohort_month BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY month
            ORDER BY month
        """,
        "visualization_type": "line",
        "keywords": ["время", "сессия", "средний", "минут"]
    },
    {
        "name": "Вовлеченность по типам пользователей",
        "sql": """
            SELECT user_type,
                   AVG(total_sessions) AS avg_sessions,
                   AVG(active_days) AS avg_active_days,
                   AVG(avg_session_minutes) AS avg_session_time
            FROM test_staging.user_metrics_dashboard_optimized
            WHERE cohort_month BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY user_type
            ORDER BY user_type
        """,
        "visualization_type": "bar",
        "keywords": ["вовлеченность", "сравнение", "тип пользователей"]
    }
]

# Полный словарь метаданных представления
USER_METRICS_DASHBOARD_SCHEMA = {
    "name": "test_staging.user_metrics_dashboard_optimized",
    "description": "Представление содержит детальную информацию о пользовательской активности на платформе Atlantix",
    "columns": [
        {"name": "user_id", "type": "text", "nullable": False, 
         "description": "Уникальный идентификатор зарегистрированного пользователя"},
        {"name": "cohort_month", "type": "timestamp", "nullable": True, 
         "description": "Месяц, когда пользователь впервые посетил платформу (для когортного анализа)"},
        {"name": "user_type", "type": "text", "nullable": True, 
         "description": "Категория пользователя ('Подписчик', 'Активированный', 'Заинтересованный')"},
        {"name": "technology_views", "type": "bigint", "nullable": True, 
         "description": "Количество просмотров страниц 'технологий'"},
        {"name": "technology_sessions", "type": "bigint", "nullable": True, 
         "description": "Количество уникальных сессий с просмотрами страниц 'технологий'"},
        {"name": "business_plan_clicks", "type": "bigint", "nullable": True, 
         "description": "Количество просмотров страницы 'бизнес-планов'"},
        {"name": "custom_business_plan_views", "type": "bigint", "nullable": True, 
         "description": "Количество просмотров страницы 'Custom Business Plans'"},
        {"name": "discovery_views", "type": "bigint", "nullable": True, 
         "description": "Количество просмотров страницы 'Discover'"},
        {"name": "collection_views", "type": "bigint", "nullable": True, 
         "description": "Количество просмотров 'Коллекций'"},
        {"name": "search_queries", "type": "bigint", "nullable": True, 
         "description": "Количество поисковых запросов"},
        {"name": "total_sessions", "type": "bigint", "nullable": True, 
         "description": "Общее количество сессий пользователя"},
        {"name": "active_days", "type": "bigint", "nullable": True, 
         "description": "Количество уникальных дней, в которые пользователь был активен"},
    ],
    "common_queries": [
        {
            "name": "Активные пользователи по месяцам",
            "sql": """
                SELECT DATE_TRUNC('month', cohort_month) AS month,
                       COUNT(DISTINCT user_id) AS active_users
                FROM test_staging.user_metrics_dashboard_optimized
                WHERE cohort_month BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY month
                ORDER BY month
            """,
            "visualization_type": "line",
            "keywords": ["активные пользователи", "месяц", "динамика"]
        },
    ]
}