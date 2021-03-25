#=======================================================================================================================
def checkId(msg):

    if msg['value']['action'] == "enhance" and msg['value']['user'] != "Guest":
        score = 0.0

        if execute('EXISTS', "Identity:%s:IPS" % msg['value']['user']) > 0 or execute('EXISTS', "Identity:%s:BrowserFingerprint" % msg['value']['user']) > 0:
            score += execute('SISMEMBER', "Identity:%s:IPS" % msg['value']['user'], msg['value']['ipaddr'])
            score += execute('SISMEMBER', "Identity:%s:BrowserFingerprint" % msg['value']['user'], msg['value']['fingerprint'])

        msg['value']['identity_score'] = "%.2f" %(score/2.0)
        msg['value']['cart_id'] =  msg['id']
        del msg['value']['action']
        newmsg= [ 'XADD', 'CHECK-PROFILE', '*' ] 
        [newmsg.extend([k,v]) for k,v in msg['value'].items()]
        execute(*newmsg)
        execute(
                'XADD', 'microservice-logs', '*',
                'microservice', 'identity',
                'user', 'system',
                'message', "Check identity for user: %s , result: %f" %( msg['value']['user'], score/2.0 )
                )
            
    elif  msg['value']['action'] == "update" and msg['value']['user'] != "Guest":
        execute('SADD', "Identity:%s:IPS" % msg['value']['user'], msg['value']['ipaddr'])
        execute('SADD', "Identity:%s:BrowserFingerprint" % msg['value']['user'], msg['value']['fingerprint'])
        execute(
                'XADD', 'microservice-logs', '*',
                'microservice', 'identity',
                'user', 'system',
                'message', "Updated identity for user: %s" %( msg['value']['user'] )
                )

    else:
        execute(
                'XADD', 'microservice-logs', '*',
                'microservice', 'identity',
                'user', 'system',
                'message', "Invalid action: %s or user: %s" %( msg['value']['action'], msg['value']['user'] )
                )


#=======================================================================================================================
gb = GearsBuilder(
        reader = 'StreamReader',
        desc   = "Check or Update Digital Identity")

gb.map(checkId)
gb.register('CHECK-IDENTITY')
