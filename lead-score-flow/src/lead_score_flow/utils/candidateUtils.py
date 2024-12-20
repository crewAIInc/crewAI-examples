from typing import List

from lead_score_flow.types import Candidate, CandidateScore, ScoredCandidate


def combine_candidates_with_scores(
    candidates: List[Candidate], candidate_scores: List[CandidateScore]
) -> List[ScoredCandidate]:
    """
    Combine the candidates with their scores using a dictionary for efficient lookups.
    """
    print("COMBINING CANDIDATES WITH SCORES")
    print("SCORES:", candidate_scores)
    print("CANDIDATES:", candidates)
    # Create a dictionary to map score IDs to their corresponding CandidateScore objects
    score_dict = {score.id: score for score in candidate_scores}
    print("SCORE DICT:", score_dict)

    scored_candidates = []
    for candidate in candidates:
        score = score_dict.get(candidate.id)
        if score:
            scored_candidates.append(
                ScoredCandidate(
                    id=candidate.id,
                    name=candidate.name,
                    email=candidate.email,
                    bio=candidate.bio,
                    skills=candidate.skills,
                    score=score.score,
                    reason=score.reason,
                )
            )

    print("SCORED CANDIDATES:", scored_candidates)
    return scored_candidates
