import sched
import time
from lxml import html
import requests
from pushbullet import Pushbullet

API_KEY = ''
pb = Pushbullet(API_KEY)

earliest_day_before_mid = ""
earliest_day_before_north = ""
earliest_day_before_stress = ""


def send_message(title, body):
    pb.push_note(title, body)


def get_earliest_days():
    global earliest_day_before_mid
    global earliest_day_before_north
    global earliest_day_before_stress

    # Request the page
    page = requests.get('https://www.service.bremen.de/dienstleistungen/personalausweis-beantragen-8363')
    tree = html.fromstring(page.content)
    earliest_day_before_north = tree.xpath('//*[@id="collapse-stellen"]/div/div/ul/li[3]/text()[3]')
    earliest_day_before_mid = tree.xpath('//*[@id="collapse-stellen"]/div/div/ul/li[2]/text()[3]')
    earliest_day_before_stress = tree.xpath('//*[@id="collapse-stellen"]/div/div/ul/li[4]/text()[3]')


def check_for_new_date():
    page = requests.get('https://www.service.bremen.de/dienstleistungen/personalausweis-beantragen-8363')
    tree = html.fromstring(page.content)
    earliest_day_before_north_temp = tree.xpath('//*[@id="collapse-stellen"]/div/div/ul/li[3]/text()[3]')
    earliest_day_before_mid_temp = tree.xpath('//*[@id="collapse-stellen"]/div/div/ul/li[2]/text()[3]')
    earliest_day_before_stress_temp = tree.xpath('//*[@id="collapse-stellen"]/div/div/ul/li[4]/text()[3]')
    if earliest_day_before_north_temp != earliest_day_before_north:
        return (True, earliest_day_before_north_temp, "BürgerServiceCenter-Nord")
    elif earliest_day_before_mid_temp != earliest_day_before_mid:
        return (True, earliest_day_before_mid_temp, "BürgerServiceCenter-Mitte")
    elif earliest_day_before_stress_temp != earliest_day_before_stress:
        return (True, earliest_day_before_stress_temp, "BürgerServiceCenter-Stresemannstr")
    else:
        return (False, None, None)


def loop(scheduler):
    # schedule the next call first
    scheduler.enter(300, 1, loop, (scheduler,))
    print("Searching...")
    if check_for_new_date()[0]:
        send_message("HINWEIS!", f'Neuer Termin beim {check_for_new_date()[2]} am {check_for_new_date()[1]}!')
        get_earliest_days()


get_earliest_days()
my_scheduler = sched.scheduler(time.time, time.sleep)
my_scheduler.enter(300, 1, loop, (my_scheduler,))
my_scheduler.run()
