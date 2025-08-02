# ResourceType person
from cubicweb import _

restype = rql('INSERT Resourcetype RT: RT title "person"').rows[0][0]

# Activity workflow
wf = add_workflow("activities default workflow", "Activity")
pending = wf.add_state(_("pending"), initial=True)
validated = wf.add_state(_("validated"))
archived = wf.add_state(_("archived"))
wf.add_transition(
    _("validate"), pending, validated, ("managers",), "X done_for W, W owned_by U"
)
wf.add_transition(_("archive"), validated, archived, ("managers",))
