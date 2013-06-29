from django.core.management.base import BaseCommand
from django.db import connections

from symposion.reviews.models import ProposalResult, promote_proposal


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        accepted_proposals = ProposalResult.objects.filter(status="accepted")
        accepted_proposals = accepted_proposals.order_by("proposal")
        
        for result in accepted_proposals:
            promote_proposal(result.proposal)
