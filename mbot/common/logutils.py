import logging

from mbot.common.errcode import ErrCode


def print_error(err_code: ErrCode, message_args=None, logger=None):
    if not err_code:
        return
    if logger:
        logger.error(err_code.message(message_args))
    else:
        logging.error(err_code.message(message_args))
