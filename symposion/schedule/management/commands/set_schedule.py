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


def create_talk(day, time, length, room, id_, kind=None, fullwidth=False):
    print "create_talk", day, time, length, room, id_, fullwidth
    slot = models.Slot(
        id=id_,
        day_id=day,
        kind=kind,
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
        id=id_,
        slot=slot,
        title=proposal.title,
        abstract=proposal.abstract,
        description=proposal.description,
        speaker=proposal.speaker,
        proposal_base=proposal,
        section=talk_section,
    )
    presentation.save()
    for s in proposal.additional_speakers.all():
        presentation.additional_speakers.add(s)


slot_id = autoincrement(start=1000)

SLOT_KINDS = {
    # XXX WARNING: MAKE SURE THAT SlotKind.normal_labels IS ALSO CHANGED
    "lunch": models.SlotKind(label="Lunch"),
    "talk20": models.SlotKind(label="Talk"),
    "talk40": models.SlotKind(label="Talk"),
    "tutorial": models.SlotKind(label="Tutorial"),
    "messages": models.SlotKind(label="Messages"),
    "keynote": models.SlotKind(label="Keynote"),
    "lightning": models.SlotKind(label="Lightning talk"),
}


def create_slot(day, time, length, room, message, kind=None, fullwidth=False):
    print "create_slot", day, time, length, room, message, fullwidth
    slot = models.Slot(
        id=slot_id.next(),
        day_id=day,
        kind=kind,
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
        kind = SLOT_KINDS["talk40"]
        create_talk(day, time, 40, room, int(talk40.group('id')), kind=kind)
    elif talk:
        kind = SLOT_KINDS["talk20"]
        create_talk(day, time, 20, room, int(talk.group('id')), kind=kind)
    elif lightning:
        kind = SLOT_KINDS["lightning"]
        for (offset, length), id_ in zip([(0, 7), (7, 7), (14, 6)], lightning):
            if id_ == '??':
                create_slot(
                    day,
                    get_end(time, offset),
                    length,
                    room,
                    'Lightning Talk',
                    kind=kind)
            else:
                create_talk(
                    day,
                    get_end(time, offset),
                    length,
                    room,
                    int(id_),
                    kind=kind)
    elif keynote:
        kind = SLOT_KINDS["keynote"]
        create_talk(day, time, 45, room, int(keynote.group('id')), kind=kind, fullwidth=True)
    elif tutorial:
        kind = SLOT_KINDS["tutorial"]
        create_talk(day, time, int(tutorial.group('length')), room, int(tutorial.group('id')), kind=kind)
    elif lunch:
        kind = SLOT_KINDS["lunch"]
        create_slot(day, time, 90, room, 'Lunch', kind=kind, fullwidth=True)
    elif break_:
        #create_slot(day, time, int(break_.group('length')), room, 'Break')
        pass
    elif messages:
        kind = SLOT_KINDS["messages"]
        create_slot(day, time, int(messages.group('length')), room, messages.group('message'), kind, fullwidth=True)
    else:
        print "UNKNOWN KIND:", talk40, talk, lightning, keynote, tutorial, lunch, break_, content

class Command(BaseCommand):

    def cleanup(self):
        # All of these will be re-created from scratch by the
        # script.
        models.SlotRoom.objects.all().delete()
        models.Presentation.objects.all().delete()
        models.Slot.objects.all().delete()
        models.SlotKind.objects.all().delete()

    def setup(self):
        for slot_kind in SLOT_KINDS.values():
            slot_kind.schedule_id = 2
            slot_kind.save()

    def handle(self, *args, **options):
        with transaction.commit_on_success():
            self.cleanup()
            self.setup()
            reader = filter(
                lambda x: x[0].startswith((
                    'Saturday', 'Sunday')),
                csv.reader(open(args[0])))
            for line in reader:
                day, time, length, content1, content2, content3 = line[:6]
                day = day_map[day]
                if content1:
                    do_room(day, time, 1, content1)
                if content2:
                    do_room(day, time, 2, content2)
                if content3:
                    do_room(day, time, 3, content3)
