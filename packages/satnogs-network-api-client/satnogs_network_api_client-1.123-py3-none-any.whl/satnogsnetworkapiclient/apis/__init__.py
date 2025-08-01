
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from .api.station_registration_api import StationRegistrationApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from satnogsnetworkapiclient.api.station_registration_api import StationRegistrationApi
from satnogsnetworkapiclient.api.configuration_api import ConfigurationApi
from satnogsnetworkapiclient.api.jobs_api import JobsApi
from satnogsnetworkapiclient.api.observations_api import ObservationsApi
from satnogsnetworkapiclient.api.stations_api import StationsApi
from satnogsnetworkapiclient.api.transmitters_api import TransmittersApi
