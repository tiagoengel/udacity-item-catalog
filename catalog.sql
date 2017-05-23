DROP TABLE if exists items CASCADE;
DROP TABLE if exists categories CASCADE;
DROP TABLE if exists users CASCADE;

create table users (
    id serial primary key,
    provider varchar(80) not null,
    provider_user_id varchar(80) not null,
    inserted_at timestamp not null default now(),
    UNIQUE(provider, provider_user_id)
);

create table categories (
    id serial primary key,
    description text not null,
    inserted_at timestamp not null default now()
);

create table items (
    id serial primary key,
    title varchar(80) not null,
    description text not null,
    user_id integer references users(id),
    category_id integer references categories(id),
    inserted_at timestamp not null default now(),
    UNIQUE(title, category_id)
);