create table items (
    id serial primary key,
    title varchar(80) not null,
    description text not null,
    category varchar(80) not null,
    inserted_at timestamp not null default now(),
    UNIQUE(title, category)
);

create view categories as
    select DISTINCT category from items;