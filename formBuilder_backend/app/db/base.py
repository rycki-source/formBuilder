from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here for Alembic migrations
from app.models.user import User
from app.models.formulaire import Formulaire
from app.models.soumission import Soumission
from app.models.referentiel import Referentiel
from app.models.analytics import FormAnalytics, SubmissionEvent, FieldAnalytics
from app.models.versioning import FormulaireVersion, AuditLog
from app.models.templates import FormTemplate, FormTheme

