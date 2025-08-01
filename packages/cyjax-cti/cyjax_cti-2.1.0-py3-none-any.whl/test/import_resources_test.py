import unittest

from cyjax.resources.resource import Resource
from cyjax.resources.model_dto import ModelDto


class ImportResourcesTest(unittest.TestCase):

    def test_import_from_cyjax_namespace(self):
        from cyjax import Dashboard, DataBreach, LeakedEmail, IncidentReport, IndicatorOfCompromise, MaliciousDomain, \
            Paste, SocialMedia, TailoredReport, ThreatActor, TorExitNode, Tweet, Supplier, Tier

        self.assertIsInstance(Dashboard(), Resource)
        self.assertIsInstance(DataBreach(), Resource)
        self.assertIsInstance(LeakedEmail(), Resource)
        self.assertIsInstance(IncidentReport(), Resource)
        self.assertIsInstance(IndicatorOfCompromise(), Resource)
        self.assertIsInstance(MaliciousDomain(), Resource)
        self.assertIsInstance(TailoredReport(), Resource)
        self.assertIsInstance(Paste(), Resource)
        self.assertIsInstance(SocialMedia(), Resource)
        self.assertIsInstance(ThreatActor(), Resource)
        self.assertIsInstance(TorExitNode(), Resource)
        self.assertIsInstance(Tweet(), Resource)
        self.assertIsInstance(Supplier(), Resource)
        self.assertIsInstance(Tier(), Resource)

    def test_import_from_resources_namespace(self):
        from cyjax.resources import Dashboard, DataBreach, LeakedEmail, IncidentReport, IndicatorOfCompromise, \
            MaliciousDomain, Paste, SocialMedia, TailoredReport, ThreatActor, TorExitNode, Tweet, Supplier, Tier

        self.assertIsInstance(Dashboard(), Resource)
        self.assertIsInstance(DataBreach(), Resource)
        self.assertIsInstance(LeakedEmail(), Resource)
        self.assertIsInstance(IncidentReport(), Resource)
        self.assertIsInstance(IndicatorOfCompromise(), Resource)
        self.assertIsInstance(MaliciousDomain(), Resource)
        self.assertIsInstance(TailoredReport(), Resource)
        self.assertIsInstance(Paste(), Resource)
        self.assertIsInstance(SocialMedia(), Resource)
        self.assertIsInstance(ThreatActor(), Resource)
        self.assertIsInstance(TorExitNode(), Resource)
        self.assertIsInstance(Tweet(), Resource)
        self.assertIsInstance(Supplier(), Resource)
        self.assertIsInstance(Tier(), Resource)

    def test_import_from_data_breach_namespace(self):
        from cyjax.resources.data_breach import DataBreach, DataBreachDto, DataBreachListDto

        self.assertIsInstance(DataBreach(), Resource)
        self.assertIsInstance(DataBreachDto(), ModelDto)
        self.assertIsInstance(DataBreachListDto(), ModelDto)

    def test_import_from_incident_report_namespace(self):
        from cyjax.resources.incident_report import IncidentReport, IncidentReportDto

        self.assertIsInstance(IncidentReport(), Resource)
        self.assertIsInstance(IncidentReportDto(), ModelDto)

    def test_import_from_indicator_of_compromise_namespace(self):
        from cyjax.resources.indicator_of_compromise import IndicatorOfCompromise, IndicatorDto

        self.assertIsInstance(IndicatorOfCompromise(), Resource)
        self.assertIsInstance(IndicatorDto(), ModelDto)

    def test_import_from_malicious_domain_namespace(self):
        from cyjax.resources.malicious_domain import MaliciousDomain

        self.assertIsInstance(MaliciousDomain(), Resource)

    def test_import_from_tailored_report_namespace(self):
        from cyjax.resources.tailored_report import TailoredReport

        self.assertIsInstance(TailoredReport(), Resource)

    def test_import_from_paste_namespace(self):
        from cyjax.resources.paste import Paste

        self.assertIsInstance(Paste(), Resource)

    def test_import_from_social_media_namespace(self):
        from cyjax.resources.social_media import SocialMedia, SocialMediaDto

        self.assertIsInstance(SocialMedia(), Resource)
        self.assertIsInstance(SocialMediaDto(), ModelDto)

    def test_import_from_threat_actor_namespace(self):
        from cyjax.resources.threat_actor import ThreatActor

        self.assertIsInstance(ThreatActor(), Resource)

    def test_import_from_tor_exit_node_namespace(self):
        from cyjax.resources.tor_exit_node import TorExitNode

        self.assertIsInstance(TorExitNode(), Resource)

    def test_import_from_tweet_namespace(self):
        from cyjax.resources.tweet import Tweet

        self.assertIsInstance(Tweet(), Resource)

    def test_import_from_third_party_risk_namespace(self):
        from cyjax.resources.third_party_risk import Supplier, Tier, TierDto, SupplierDto, SupplierListDto

        self.assertIsInstance(Supplier(), Resource)
        self.assertIsInstance(Tier(), Resource)
        self.assertIsInstance(TierDto(), ModelDto)
        self.assertIsInstance(SupplierDto(), ModelDto)
        self.assertIsInstance(SupplierListDto(), ModelDto)

    def test_import_from_dashboard_namespace(self):
        from cyjax.resources.dashboard import Dashboard, DashboardDto, WidgetDto

        self.assertIsInstance(Dashboard(), Resource)
        self.assertIsInstance(DashboardDto(), ModelDto)
        self.assertIsInstance(WidgetDto(), ModelDto)
