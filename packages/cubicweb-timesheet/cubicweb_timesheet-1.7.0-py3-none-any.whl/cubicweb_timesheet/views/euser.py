import datetime
from collections import defaultdict

from logilab.mtconverter import xml_escape
from logilab.common.date import (
    date_range,
    previous_month,
    next_month,
    first_day,
    last_day,
)

from cubicweb import _
from cubicweb_web.view import EntityView
from cubicweb.predicates import is_instance, one_line_rset
from cubicweb_web import form
from cubicweb_web.views import json

from cubicweb_calendar.entities import BadCalendar
from cubicweb_calendar.views import get_date_range_from_reqform


class ResourceActivitySubmitFormView(form.FormViewMixIn, EntityView):
    __regid__ = "activities-submitform"
    __select__ = one_line_rset() & is_instance("Resource")
    domid = "activityForm"

    def cell_call(self, row, col, **formvalues):
        self._cw.add_css("cubicweb.form.css")
        resource = self.cw_rset.get_entity(row, col)
        if "diem" in formvalues:
            diem = formvalues["diem"]
        else:
            diem = formvalues["diem"] = (
                self.cw_extra_kwargs.get("date") or datetime.date.today()
            )
        formvalues["duration"] = resource.missing_for(diem)
        self.w("<h2>%s</h2>" % self._cw._("declare activities").capitalize())
        self._make_activity_form(resource, **formvalues)

    def _make_activity_form(self, resource, **formvalues):
        if resource is None:
            return '<div class="error">%s</div>' % (
                self._cw._("no resource for user %s") % resource.dc_title()
            )
        display_fields = [
            ("diem", "subject"),
            ("duration", "subject"),
            ("done_for", "subject"),
            ("description", "subject"),
            ("done_by", "subject"),
        ]
        vreg = self._cw.vreg
        activity = vreg["etypes"].etype_class("Activity")(self._cw)
        activity.eid = self._cw.varmaker.next()
        form = vreg["forms"].select(
            "edition",
            self._cw,
            entity=activity,
            display_fields=display_fields,
            redirect_path=self._cw.relative_path(False),
        )
        form.form_buttons = form.form_buttons[:1]  # only keep ok button
        renderer = vreg["formrenderers"].select_or_none("htable", self._cw)
        formvalues.setdefault("done_by", resource.eid)
        form.render(formvalues=formvalues, renderer=renderer, w=self.w)


