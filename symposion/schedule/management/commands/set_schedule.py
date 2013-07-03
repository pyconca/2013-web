import csv
import datetime
import re

from django.core.management.base import BaseCommand
from django.db import transaction

from symposion.conference.models import Section
from symposion.schedule import models
from symposion.proposals.models import ProposalBase


day_map = {
    'Saturday': 3,
    'Sunday': 4,
}


def autoincrement(start=1):
    i = start
    while True:
        yield i
        i += 1


def get_end(time, length):
    # I don't actually care which day, but timedeltas only work on
    # datetimes.
    return (
        datetime.datetime(2013, 8, 10, *map(int,time.split(':'))) +
        datetime.timedelta(minutes=length)
    ).strftime("%H:%M")


rooms = {
    r: models.Room.objects.get(pk=r)
    for r in (1, 2, 3)
}


talk_section = Section.objects.get(pk=2)


def create_talk(day, time, length, room, id_, fullwidth=False):
    print "create_talk", day, time, length, room, id_, fullwidth
    slot = models.Slot(
        id=id_,
        day_id=day,
        kind_id=1,
        start=time,
        end=get_end(time, length),
    )
    slot.save()
    models.SlotRoom(slot=slot, room=rooms[room]).save()
    if fullwidth:
        models.SlotRoom(slot=slot, room=rooms[2]).save()
        models.SlotRoom(slot=slot, room=rooms[3]).save()
    try:
        proposal = ProposalBase.objects.get(pk=id_)
    except:
        print "XXX Couldn't find ProposalBase(pk=%d)" % (id_,)
        return
    presentation = models.Presentation(
        slot=slot,
        title=proposal.title,
        abstract=proposal.abstract,
        description=proposal.description,
        speaker=proposal.speaker,
        proposal_base=proposal,
        section=talk_section,
    )
    #    additional_speakers=[
    #        s
    #        for s in proposal.additional_speakers.all()
    #        if s.status == 2
    #    ],
    presentation.save()



slot_id = autoincrement(start=1000)


def create_slot(day, time, length, room, message, fullwidth=False):
    print "create_slot", day, time, length, room, message, fullwidth
    slot = models.Slot(
        id=slot_id.next(),
        day_id=day,
        kind_id=2,
        start=time,
        end=get_end(time, length),
        content_override=message,
    )
    slot.save()
    models.SlotRoom(slot=slot, room=rooms[room]).save()
    if fullwidth:
        models.SlotRoom(slot=slot, room=rooms[2]).save()
        models.SlotRoom(slot=slot, room=rooms[3]).save()


talk40_re = re.compile(r'^A(?P<id>\d+):')
talk_re = re.compile(r'^B(?P<id>\d+):')
lightning_re = re.compile(r'^L(?P<id>\d+|\?\?):', re.M)
keynote_re = re.compile(r'^K(?P<id>\d+):')
tutorial_re = re.compile(r'^T(?P<id>\d+):(?P<length>\d+)')
lunch_re = re.compile(r'^lunch')
break_re = re.compile(r'^break (?P<length>\d+)')
messages_re = re.compile(r'^M:(?P<length>\d+) (?P<message>.*)')


def do_room(day, time, room, content):
    if content in ['Setup', 'SEEYA']:
        return
    talk40 = talk40_re.match(content)
    talk = talk_re.match(content)
    lightning = lightning_re.findall(content)
    keynote = keynote_re.match(content)
    tutorial = tutorial_re.match(content)
    lunch = lunch_re.match(content)
    break_ = break_re.match(content)
    messages = messages_re.match(content)
    if talk40:
        create_talk(day, time, 40, room, int(talk40.group('id')))
    elif talk:
        create_talk(day, time, 20, room, int(talk.group('id')))
    elif lightning:
        for (offset, length), id_ in zip([(0, 7), (7, 7), (14, 6)], lightning):
            if id_ == '??':
                create_slot(
                    day,
                    get_end(time, offset),
                    length,
                    room,
                    'Lightning Talk')
            else:
                create_talk(
                    day,
                    get_end(time, offset),
                    length,
                    room,
                    int(id_))
    elif keynote:
        create_talk(day, time, 45, room, int(keynote.group('id')), fullwidth=True)
    elif tutorial:
        create_talk(day, time, int(tutorial.group('length')), room, int(tutorial.group('id')))
    elif lunch:
        create_slot(day, time, 90, room, 'Lunch', fullwidth=True)
    elif break_:
        create_slot(day, time, int(break_.group('length')), room, 'Break')
    elif messages:
        create_slot(day, time, int(messages.group('length')), room, messages.group('message'), fullwidth=True)
    else:
        print talk40, talk, lightning, keynote, tutorial, lunch, break_, content

