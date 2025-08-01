SAMPLE_DICT_DATA: dict = {
    'Ai1': {
        'Ai2k1': 45,
        'Ai2k2': 'yes',
        'Ai2k3': "yes",
        'Ai2k4': '',
        'Ai2k5': ""
    },
    'Bi1': {
        'Bi2': {
            'Bi3': {
                'Bi3k1': 45,
                'Bi3k2': 'yes',
                'Bi3k3': "yes",
                'Bi3k4': '',
                'Bi3k5': ""
            }
        }
    },
    'Ci1': {},
    'Di1': {
        'Di2': {
            'Di3': {}
        }
    },
    'Ei1': '',
    'Fi1': ['a', 'b', 'c'],
    'Gi1': [0, 1, 2],
    'Hi1': [0, 'a', 'c', 4],
    'Ii1': [],
    'Ji1': [
        {
            'Ji1k1': 0,
            'Ji1k2': 'a'
        },
        {
            'Ji1k1': 0,
            'Ji1k2': 'a',
            'Ji1k3': ''
        }
    ]
}

SAMPLE_DICT_FLATTEN: dict = {
    'Ai1.Ai2k1': 45,
    'Ai1.Ai2k2': 'yes',
    'Ai1.Ai2k3': 'yes',
    'Ai1.Ai2k4': '',
    'Ai1.Ai2k5': '',
    'Bi1.Bi2.Bi3.Bi3k1': 45,
    'Bi1.Bi2.Bi3.Bi3k2': 'yes',
    'Bi1.Bi2.Bi3.Bi3k3': 'yes',
    'Bi1.Bi2.Bi3.Bi3k4': '',
    'Bi1.Bi2.Bi3.Bi3k5': '',
    'Ci1': {},
    'Di1.Di2.Di3': {},
    'Ei1': '',
    'Fi1.0': 'a',
    'Fi1.1': 'b',
    'Fi1.2': 'c',
    'Gi1.0': 0,
    'Gi1.1': 1,
    'Gi1.2': 2,
    'Hi1.0': 0,
    'Hi1.1': 'a',
    'Hi1.2': 'c',
    'Hi1.3': 4,
    'Ii1': [],
    'Ji1.0.Ji1k1': 0,
    'Ji1.0.Ji1k2': 'a',
    'Ji1.1.Ji1k1': 0,
    'Ji1.1.Ji1k2': 'a',
    'Ji1.1.Ji1k3': ''
}

SAMPLE_LIST_DATA: list = [
    {
        'Ai1': {
            'Ai2k1': 45,
            'Ai2k2': 'yes',
            'Ai2k3': "yes",
            'Ai2k4': '',
            'Ai2k5': ""
        },
        'Bi1': {
            'Bi2': {
                'Bi3': {
                    'Bi3k1': 45,
                    'Bi3k2': 'yes',
                    'Bi3k3': "yes",
                    'Bi3k4': '',
                    'Bi3k5': ""
                }
            }
        },
        'Ci1': {},
        'Di1': {
            'Di2': {
                'Di3': {}
            }
        },
        'Ei1': '',
        'Fi1': ['a', 'b', 'c'],
        'Gi1': [0, 1, 2],
        'Hi1': [0, 'a', 'c', 4],
        'Ii1': [],
        'Ji1': [
            {
                'Ji1k1': 0,
                'Ji1k2': 'a'
            },
            {
                'Ji1k1': 0,
                'Ji1k2': 'a',
                'Ji1k3': ''
            }
        ]
    },
    {
        'Ai1': {
            'Ai2k1': 45,
            'Ai2k2': 'yes',
            'Ai2k3': "yes",
            'Ai2k4': '',
            'Ai2k5': ""
        },
        'Bi1': {
            'Bi2': {
                'Bi3': {
                    'Bi3k1': 45,
                    'Bi3k2': 'yes',
                    'Bi3k3': "yes",
                    'Bi3k4': '',
                    'Bi3k5': ""
                }
            }
        },
        'Ci1': {},
        'Di1': {
            'Di2': {
                'Di3': {}
            }
        },
        'Ei1': '',
        'Fi1': ['a', 'b', 'c'],
        'Gi1': [0, 1, 2],
        'Hi1': [0, 'a', 'c', 4],
        'Ii1': [],
        'Ji1': [
            {
                'Ji1k1': 0,
                'Ji1k2': 'a'
            },
            {
                'Ji1k1': 0,
                'Ji1k2': 'a',
                'Ji1k3': ''
            }
        ]
    }
]

SAMPLE_LIST_FLATTEN: dict = {
    '0.Ai1.Ai2k1': 45,
    '0.Ai1.Ai2k2': 'yes',
    '0.Ai1.Ai2k3': 'yes',
    '0.Ai1.Ai2k4': '',
    '0.Ai1.Ai2k5': '',
    '0.Bi1.Bi2.Bi3.Bi3k1': 45,
    '0.Bi1.Bi2.Bi3.Bi3k2': 'yes',
    '0.Bi1.Bi2.Bi3.Bi3k3': 'yes',
    '0.Bi1.Bi2.Bi3.Bi3k4': '',
    '0.Bi1.Bi2.Bi3.Bi3k5': '',
    '0.Ci1': {},
    '0.Di1.Di2.Di3': {},
    '0.Ei1': '',
    '0.Fi1.0': 'a',
    '0.Fi1.1': 'b',
    '0.Fi1.2': 'c',
    '0.Gi1.0': 0,
    '0.Gi1.1': 1,
    '0.Gi1.2': 2,
    '0.Hi1.0': 0,
    '0.Hi1.1': 'a',
    '0.Hi1.2': 'c',
    '0.Hi1.3': 4,
    '0.Ii1': [],
    '0.Ji1.0.Ji1k1': 0,
    '0.Ji1.0.Ji1k2': 'a',
    '0.Ji1.1.Ji1k1': 0,
    '0.Ji1.1.Ji1k2': 'a',
    '0.Ji1.1.Ji1k3': '',
    '1.Ai1.Ai2k1': 45,
    '1.Ai1.Ai2k2': 'yes',
    '1.Ai1.Ai2k3': 'yes',
    '1.Ai1.Ai2k4': '',
    '1.Ai1.Ai2k5': '',
    '1.Bi1.Bi2.Bi3.Bi3k1': 45,
    '1.Bi1.Bi2.Bi3.Bi3k2': 'yes',
    '1.Bi1.Bi2.Bi3.Bi3k3': 'yes',
    '1.Bi1.Bi2.Bi3.Bi3k4': '',
    '1.Bi1.Bi2.Bi3.Bi3k5': '',
    '1.Ci1': {},
    '1.Di1.Di2.Di3': {},
    '1.Ei1': '',
    '1.Fi1.0': 'a',
    '1.Fi1.1': 'b',
    '1.Fi1.2': 'c',
    '1.Gi1.0': 0,
    '1.Gi1.1': 1,
    '1.Gi1.2': 2,
    '1.Hi1.0': 0,
    '1.Hi1.1': 'a',
    '1.Hi1.2': 'c',
    '1.Hi1.3': 4,
    '1.Ii1': [],
    '1.Ji1.0.Ji1k1': 0,
    '1.Ji1.0.Ji1k2': 'a',
    '1.Ji1.1.Ji1k1': 0,
    '1.Ji1.1.Ji1k2': 'a',
    '1.Ji1.1.Ji1k3': ''
}
