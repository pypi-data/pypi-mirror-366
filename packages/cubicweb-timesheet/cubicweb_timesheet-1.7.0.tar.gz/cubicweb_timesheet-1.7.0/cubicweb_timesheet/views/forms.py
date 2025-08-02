import six
from cubicweb_web import INTERNAL_FIELD_VALUE, formwidgets as fw
from cubicweb_web.views import uicfg

_afs = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs

_afs.tag_subject_of(("Resource", "use_calendar", "*"), "main", "inlined")
_afs.tag_subject_of(("WorkOrder", "uses_technology", "*"), "main", "attributes")
_afs.tag_subject_of(("WorkOrder", "uses_technology", "*"), "muledit", "attributes")
# XXX should not be always hidden
_affk.tag_subject_of(("Activity", "done_by", "*"), {"widget": fw.HiddenInput})


def tp_periods_choices(form, field, limit=None):
    if form._cw.form.get("vid") == "holidays_form":
        rset = form._cw.execute(
            "Any C WHERE R use_calendar CU, CU use_calendar C, "
            "R euser U, U eid %(u)s",
            {"u": form._cw.user.eid},
        )
        return sorted(
            (v.view("combobox"), six.text_type(v.eid)) for v in rset.entities()
        )
    return field.__class__.choices(field, form, limit=limit)


_affk.tag_object_of(("*", "periods", "Timeperiod"), {"choices": tp_periods_choices})


def activity_done_by_choices(form, field, limit=None):
    user = form._cw.user
    entity = form.edited_entity
    # managers can edit the done_by relation as they wish
    if user.is_in_group("managers"):
        rql = "Any R,T "
        if limit is not None:
            rql += "LIMIT %s " % limit
        rql += "WHERE R is Resource, R title T"
        return sorted(
            (entity.view("combobox"), six.text_type(entity.eid))
            for entity in form._cw.execute(rql).entities()
        )
    # users can't edit an existing done_by relation
    if entity.has_eid():
        return []
    rql = "Any R,T WHERE R euser U, R title T, U eid %(u)s"
    res = form._cw.execute(rql, {"u": user.eid}).get_entity(0, 0)
    return [(res.view("combobox"), six.text_type(res.eid))]


_affk.tag_subject_of(
    ("Activity", "done_by", "*"), {"choices": activity_done_by_choices}
)


def activity_done_for_choices(form, field, limit=None):
    req = form._cw
    user = req.user
    options = []
    open_state = req.vreg["etypes"].etype_class("WorkOrder").open_state
    # managers can edit the done_for relation as they wish
    if user.is_in_group("managers"):
        if limit is None:
            limit = ""
        else:
            limit = " LIMIT %s" % limit
        rql = (
            "Any WO,T %s WHERE WO is WorkOrder, WO title T, "
            'WO in_state S, S name "%s"' % (limit, open_state)
        )
        rset = form._cw.execute(rql)
        if rset:
            options += [(req._("workorders in state %s") % req._(open_state), None)]
            options += sorted(
                (entity.view("combobox"), six.text_type(entity.eid))
                for entity in rset.entities()
            )
        else:
            options += [
                (
                    req._("no workorders in state %s") % req._(open_state),
                    INTERNAL_FIELD_VALUE,
                )
            ]
    else:
        # for new entities, users will only see their matching resource
        rset = req.execute(
            "DISTINCT Any WO,T WHERE WO is WorkOrder, WO title T, "
            "WO in_state S, S name %(s)s, "
            "WO todo_by R, R euser U, U eid %(u)s",
            {"u": req.user.eid, "s": open_state},
        )
        if rset:
            options += sorted(
                (entity.view("combobox"), six.text_type(entity.eid))
                for entity in rset.entities()
            )
        else:
            options += [(req._("no workorders"), INTERNAL_FIELD_VALUE)]
    # ensure current value is in the list
    if form.edited_entity.has_eid():
        budget = form.edited_entity.done_for[0]
        cval = six.text_type(budget.eid)
        if not any(val == cval for _, val in options):
            options.insert(0, (budget.view("combobox"), six.text_type(budget.eid)))
    return options


_affk.tag_subject_of(
    ("Activity", "done_for", "*"), {"choices": activity_done_for_choices}
)


def commitment_commit_for_choices(form, field, limit=None):
    req = form._cw
    options = []
    rset = req.execute(
        "DISTINCT Any WO,T WHERE "
        " WO is WorkOrder, WO title T, "
        " WO end_date >= NOW, "
        " WO todo_by R, R euser U, U eid %(u)s",
        {"u": req.user.eid},
    )
    if rset:
        options += sorted(
            (entity.view("combobox"), six.text_type(entity.eid))
            for entity in rset.entities()
        )
    else:
        options += [(req._("no workorders"), INTERNAL_FIELD_VALUE)]
    # ensure current value is in the list
    if form.edited_entity.has_eid():
        budget = form.edited_entity.commit_for[0]
        cval = six.text_type(budget.eid)
        if all(val != cval for _, val in options):
            options.insert(0, (budget.view("combobox"), six.text_type(budget.eid)))
    return options


_affk.tag_subject_of(
    ("Commitment", "commit_for", "*"), {"choices": commitment_commit_for_choices}
)
