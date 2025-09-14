"""
Package for API route modules.

This package exposes the main route modules for the application:
- events: endpoints for creating/listing/updating/deleting events
- bookings: endpoints for creating/canceling bookings and listing user bookings
- admin: admin/analytics endpoints
- users: endpoints for creating/listing/deleting users
"""
from . import events, bookings, admin, users
