-- Create industries table
CREATE TABLE IF NOT EXISTS industries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    company VARCHAR(255),
    title VARCHAR(255),
    industry_id INTEGER REFERENCES industries(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create tags table
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create industry_tags association table
CREATE TABLE IF NOT EXISTS industry_tags (
    industry_id INTEGER REFERENCES industries(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (industry_id, tag_id)
);

-- Create user_tags association table
CREATE TABLE IF NOT EXISTS user_tags (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    tag_type VARCHAR(10) NOT NULL DEFAULT 'own' CHECK (tag_type IN ('own', 'search')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, tag_id)
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_industries_updated_at
    BEFORE UPDATE ON industries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tags_updated_at
    BEFORE UPDATE ON tags
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_industries_name ON industries(name);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_user_tags_tag_type ON user_tags(tag_type);

-- Insert predefined industries
INSERT INTO industries (name, description) VALUES
    ('IT и разработка', 'Информационные технологии и разработка программного обеспечения'),
    ('Маркетинг и реклама', 'Маркетинг, реклама и продвижение'),
    ('Продажи', 'Продажи и бизнес-развитие'),
    ('Финансы и банки', 'Финансы, банковское дело и инвестиции'),
    ('HR и рекрутинг', 'Управление персоналом и рекрутинг'),
    ('Дизайн', 'Графический дизайн и UX/UI'),
    ('Медиа и коммуникации', 'Медиа, PR и коммуникации'),
    ('Образование', 'Образование и обучение'),
    ('Медицина', 'Медицина и здравоохранение'),
    ('Другое', 'Другие индустрии')
ON CONFLICT (name) DO NOTHING;

-- Insert predefined tags
INSERT INTO tags (name, description) VALUES
    -- IT и разработка
    ('Python', 'Язык программирования Python'),
    ('JavaScript', 'Язык программирования JavaScript'),
    ('Java', 'Язык программирования Java'),
    ('C++', 'Язык программирования C++'),
    ('Go', 'Язык программирования Go'),
    ('DevOps', 'DevOps практики и инструменты'),
    ('Cloud', 'Облачные технологии'),
    ('Security', 'Информационная безопасность'),
    ('Mobile Development', 'Мобильная разработка'),
    ('Web Development', 'Веб-разработка'),
    ('Backend', 'Бэкенд разработка'),
    ('Frontend', 'Фронтенд разработка'),
    ('Full Stack', 'Full Stack разработка'),
    ('Architecture', 'Архитектура ПО'),
    ('Data Science', 'Наука о данных'),
    ('Machine Learning', 'Машинное обучение'),
    ('AI', 'Искусственный интеллект'),
    
    -- Маркетинг и реклама
    ('Digital Marketing', 'Цифровой маркетинг'),
    ('Content Marketing', 'Контент-маркетинг'),
    ('SEO', 'Поисковая оптимизация'),
    ('Branding', 'Брендинг'),
    
    -- Продажи
    ('Sales', 'Продажи'),
    ('Business Development', 'Развитие бизнеса'),
    ('Partnerships', 'Партнерства'),
    
    -- HR и рекрутинг
    ('HR', 'Управление персоналом'),
    ('Recruitment', 'Рекрутинг'),
    ('Talent Management', 'Управление талантами'),
    
    -- Дизайн
    ('UI/UX Design', 'UI/UX дизайн'),
    ('Graphic Design', 'Графический дизайн'),
    
    -- Управление проектами
    ('Product Management', 'Управление продуктом'),
    ('Project Management', 'Управление проектами'),
    ('Agile', 'Agile методологии')
ON CONFLICT (name) DO NOTHING;

-- Link tags to industries
INSERT INTO industry_tags (industry_id, tag_id)
SELECT i.id, t.id
FROM industries i
CROSS JOIN tags t
WHERE 
    (i.name = 'IT и разработка' AND t.name IN (
        'Python', 'JavaScript', 'Java', 'C++', 'Go',
        'DevOps', 'Cloud', 'Security',
        'Mobile Development', 'Web Development', 'Backend',
        'Frontend', 'Full Stack', 'Architecture',
        'Data Science', 'Machine Learning', 'AI'
    ))
    OR (i.name = 'Маркетинг и реклама' AND t.name IN (
        'Digital Marketing', 'Content Marketing', 'SEO', 'Branding'
    ))
    OR (i.name = 'Продажи' AND t.name IN (
        'Sales', 'Business Development', 'Partnerships'
    ))
    OR (i.name = 'HR и рекрутинг' AND t.name IN (
        'HR', 'Recruitment', 'Talent Management'
    ))
    OR (i.name = 'Дизайн' AND t.name IN (
        'UI/UX Design', 'Graphic Design'
    ))
    OR (i.name = 'IT и разработка' AND t.name IN (
        'Product Management', 'Project Management', 'Agile'
    ))
ON CONFLICT (industry_id, tag_id) DO NOTHING;