from yams.buildobjs import (
    EntityType,
    RelationDefinition,
    SubjectRelation,
    String,
    Float,
    Date,
)

from cubicweb.schema import (
    WorkflowableEntityType,
    ERQLExpression,
    RRQLExpression,
    RQLVocabularyConstraint,
)


class Activity(WorkflowableEntityType):
    """time someone spent working on something"""

    __permissions__ = {
        "read": ("managers", "users"),
        "update": (
            "managers",
            ERQLExpression('X in_state ST, ST name "pending", X owned_by U'),
        ),
        "delete": (
            "managers",
            ERQLExpression('X in_state ST, ST name "pending", X owned_by U'),
        ),
        "add": ("managers", "users"),
    }
    duration = Float(required=True, default=1.0)
    diem = Date(default="TODAY", required=True)
    description = String(fulltextindexed=True, maxsize=256)


class Resourcetype(EntityType):
    """see projman"""

    title = String(required=True, maxsize=64)


class Resource(EntityType):
    """see projman"""

    title = String(required=True, unique=True, maxsize=64)
    rate = Float()
    rtype = SubjectRelation("Resourcetype", cardinality="1*")
    use_calendar = SubjectRelation("Calendaruse", cardinality="+?", composite="subject")
    euser = SubjectRelation("CWUser", cardinality="??")


class done_by(RelationDefinition):
    """activity performed by a Resource"""

    __permissions__ = {
        "read": ("managers", "users"),
        "delete": (
            "managers",
            RRQLExpression('S in_state ST, ST name "pending", O euser U'),
        ),
        "add": (
            "managers",
            RRQLExpression("O euser U"),
        ),
    }
    subject = "Activity"
    object = "Resource"
    cardinality = "1*"
    constraints = [
        RQLVocabularyConstraint(
            'O euser OU?, OU in_state ST, NOT ST name "deactivated"'
        )
    ]


class done_for(RelationDefinition):
    subject = "Activity"
    object = "WorkOrder"
    cardinality = "1*"


class todo_by(RelationDefinition):
    __permissions__ = {
        "read": ("managers", "users"),
        "delete": ("managers", RRQLExpression("S owned_by U")),
        "add": ("managers", RRQLExpression("S owned_by U")),
    }
    subject = "WorkOrder"
    object = "Resource"
    cardinality = "+*"
    constraints = [
        RQLVocabularyConstraint(
            'O euser OU?, OU in_state ST, NOT ST name "deactivated"'
        )
    ]


class Commitment(EntityType):
    __permissions__ = {
        "read": ("managers", "users"),
        "update": ("managers", ERQLExpression("X owned_by U")),
        "delete": (
            "managers",
            ERQLExpression("X owned_by U"),
            ERQLExpression("X commit_for S, S owned_by U"),
        ),
        "add": ("managers", "users"),
    }
    duration = Float(required=True, default=1.0)
    begin_date = Date()
    end_date = Date()


class commit_by(RelationDefinition):
    __permissions__ = {
        "read": ("managers", "users"),
        "delete": ("managers", RRQLExpression("O euser U")),
        "add": (
            "managers",
            RRQLExpression("O euser U"),
        ),
    }
    subject = "Commitment"
    object = "Resource"
    cardinality = "1*"
    constraints = [
        RQLVocabularyConstraint(
            'O euser OU?, OU in_state ST, NOT ST name "deactivated"'
        )
    ]


class commit_for(RelationDefinition):
    __permissions__ = {
        "read": ("managers", "users"),
        "delete": (
            "managers",
            RRQLExpression("O todo_by R, R euser U"),
            RRQLExpression("O owned_by U"),
        ),
        "add": (
            "managers",
            RRQLExpression("O todo_by R, R euser U"),
        ),
    }
    subject = "Commitment"
    object = "WorkOrder"
    cardinality = "1*"
    constraints = [RQLVocabularyConstraint("O todo_by R, R euser U")]
