from robocorp.tasks import task
from tasks_methods.methods import ProducerMethods
from webdriver_util.webdrv_util import *
from dotenv import load_dotenv

load_dotenv("config/.env")

@task
def produce_workitems():
    get_csv_produce_work_item()
    logger.info("The current item from the work item has been created")
    


def get_csv_produce_work_item():
    ProducerMethods.read_csv_create_work_item()