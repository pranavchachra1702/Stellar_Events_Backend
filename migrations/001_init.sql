-- 001_init.sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  venue TEXT,
  description TEXT,
  start_time TIMESTAMP WITH TIME ZONE NOT NULL,
  end_time TIMESTAMP WITH TIME ZONE,
  capacity INTEGER NOT NULL CHECK (capacity >= 0),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS event_inventory (
  event_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
  seats_available INTEGER NOT NULL CHECK (seats_available >= 0),
  seats_reserved INTEGER NOT NULL DEFAULT 0,
  version BIGINT NOT NULL DEFAULT 0
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'booking_status') THEN
        CREATE TYPE booking_status AS ENUM ('PENDING','CONFIRMED','CANCELLED');
    END IF;
END$$;


CREATE TABLE IF NOT EXISTS bookings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  event_id UUID REFERENCES events(id) ON DELETE CASCADE,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  status booking_status NOT NULL DEFAULT 'PENDING',
  idempotency_key TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_bookings_idempotency_key ON bookings(idempotency_key) WHERE idempotency_key IS NOT NULL;

CREATE TABLE IF NOT EXISTS booking_events (
  id BIGSERIAL PRIMARY KEY,
  booking_id UUID REFERENCES bookings(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  event_payload JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS waitlist (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID REFERENCES events(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  joined_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS seats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID REFERENCES events(id) ON DELETE CASCADE,
  seat_label TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('AVAILABLE','HELD','BOOKED','UNAVAILABLE')),
  booking_id UUID REFERENCES bookings(id) NULL,
  UNIQUE (event_id, seat_label)
);

CREATE INDEX IF NOT EXISTS idx_events_start_time ON events(start_time);
CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_event ON bookings(event_id);
CREATE INDEX IF NOT EXISTS idx_inventory_available ON event_inventory(seats_available);

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_event_booking_stats AS
SELECT
  e.id AS event_id,
  e.name,
  e.capacity,
  COALESCE(SUM(b.quantity) FILTER (WHERE b.status = 'CONFIRMED'), 0) AS total_booked,
  CASE WHEN e.capacity > 0 THEN (COALESCE(SUM(b.quantity) FILTER (WHERE b.status = 'CONFIRMED'), 0)::float / e.capacity) END AS utilization
FROM events e
LEFT JOIN bookings b ON b.event_id = e.id
GROUP BY e.id, e.name, e.capacity;

CREATE INDEX IF NOT EXISTS idx_mv_event_booking_stats_event_id ON mv_event_booking_stats(event_id);
