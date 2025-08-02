# -*- coding: utf-8 -*-
"""activity related views.

:organization: Logilab
:copyright: 2007-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"


from logilab.mtconverter import xml_escape

from cubicweb import _
from cubicweb.utils import UStringIO
from cubicweb.schema import display_name
from cubicweb.predicates import (
    is_instance,
    multi_columns_rset,
    match_user_groups,
    score_entity,
    rql_condition,
)
from cubicweb_web.view import AnyRsetView, EntityView, EntityAdapter
from cubicweb_web import action
from cubicweb_web.component import Link
from cubicweb_web.views import tableview, calendar, navigation, editcontroller

from cubicweb_calendar.views import get_date_range_from_reqform


class ActivitySummaryView(AnyRsetView):
    __regid__ = "actsummary"
    __select__ = is_instance("Activity") & multi_columns_rset(7)

    # XXX we should make a very strict selector here
    def call(self):
        total_duration = sum(e.duration for e in self.cw_rset.entities())
        self.w("<h3>%s: %s</h3>" % (_("total"), total_duration))
        self.wview("table", self.cw_rset, "null", displaycols=range(1, 6))

        resdict = {}
        for __, __, res, __, duration, __, login in self.cw_rset:
            resdur = resdict.get(login, 0)
            resdur += duration
            resdict[login] = resdur
        self.w("<h2>%s</h2>" % _("statistics"))
        self.w('<table class="listing">')
        self.w("<tr><th>%s</th><th>%s</th></tr>" % (_("resource"), _("duration")))
        for even_odd, (login, resdur) in enumerate(sorted(resdict.iteritems())):
            self.w('<tr class="%s">' % (even_odd % 2 and "odd" or "even"))
            self.w("<td>%s</td>" % login)
            self.w("<td>%s</td>" % resdur)
            self.w("</tr>")
        self.w("</table>")


class ActivitySubmitView(EntityView):
    __regid__ = "activities-list"
    __select__ = is_instance("Resource")

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        firstday, lastday = get_date_range_from_reqform(self._cw.form)
        rql = "Any A WHERE A is Activity, A done_by R, R eid %(r)s"
        if lastday is None:
            rql += ", A diem %(fd)s"
        else:
            rql += ", A diem >= %(fd)s, A diem <= %(ld)s"
        rset = self._cw.execute(rql, {"r": entity.eid, "fd": firstday, "ld": lastday})
        self.wview("activitytable", rset, "null")
        self.wview(
            "activities-submitform",
            rset=self.cw_rset,
            row=row,
            col=col,
            initargs={"date": firstday},
        )


# XXX see generic definition for tablecontext view in gingouz.views
class ActivityTableContext(EntityView):
    __regid__ = "tablecontext"
    __select__ = is_instance("Activity")

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(
            '<a href="%s"><img alt="%s" src="data/accessories-text-editor.png" /></a>'
            % (
                xml_escape(entity.absolute_url(vid="edition")),
                self._cw._("actions_edit"),
            )
        )


class ActivityTableView(EntityView):
    __regid__ = "activitytable"
    __select__ = is_instance("Activity")
    title = _("activitytable")

    def call(self, showresource=True):
        eids = ",".join(str(row[0]) for row in self.cw_rset)
        rql = (
            "Any R, D, DUR, WO, DESCR, S, A, SN, RT, WT ORDERBY D DESC "
            "WHERE "
            "   A is Activity, A done_by R, R title RT, "
            "   A diem D, A duration DUR, "
            "   A done_for WO, WO title WT, "
            "   A description DESCR, A in_state S, S name SN, A eid IN (%s)" % eids
        )
        rset = self._cw.execute(rql)
        self.wview("activity-table", rset, "null", showresource=showresource)


class GenericActivityTable(tableview.RsetTableView):
    __regid__ = "generic-activitytable"
    __select__ = multi_columns_rset()
    title = _("activitytable")
    cellvids = {4: "editable-final"}
    finalvid = "editable-final"
    layout_args = {
        "display_filter": "top",
        "add_view_actions": False,
    }

    def call(self, title=None):
        strio = UStringIO()
        self.paginate(self, w=strio.write, page_size=20)
        super(GenericActivityTable, self).call()
        self.w(strio.getvalue())


class ActivityTable(tableview.RsetTableView):
    __regid__ = "activity-table"

    def call(self, title=None, showresource=True):
        _ = self._cw._
        self.headers = [
            _("diem"),
            _("duration"),
            _("workpackage"),
            _("description"),
            _("state"),
            "",
        ]
        if showresource:
            self.displaycols = range(7)
            self.headers.insert(0, display_name(self._cw, "Resource"))
            self.cellvids = {
                1: "editable-final",
                2: "editable-final",
                3: "editable-final",
                4: "editable-final",
            }
        else:  # skip resource column if asked to
            self.displaycols = range(1, 7)
            self.cellvids = {
                0: "editable-final",
                1: "editable-final",
                2: "editable-final",
                3: "editable-final",
            }
        super(ActivityTable, self).call()


class ActivityCalendarItemView(calendar.CalendarItemView):
    __select__ = is_instance("Activity")

    def cell_call(self, row, col):
        activity = self.cw_rset.get_entity(row, col)
        self.w(
            '<a href="%s">%s %s</a>'
            % (
                xml_escape(activity.absolute_url()),
                xml_escape(activity.workorder.dc_long_title()),
                activity.duration,
            )
        )


class DeleteCommitments(action.Action):
    __regid__ = "delete-commitments"
    __select__ = (
        is_instance("WorkOrder")
        & score_entity(lambda x: x.cw_adapt_to("IWorkflowable").state == "closed")
        & score_entity(lambda x: x.reverse_commit_for)
        & (match_user_groups("managers") | rql_condition("X owned_by U"))
    )
    category = "moreactions"
    submenu = _("commitments")
    title = _("delete commitments")

    def fill_menu(self, box, menu):
        eid = self.cw_rset[self.cw_row or 0][self.cw_col or 0]
        menu.append(self.build_link(eid))

    def build_link(self, eid):
        rql = f"DELETE Commitment C WHERE C commit_for WO, WO eid {eid}"
        self._cw.add_js("cubes.timesheet.js")
        href = self._cw.build_url("rqlio/1.0")
        attrs = {"class": "rqlio", "data-rql": rql}
        return Link(href, self._cw._(self.title), **attrs)


class ValidateActivitiesAction(action.Action):
    __regid__ = "validate-activities"
    __select__ = (
        action.Action.__select__
        & is_instance("Activity")
        & (match_user_groups("managers") | rql_condition("X done_for W, W owned_by U"))
        & score_entity(lambda x: x.cw_adapt_to("IWorkflowable").state == "pending")
    )

    category = "mainactions"
    title = _("validate activities")
    trname = "validate"

    def fill_menu(self, box, menu):
        if self.cw_row is None:
            eids = [row[0] for row in self.cw_rset]
        else:
            eids = (self.cw_rset[self.cw_row][self.cw_col or 0],)
        menu.append(self.build_link(self.title, eids))

    def build_link(self, title, eids, item=None):
        rql = (
            "INSERT TrInfo X: "
            "X by_transition BT, X wf_info_for Y "
            "WHERE Y eid in ({0}), Y in_state S, S state_of W, "
            "BT transition_of W, BT name '{1}'"
        )
        rql = rql.format(",".join(str(eid) for eid in eids), self.trname)
        self._cw.add_js("cubes.timesheet.js")
        href = self._cw.build_url("rqlio/1.0")
        attrs = {"class": "rqlio", "data-rql": rql}
        return Link(href, self._cw._(title), **attrs)


class ArchiveActivitiesAction(ValidateActivitiesAction):
    __regid__ = "archive-activities"
    __select__ = (
        action.Action.__select__
        & match_user_groups("managers")
        & is_instance("Activity")
        & score_entity(lambda x: x.cw_adapt_to("IWorkflowable").state == "validated")
    )

    title = _("archive activities")
    trname = "archive"


WORKORDER_CLOSED_STATES = ["validated", "canceled"]


class MoveActivitiesAction(action.Action):
    __regid__ = "move-activities"
    __select__ = (
        action.Action.__select__
        & ~match_user_groups("managers")
        & is_instance("Activity")
        & rql_condition("X done_for W, W owned_by U")
        & score_entity(lambda x: x.cw_adapt_to("IWorkflowable").state == "pending")
    )

    category = "mainactions"
    submenu = _("move activities")

    def fill_menu(self, box, menu):
        self._cw.add_js("cubes.timesheet.js")
        if self.cw_row is None:
            eids = [str(row[self.cw_col or 0]) for row in self.cw_rset]
        else:
            eids = [str(self.cw_rset[self.cw_row][self.cw_col or 0])]
        for item in self.actual_actions():
            menu.append(self.build_link(item.dc_long_title(), item, eids))

    def actual_actions(self):
        states = ",".join('"%s"' % state for state in WORKORDER_CLOSED_STATES)
        return self._cw.execute(
            "Any W,WT,O,OT ORDERBY OT,WT WHERE W is WorkOrder, "
            f"W in_state S, NOT S name IN ({states}), "
            "O split_into W, O title OT, W title WT, "
            "W owned_by U, U eid %(eid)s",
            {"eid": self._cw.cnx.user.eid},
        ).entities()

    def build_link(self, title, workorder, eids):
        rql = "SET X done_for Y WHERE X eid IN({0}), Y eid {1}"
        rql = rql.format(",".join(eids), workorder.eid)
        href = self._cw.build_url("rqlio/1.0")
        attrs = {
            "class": "rqlio",
            "data-rql": rql,
        }
        return Link(href, title, **attrs)


class ManagerMoveActivitiesAction(MoveActivitiesAction):
    __select__ = (
        action.Action.__select__
        & match_user_groups("managers")
        & is_instance("Activity")
        & score_entity(lambda x: x.cw_adapt_to("IWorkflowable").state != "archived")
    )

    def actual_actions(self):
        return self._cw.execute(
            "Any W,WT,O,OT ORDERBY OT,WT WHERE W is WorkOrder, "
            "O split_into W, O title OT, W title WT"
        ).entities()


class ActivityIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance("Activity")

    def previous_entity(self):
        entity = self.entity
        execute = self._cw.execute
        # if the smallest duration
        rset = execute(
            "Activity A ORDERBY DUR DESC LIMIT 1 WHERE "
            "A done_by R, R euser U, U eid %(u)s, A diem %(d)s, "
            "A duration DUR, A duration < %(t)s",
            {"u": entity.user.eid, "d": entity.diem, "t": entity.duration},
        )
        if rset:
            return rset.get_entity(0, 0)
        # the smallest id
        rset = execute(
            "Activity A ORDERBY A DESC LIMIT 1 WHERE "
            "A done_by R, R euser U, U eid %(u)s, A diem %(d)s, "
            "A duration < %(t)s, A eid < %(eid)s",
            {
                "u": entity.user.eid,
                "d": entity.diem,
                "t": entity.duration,
                "eid": entity.eid,
            },
        )
        if rset:
            return rset.get_entity(0, 0)
        # next days
        rset = execute(
            "Activity A ORDERBY D DESC LIMIT 1 WHERE "
            "A done_by R, R euser U, U eid %(u)s, "
            "A diem D, A diem < %(d)s ",
            {"u": entity.user.eid, "d": entity.diem},
        )
        if rset:
            return rset.get_entity(0, 0)

    def next_entity(self):
        entity = self.entity
        execute = self._cw.execute
        rset = execute(
            "Activity A ORDERBY DUR LIMIT 1 WHERE "
            "A done_by R, R euser U, U eid %(u)s, A diem %(d)s, "
            "A duration DUR, A duration > %(t)s",
            {"u": entity.user.eid, "d": entity.diem, "t": entity.duration},
        )
        if rset:
            return rset.get_entity(0, 0)
        rset = execute(
            "Activity A ORDERBY A LIMIT 1 WHERE "
            "A done_by R, R euser U, U eid %(u)s, A diem %(d)s, "
            "A eid > %(eid)s, A duration > %(t)s",
            {
                "u": entity.user.eid,
                "d": entity.diem,
                "t": entity.duration,
                "eid": entity.eid,
            },
        )
        if rset:
            return rset.get_entity(0, 0)
        rset = execute(
            "Activity A ORDERBY D LIMIT 1 WHERE "
            "A done_by R, R euser U, U eid %(u)s, "
            "A diem D, A diem > %(d)s ",
            {"u": entity.user.eid, "d": entity.diem},
        )
        if rset:
            return rset.get_entity(0, 0)


class ActivityIEditControlAdapter(editcontroller.IEditControlAdapter):
    __select__ = is_instance("Activity")

    def after_deletion_path(self):
        """return (path, parameters) which should be used as redirect
        information when this entity is being deleted
        """
        return "view", {}


class ActivityICalendarViewsAdapter(EntityAdapter):
    """calendar views interface"""

    __regid__ = "ICalendarViews"
    __select__ = is_instance("Activity")

    def matching_dates(self, begin, end):
        """calendar views interface"""
        return [self.entity.diem]
