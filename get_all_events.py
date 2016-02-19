#!/usr/bin/python3
import facebook
import datetime
import codecs  # for russian character
import webbrowser

__author__ = 'adiro'


def get_all_future_user_events(access_token):
    graph = facebook.GraphAPI(access_token = access_token)
    profile = graph.get_object('me')
    events_rsvpd = graph.get_connections(profile['id'], 'events')
    events_not_replied = graph.get_connections(profile['id'], 'events/not_replied/?since=now')
    events_created = graph.get_connections(profile['id'], 'events/created?since=now')
    events_maybe = graph.get_connections(profile['id'], 'events/maybe?since=now')
    events_liked_pages = get_liked_pages_future_events(access_token)
    all_events = events_rsvpd['data'] + events_not_replied['data'] + events_created['data'] + \
        events_maybe['data'] + events_liked_pages

    # delete duplicates
    seen = set()
    new_events = []
    for d in all_events:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_events.append(d)

    return new_events


def get_liked_pages_future_events(access_token):
    graph = facebook.GraphAPI(access_token = access_token)
    profile = graph.get_object('me')
    liked_pages = graph.get_connections(profile['id'], 'likes?limit=10000')
    liked_pages = liked_pages['data']
    events_liked_pages = []
    for page in liked_pages:
        events_liked_page = graph.get_connections(page['id'], 'events?since=now')
        events_liked_page = events_liked_page['data']
        if events_liked_page:  # page has events
            events_liked_pages = events_liked_pages + events_liked_page[:]
    return events_liked_pages


def parse_event_time(events):
    for event in events:
        event['min'] = event['start_time'][14:16]
        event['hour'] = event['start_time'][11:13]
        event['day'] = event['start_time'][8:10]
        event['month'] = event['start_time'][5:7]
        event['year'] = event['start_time'][0:4]
        event['date_obj'] = datetime.date(int(event['year']),int(event['month']),int(event['day']))

    return events


def events_in_the_next_num_day(num, events):
    today = datetime.date.today()
    date_in_num_days = today + datetime.timedelta(days=+num)
    new_event_list = []

    for event in events:
        if event['date_obj'] <= date_in_num_days and event['date_obj'] >= today:
            new_event_list.append(event)

    return new_event_list


def sort(events):
    return sorted(events, key=lambda k: k['date_obj'])


def get_event_info2txt_file(access_token, num_of_days_ahead):
    events = get_all_future_user_events(access_token)
    events = parse_event_time(events)
    events = events_in_the_next_num_day(num_of_days_ahead, events)
    events = sort(events)
    info_file = codecs.open('info_file', 'w', 'utf-16')
    first_event = events[0]
    day1 = first_event['day']
    info_file.writelines(first_event['day']+'.'+first_event['month']+':\n\n')

    for event in events:
        day2 = event['day']
        if day2 != day1:
            info_file.writelines(event['day']+'.'+event['month']+':\n\n')
            day1 = day2
        event_url = 'https://www.facebook.com/events/' + event['id']
        info_file.writelines('\n'.join([event['name'] + ' ', event.get('location', ''), event_url]))
        info_file.writelines('\n\n')

    info_file.close()
    return info_file

#access_token = input("go to https://developers.facebook.com/tools/explorer/ . press 'get user access token. mark the checkbox user_events, and pres 'get access token'. copy and paste the access token here (the long list of letters and numbers: ")
#days = input('This will get all the events in the next days. How me days ahead do you want?')
access_token = 'CAACEdEose0cBAJuRmOqgCuFmWWblvAHiFgTOZCXGucFJ9i1iNjqT1tHxOhTEhwFSxzcFjS6XEseAAqeDpW8xcNzVesqs5Gti7JCoZChZCVi3YSn7s7syu6I1KNAI0f27paWfCkQhPOZBUAP1TZAbME6rlHuZA0NtlmVDRqmeNZAQt97mZC3f5UMgJRAnZAtKc7YZBJNforcP0QyAZDZD'
days = 8
get_event_info2txt_file(access_token, int(days))
webbrowser.open("info_file")