create table items (
    id serial primary key,
    title varchar(80) not null,
    description text not null,
    category varchar(80) not null,
    UNIQUE(title, category)
);

create view categories as
    select DISTINCT category from items