from diary.models import QuestionSet

def get_limits(user):
    profile = user.userprofile
    if profile.plan == 'premium':
        return {'max_answers': 20, 'max_qsets': 3}
    return {'max_answers': 5, 'max_qsets': 1}

def can_answer_more(user):
    return user.userprofile.weekly_answer_count < get_limits(user)['max_answers']

def can_create_qset(user):
    limit = 3 if user.userprofile.plan == 'premium' else 1
    return QuestionSet.objects.filter(owner=user).count() < limit