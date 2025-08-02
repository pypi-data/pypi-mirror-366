"""template-specific forms/views/actions/components"""

from cubicweb_web.views import uicfg
from cubicweb_web.views.urlrewrite import SimpleReqRewriter, rgx

uicfg.primaryview_section.tag_object_of(("*", "use_calendar", "Calendar"), "hidden")

uicfg.actionbox_appearsin_addmenu.tag_subject_of(
    ("Resource", "has_vacation", "*"), True
)
uicfg.actionbox_appearsin_addmenu.tag_object_of(("Resource", "euser", "CWUser"), True)
uicfg.actionbox_appearsin_addmenu.tag_object_of(
    ("Commitment", "commit_for", "WorkOrder"), True
)

uicfg.reledit_ctrl.tag_subject_of(
    ("Activity", "done_for", "*"), {"rvid": "outofcontext"}
)


rql_all_users_resources = (
    r"Any R,L ORDERBY L WHERE R is Resource, R euser U,"
    r' U login L,U in_state S, S name "activated"'
)

rql_user_or_group_resources = (
    r"Any R WHERE R is Resource, R euser U,"
    r' EXISTS (U login "\1")'
    r' OR EXISTS(U in_group G, G name "\1")'
)


class TimesheetReqRewriter(SimpleReqRewriter):
    rules = [
        # activities
        (
            rgx(r"/activities/(.*?)/(\d{4})$"),
            dict(
                year=r"\2",
                month=r"01",
                day=r"01",
                vid="activities-submit",
                rql=(
                    r"Any A ORDERBY D WHERE A is Activity, A diem D,"
                    r' A diem >= "\2-01-01", A diem <= "\2-12-31", A done_by R,'
                    r' R euser U, U login "\1"'
                ),
            ),
        ),
        (
            rgx(r"/activities/(.*?)/(\d{4})-(\d\d)"),
            dict(
                year=r"\2",
                month=r"\3",
                day=r"01",
                vid="activities-submit",
                rql=(
                    r'Any A WHERE A is Activity, A diem "\2-\3-01",'
                    r' A done_by R, R euser U, U login "\1"'
                ),
            ),
        ),
        (
            rgx(r"/activities/(.*?)/(\d{8})-(\d{8})"),
            dict(
                vid="activities-list",
                firstday=r"\2",
                lastday=r"\3",
                rql=r'Any R WHERE R is Resource, R title "\1"',
            ),
        ),
        (
            rgx(r"/activities/(.*?)/(\d{8})$"),
            dict(
                vid="activities-list",
                firstday=r"\2",
                rql=r'Any R WHERE R is Resource, R title "\1"',
            ),
        ),
        # this rule is for backward compatibility
        (
            rgx(r"/activities/(.*?)/(\d{4})-(\d\d)-(\d\d)"),
            dict(
                year=r"\2",
                month=r"\3",
                day=r"\4",
                vid="activities-submit",
                rql=(
                    r'Any A WHERE A is Activity, A diem "\2-\3-\4", A done_by R,'
                    r' R euser U, U login "\1"'
                ),
            ),
        ),
        # missing-activites
        (
            rgx(r"/missing-activities/all/(\d{8})"),
            dict(vid="missing-activities", firstday=r"\1", rql=rql_all_users_resources),
        ),
        (
            rgx(r"/missing-activities/all/(\d{8})-(\d{8})"),
            dict(
                vid="missing-activities",
                firstday=r"\1",
                lastday=r"\2",
                rql=rql_all_users_resources,
            ),
        ),
        (
            rgx(r"/missing-activities/all/(\d{8})-[tT][oO][dD][aA][yY]"),
            dict(
                vid="missing-activities",
                firstday=r"\1",
                lastday="TODAY",
                rql=rql_all_users_resources,
            ),
        ),
        (
            rgx(r"/missing-activities/(.*?)/(\d{8})"),
            dict(
                vid="missing-activities",
                firstday=r"\2",
                rql=rql_user_or_group_resources,
            ),
        ),
        (
            rgx(r"/missing-activities/(.*?)/(\d{8})-(\d{8})"),
            dict(
                vid="missing-activities",
                firstday=r"\2",
                lastday=r"\3",
                rql=rql_user_or_group_resources,
            ),
        ),
        (
            rgx(r"/missing-activities/(.*?)/(\d{8})-[tT][oO][dD][aA][yY]"),
            dict(
                vid="missing-activities",
                firstday=r"\2",
                lastday="TODAY",
                rql=rql_user_or_group_resources,
            ),
        ),
        # commitments
        (
            rgx(r"/commitments/(.*?)$"),
            dict(
                vid="resource.commitment-dashboard",
                rql=r'Any R WHERE R is Resource, R title "\1"',
            ),
        ),
    ]
