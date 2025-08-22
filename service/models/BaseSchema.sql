create table roles
(
    role_id   uuid default gen_random_uuid() not null
        primary key,
    role_name varchar(50)                    not null
        unique
);

create table users
(
    user_id       uuid      default gen_random_uuid() not null
        primary key,
    full_name     varchar(150)                        not null,
    email         varchar(150)                        not null
        unique,
    password_hash text                                not null,
    role_id       uuid
                                                      references roles
                                                          on delete set null,
    created_at    timestamp default CURRENT_TIMESTAMP
);

create table properties
(
    property_id uuid  default gen_random_uuid() not null
        primary key,
    survey_no   varchar(100),
    metadata    jsonb default '{}'::jsonb,
    state       varchar(100),
    district    varchar(100),
    tahasil     varchar(100),
    city        varchar(100),
    village     varchar(100),
    locality    locality_type
);

create table documents
(
    document_id          uuid      default gen_random_uuid() not null
        primary key,
    file_uri             text                                not null,
    uploaded_by          uuid
                                                             references users
                                                                 on delete set null,
    uploaded_at          timestamp default CURRENT_TIMESTAMP,
    doc_no               varchar(100),
    dname                varchar(255),
    rdate                date,
    sro_name             varchar(255),
    property_description text,
    sro_code             varchar(50),
    status               varchar(50),
    extra_data           jsonb     default '{}'::jsonb,
    property_id          uuid
        references properties
            on delete cascade,
    seller_name          text[],
    purchaser_name       text[]
);

create table jobs
(
    job_id        uuid       default gen_random_uuid() not null
        primary key,
    document_id   uuid
        references documents
            on delete cascade,
    job_type      varchar(50)                          not null,
    status        job_status default 'scheduled'::job_status,
    created_at    timestamp  default CURRENT_TIMESTAMP,
    started_at    timestamp,
    finished_at   timestamp,
    result        jsonb      default '{}'::jsonb,
    error_message text,
    property_id   uuid
        references properties
            on delete cascade
);

create table parties
(
    party_id     uuid  default gen_random_uuid() not null
        primary key,
    name         varchar(150)                    not null,
    contact_info jsonb default '{}'::jsonb,
    state        varchar(100),
    district     varchar(100),
    tahasil      varchar(100),
    city         varchar(100),
    village      varchar(100),
    pan          varchar(100)
);

create table transactions
(
    transaction_id   uuid      default gen_random_uuid() not null
        primary key,
    property_id      uuid
        references properties
            on delete cascade,
    seller_id        uuid
        references parties,
    purchaser_id     uuid
        references parties,
    transaction_date date                                not null,
    amount           numeric(18, 2),
    created_at       timestamp default CURRENT_TIMESTAMP,
    document_id      uuid
                                                         references documents
                                                             on delete set null
);
