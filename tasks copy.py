from Log.logs import Logs
from webdriver_util.webdrv_util import *
from dotenv import load_dotenv
from tasks_methods.methods import ExcelOtherMethods, ProducerMethods, ScraperMethods

load_dotenv("config\.env")
logger = Logs.Returnlog(os.getenv("name_app"), "Tasks")

def get_csv_produce_work_item():
    ProducerMethods.read_csv_create_work_item()



def scraper_and_output_file():
    pay = ProducerMethods.read_csv_create_work_item()
    if pay:
        logger.info("The current item from the work item has been retrieved")
    driver = get_driver(site_url=os.getenv('site_url'))
    initial_search = ScraperMethods.inicial_search(
        driver=driver, phrase=pay.phrase_test
    )
    if initial_search:
        logger.info("Initial search done")
        logger.info("Starting fine searching")
        fine_searching, data_range_ret= ScraperMethods.fine_search(
            driver=driver,
            phrase=pay.phrase_test,
            section=pay.section,
            data_range=pay.data_range,
            sort_by=pay.sort_by,
        )
        if fine_searching:
            logger.info("Fine searching done")
            logger.info("Starting collect articles")
            if data_range_ret==0: 
                logger.info("Actual Page results will be collected")
            elif data_range_ret ==1:
                if pay.results>0:
                    logger.info(f"{pay.results} will be collected")
            elif data_range_ret==2:
                logger.info("All results will be collected")
            coll_articles = ScraperMethods.collect_articles(driver=driver, data_range= pay.results)
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

scraper_and_output_file()