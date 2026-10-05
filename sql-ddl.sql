CREATE TYPE work_item_status AS ENUM (
    'todo',
    'in_progress',
    'done'
);


CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);


CREATE TABLE projects (
    id UUID PRIMARY KEY,
    owner_id UUID NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    FOREIGN KEY (owner_id)
        REFERENCES users(user_id)
);


CREATE TABLE project_members (
    project_id UUID NOT NULL,
    user_id UUID NOT NULL,

    PRIMARY KEY (project_id, user_id),

    FOREIGN KEY (project_id)
        REFERENCES projects(id),

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
);


CREATE TABLE work_items (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL,
    creator_id UUID NOT NULL,
    human_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status work_item_status NOT NULL,
    extrafields JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    FOREIGN KEY (project_id)
        REFERENCES projects(id),

    FOREIGN KEY (creator_id)
        REFERENCES users(user_id),

    UNIQUE (project_id, human_id)
);


CREATE INDEX idx_work_items_project
    ON work_items(project_id);


CREATE INDEX idx_work_items_creator
    ON work_items(creator_id);


CREATE INDEX idx_work_items_status
    ON work_items(status);


CREATE INDEX idx_work_items_extrafields
    ON work_items
    USING GIN (extrafields);


CREATE TABLE work_item_estim (
    work_item_id UUID PRIMARY KEY,
    storypoints INTEGER,
    hours_estim INTEGER,
    hours_spent INTEGER,
    hours_remain INTEGER,

    FOREIGN KEY (work_item_id)
        REFERENCES work_items(id),

    CHECK (storypoints IS NULL OR storypoints >= 0),
    CHECK (hours_estim IS NULL OR hours_estim >= 0),
    CHECK (hours_spent IS NULL OR hours_spent >= 0),
    CHECK (hours_remain IS NULL OR hours_remain >= 0)
);


CREATE TABLE comments (
    id UUID PRIMARY KEY,
    work_item_id UUID NOT NULL,
    author_id UUID NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    FOREIGN KEY (work_item_id)
        REFERENCES work_items(id),

    FOREIGN KEY (author_id)
        REFERENCES users(user_id)
);


CREATE INDEX idx_comments_work_item
    ON comments(work_item_id);