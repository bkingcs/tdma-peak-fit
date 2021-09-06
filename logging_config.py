"""
# REVIEW Documentation
"""
import logging
import logging.config


def configure_logger_env():
    """
    # REVIEW Documentation
    """
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'formatter': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                          'datefmt': '%m/%d/%Y %I:%M:%S %p'}
        },
        'handlers': {
            'stream_handler': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'formatter',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            'root': {
                'level': 'DEBUG',
                'handlers': ['stream_handler']
            },
            'main': {
                'level': 'DEBUG',
                'handlers': ['stream_handler'],
                'qualname': 'main',
                'propagate': 0
            },
            'controller': {
                'level': 'DEBUG',
                'handlers': ['stream_handler'],
                'qualname': 'controller',
                'propagate': 0
            },
            'scan': {
                'level': 'DEBUG',
                'handlers': ['stream_handler'],
                'qualname': 'scan',
                'propagate': 0
            }
        },
        'disable_existing_loggers': False
    })


def configure_logger_frz(log_path):
    """
    # REVIEW Documentation
    """
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'formatter': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                          'datefmt': '%m/%d/%Y %I:%M:%S %p'}
        },
        'handlers': {
            'stream_handler': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'formatter',
                'stream': 'ext://sys.stdout'
            },
            'file_handler': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'formatter',
                'filename': log_path,
                'maxBytes': 1024,
                'backupCount': 3
            }
        },
        'loggers': {
            'root': {
                'level': 'DEBUG',
                'handlers': ['stream_handler', 'file_handler']
            },
            'main': {
                'level': 'DEBUG',
                'handlers': ['stream_handler', 'file_handler'],
                'qualname': 'main',
                'propagate': 0
            },
            'controller': {
                'level': 'DEBUG',
                'handlers': ['stream_handler', 'file_handler'],
                'qualname': 'controller',
                'propagate': 0
            },
            'scan': {
                'level': 'DEBUG',
                'handlers': ['stream_handler', 'file_handler'],
                'qualname': 'scan',
                'propagate': 0
            }
        },
        'disable_existing_loggers': False
    })
