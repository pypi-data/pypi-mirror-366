import datetime
from django.utils import timezone
from lino.api import rt, dd, _
from lino.modlib.publisher.choicelists import PublishingStates
from lino.utils import Cycler
from lino.utils.instantiator import Instantiator
from lorem import get_paragraph

TOPICS = (
    ("Cascaded Continuous Voting", dd.today(), "11:00"),
    ("Liquid democracy", dd.today(), "14:00"),
    ("Digital vs analog", dd.today(1), "11:00"),
    ("Software should be free", dd.today(1), "14:00"),
    ("Synodality", dd.today(2), "11:00"),
)


def objects():
    event = Instantiator("cal.Event").build
    page = Instantiator("publisher.Page").build
    robin = rt.models.users.User.objects.get(username='robin')

    event_type = Instantiator("cal.EventType").build
    company = Instantiator("contacts.Company").build

    synodalworld = company(name="Synodalworld.org")
    yield synodalworld

    con = event_type(planner_column=rt.models.cal.PlannerColumns.external,
                     is_appointment=False, fill_presences=False,
                     max_days=15, is_public=True,
                     **dd.str2kw("name", _("Conference")))
    yield con

    seminar = event_type(planner_column=rt.models.cal.PlannerColumns.external,
                         is_appointment=False, fill_presences=False,
                         default_duration="1:00", is_public=True,
                         **dd.str2kw("name", _("Seminar")))
    yield seminar

    sc_page = page(title="SynodalCon", body=get_paragraph(), publishing_state=PublishingStates.published)
    yield sc_page

    yield event(summary="SynodalCon", description="Conference arranged by synodalworld.org.", event_type=con,
                start_date=dd.today(), start_time="10:00", company=synodalworld, descriptive_page=sc_page,
                end_date=dd.today() + datetime.timedelta(days=3), user=robin)

    def add_seminar(summary, start_date, start_time):
        sc_page = page(title=summary, body=get_paragraph(), publishing_state=PublishingStates.published)
        yield sc_page
        yield event(summary=summary, event_type=seminar, start_date=start_date, start_time=start_time,
                    company=synodalworld, descriptive_page=sc_page, user=robin)

    for topic in TOPICS:
        yield add_seminar(*topic)
