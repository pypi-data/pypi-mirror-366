# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from satnogsnetworkapiclient.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from satnogsnetworkapiclient.model.demod_data import DemodData
from satnogsnetworkapiclient.model.inline_object import InlineObject
from satnogsnetworkapiclient.model.inline_object1 import InlineObject1
from satnogsnetworkapiclient.model.inline_response200 import InlineResponse200
from satnogsnetworkapiclient.model.inline_response400 import InlineResponse400
from satnogsnetworkapiclient.model.job import Job
from satnogsnetworkapiclient.model.new_observation import NewObservation
from satnogsnetworkapiclient.model.observation import Observation
from satnogsnetworkapiclient.model.paginated_observation_list import PaginatedObservationList
from satnogsnetworkapiclient.model.patched_observation import PatchedObservation
from satnogsnetworkapiclient.model.station import Station
from satnogsnetworkapiclient.model.station_antenna import StationAntenna
from satnogsnetworkapiclient.model.station_configuration import StationConfiguration
from satnogsnetworkapiclient.model.status_enum import StatusEnum
from satnogsnetworkapiclient.model.transmitter import Transmitter
from satnogsnetworkapiclient.model.transmitter_stats import TransmitterStats
from satnogsnetworkapiclient.model.transmitter_status_enum import TransmitterStatusEnum
from satnogsnetworkapiclient.model.transmitter_type_enum import TransmitterTypeEnum
from satnogsnetworkapiclient.model.update_observation import UpdateObservation
from satnogsnetworkapiclient.model.waterfall_status_enum import WaterfallStatusEnum
