import robocorp.log as logger
from robocorp.tasks import task
from webdriver_util.webdrv_util import *

from tasks_methods.methods import ExcelOtherMethods, ProducerMethods, ScraperMethods

@task
def get_csv_produce_work_item():
    ProducerMethods.read_csv_create_work_item()


@task
def scraper_and_output_file():
    pay = ScraperMethods.get_work_item()
    if pay:
        logger.info("The current item from the work item has been retrieved")
    driver = get_chromedriver()
    initial_search = ScraperMethods.inicial_search(
        driver=driver, phrase=pay.phrase_test
    )
    if initial_search:
        logger.info("Initial search done")
        logger.info("Starting fine searching")
        fine_searching = ScraperMethods.fine_search(
            driver=driver,
            phrase=pay.phrase_test,
            section=pay.section,
            data_range=pay.data_range,
            sort_by=pay.sort_by,
        )
        if fine_searching:
            logger.info("Fine searching done")
            logger.info("Starting collect articles")
            coll_articles = ScraperMethods.collect_articles(driver=driver)
            if coll_articles:
                logger.info("Preparing articles to save")
                articles_to_save = ExcelOtherMethods.prepare_articles(
                    list_articles=coll_articles, phrase=pay.phrase_test
                )
                if articles_to_save:
                    logger.info("Saving articles to excel")
                    ExcelOtherMethods.export_excel(articles_to_save)
        else:
            logger.critical(f"There is no search results with phrase:")
