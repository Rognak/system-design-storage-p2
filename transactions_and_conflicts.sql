-- СЦЕНАРИЙ 1.
-- СОЗДАНИЕ ПРОЕКТА И ДОБАВЛЕНИЕ ВЛАДЕЛЬЦА В УЧАСТНИКИ
--
-- Требование:
-- проект и запись в project_members должны появиться вместе.
--
-- Если второй INSERT завершится ошибкой, вся транзакция
-- откатывается, и проект не останется без участника.
--
-- Уровень изоляции:
-- READ COMMITTED.

BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;

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
    'Учебный проект',
    FALSE,
    NOW(),
    NOW()
);

INSERT INTO project_members (
    project_id,
    user_id
)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111'
);

COMMIT;


-- СЦЕНАРИЙ 2.
-- ОБНОВЛЕНИЕ ЗАТРАЧЕННОГО И ОСТАВШЕГОСЯ ВРЕМЕНИ
--
-- Проблема:
-- две транзакции могут одновременно прочитать одну и ту же
-- запись оценки и попытаться ее изменить.
--
-- Возможный конфликт:
-- lost update — одно изменение может перезаписать другое.
--
-- Решение:
-- SELECT ... FOR UPDATE блокирует выбранную строку до конца
-- транзакции. Вторая транзакция будет ждать освобождения строки.
--
-- Уровень изоляции:
-- READ COMMITTED + блокировка строки FOR UPDATE.

BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;

SELECT
    hours_spent,
    hours_remain
FROM work_item_estim
WHERE work_item_id = '33333333-3333-3333-3333-333333333333'
FOR UPDATE;

UPDATE work_item_estim
SET
    hours_spent = COALESCE(hours_spent, 0) + 2,
    hours_remain = GREATEST(COALESCE(hours_remain, 0) - 2, 0)
WHERE work_item_id = '33333333-3333-3333-3333-333333333333';

UPDATE work_items
SET updated_at = NOW()
WHERE id = '33333333-3333-3333-3333-333333333333';

COMMIT;


-- СЦЕНАРИЙ 3.
-- УДАЛЕНИЕ УЧАСТНИКА С ПРОВЕРКОЙ, ЧТО ПРОЕКТ НЕ ОСТАНЕТСЯ БЕЗ УЧАСТНИКОВ
--
-- Проблема:
-- если в проекте два участника, две параллельные транзакции
-- могут одновременно увидеть COUNT(*) = 2 и удалить по одному
-- участнику. В результате участников станет 0.
--
-- Решение:
-- использовать SERIALIZABLE.

BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

DELETE FROM project_members
WHERE project_id = '22222222-2222-2222-2222-222222222222'
  AND user_id = '11111111-1111-1111-1111-111111111111'
  AND (
      SELECT COUNT(*)
      FROM project_members
      WHERE project_id = '22222222-2222-2222-2222-222222222222'
  ) > 1
RETURNING user_id;

COMMIT;