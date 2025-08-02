"""Application configuration for ``gracedb.ligo.org``.

Inherits all settings from :mod:`gwcelery.conf.playground`, with the exceptions
below.
"""

from base64 import b64encode

from . import *  # noqa: F401, F403

condor_accounting_group = 'ligo.prod.o4.cbc.pe.bayestar'
"""HTCondor accounting group for Celery workers launched with condor_submit."""

expose_to_public = True
"""Set to True if events meeting the public alert threshold really should be
exposed to the public."""

igwn_alert_group = 'gracedb'
"""IGWN alert group."""

gracedb_host = 'gracedb.ligo.org'
"""GraceDB host."""

create_mattermost_channel = True
"""Create Mattermost channel in production"""

kafka_alert_config = {
    'scimma': {'url': 'kafka://kafka.scimma.org/igwn.gwalert',
               'suffix': 'avro', 'skymap_encoder': lambda _: _},
    'gcn': {'url': 'kafka://kafka.gcn.nasa.gov/igwn.gwalert',
            'suffix': 'json', 'skymap_encoder': lambda b:
            b64encode(b).decode('utf-8')}
}
"""Kafka broker configuration details"""

kafka_consumer_config = {
    'fermi_gbm_alert': {'url': 'kafka://kafka.gcn.nasa.gov/'
                        'gcn.classic.voevent.FERMI_GBM_ALERT',
                        'suffix': 'xml'},
    'fermi_gbm_flt_pos': {'url': 'kafka://kafka.gcn.nasa.gov/'
                          'gcn.classic.voevent.FERMI_GBM_FLT_POS',
                          'suffix': 'xml'},
    'fermi_gbm_gnd_pos': {'url': 'kafka://kafka.gcn.nasa.gov/'
                          'gcn.classic.voevent.FERMI_GBM_GND_POS',
                          'suffix': 'xml'},
    'fermi_gbm_fin_pos': {'url': 'kafka://kafka.gcn.nasa.gov/'
                          'gcn.classic.voevent.FERMI_GBM_FIN_POS',
                          'suffix': 'xml'},
    'fermi_gbm_subthresh': {'url': 'kafka://kafka.gcn.nasa.gov/'
                            'gcn.classic.voevent.FERMI_GBM_SUBTHRESH',
                            'suffix': 'xml'},
    'swift_bat_grb_pos_ack': {'url': 'kafka://kafka.gcn.nasa.gov/'
                              'gcn.classic.voevent.SWIFT_BAT_GRB_POS_ACK',
                              'suffix': 'xml'},
    'integral_wakeup': {'url': 'kafka://kafka.gcn.nasa.gov/'
                        'gcn.classic.voevent.INTEGRAL_WAKEUP',
                        'suffix': 'xml'},
    'integral_refined': {'url': 'kafka://kafka.gcn.nasa.gov/'
                         'gcn.classic.voevent.INTEGRAL_REFINED',
                         'suffix': 'xml'},
    'integral_offline': {'url': 'kafka://kafka.gcn.nasa.gov/'
                         'gcn.classic.voevent.INTEGRAL_OFFLINE',
                         'suffix': 'xml'},
    'snews': {'url': 'kafka://kafka.gcn.nasa.gov/gcn.classic.voevent.SNEWS',
              'suffix': 'xml'},
    'fermi_targeted': {'url': 'kafka://kafka.gcn.nasa.gov/'
                       'fermi.gbm.targeted.private.igwn', 'suffix': 'json'},
    'swift_targeted': {'url': 'kafka://kafka.gcn.nasa.gov/'
                       'gcn.notices.swift.bat.guano', 'suffix': 'json'},
    'svom_eclairs_alert': {'url': 'kafka://kafka.gcn.nasa.gov/'
                           'gcn.notices.svom.voevent.eclairs',
                           'suffix': 'json'}
}
"""Kafka consumer configuration details. The keys describe the senders of the
messages to be consumed. The values are a dictionary of the URL to listen to
and information about the message serializer."""

significant_alert_trials_factor = {
    'cbc': {'allsky': 6,
            'earlywarning': 4,
            'mdc': 6,
            'ssm': 3},
    'burst': {'allsky': 3,
              'bbh': 6}
}
"""Trials factor corresponding to trigger categories. The CBC AllSky and Burst
BBH searches are treated as one group with a common trials factor. CBC AllSky
pipelines are gstlal, pycbc, mbta, spiir, and raven. The Burst BBH pipeline
is cwb. CBC EarlyWarning pipelines are gstlal, pycbc, mbta, and spiir.
CBC SSM pipelines are gstlal, mbta, and raven.
The Burst AllSky searches are treated as one group with one
trials factor. The Burst AllSky piplines are cwb, mly, and raven."""

