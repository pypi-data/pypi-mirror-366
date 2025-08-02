"""unit tests for get_day_types web service
"""

import json

from cubicweb_web.devtools.testlib import WebCWTC


class JsonTests(WebCWTC):
    def setup_database(self):
        with self.admin_access.web_request() as req:
            # get default french calendar
            defaultcal = req.find("Calendar", title="Calendrier Francais").one()
            # make 1st of may a non working day
            feast_day = req.create_entity(
                "Recurrentday",
                day_month="05-01",
                day_type=req.create_entity(
                    "Daytype", title="1er mai", type="dt_nonworking"
                ),
            )
            defaultcal.cw_set(days=feast_day)
            # create a test user and corresponding resource, and make this resource
            # use this calendar
            restype = req.find("Resourcetype", title="person").one()
            testuser = req.create_entity(
                "CWUser",
                login="testuser",
                upassword="testuser",
                in_group=req.find("CWGroup", name="users").one(),
            )
            caluse = req.create_entity("Calendaruse", use_calendar=defaultcal)
            req.create_entity(
                "Resource",
                title="testuser",
                rate=1,
                euser=testuser,
                rtype=restype,
                use_calendar=caluse,
            )
            req.cnx.commit()

    def test_get_daytypes(self):
        """test daytypes.json web service"""
        with self.admin_access.web_request(
            url="view",
            login="testuser",
            start="2014-04-28",
            stop="2014-05-05",
            vid="daytypes.json",
        ) as req:
            response = self.app_handle_request(req)
            self.assertEqual(
                json.loads(response),
                [
                    ["2014-04-28", "dt_working"],
                    ["2014-04-29", "dt_working"],
                    ["2014-04-30", "dt_working"],
                    ["2014-05-01", "dt_nonworking"],
                    ["2014-05-02", "dt_working"],
                    ["2014-05-03", "dt_nonworking"],
                    ["2014-05-04", "dt_nonworking"],
                    ["2014-05-05", "dt_working"],
                ],
            )


if __name__ == "__main__":
    import unittest

    unittest.main()
