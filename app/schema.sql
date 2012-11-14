drop table peeps cascade;
drop table users cascade;
drop table follow cascade;

create table users (
    id serial primary key,
    username text unique not null
);

create table peeps (
    id serial primary key,
    userid integer REFERENCES users,
    message_text text not null,
    t timestamp default current_timestamp
);


create table follow (
    follower integer REFERENCES users,
    followed integer REFERENCES users,
    UNIQUE (follower, followed)
);
