# app/models/__init__.py
# Models are imported lazily to avoid circular imports with database.py
# They are explicitly imported in alembic/env.py instead

def import_all_models():
    from app.models.audit_log import AuditLog           # noqa: F401
    from app.models.document import Document             # noqa: F401
    from app.models.document_type import DocumentType   # noqa: F401
    from app.models.land_use_category import LandUseCategory  # noqa: F401
    from app.models.parcel import Parcel                # noqa: F401
    from app.models.parish import Parish                # noqa: F401
    from app.models.physical_location import PhysicalLocation  # noqa: F401
    from app.models.qr_code_registry import QRCodeRegistry  # noqa: F401
    from app.models.storage_cabinet import StorageCabinet  # noqa: F401
    from app.models.tax_payment import TaxPayment       # noqa: F401
    from app.models.tax_record import TaxRecord         # noqa: F401