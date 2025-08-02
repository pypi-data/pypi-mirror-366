# -*- coding: utf-8 -*-
"""commitment related views.

:organization: Logilab
:copyright: 2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"


from cubicweb.predicates import is_instance

from cubicweb_web.view import EntityView
from cubicweb_web.views import tableview


class ResourceCommitmentDashboard(EntityView):
    __regid__ = "resource.commitment-dashboard"
    __select__ = is_instance("Resource")

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rql = (
            "Any R, WO, BD, ED, DU, C ORDERBY WOT "
            "WHERE "
            "   R eid %(r)s, R is Resource, "
            "   C commit_by R, C is Commitment, "
            "   C duration DU, "
            "   C begin_date BD, C end_date ED, "
            "   C commit_for WO, WO title WOT"
        )
        rset = self._cw.execute(rql, {"r": entity.eid})
        self.wview("commitment.table", rset, "null")
        self.wview(
            "commitment.submitform", rset=self.cw_rset, row=row, col=col, initargs={}
        )


class CommitmentTable(tableview.RsetTableView):
    __regid__ = "commitment.table"

    def call(self):
        self.cellvids = {
            1: "outofcontext",
            2: "editable-final",
            3: "editable-final",
            4: "editable-final",
        }
        super(CommitmentTable, self).call()
