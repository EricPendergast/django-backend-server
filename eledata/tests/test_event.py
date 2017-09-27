# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.event import Event
from eledata.models.users import User, Group
import eledata.handlers.event as event_handler
from project.settings import CONSTANTS
import datetime
from eledata.core_engine.provider import EngineProvider


class EventTestCase(TestCase):
    def doCleanups(self):
        Group.drop_collection()
        User.drop_collection()
        Event.drop_collection()

    def setUp(self):
        assert len(Group.objects) == 0
        assert len(User.objects) == 0
        assert len(Event.objects) == 0

        self.admin = User.create_admin(username="admin", password="pass", group_name="dummy_group")
        self.admin_group = Group.objects.get(name="dummy_group")
        self.admin_client = Client()
        self.admin_client.post("/users/login/", {"username": "admin", "password": "pass"})

    def test_init_event(self):
        assert len(Group.objects) == 1

        test_data = {
            "event_category": CONSTANTS.EVENT.CATEGORY.get("OPPORTUNITY"),
            "event_type": "Capture customer likely to repeat purchase", "event_value": "VaO: $102,000",
            "event_desc": [
                {
                    "key": "Captured User",
                    "value": 154
                },
                {
                    "key": "Average Value Change per User",
                    "value": "$662"
                },
                {
                    "key": "Expiry Date",
                    "value": "30/06/2017"
                }
            ],
            "detailed_desc": [
                {
                    "key": "Average Transaction Value per User",
                    "value": "$2,078"
                },
                {
                    "key": "Average Transaction Quantity per User",
                    "value": "10"
                },
                {
                    "key": "Most Popular Product",
                    "value": "ASIA_ITEM_001_RED"
                },
                {
                    "key": "Mostly Involved Region",
                    "value": "HK (68/154)"
                }
            ],
            "analysis_desc": [
                {
                    "key": "Back-tested accuracy",
                    "value": "84.3% (80:20 split for training vs test data)",
                    "isFullWidth": True
                },
                {
                    "key": "Training set (customer)",
                    "value": "4,000"
                },
                {
                    "key": "Test set (customer)",
                    "value": "1,000"
                },
                {
                    "key": "Training set (transaction)",
                    "value": "400,000"
                },
                {
                    "key": "Test set (transaction)",
                    "value": "100,000"
                }
            ],
            "chart_type": "Line",
            "chart": {
                "labels": [
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July"
                ],
                "x_label": "Transaction Time",
                "y_label": "Total transaction",
                "datasets": [
                    {
                        "border": False,
                        "label": "Actual",
                        "xLabels": "Month",
                        "yLabels": "Total transaction within captured users",
                        "data": [
                            208900,
                            230700,
                            210000,
                            242000,
                            297000,
                            363300,
                            None
                        ]
                    },
                    {
                        "border": True,
                        "label": "Prediction",
                        "xLabels": "Month",
                        "yLabels": "Total transaction within captured users",
                        "data": [
                            None,
                            None,
                            None,
                            None,
                            None,
                            363300,
                            465300
                        ]
                    }
                ]
            },
            "detailed_data": {
                "data": [
                    {
                        "username": "Nissie Trynor",
                        "Email": "ntrynor11@ox.ac.uk",
                        "firstPurchaseDate": "17/05/2016",
                        "lastPurchaseDate": "21/07/2016",
                        "supervisedPurchaseValue": "$1,042.84",
                        "predictedPurchaseValue": "$2,870.28",
                        "ratioChange": "175%"
                    },
                    {
                        "username": "Fawn Gatch",
                        "Email": "fgatchq@gov.uk",
                        "firstPurchaseDate": "8/5/2016",
                        "lastPurchaseDate": "16/06/2016",
                        "supervisedPurchaseValue": "$1,060.92",
                        "predictedPurchaseValue": "$2,906.75",
                        "ratioChange": "174%"
                    }
                ],
                "columns": [
                    {
                        "key": "username",
                        "sortable": True,
                        "label": "User Name"
                    },
                    {
                        "key": "Email",
                        "sortable": True,
                        "label": "E-Mail"
                    }
                ]
            },
            "expiry_date": datetime.datetime.now()
        }

        response = event_handler.init_new_event(test_data, self.admin_group)
        assert response == {'msg': 'Change successful'}
        response = self.admin_client.get("/event/get_general_event/")
        assert len(response.data.get('opportunity')) == 1

    # def test_scraping_on_engine(self):
        # summary_entity_stats_engine = EngineProvider.provide("Monitoring.JD",
        #                                                      group=self.admin_group,
        #                                                      params=None,
        #                                                      keyword="DELL",
        #                                                      _page=3
        #                                                      )
        # summary_entity_stats_engine_2 = EngineProvider.provide("Monitoring.TMall",
        #                                                        group=self.admin_group,
        #                                                        params=None,
        #                                                        keyword="DELL",
        #                                                        _u_key="alexkamlivelyimpact",
        #                                                        _p_key="53231323A",
        #                                                        _page=3
        #                                                        )
        # summary_entity_stats_engine.get_multi_page()
        # summary_entity_stats_engine_2.get_multi_page()
