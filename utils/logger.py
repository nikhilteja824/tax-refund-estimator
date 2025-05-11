import logging

logger = logging.getLogger("tax_refund_service")
logger.setLevel(logging.DEBUG) 


# To decide what format each log should be printed
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

#service.log
file_handler_all = logging.FileHandler("service.log")
file_handler_all.setLevel(logging.INFO)
file_handler_all.setFormatter(formatter)

#service-error.log
file_handler_errors = logging.FileHandler("service-error.log")
file_handler_errors.setLevel(logging.ERROR)
file_handler_errors.setFormatter(formatter)

#For console(Will not be use this for now)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler_all)
    logger.addHandler(file_handler_errors)
    logger.addHandler(console_handler)