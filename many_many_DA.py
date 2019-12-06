import collections

# PROPOSING-SIDE
# inputs:

# unmatched_dancer_preferences: list of remaining unmatched preferences for each dancer
# prev_proposals: list-of-lists; outer layer of lists records the rounds; inner layer records each players's proposals for the round (as indices)
# choreographer_acceptance: list-of-lists; outer layer of lists records the rounds; inner layer records the choreographers' acceptance for each player (as a boolean)
# dancer_quota: a list signifying the upper bound of proposals each dancer can make per round

def dancer_pairing_many(unmatched_dancer_preferences, prev_proposals, choreographer_acceptance, dancer_quota):
    new_proposals = prev_proposals
    entire_round_proposals = []
    finished = True

    # if there have been no matches (round = 0), give everyone first preference
    if len(prev_proposals) == 0:

        # rankings = each dancer's rankings
        for index, rankings in enumerate(unmatched_dancer_preferences):

            temp_dancer_proposals = []

            # add q number of top rankings
            for i in range(dancer_quota[index]):

                # if there are still unmatched preferences:
                if rankings:
                    temp_dancer_proposals.append(rankings[0])
                    rankings.remove(rankings[0])

            entire_round_proposals.append(temp_dancer_proposals)
            finished = False

    # else match unmatched dancers with their top choice that has not yet been matched
    # index = index of dancer, dancer = list of all dancer's proposals in the previous round
    else:
        for index, dancer in enumerate(prev_proposals[-1]):
            temp_dancer_proposals = []

            # check if dancer is unmatched for one of their i proposals
            for i in range(len(dancer)):

                # if the choreographer did not accept the dancer's i'th proposal from the last round
                if choreographer_acceptance[-1][index][i] == 0:

                    # if there are still unmatched preferences:
                    if (unmatched_dancer_preferences[index]):

                        # add the highest remaining preference to temp_matches
                        # and remove it from the unmatched preferences list
                        temp_dancer_proposals.append(unmatched_dancer_preferences[index][0])
                        unmatched_dancer_preferences[index].remove(unmatched_dancer_preferences[index][0])

                        finished = False

                # if choreographer did accept the i'th proposal, count it in this round's proposals
                else:
                    temp_dancer_proposals.append(dancer[i])

            entire_round_proposals.append(temp_dancer_proposals)

    new_proposals.append(entire_round_proposals)
    return unmatched_dancer_preferences, new_proposals, finished

# ACCEPTING SIDE
# inputs:

# choreographer_preferences: list of choreographer's preferences for each song
# prev_proposals: list-of-lists; outer layer of lists records the rounds; inner layer records each players's proposals for the round (as indices)
# choreographer_acceptance: list-of-lists; outer layer of lists records the rounds; inner layer records the choreographers' acceptance for each player (as a boolean)
# dancer_quota: a list signifying the upper bound of proposals each dancer can make per round
# song_quota: a list of the number of positions available for each song

def choreographer_tiebreak_many(choreographer_preferences, prev_proposals, choreographer_acceptance, dancer_quota, song_quota):
    songs_done = set()
    entire_round_responses = []

    # create a dict for each song
    proposals_per_song = collections.defaultdict(list)

    # iterate through each dancer's proposals
    # and append (dancer's index, choreographer's rank of the dancer) to the appropriate song key
    for dancer_index, dancer_proposal in enumerate(prev_proposals[-1]):
        for song_proposal in dancer_proposal:
            choreographer_rank = choreographer_preferences[song_proposal].index(dancer_index)
            proposals_per_song[song_proposal].append((dancer_index, choreographer_rank))

    # sort by choreographer's rank of the dancers
    for song_index in range(len(choreographer_preferences)):
        proposals_per_song[song_index].sort(key=lambda x: x[1])

    # go through each dancer's proposals and responds accordingly
    for dancer_index, dancer_proposal in enumerate(prev_proposals[-1]):

        dancer_response = []

        for song_proposal in dancer_proposal:

            # find index of dancer in the sorted list of proposals per song
            for song_index, tup in enumerate(proposals_per_song[song_proposal]):

                if tup[0] == dancer_index:

                    # accept if dancer is ranked within the quota of positions available
                    # reject if not
                    if song_index < song_quota[song_proposal]:
                        dancer_response.append(1)
                    else:
                        dancer_response.append(0)

        entire_round_responses.append(dancer_response)

    choreographer_acceptance.append(entire_round_responses)
    return choreographer_acceptance

# USE THIS FUNCTION TO CALL/RUN THE DEFERRED ACCEPTANCE ALGORITHM
# Example input:
# deferred_acceptance_many(
#     [[4, 5, 3, 0, 1, 2], [3, 1, 4, 5, 0, 2], [2, 1, 0, 5, 3, 4], [2, 0, 1, 5, 4, 3], [3, 1, 4, 2, 5, 0], [2, 0, 1, 5, 4, 3], [1, 2, 4, 0, 5, 3], [3, 4, 5, 1, 0, 2], [3, 4, 5, 1, 2, 0], [3, 5, 1, 0, 4, 2], [3, 1, 0, 5, 2, 4], [0, 1, 2, 3, 5, 4], [1, 0, 3, 2, 5, 4], [3, 4, 1, 0, 5, 2], [2, 1, 0, 5, 3, 4], [3, 4, 1, 5, 0, 2]],
#     [[12, 5, 11, 15, 4, 1, 2, 14, 9, 6, 3, 8, 10, 7, 13, 0], [4, 1, 7, 3, 2, 12, 9, 5, 6, 14, 15, 13, 8, 11, 10, 0], [4, 6, 14, 2, 15, 1, 3, 8, 12, 5, 11, 7, 10, 13, 9, 0], [7, 1, 4, 13, 9, 8, 0, 15, 10, 2, 12, 3, 6, 5, 14, 11], [7, 1, 4, 0, 9, 15, 13, 2, 5, 8, 10, 12, 3, 6, 14, 11], [2, 3, 5, 6, 7, 11, 15, 14, 13, 9, 1, 4, 0, 8, 10, 12]],
#     [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
#     [4, 7, 3, 8, 6, 9])

def deferred_acceptance_many(dancer_preferences, choreographer_preferences, dancer_quota, song_quota):
    unmatched_preferences = dancer_preferences
    new_proposals = []
    choreographer_acceptance = []
    prev_matches_cleaned = []
    finished = False

    exists_unmatched = True

    while not finished:
        unmatched_preferences, new_proposals, finished = dancer_pairing_many(unmatched_preferences, new_proposals, choreographer_acceptance, dancer_quota)
        choreographer_acceptance = choreographer_tiebreak_many(choreographer_preferences, new_proposals, choreographer_acceptance, dancer_quota, song_quota)

    return new_proposals[-1]