class Command(BaseCommand):

    def cleanup(self):
        # All of these will be re-created from scratch by the
        # script.
        models.SlotRoom.objects.all().delete()
        models.Presentation.objects.all().delete()
        models.Slot.objects.all().delete()

    def handle(self, *args, **options):
        with transaction.commit_on_success():
            self.cleanup()
            reader = filter(
                lambda x: x[0].startswith((
                    'Saturday', 'Sunday')),
                csv.reader(open(args[0])))
            slots = []
            for line in reader:
                day, time, length, content1, content2, content3 = line[:6]
                day = day_map[day]
                if content1:
                    do_room(day, time, 1, content1)
                if content2:
                    do_room(day, time, 2, content2)
                if content3:
                    do_room(day, time, 3, content3)

#import copy
#from cStringIO import StringIO
#import datetime
#schedule_f = StringIO(schedule_csv)
#slots = []
#
#
#slot_number = autoincrement()
#slot_room_number = autoincrement()
#
#
#def make_slot(day, time, length, kind):
#    return {
#        "pk": slot_number.next(),
#        "model": "schedule.slot",
#        "fields": {
#            "day": day,
#            "start": time,
#            "end": get_end(time, length),
#            "kind": kind,
#        },
#    }
#
#
#def make_room(slot, room):
#    return {
#        "pk": slot_room_number.next(),
#        "model": "schedule.slotroom",
#        "fields": {
#            "slot": slot,
#            "room": room,
#        },
#    }
#
#
#
#
#def do_lightning(day, time, length, room):
#    slots = []
#    for offset in range(0, length, 5):
#        slot = make_slot(
#            day=day, time=get_end(time, offset), length=5, kind=3)
#        slots.append(slot)
#        slots.append(make_room(slot['pk'], room))
#    return slots
#
#
#talk40_re = re.compile(r'^A(?P<id>\d+):')
#talk_re = re.compile(r'^B(?P<id>\d+):')
#lightning_re = re.compile(r'^L(?P<id>\d+|\?\?):')
#keynote_re = re.compile(r'^K(?P<id>\d+):')
#tutorial_re = re.compile(r'^T(?P<id>\d+):(?P<length>\d+)')
#
#
#def do_room(day, time, length, room, contents):
#    talk40 = talk40_re.match(contents)
#    talk = talk_re.match(contents)
#    lightning = lightning_re.search_all(contents)
#    keynote = keynote_re.match(contents)
#    tutorial = tutorial_re.match(contents)
#    if talk40:
#        slot = make_slot(day, time, length, kind=1)
#    elif contents == 'TALK 20':
#        slot = make_slot(day, time, length, kind=2)
#    elif contents == 'LIGHTNING 20':
#        return do_lightning(day, time, length, room)
#    elif 'keynote' in contents.lower():
#        slot = make_slot(day, time, length, kind=4)
#    elif 'tutorial' in contents.lower():
#        slot = make_slot(day, time, int(contents.split(' ')[1]), kind=5)
#    elif 'lunch' in contents.lower():
#        slot = make_slot(day, time, length, kind=6)
#    elif 'welcome to' in contents.lower():
#        slot = make_slot(day, time, length, kind=7)
#    elif 'morning messages' in contents.lower():
#        slot = make_slot(day, time, length, kind=7)
#    elif 'closing messages' in contents.lower():
#        slot = make_slot(day, time, length, kind=8)
#    elif 'closing ceremonies' in contents.lower():
#        slot = make_slot(day, time, length, kind=8)
#    else:
#        raise Exception("Unhandled " + contents)
#    return [slot, make_room(slot['pk'], room)]
#
#
#for line in csv.reader(schedule_f):
#    if line[0] not in ['Saturday', 'Sunday']:
#        continue
#    day, time, length, room1, room2, room3 = line[:6]
#    length = int(length)
#    if room1:
#        slots.extend(do_room(day, time, length, 1, room1))
#    if room2:
#        slots.extend(do_room(day, time, length, 2, room2))
#    if room3:
#        slots.extend(do_room(day, time, length, 3, room3))
#
#import json
#print json.dumps(slots, indent=4)
