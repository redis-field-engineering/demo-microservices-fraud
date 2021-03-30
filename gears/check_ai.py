import random
#=======================================================================================================================
def checkAI(msg):

    score = random.random()
    next_stage = "CART-ADD"

    msg['value']['ai_score'] = score

    newmsg= [ 'XADD', next_stage, '*' ] 
    [newmsg.extend([k,v]) for k,v in msg['value'].items()]
    execute(*newmsg)
    execute(
            'XADD', 'microservice-logs', '*',
            'microservice', 'ai',
            'user', 'system',
            'message', "Check AI for user: %s , result: %f" %( msg['value']['user'], score)
            )


#=======================================================================================================================
gb = GearsBuilder(
        reader = 'StreamReader',
        desc   = "Perform the AI analysis")

gb.map(checkAI)
gb.register('CHECK-AI')
