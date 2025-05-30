-- Enable necessary extensions
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

-- Create users table
create table if not exists public.users (
    id uuid default gen_random_uuid() primary key,
    telegram_id bigint unique not null,
    name text,
    role text,
    industry text,
    skills text[],
    goals text[],
    interests text[],
    social_points integer default 0,
    free_requests_remaining integer default 5,
    subscription_tier text,
    subscription_expires_at timestamp with time zone,
    last_active_at timestamp with time zone default now(),
    is_active_in_search boolean default true,
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now()
);

-- Create connections table
create table if not exists public.connections (
    id uuid default gen_random_uuid() primary key,
    user1_id uuid references public.users(id) not null,
    user2_id uuid references public.users(id) not null,
    connection_type text not null check (connection_type in ('worked_together', 'intro_made', 'personal_contact', 'chat_help')),
    trust_score integer not null check (trust_score between 1 and 3),
    status text not null default 'active' check (status in ('active', 'inactive', 'blocked')),
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now(),
    -- Ensure user1_id is always less than user2_id to prevent duplicate connections
    constraint unique_connection unique (user1_id, user2_id),
    constraint different_users check (user1_id != user2_id)
);

-- Create requests table
create table if not exists public.requests (
    id uuid default gen_random_uuid() primary key,
    requester_id uuid references public.users(id) not null,
    description_text text not null,
    status text not null default 'open' check (status in ('open', 'pending_intro', 'intro_made', 'closed', 'expired')),
    created_at timestamp with time zone default now(),
    expires_at timestamp with time zone not null,
    updated_at timestamp with time zone default now()
);

-- Create request_matches_log table
create table if not exists public.request_matches_log (
    id uuid default gen_random_uuid() primary key,
    request_id uuid references public.requests(id) not null,
    suggested_user_id uuid references public.users(id) not null,
    introducer_user_id uuid references public.users(id),
    match_score float not null,
    status text not null default 'suggested' check (status in ('suggested', 'intro_requested', 'helper_accepted', 'helper_declined')),
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now()
);

-- Create activity_history table
create table if not exists public.activity_history (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references public.users(id) not null,
    action_type text not null check (action_type in ('helped_on_request', 'made_request', 'connected_with_user', 'earned_points', 'spent_points')),
    related_request_id uuid references public.requests(id),
    points_change integer not null default 0,
    timestamp timestamp with time zone default now()
);

-- Create subscriptions table
create table if not exists public.subscriptions (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references public.users(id) not null,
    plan_name text not null,
    payment_provider_subscription_id text,
    start_date timestamp with time zone default now(),
    end_date timestamp with time zone not null,
    status text not null default 'active' check (status in ('active', 'cancelled', 'expired')),
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now()
);

-- Create indexes
create index if not exists users_telegram_id_idx on public.users(telegram_id);
create index if not exists users_is_active_in_search_idx on public.users(is_active_in_search);
create index if not exists connections_user1_id_idx on public.connections(user1_id);
create index if not exists connections_user2_id_idx on public.connections(user2_id);
create index if not exists requests_requester_id_idx on public.requests(requester_id);
create index if not exists requests_status_idx on public.requests(status);
create index if not exists request_matches_log_request_id_idx on public.request_matches_log(request_id);
create index if not exists request_matches_log_suggested_user_id_idx on public.request_matches_log(suggested_user_id);
create index if not exists activity_history_user_id_idx on public.activity_history(user_id);
create index if not exists subscriptions_user_id_idx on public.subscriptions(user_id);

-- Create updated_at trigger function
create or replace function public.handle_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

-- Create triggers for updated_at
create trigger set_users_updated_at
    before update on public.users
    for each row
    execute function public.handle_updated_at();

create trigger set_connections_updated_at
    before update on public.connections
    for each row
    execute function public.handle_updated_at();

create trigger set_requests_updated_at
    before update on public.requests
    for each row
    execute function public.handle_updated_at();

create trigger set_request_matches_log_updated_at
    before update on public.request_matches_log
    for each row
    execute function public.handle_updated_at();

create trigger set_subscriptions_updated_at
    before update on public.subscriptions
    for each row
    execute function public.handle_updated_at();

-- Enable Row Level Security
alter table public.users enable row level security;
alter table public.connections enable row level security;
alter table public.requests enable row level security;
alter table public.request_matches_log enable row level security;
alter table public.activity_history enable row level security;
alter table public.subscriptions enable row level security;

-- Create RLS policies for users table
create policy "Users can read their own data"
    on public.users
    for select
    using (auth.uid() = id);

create policy "Users can update their own data"
    on public.users
    for update
    using (auth.uid() = id);

-- Create RLS policies for connections table
create policy "Users can read their own connections"
    on public.connections
    for select
    using (auth.uid() = user1_id or auth.uid() = user2_id);

create policy "Users can create their own connections"
    on public.connections
    for insert
    with check (auth.uid() = user1_id or auth.uid() = user2_id);

-- Create RLS policies for requests table
create policy "Users can read all open requests"
    on public.requests
    for select
    using (status = 'open');

create policy "Users can read their own requests"
    on public.requests
    for select
    using (auth.uid() = requester_id);

create policy "Users can create their own requests"
    on public.requests
    for insert
    with check (auth.uid() = requester_id);

-- Create RLS policies for request_matches_log table
create policy "Users can read their own request matches"
    on public.request_matches_log
    for select
    using (
        exists (
            select 1 from public.requests
            where id = request_matches_log.request_id
            and requester_id = auth.uid()
        )
        or suggested_user_id = auth.uid()
        or introducer_user_id = auth.uid()
    );

-- Create RLS policies for activity_history table
create policy "Users can read their own activity history"
    on public.activity_history
    for select
    using (auth.uid() = user_id);

-- Create RLS policies for subscriptions table
create policy "Users can read their own subscriptions"
    on public.subscriptions
    for select
    using (auth.uid() = user_id);

-- Add comments to tables
comment on table public.users is 'Stores user profiles and their basic information';
comment on table public.connections is 'Stores connections between users and their trust scores';
comment on table public.requests is 'Stores user requests for help or connections';
comment on table public.request_matches_log is 'Logs potential matches for requests';
comment on table public.activity_history is 'Tracks user activities and point changes';
comment on table public.subscriptions is 'Manages user subscription information'; 