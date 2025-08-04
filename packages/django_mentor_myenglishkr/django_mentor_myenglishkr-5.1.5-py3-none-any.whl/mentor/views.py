from shared_lib import utils
from _data import mentor, shared_lib

c = mentor.context_eng
c.update(shared_lib.analytics)

def mentor_home(request, lang='eng'):
    if lang == 'kor':
        c = mentor.context_kor
        c['lang']['selected'] = 'kor'
    elif lang == 'eng':
        c = mentor.context_eng
        c['lang']['selected'] = 'eng'
    else:
        c = mentor.context_eng
        c['lang']['selected'] = 'eng'
    return utils.home(request, 'mentor/index.html', c)
        
        
def mentor_terms(request):
    return utils.terms(request, 'mentor/pages/terms.html', c)

def mentor_privacy(request):
    return utils.privacy(request, 'mentor/pages/privacy.html', c)
