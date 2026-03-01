import logging
import os
from flask import has_request_context, g
from app import db
from app.models import AILog

def setup_logger(name):
    log_dir = os.path.join(os.path.dirname(__file__), '../../logs')
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(os.path.join(log_dir, f'{name}.log'))
    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

def log_ai_interaction(module, prompt, response, model='claude-3-5-sonnet', 
                       product_id=None, proposal_id=None, order_id=None,
                       success=True, error_message=None, latency_ms=None,
                       auto_commit=True):
    try:
        request_id = getattr(g, 'request_id', None) if has_request_context() else None
        ai_log = AILog(
            module=module,
            prompt=prompt,
            response=response,
            model=model,
            product_id=product_id,
            proposal_id=proposal_id,
            order_id=order_id,
            success=success,
            error_message=error_message,
            latency_ms=latency_ms,
            request_id=request_id
        )
        db.session.add(ai_log)
        if auto_commit:
            db.session.commit()
        return ai_log
    except Exception as e:
        logging.getLogger('ai_log').exception('ai_log_write_failed module=%s', module)
        raise
