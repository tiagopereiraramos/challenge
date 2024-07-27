from robocorp.tasks import task
from webdriver_util.webdrv_util import *
from dotenv import load_dotenv

load_dotenv("config/.env")

@task
def produce_workitems():
    logger.info("The current item from the work item has been created")
    

