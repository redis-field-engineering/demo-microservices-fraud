#=======================================================================================================================
def checkProfile(msg):

    score = 0.0
    if msg['value']['user'] != "Guest":

        score += execute('BF.EXISTS', "BFPROFILE:%s:%s" % (msg['value']['category'], msg['value']['level']),  msg['value']['user'])
        score += execute('BF.EXISTS', "BFPROFILE:Category:%s" % msg['value']['category'], msg['value']['user'])
    
    if msg['value']['user'] == "Guest":
        next_stage = "CART-ADD"
    elif score <= 1.0:
        next_stage = "CHECK-AI"
    else:
        next_stage = "CART-ADD"


    msg['value']['profile_score'] = "%.2f" %(score/2.0)
    msg['value']['ai_score'] = "0"
    newmsg= [ 'XADD', next_stage, '*' ] 
    [newmsg.extend([k,v]) for k,v in msg['value'].items()]
    execute(*newmsg)
    execute(
            'XADD', 'microservice-logs', '*',
            'microservice', 'profile',
            'user', 'system',
            'message', "Check profile for user: %s , result: %f , next_stage: %s" %( msg['value']['user'], score/2.0, next_stage )
            )


#=======================================================================================================================
gb = GearsBuilder(
        reader = 'StreamReader',
        desc   = "Filter based on user profile")

gb.map(checkProfile)
gb.register('CHECK-PROFILE')
