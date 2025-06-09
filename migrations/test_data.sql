-- Вставка пользователей
INSERT INTO users (telegram_id, username, first_name, last_name, company, title, industry_id, is_active) VALUES
(1001, 'ivan_dev', 'Иван', 'Петров', 'TechCorp', 'Backend Developer',1, true),
(1002, 'anna_react', 'Анна', 'Смирнова', 'WebSolutions', 'Frontend Developer',1, true),
(1003, 'alex_devops', 'Алексей', 'Иванов', 'CloudTech', 'DevOps Engineer',1, true),
(1004, 'maria_pm', 'Мария', 'Козлова', 'ProductLab', 'Product Manager',1, true),
(1005, 'dmitry_ml', 'Дмитрий', 'Соколов', 'AITech', 'Data Scientist',1, true),
(1006, 'elena_full', 'Елена', 'Новикова', 'DevStudio', 'Full Stack Developer',1, true),
(1007, 'sergey_java', 'Сергей', 'Морозов', 'EnterpriseSoft', 'Backend Developer',1, true),
(1008, 'olga_ui', 'Ольга', 'Волкова', 'DesignHub', 'Frontend Developer',1, true),
(1009, 'pavel_cloud', 'Павел', 'Кузнецов', 'CloudSystems', 'DevOps Engineer',1, true),
(1010, 'natalia_agile', 'Наталья', 'Лебедева', 'AgileTeam', 'Product Manager',1, true),
(1011, 'artem_python', 'Артем', 'Семенов', 'DataLab', 'Data Scientist',1, true),
(1012, 'kate_js', 'Екатерина', 'Павлова', 'WebDev', 'Full Stack Developer',1, true),
(1013, 'mikhail_rust', 'Михаил', 'Голубев', 'SecureTech', 'Backend Developer',1, true),
(1014, 'sofia_react', 'София', 'Медведева', 'ReactStudio', 'Frontend Developer',1, true),
(1015, 'roman_go', 'Роман', 'Егоров', 'Microservices', 'Backend Developer',1, true);

-- Вставка связей пользователей с тегами (own tags)
INSERT INTO user_tags (user_id, tag_id, tag_type) VALUES
-- Иван Петров (Backend Developer)
(83, 1, 'own'), -- Python
(83, 11, 'own'), -- Backend
(83, 14, 'own'), -- Architecture

-- Анна Смирнова (Frontend Developer)
(84, 2, 'own'), -- JavaScript
(84, 12, 'own'), -- Frontend
(84, 28, 'own'), -- UI/UX Design

-- Алексей Иванов (DevOps Engineer)
(85, 6, 'own'), -- DevOps
(85, 7, 'own'), -- Cloud
(85, 8, 'own'), -- Security

-- Мария Козлова (Product Manager)
(86, 30, 'own'), -- Product Management
(86, 31, 'own'), -- Project Management
(86, 32, 'own'), -- Agile

-- Дмитрий Соколов (Data Scientist)
(87, 15, 'own'), -- Data Science
(87, 16, 'own'), -- Machine Learning
(87, 17, 'own'), -- AI

-- Елена Новикова (Full Stack Developer)
(88, 1, 'own'), -- Python
(88, 2, 'own'), -- JavaScript
(88, 13, 'own'), -- Full Stack

-- Сергей Морозов (Backend Developer)
(89, 3, 'own'), -- Java
(89, 11, 'own'), -- Backend
(89, 14, 'own'), -- Architecture

-- Ольга Волкова (Frontend Developer)
(90, 2, 'own'), -- JavaScript
(90, 12, 'own'), -- Frontend
(90, 28, 'own'), -- UI/UX Design

-- Павел Кузнецов (DevOps Engineer)
(91, 6, 'own'), -- DevOps
(91, 7, 'own'), -- Cloud
(91, 8, 'own'), -- Security

-- Наталья Лебедева (Product Manager)
(92, 30, 'own'), -- Product Management
(92, 31, 'own'), -- Project Management
(92, 32, 'own'), -- Agile

-- Артем Семенов (Data Scientist)
(93, 1, 'own'), -- Python
(93, 15, 'own'), -- Data Science
(93, 16, 'own'), -- Machine Learning

-- Екатерина Павлова (Full Stack Developer)
(94, 2, 'own'), -- JavaScript
(94, 13, 'own'), -- Full Stack
(94, 10, 'own'), -- Web Development


-- Михаил Голубев (Backend Developer)
(95, 5, 'own'), -- Go
(95, 11, 'own'), -- Backend
(95, 8, 'own'), -- Security

-- София Медведева (Frontend Developer)
(96, 2, 'own'), -- JavaScript
(96, 12, 'own'), -- Frontend
(96, 28, 'own'), -- UI/UX Design

-- Роман Егоров (Backend Developer)
(97, 5, 'own'), -- Go
(97, 11, 'own'), -- Backend
(97, 14, 'own'); -- Architecture