preliminary_alert_trials_factor = {
    'cbc': {'allsky': 7,
            'earlywarning': 4,
            'mdc': 4,
            'ssm': 2},
    'burst': {'allsky': 7,
              'bbh': 7}
}
"""Trials factor for less significant alert categories. The CBC AllSky, Burst
AllSky, and Burst BBH searches are all treated as one group with a shared
trials factor. CBC AllSky pipelines are gstlal, pycbc, mbta, and spiir.
Burst AllSky pipelines are cwb, and mly. The Burst BBH pipelines is cwb."""

preliminary_alert_far_threshold = {
    'cbc': {
        'allsky': 2 / (1 * 86400) * preliminary_alert_trials_factor['cbc']['allsky'],  # noqa: E501
        'earlywarning': -1 * float('inf'),
        'mdc': -1 * float('inf'),
        'ssm': -1 * float('inf')
    },
    'burst': {
        'allsky': 2 / (1 * 86400) * preliminary_alert_trials_factor
        ['burst']['allsky'],
        'bbh': 2 / (1 * 86400) * preliminary_alert_trials_factor
        ['burst']['bbh']
    },
    'test': {
        'allsky': 2 / (1 * 86400) * preliminary_alert_trials_factor
        ['cbc']['allsky'],
        'earlywarning': -1 * float('inf'),
        'ssm': -1 * float('inf')
    }
}
"""Group and search specific maximum false alarm rate to consider sending less
significant alerts. Trials factors are included here to ensure events are sent
with the false alarm rate initially listed and removing trials factors are from
the threshold calculation. A threshold of negative infinity disables alerts."""

raven_targeted_far_thresholds = {
    'GW': {
        'Fermi': preliminary_alert_far_threshold['cbc']['allsky'],
        'Swift': preliminary_alert_far_threshold['cbc']['allsky']
    },
    'GRB': {
        'Fermi': 1 / 10000,
        'Swift': 1 / 1000
    }
}
"""Max FAR thresholds used for the subthreshold targeted searches with Fermi
and Swift. Since we only listen to CBC low significance alerts, we use that
FAR threshold for now. Note that Swift current listens to events with the
threshold before and Fermi after trials factors."""

voevent_broadcaster_address = ':5341'
"""The VOEvent broker will bind to this address to send GCNs.
This should be a string of the form `host:port`. If `host` is empty,
then listen on all available interfaces."""

voevent_broadcaster_whitelist = ['capella2.gsfc.nasa.gov']
"""List of hosts from which the broker will accept connections.
If empty, then completely disable the broker's broadcast capability."""

llhoft_glob = '/dev/shm/kafka/{detector}/*.gwf'
"""File glob for low-latency h(t) frames."""

low_latency_frame_types = {'H1': 'H1_llhoft',
                           'L1': 'L1_llhoft',
                           'V1': 'V1_llhoft'}
"""Types of frames used in Parameter Estimation (see
:mod:`gwcelery.tasks.inference`) and in cache creation for detchar
checks (see :mod:`gwcelery.tasks.detchar`).
"""

high_latency_frame_types = {'H1': 'H1_HOFT_C00',
                            'L1': 'L1_HOFT_C00',
                            'V1': 'V1Online'}
"""Types of high latency frames used in Parameter Estimation
(see :mod:`gwcelery.tasks.inference`) and in cache creation for detchar
checks (see :mod:`gwcelery.tasks.detchar`).
"""

idq_channels = ['H1:IDQ-FAP_OVL_10_2048',
                'L1:IDQ-FAP_OVL_10_2048']
"""Low-latency iDQ false alarm probability channel names from live O3 frames"""

strain_channel_names = {'H1': 'H1:GDS-CALIB_STRAIN_CLEAN',
                        'L1': 'L1:GDS-CALIB_STRAIN_CLEAN',
                        'V1': 'V1:Hrec_hoft_16384Hz'}
"""Names of h(t) channels used in Parameter Estimation (see
:mod:`gwcelery.tasks.inference`)"""

sentry_environment = 'production'
"""Record this `environment tag
<https://docs.sentry.io/enriching-error-data/environments/>`_ in Sentry log
messages."""

only_alert_for_mdc = False
"""If True, then only sends alerts for MDC events. Useful for times outside
of observing runs."""

condor_retry_kwargs = dict(
    max_retries=None, retry_backoff=True, retry_jitter=True,
    retry_backoff_max=600
)
"""Retry settings of condor.submit task."""

rapidpe_settings = {
    'run_mode': 'online',
    'accounting_group': 'ligo.prod.o4.cbc.pe.lalinferencerapid',
    'use_cprofile': False
}
"""Config settings used for rapidpe"""
