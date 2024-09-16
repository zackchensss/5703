"""Peewee migrations -- 003_add_subscription_fields.py.

Add subscription-related fields to the User model.
"""

import peewee as pw
from peewee_migrate import Migrator


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""
    migrator.add_fields('user',
                        subscription_start_time=pw.BigIntegerField(null=True),  # 添加订阅开始时间
                        subscription_product=pw.CharField(max_length=255, null=True),  # 添加订阅产品
                        orvip=pw.BooleanField(default=False),  # 添加是否为VIP订阅
                        )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""
    migrator.remove_fields('user',
                           'subscription_start_time',
                           'subscription_product',
                           'orvip',
                           )
