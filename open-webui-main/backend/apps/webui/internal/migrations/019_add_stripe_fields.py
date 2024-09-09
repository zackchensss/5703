"""Peewee migrations -- 002_add_stripe_fields.py.

Add Stripe-related fields to the User model.
"""

import peewee as pw
from peewee_migrate import Migrator


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""

    migrator.add_fields('user',
                        subscription_status=pw.CharField(max_length=255, null=True),
                        subscription_expiration=pw.BigIntegerField(null=True),
                        )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""

    migrator.remove_fields('user',
                           'subscription_status',
                           'subscription_expiration',
                           )