class ResourceMonitorCalendar(EntityView):
    __regid__ = "activity_calendar"
    __select__ = is_instance("Resource")

    def call(self):
        for row in range(len(self.cw_rset)):
            # only display resource title if there's more than one in the resultset
            if len(self.cw_rset) > 1:
                entity = self.cw_rset.get_entity(row, 0)
                self.w("<h2>%s</h2>" % xml_escape(entity.dc_title()))
            self.cell_call(row, 0)

    def cell_call(self, row, col, firstday=None, calid=None):
        self._cw.add_js("cubicweb.ajax.js")
        self._cw.add_css("cubes.calendar.css")
        resource = self.cw_rset.get_entity(row, col)
        calid = calid or "tid%s" % resource.eid
        if firstday is None:
            firstday, lastday = get_date_range_from_reqform(
                self._cw.form, autoset_lastday=True
            )
        else:
            lastday = last_day(firstday)
        firstday = first_day(firstday)
        # make calendar
        caption = "%s %s" % (self._cw._(firstday.strftime("%B").lower()), firstday.year)
        prevurl, nexturl = self._prevnext_links(firstday, resource, calid)
        prevlink = '<a href="%s">&lt;&lt;</a>' % xml_escape(prevurl)
        nextlink = '<a href="%s">&gt;&gt;</a>' % xml_escape(nexturl)

        # build cells
        try:
            celldatas = self._build_activities(resource, firstday, lastday)
        except BadCalendar as exc:  # in case of missing week day information
            self.w('<div class="error">%s</div>' % exc)
            return
        # build table/header
        self.w(
            '<table id="%s" class="activitiesCal">'
            '<tr><th class="prev">%s</th>'
            '<th class="calTitle" colspan="5"><span>%s</span></th>'
            '<th class="next">%s</th></tr>'
            "<tr><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th><th>D</th></tr>"
            % (calid, prevlink, caption, nextlink)
        )
        start = firstday - datetime.timedelta(firstday.weekday())
        # date range exclude last day so we should add one day, hence the 7
        stop = lastday + datetime.timedelta(7 - lastday.weekday())
        for curdate in date_range(start, stop):
            if curdate == start or curdate.weekday() == 0:  # sunday
                self.w("<tr>")
            self._build_calendar_cell(curdate, celldatas, firstday)
            if curdate.weekday() == 6:
                self.w("</tr>")
        self.w("</table>")

    def _build_calendar_cell(self, curdate, celldatas, firstday):
        if curdate.month != firstday.month:
            self.w('<td class="outofrange"></td>')
        else:
            cssclasses, total_duration, url, workcases = celldatas[curdate]
            total = total_duration
            if workcases:
                total = "%s (%s)" % (total, workcases)
            cellcontent = '<a title="total %s" href="%s">%s</a>' % (
                total,
                url,
                curdate.day,
            )
            self.w('<td class="%s">%s</td>' % (" ".join(cssclasses), cellcontent))

    def _prevnext_links(self, curdate, resource, calid):
        prevdate = previous_month(curdate)
        nextdate = next_month(curdate)
        rql = "Any X WHERE X eid %s" % resource.eid
        prevlink = self._cw.ajax_replace_url(
            calid,
            rql=rql,
            vid="activity_calendar",
            replacemode="swap",
            firstday=prevdate.strftime("%Y%m01"),
        )
        nextlink = self._cw.ajax_replace_url(
            calid,
            rql=rql,
            vid="activity_calendar",
            replacemode="swap",
            firstday=nextdate.strftime("%Y%m01"),
        )
        return prevlink, nextlink

    def _build_activities(self, resource, firstday, lastday):
        # build result
        celldatas = {}
        _today = datetime.date.today()
        dtypes = resource.get_day_types(firstday, lastday)
        for date_, dtstate, expected, day_report in resource.iter_activities(
            firstday, lastday
        ):
            declared = sum([a.duration for a in day_report])
            cssclass = []
            total_duration = ""
            needs_validation = any(
                a.cw_adapt_to("IWorkflowable").state == "pending" for a in day_report
            )
            try:
                dtype = self._cw.entity_from_eid(dtypes[date_][0])
            except KeyError:
                self.error(
                    "no day type on %s for %s (from %s to %s)",
                    resource,
                    date_,
                    firstday,
                    lastday,
                )
                dtype = None
            if dtstate == "pending":
                cssclass.append("daytype_pending")
            if dtype is not None and dtype.day_worked:
                if date_ <= _today:
                    if abs(declared - expected) > 1e-3:
                        cssclass.append("problem")
                    elif needs_validation:
                        cssclass.append("pending")
                    else:
                        cssclass.append("completed")
                total_duration = "%.2f / %.1f" % (declared, expected)
            else:
                if dtstate != "pending":
                    cssclass.append("closed")
                if declared:
                    cssclass.append("problem")
            summary = ",".join(a.workorder.dc_long_title() for a in day_report)
            url = xml_escape(
                self._cw.build_url(
                    "activities/%s/%s" % (resource.title, date_.strftime("%Y%m%d"))
                )
            )
            celldatas[date_] = (cssclass, total_duration, url, summary)
        if _today in celldatas:
            # celldatas maps days to tuples (cssclass, duration, url, descr)
            celldatas[_today][0].append("today")
        return celldatas


class ResourceMissingActivitiesMixIn(object):

    def missing_activities(self, entity):
        firstday, lastday = get_date_range_from_reqform(
            self._cw.form, autoset_lastday=True
        )
        for first_day_of_month in date_range(firstday, lastday, incmonth=1):
            last_day_of_month = min(lastday, last_day(first_day_of_month))
            for date_, __, expected, day_report in entity.iter_activities(
                first_day_of_month, last_day_of_month
            ):
                declared = sum([a.duration for a in day_report])
                if abs(declared - expected) > 1e-3:
                    summary = ",".join(a.workorder.dc_long_title() for a in day_report)
                    yield date_, expected, declared, summary


