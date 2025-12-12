"""Constantes métier"""


# Rôles
class RoleEnum:
    ADMIN = "ADMIN"
    DEVELOPPEUR = "DEVELOPPEUR"
    UTILISATEUR = "UTILISATEUR"


ROLES = [RoleEnum.ADMIN, RoleEnum.DEVELOPPEUR, RoleEnum.UTILISATEUR]


# Statuts utilisateur
class UserStatusEnum:
    ACTIF = "ACTIF"
    INACTIF = "INACTIF"
    BLOQUE = "BLOQUE"


USER_STATUSES = [UserStatusEnum.ACTIF, UserStatusEnum.INACTIF, UserStatusEnum.BLOQUE]


# Statuts soumission
class SoumissionStatusEnum:
    SOUMIS = "SOUMIS"
    EN_COURS = "EN_COURS"
    VALIDE = "VALIDE"
    REJETE = "REJETE"
    ARCHIVE = "ARCHIVE"


SOUMISSION_STATUSES = [
    SoumissionStatusEnum.SOUMIS,
    SoumissionStatusEnum.EN_COURS,
    SoumissionStatusEnum.VALIDE,
    SoumissionStatusEnum.REJETE,
    SoumissionStatusEnum.ARCHIVE,
]


# Types de champs
class ChampTypeEnum:
    TEXT = "text"
    NUMBER = "number"
    EMAIL = "email"
    DATE = "date"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FILE = "file"
    TEXTAREA = "textarea"
    GEOLOCATION = "geolocation"
    SIGNATURE = "signature"
    BUTTON = "button"


CHAMP_TYPES = [
    ChampTypeEnum.TEXT,
    ChampTypeEnum.NUMBER,
    ChampTypeEnum.EMAIL,
    ChampTypeEnum.DATE,
    ChampTypeEnum.SELECT,
    ChampTypeEnum.CHECKBOX,
    ChampTypeEnum.RADIO,
    ChampTypeEnum.FILE,
    ChampTypeEnum.TEXTAREA,
    ChampTypeEnum.GEOLOCATION,
    ChampTypeEnum.SIGNATURE,
    ChampTypeEnum.BUTTON,
]


# Permissions
class PermissionEnum:
    CREATE_FORM = "CREATE_FORM"
    EDIT_FORM = "EDIT_FORM"
    DELETE_FORM = "DELETE_FORM"
    PUBLISH_FORM = "PUBLISH_FORM"
    VIEW_SUBMISSION = "VIEW_SUBMISSION"
    MANAGE_USERS = "MANAGE_USERS"
    VIEW_AUDIT = "VIEW_AUDIT"


# Types de source référentiel
class ReferentielSourceEnum:
    EXCEL = "EXCEL"
    BDD = "BDD"
    API = "API"


# Types de BDD
class BddTypeEnum:
    POSTGRESQL = "PostgreSQL"
    MYSQL = "MySQL"
    SQL_SERVER = "SQL Server"
    ORACLE = "Oracle"
