from pathlib import Path
from robocorp import workitems
from robocorp.tasks import task
from Log.logs import Logs
from webdriver_util.webdrv_util import *
from dotenv import load_dotenv
from tasks_methods.methods import ExcelOtherMethods, ProducerMethods, ScraperMethods

load_dotenv("config\.env")
logger = Logs.Returnlog(os.getenv("name_app"), "Tasks")


@task
def producer():
    try:
        logger.info("Initial create workitem")
        payload = get_csv_produce_work_item()
        logger.info("End of create workitem")
        return payload
    except ValueError as e:
        logger.critical(f"ValueError: {e}")
        return None


@task
def scrapper():
    """Process all the produced input Work Items from the previous step."""
    pay = workitems.inputs.current
    if pay:
        logger.info("The current item from the work item has been retrieved")
    driver = get_driver(site_url=os.getenv("site_url"), headless=os.getenv("headless"))
    initial_search = ScraperMethods.inicial_search(
        driver=driver, phrase=pay.phrase_test
    )
    if initial_search:
        logger.info("Initial search done")
        logger.info("Starting fine searching")

        # Perform fine search
        fine_searching = ScraperMethods.fine_search(
            driver=driver,
            section=pay.section,
            sort_by=pay.sort_by,
        )
        if fine_searching:
            logger.info("Fine searching done")
            logger.info("Starting to collect articles")

            if pay.results > 0:
                logger.info(f"{pay.results} results will be collected")

            # Collect articles
            coll_articles = ScraperMethods.collect_articles(
                driver=driver, results=pay.results
            )
            if coll_articles:
                logger.info("Preparing articles to save")

                # Prepare articles for saving
                articles_to_save = ExcelOtherMethods.prepare_articles(
                    list_articles=coll_articles, phrase=pay.phrase_test
                )
                if articles_to_save:
                    logger.info("Saving articles to Excel")

                    # Export articles to Excel
                    ExcelOtherMethods.export_excel(articles_to_save)
            else:
                logger.critical("There are problems to generate articles collection")
        else:
            logger.critical(
                f"There are no search results with the phrase: {pay.phrase_test}"
            )
    else:
        logger.critical("There is a problem with a inicial search")


def get_csv_produce_work_item()->str:
    payload = ProducerMethods.read_csv_create_work_item()
    return payload
