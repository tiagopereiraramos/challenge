from robocorp.tasks import task
from webdriver_util.webdrv_util import *
from Log.logs import Logs
from tasks_methods.methods import ExcelOtherMethods, ScraperMethods
from dotenv import load_dotenv
from robocorp import storage, workitems
from helpers.payload import Payload

load_dotenv("config/.env")

@task
def produce_workitems():
    logger.info("The current item from the work item has been created")
    pass

