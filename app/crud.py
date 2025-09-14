import json
import uuid
from typing import Optional
from asyncpg import Pool
from asyncpg.exceptions import UniqueViolationError

# ------------------- EVENTS -------------------

async def list_events(pool: Pool, limit: int = 25, offset: int = 0):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT e.*, ei.seats_available
            FROM events e
            LEFT JOIN event_inventory ei ON ei.event_id = e.id
            ORDER BY e.start_time ASC
            LIMIT $1 OFFSET $2
        """, limit, offset)
        events = []
        for r in rows:
            event = dict(r)
            event['id'] = str(event['id'])
            events.append(event)
        return events

async def create_event(pool: Pool, event_data: dict):
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow("""
                INSERT INTO events (name, venue, description, start_time, end_time, capacity)
                VALUES ($1,$2,$3,$4,$5,$6)
                RETURNING id, name, venue, description, start_time, end_time, capacity
            """, event_data['name'], event_data.get('venue'), event_data.get('description'),
                   event_data['start_time'], event_data.get('end_time'), event_data['capacity'])

            await conn.execute("""
                INSERT INTO event_inventory (event_id, seats_available)
                VALUES ($1, $2)
            """, row['id'], row['capacity'])

            result = dict(row)
            result['id'] = str(result['id'])
            result['seats_available'] = row['capacity']
            return result

async def get_event(pool: Pool, event_id: str):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT e.*, ei.seats_available
            FROM events e
            LEFT JOIN event_inventory ei ON ei.event_id = e.id
            WHERE e.id = $1
        """, event_id)
        if row:
            event = dict(row)
            event['id'] = str(event['id'])
            if 'seats_available' not in event:
                event['seats_available'] = 0
            return event
        return None

async def update_event(pool: Pool, event_id: str, event_data: dict):
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow("""
                UPDATE events
                SET name=$1, venue=$2, description=$3, start_time=$4, end_time=$5, capacity=$6
                WHERE id=$7
                RETURNING id, name, venue, description, start_time, end_time, capacity
            """, event_data['name'], event_data.get('venue'), event_data.get('description'),
                   event_data['start_time'], event_data.get('end_time'), event_data['capacity'], event_id)
            if not row:
                return None
            await conn.execute("""
                UPDATE event_inventory
                SET seats_available = $1
                WHERE event_id = $2
            """, event_data['capacity'], event_id)

            result = dict(row)
            result['id'] = str(result['id'])
            result['seats_available'] = event_data['capacity']
            return result

async def delete_event(pool: Pool, event_id: str):
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("DELETE FROM event_inventory WHERE event_id = $1", event_id)
            row = await conn.fetchrow("""
                DELETE FROM events
                WHERE id=$1
                RETURNING id, name, venue, description, start_time, end_time, capacity
            """, event_id)
            if row:
                result = dict(row)
                result['id'] = str(result['id'])
                result['seats_available'] = 0
                return result
            return None

# ------------------- USERS -------------------

async def create_user(pool: Pool, email: str, name: Optional[str] = None):
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow("""
                INSERT INTO users (email, name)
                VALUES ($1,$2)
                RETURNING id, email, name, created_at
            """, email, name)
            if row:
                row = dict(row)
                row['id'] = str(row['id'])
            return row
        except UniqueViolationError:
            row = await conn.fetchrow("SELECT id, email, name, created_at FROM users WHERE email=$1", email)
            if row:
                row = dict(row)
                row['id'] = str(row['id'])
            return row

async def get_user(pool: Pool, user_id: str):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT id, email, name, created_at
            FROM users
            WHERE id = $1
        """, user_id)
        if row:
            row = dict(row)
            row['id'] = str(row['id'])
        return row

async def list_users(pool: Pool):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, email, name, created_at
            FROM users
            ORDER BY created_at DESC
        """)
        result = [dict(r) for r in rows]
        for r in result:
            r['id'] = str(r['id'])
        return result

async def delete_user(pool: Pool, user_id: str):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            DELETE FROM users
            WHERE id=$1
            RETURNING id, email, name, created_at
        """, user_id)
        if row:
            row = dict(row)
            row['id'] = str(row['id'])
        return row

# ------------------- BOOKINGS -------------------

async def book_tickets(pool: Pool, user_id: str, event_id: str, quantity: int, idempotency_key: Optional[str] = None):
    async with pool.acquire() as conn:
        async with conn.transaction():
            if idempotency_key:
                existing = await conn.fetchrow("SELECT id, status FROM bookings WHERE idempotency_key=$1 LIMIT 1", idempotency_key)
                if existing:
                    return {'reused': True, 'id': str(existing['id']), 'status': existing['status']}

            updated = await conn.fetchrow("""
                UPDATE event_inventory
                SET seats_available = seats_available - $1,
                    seats_reserved = seats_reserved + $1,
                    version = version + 1
                WHERE event_id = $2 AND seats_available >= $1
                RETURNING seats_available
            """, quantity, event_id)

            if not updated:
                raise Exception('NOT_ENOUGH_SEATS')

            booking_id = str(uuid.uuid4())
            await conn.execute("""
                INSERT INTO bookings (id, user_id, event_id, quantity, status, idempotency_key)
                VALUES ($1,$2,$3,$4,'CONFIRMED',$5)
            """, booking_id, user_id, event_id, quantity, idempotency_key)

            payload = json.dumps({'quantity': quantity, 'user_id': user_id, 'event_id': event_id})
            await conn.execute("""
                INSERT INTO booking_events (booking_id, event_type, event_payload)
                VALUES ($1, 'BOOK', $2::jsonb)
            """, booking_id, payload)

            # <-- FIXED: refresh without CONCURRENTLY
            await conn.execute("REFRESH MATERIALIZED VIEW mv_event_booking_stats")
            return {'id': booking_id, 'status': 'CONFIRMED'}

async def cancel_booking(pool: Pool, booking_id: str):
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow("""
                UPDATE bookings
                SET status = 'CANCELLED', updated_at = now()
                WHERE id=$1 AND status='CONFIRMED'
                RETURNING quantity, event_id
            """, booking_id)
            if not row:
                raise Exception('CANNOT_CANCEL')

            qty = row['quantity']
            event_id = row['event_id']

            await conn.execute("""
                UPDATE event_inventory
                SET seats_available = seats_available + $1,
                    seats_reserved = seats_reserved - $1,
                    version = version + 1
                WHERE event_id = $2
            """, qty, event_id)

            await conn.execute("""
                INSERT INTO booking_events (booking_id, event_type, event_payload)
                VALUES ($1, 'CANCEL', $2::jsonb)
            """, booking_id, json.dumps({'quantity': qty}))

            # <-- FIXED: refresh without CONCURRENTLY
            await conn.execute("REFRESH MATERIALIZED VIEW mv_event_booking_stats")
            return {'id': str(booking_id), 'event_id': str(event_id), 'cancelled_quantity': qty}

async def get_user_bookings(pool: Pool, user_id: str):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, user_id, event_id, quantity, status, created_at
            FROM bookings
            WHERE user_id=$1
            ORDER BY created_at DESC
        """, user_id)
        bookings = []
        for r in rows:
            booking = dict(r)
            booking["id"] = str(booking["id"])
            booking["user_id"] = str(booking["user_id"])
            booking["event_id"] = str(booking["event_id"])
            bookings.append(booking)
        return bookings

async def admin_event_stats(pool: Pool):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT event_id, name, capacity, total_booked, utilization
            FROM mv_event_booking_stats
            ORDER BY total_booked DESC NULLS LAST
        """)
        return [dict(r) for r in rows]
