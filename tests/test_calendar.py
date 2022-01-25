import datetime
import io
import textwrap

from util import parse_yaml

from yaml2ics import events_to_calendar, files_to_calendar


def test_calendar_structure():
    cal = events_to_calendar([])
    cal_str = cal.serialize()
    assert cal_str.startswith('BEGIN:VCALENDAR')
    assert cal_str.endswith('END:VCALENDAR')

def test_calendar_event():
    cal = files_to_calendar(
        [io.StringIO(textwrap.dedent(
            '''
            events:
              - summary: Earth Day
                begin: 2021-04-22
                url: https://earthday.org
                location: Earth
            '''
        ))]
    )
    cal_str = cal.serialize()
    assert cal_str.startswith('BEGIN:VCALENDAR')
    assert 'SUMMARY:Earth Day' in cal_str
    assert cal_str.endswith('END:VCALENDAR')

def test_calendar_default_timezone():
    cal = files_to_calendar(
        [io.StringIO(textwrap.dedent(
            '''
            meta:
              tz: Europe/Helsinki

            events:
              - summary: New year's day
                begin: 2022-01-01 00:00:00
                duration: {hours: 1}

              - summary: February 1
                begin: 2022-02-01 00:00:00 +02:00
                duration: {hours: 1}
            '''
        ))]
    )
    cal_str = cal.serialize()
    assert cal_str.startswith('BEGIN:VCALENDAR')
    assert 'SUMMARY:New year' in cal_str
    # It is possible that the ics-py TZID string changes, but hopefully this
    # substring is fairly safe to test against.
    assert 'Europe/Helsinki:20220101T000000' in cal_str
    # Second event: explicit UTC offset specified.
    assert '"UTC+02:00":20220201T000000' in cal_str
    assert cal_str.endswith('END:VCALENDAR')

    # Test again by normalizing to UTC.  Helsinki is two hours ahead, so the
    # times should be 22:00:00.
    cal.normalize(datetime.timezone.utc)
    cal_norm_str = cal.serialize()
    # 1 Feb midnight
    assert 'DTSTART:20211231T220000Z' # 1 jan
    assert 'DTSTART:20220131T220000Z' # 1 feb