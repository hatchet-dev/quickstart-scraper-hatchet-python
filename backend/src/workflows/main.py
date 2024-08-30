from .hatchet import hatchet
from .scraper_workflow import ScraperWorkflow, TechCrunchAIScraperWorkflow, GoogleNewsScraperWorkflow


def start():
    worker = hatchet.worker("scraper-worker")
    worker.register_workflow(ScraperWorkflow())
    worker.register_workflow(TechCrunchAIScraperWorkflow())
    worker.register_workflow(GoogleNewsScraperWorkflow())
    worker.start()