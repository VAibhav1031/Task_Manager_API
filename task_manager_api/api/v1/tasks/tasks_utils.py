from task_manager_api.models import Task
from datetime import timezone, datetime
from dateutil import parser
import logging
from sqlalchemy import and_
from task_manager_api.error_handler import internal_server_error, bad_request


logger = logging.getLogger(__name__)


def parse_query_date(value: str, end_of_day: bool = False):
    dt = None
    try:
        if len(value) == 10:  # YYYY-DD-MM
            dt = datetime.strptime(value, "%Y-%m-%d")
            if end_of_day:
                dt = dt.replace(
                    hour=23,
                    minute=59,
                    second=59,
                    tzinfo=timezone.utc,
                )
            else:
                dt = dt.replace(hour=0, minute=0, second=0,
                                tzinfo=timezone.utc)
        else:
            # whaat if  frontend guy said lets give the whole date time , but if he missed the timezone stamp
            dt = parser.isoparse(value)

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            else:
                dt = dt.astimezone(timezone.utc)

    except Exception as e:
        logger.error(
            f"Error related to the Parsing of date from the client :{e}")
        return internal_server_error("Parsing date Query ")

    logger.info(f"HEre is the parsed dt letss : {dt}")
    return dt


def filter_manager(completion, title: str, after_str: str, before_str: str, query):
    after, before = None, None
    try:
        if after_str:
            # It is  still object which is return but that object has peice of info that will use when  compare in query
            # Z is stand for the 'ZULU' which is bit common for the military and all and normal use also , python library doesnt have any way
            # to handle that or something so we replace that thing with notrmal one s
            after = parse_query_date(after_str, end_of_day=False)
        if before_str:
            before = parse_query_date(before_str, end_of_day=True)

    except Exception as e:
        logger.error(f"Invalid datetime format {e}")
        return bad_request(
            type="InvalidDatetime",
            msg="Invalid Datetime used other than the standard one",
            details=str(e),
        )

    if completion is not None:
        normalized = completion.lower()
        if normalized in ("true", "1", "yes"):
            query = query.filter(Task.completion.is_(True))
        elif normalized in ("false", "0", "no"):
            query = query.filter(Task.completion.is_(False))

    # postgres based
    # if title is not None:
    #     query = query.filter(Task.title.ilike(f"%{title}%"))

    if title:
        query = query.filter(Task.title == title)

    if after and before:
        query = query.filter(
            and_(Task.created_at >= after, Task.created_at <= before))
    elif after:
        query = query.filter(Task.created_at >= after)

    elif before:
        query = query.filter(Task.created_at <= before)

    return query
