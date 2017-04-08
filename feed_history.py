
#feeds = {"feeds":[['hello flask', 'user', ],['hello flask 2','picture']]}

feeds = {"feeds":[]}

def time_line_history():

     #feeds = {"feeds":[['hello flask', 'user'],['hello flask 2','picture']]}
     return feeds
     
def update_timeline(title, message, act, time):
     #feeds = {"feeds":[['hello flask', 'user'],['hello flask 2','picture']]}
     feeds["feeds"].append([act, title, message, time])
     return feeds     