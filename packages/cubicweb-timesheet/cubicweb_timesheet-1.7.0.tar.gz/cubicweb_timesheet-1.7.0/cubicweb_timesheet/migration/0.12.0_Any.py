# update default activity workflow
wf = rql('Workflow X WHERE A name "Activity", A default_workflow X').one()

# create state archived and transition archive
validated = wf.state_by_name("validated")
archived = wf.add_state(_("archived"))
wf.add_transition(_("archive"), validated, archived, ("managers",))

# allow owners of workorders to validate activities
validate = wf.transition_by_name("validate")
cond = create_entity(
    "RQLExpression",
    exprtype="ERQLExpression",
    mainvars="X",
    expression="X done_for W, W owned_by U",
    reverse_condition=validate,
)

# done
commit()
