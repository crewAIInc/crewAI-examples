#!/usr/bin/env python
import sys
from match_to_proposal.crew import MatchToProposalCrew


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'path_to_jd': './src/match_to_proposal/data/mlswejd.md',
         'path_to_hp': './src/match_to_proposal/data/hp.md'
    }
    MatchToProposalCrew().crew().kickoff(inputs=inputs)