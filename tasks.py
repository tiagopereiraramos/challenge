from robocorp.tasks import task
from webdriver_util.webdrv_util import *
from Log.logs import Logs
from tasks_methods.methods import ExcelOtherMethods, ScraperMethods
from dotenv import load_dotenv
from robocorp import storage, workitems
from helpers.payload import Payload

load_dotenv("config/.env")


@task
def scraper_and_output_file():
    """
    Task to perform web scraping and export the results to an Excel file.
    """
    # Initialize logger
    logger = Logs.Returnlog(storage.get_text("name_app"), "Tasks")
    pay = ScraperMethods.get_work_item()
    if pay:
        logger.info("The current item from the work item has been retrieved")

        # Initialize the Selenium driver
        driver = get_driver(site_url=storage.get_text("site_url"), headless=False)
        if driver:
            # Perform initial search
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
                        logger.critical(
                        f"There are problems to generate articles collection"
                    )        
                else:
                    logger.critical(
                        f"There are no search results with the phrase: {pay.phrase_test}"
                    )
            else:
                logger.critical(
                f"There is a problem with a inicial search"
            )
        else:
            logger.critical(
                f"There is a problem with a driver object"
            )
    else:
            logger.critical(
                f"There is a problem with a payback object"
            )

