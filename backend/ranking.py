m = 100

def weighted_score(rating, review_count, average_rating):
    v = review_count
    R = rating
    C = average_rating
    return (v/(v+m))*R + (m/(v+m))*C

def add_score(places):
    ratings = [] 
    for place in places:
        if place['rating'] is not None:
            ratings.append(place['rating'])

    average_rating = sum(ratings)/len(ratings)
    for place in places:
        if(place['rating'] is None):
            place['score'] = None
        else:
            rating = place['rating']
            review_count = place['review_count']
            place['score'] = weighted_score(rating, review_count, average_rating) 
    return average_rating