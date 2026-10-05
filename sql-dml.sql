-- 1. INSERT: добавить пользователя
INSERT INTO users (
    user_id,
    username,
    email,
    hashed_password,
    created_at,
    updated_at
)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    'alice',
    'alice@example.com',
    'hashed_password_here',
    NOW(),
    NOW()
);


-- 2. INSERT: создать проект
INSERT INTO projects (
    id,
    owner_id,
    title,
    description,
    is_deleted,
    created_at,
    updated_at
)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111',
    'Task Tracker',
    'Учебный проект трекера задач',
    FALSE,
    NOW(),
    NOW()
);


-- 3. INSERT: добавить пользователя в проект
INSERT INTO project_members (
    project_id,
    user_id
)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111'
);


-- 4. INSERT: создать задачу
INSERT INTO work_items (
    id,
    project_id,
    creator_id,
    human_id,
    title,
    description,
    status,
    extrafields,
    created_at,
    updated_at
)
VALUES (
    '33333333-3333-3333-3333-333333333333',
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111',
    'TASK-1',
    'Сделать авторизацию',
    'Реализовать вход пользователя',
    'todo',
    '{"priority": "high", "type": "backend"}'::jsonb,
    NOW(),
    NOW()
);


-- 5. SELECT: получить все задачи проекта
SELECT
    id,
    human_id,
    title,
    status,
    created_at
FROM work_items
WHERE project_id = '22222222-2222-2222-2222-222222222222'
ORDER BY created_at DESC;


-- 6. SELECT + JSONB:
-- найти задачи с высоким приоритетом
SELECT
    id,
    human_id,
    title,
    extrafields
FROM work_items
WHERE extrafields @> '{"priority": "high"}'::jsonb;


-- 7. UPDATE: изменить статус задачи
UPDATE work_items
SET
    status = 'in_progress',
    updated_at = NOW()
WHERE id = '33333333-3333-3333-3333-333333333333';


-- 8. INSERT: добавить оценку задачи
INSERT INTO work_item_estim (
    work_item_id,
    storypoints,
    hours_estim,
    hours_spent,
    hours_remain
)
VALUES (
    '33333333-3333-3333-3333-333333333333',
    5,
    8,
    2,
    6
);


-- 9. JOIN:
-- получить задачу вместе с автором и оценкой
SELECT
    wi.human_id,
    wi.title,
    wi.status,
    u.username AS creator,
    e.storypoints,
    e.hours_estim,
    e.hours_spent,
    e.hours_remain
FROM work_items wi
JOIN users u
    ON u.user_id = wi.creator_id
LEFT JOIN work_item_estim e
    ON e.work_item_id = wi.id
WHERE wi.id = '33333333-3333-3333-3333-333333333333';


-- 10. INSERT: добавить комментарий к задаче
INSERT INTO comments (
    id,
    work_item_id,
    author_id,
    message,
    created_at,
    updated_at
)
VALUES (
    '44444444-4444-4444-4444-444444444444',
    '33333333-3333-3333-3333-333333333333',
    '11111111-1111-1111-1111-111111111111',
    'Начал работу над задачей',
    NOW(),
    NOW()
);


-- 11. JOIN:
-- получить комментарии задачи вместе с именем автора
SELECT
    c.message,
    c.created_at,
    u.username
FROM comments c
JOIN users u
    ON u.user_id = c.author_id
WHERE c.work_item_id = '33333333-3333-3333-3333-333333333333'
ORDER BY c.created_at;


-- 12. DELETE:
-- удалить комментарий
DELETE FROM comments
WHERE id = '44444444-4444-4444-4444-444444444444';


-- 13. UPDATE:
-- soft delete проекта
UPDATE projects
SET
    is_deleted = TRUE,
    updated_at = NOW()
WHERE id = '22222222-2222-2222-2222-222222222222';


-- 14. SELECT:
-- получить все активные проекты пользователя
SELECT
    id,
    title,
    description,
    created_at
FROM projects
WHERE owner_id = '11111111-1111-1111-1111-111111111111'
  AND is_deleted = FALSE
ORDER BY created_at DESC;