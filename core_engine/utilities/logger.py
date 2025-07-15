import logging
import os

def setup_logger():
    logger = logging.getLogger('DeepMine')
    logger.setLevel(logging.DEBUG)
    
    # ملف الأخطاء
    error_handler = logging.FileHandler('logs/errors.json')
    error_handler.setFormatter(JsonFormatter())
    
    # ملف التفاعلات
    interaction_handler = logging.FileHandler('logs/interactions.json')
    interaction_handler.setFormatter(JsonFormatter())
    
    logger.addHandler(error_handler)
    logger.addHandler(interaction_handler)
    
    return logger

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'line': record.lineno
        })
        
def log_system_event(message: str, level: str = 'info'):
    """تسجيل حدث نظام"""
    logger = logging.getLogger('SystemLogger')
    if level == 'debug':
        logger.debug(message)
    elif level == 'warning':
        logger.warning(message)
    elif level == 'error':
        logger.error(message)
    elif level == 'critical':
        logger.critical(message)
    else:
        logger.info(message)