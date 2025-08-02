"""ajax / json / jsonp functions"""

from datetime import datetime as pydatetime
import json

import six

from cubicweb_web.view import StartupView
from cubicweb.predicates import match_form_params


def get_day_types(self, resource_title, start, stop):
    """returns a list of couples (date, day_type) for a given resource.

    ``day_type`` corresponds to the ``type`` attribute of the ``Daytype``
    entities manipulated.

    The calendar used if the last created calendar for the corresponding user.
    """
    resource = self._cw.find("Resource", title=resource_title).one()
    start = pydatetime.strptime(start, "%Y-%m-%d").date()
    stop = pydatetime.strptime(stop, "%Y-%m-%d").date()
    daytypes = []
    for date, (dtype, state) in sorted(resource.get_day_types(start, stop).items()):
        day_type = self._cw.entity_from_eid(dtype).type
        daytypes.append((date.strftime("%Y-%m-%d"), day_type))
    return daytypes


class DayTypesJsonView(StartupView):
    """Dumps a list of couples (date, day_type) for a given login.

    ``day_type`` corresponds to the ``type`` attribute of the ``Daytype``
    entities manipulated.

    Expected request parameters are :

    - ``login`` (the user's login)
    - ``start`` (format must be %Y-%m-%d)
    - ``stop`` (format must be %Y-%m-%d)

    If ``callback`` request parameter is passed, it's used as json padding
    """

    __regid__ = "daytypes.json"
    __select__ = StartupView.__select__ & match_form_params("login", "start", "stop")
    content_type = "application/json"
    binary = True
    templatable = False

    def call(self):
        data = get_day_types(
            self, self._cw.form["login"], self._cw.form["start"], self._cw.form["stop"]
        )
        if "callback" in self._cw.form:
            self._cw.set_content_type("text/javascript")
            self.w(
                "%s(%s)"
                % (
                    self._cw.form["callback"].encode("ascii"),
                    six.ensure_binary(json.dumps(data)),
                )
            )
        else:
            self.w(six.ensure_binary(json.dumps(data)))