class JsonResourceMissingActivitiesBoard(
    json.JsonMixIn, ResourceMissingActivitiesMixIn, EntityView
):
    __regid__ = "missing-activities.json"
    __select__ = is_instance("Resource")

    def call(self):
        result = []
        for entity in self.cw_rset.entities():
            result += self.entity_data(entity)
        self.wdata(result)

    def entity_call(self, entity):
        self.wdata(list(self.entity_data(entity)))

    def entity_data(self, entity):
        for date, expected, declared, summary in self.missing_activities(entity):
            yield {
                "user": entity.euser[0].login,
                "date": date,
                "expected": expected,
                "declared": declared,
                "summary": summary,
            }


class ResourceMissingActivitiesBoard(ResourceMissingActivitiesMixIn, EntityView):
    __regid__ = "missing-activities"
    __select__ = is_instance("Resource")

    def _make_report_table(self, first_day_of_month, lines):
        w = self.w
        w('<table class="listing actboard">')
        w('<tr><th colspan="4">%s</th></tr>' % first_day_of_month.strftime("%B %Y"))
        w(
            "<tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>"
            % (
                _("date"),
                _("expected activity report"),
                _("declared activity report"),
                _("same day activity summary"),
            )
        )
        for day, act_url, expected, declared, summary in lines:
            cssclass = "missing" if declared < expected else "toomuch"
            w(
                '<tr><td><a href="%s">%s</a></td><td>%s</td><td class="%s">%s</td><td>%s</td></tr>'
                % (
                    xml_escape(act_url),
                    self._cw.printable_value("Date", day),
                    expected,
                    cssclass,
                    declared,
                    xml_escape(summary),
                )
            )
        w("</table>")

    def entity_call(self, entity):
        self._cw.add_css("cubes.timesheet.css")
        lines_per_month = defaultdict(list)
        for date_, expected, declared, summary in self.missing_activities(entity):
            act_url = self._cw.build_url(
                "activities/%s/%s" % (entity.title, date_.strftime("%Y%m%d"))
            )
            month = date_.replace(day=1)
            lines_per_month[month].append((date_, act_url, expected, declared, summary))
        if lines_per_month:
            self.w("<h2>%s</h2>" % entity.dc_title())
            for month, lines in lines_per_month.items():
                self._make_report_table(month, lines)


class ResourceCommitmentSubmitFormView(form.FormViewMixIn, EntityView):
    __regid__ = "commitment.submitform"
    __select__ = one_line_rset() & is_instance("Resource")
    domid = "commitmentForm"

    def cell_call(self, row, col, **formvalues):
        self._cw.add_css("cubicweb.form.css")
        resource = self.cw_rset.get_entity(row, col)
        self.w("<h2>%s</h2>" % self._cw._("add commitment").capitalize())
        self._make_commitment_form(resource, **formvalues)

    def _make_commitment_form(self, resource, **formvalues):
        if resource is None:
            return '<div class="error">%s</div>' % (
                self._cw._("no resource for user %s") % resource.dc_title()
            )
        display_fields = [
            ("commit_by", "subject"),
            ("commit_for", "subject"),
            ("begin_date", "subject"),
            ("end_date", "subject"),
            ("duration", "subject"),
        ]
        vreg = self._cw.vreg
        commitment = vreg["etypes"].etype_class("Commitment")(self._cw)
        commitment.eid = self._cw.varmaker.next()
        form = vreg["forms"].select(
            "edition",
            self._cw,
            entity=commitment,
            display_fields=display_fields,
            redirect_path=self._cw.relative_path(False),
        )
        form.form_buttons = form.form_buttons[:1]  # only keep ok button
        renderer = vreg["formrenderers"].select_or_none("htable", self._cw)
        formvalues.setdefault("commit_by", resource.eid)
        form.render(formvalues=formvalues, renderer=renderer, w=self.w)
