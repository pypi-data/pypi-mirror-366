__author__ = 'Cyjax Ltd.'
__version__ = '2.1.0'
__email__ = 'github@cyjax.com'
__contact__ = 'github@cyjax.com'

from cyjax.exceptions import ResponseErrorException, InvalidDateFormatException, ApiKeyNotFoundException
from cyjax.resources import CaseManagement, Dashboard, DataBreach, LeakedEmail, IncidentReport, IndicatorOfCompromise, \
    MaliciousDomain, Paste, SocialMedia, Supplier, TailoredReport, Tier, TorExitNode, Tweet, ThreatActor

api_key = None  # The global API key for the Cyjax API.
api_url = None  # The base URL for the Cyjax API.
proxy_settings = None  # The proxy settings.
verify_ssl = True  # Whether to verify SSL certificate when doing API calls.
client_name = None  # The name of the client using SDK. Will be added to API calls User-Agent header.
