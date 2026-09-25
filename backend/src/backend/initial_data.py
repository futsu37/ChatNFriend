import logging

from sqlmodel import Session

from backend.core.database import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init() -> None:
    with Session(engine) as session:
        init_db(session)

def main() -> None:
    logger.info("Start initialing data")
    init()
    logger.info("Finish initialing data")

    
if __name__ == "__main__":
    main()