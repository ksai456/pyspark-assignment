CREATE TABLE IF NOT EXISTS click_session (
    click_event_id INT PRIMARY KEY,
    user_id INT,
    "url" VARCHAR(100),
    "timestamp" TIMESTAMP,
    city VARCHAR(20),
    country VARCHAR(20),
    ip_address VARCHAR(50),
    device VARCHAR(50),
    browser VARCHAR(50)
);

create unlogged table import_click_session (doc json);

COPY import_click_session FROM '/docker-entrypoint-initdb.d/user_click_data.json';


insert into click_session(click_event_id, user_id, "url", "timestamp", city, country, ip_address, device, browser)
select p.*
from import_click_session l
  cross join lateral json_populate_recordset(null::click_session, doc) as p
on conflict (click_event_id) do update 
  set user_id = excluded.user_id, 
      "url" = excluded.url,
      "timestamp" = excluded.timestamp,
      city = excluded.city,
      country = excluded.country,
      ip_address = excluded.ip_address, 
      device = excluded.device, 
      browser = excluded.browser;


