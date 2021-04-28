CATEGORIES = [ 
        "Apparel", "Automotive", "Baby", "Beauty", "Books", "Camera", "Digital_Ebook_Purchase",
        "Digital_Music_Purchase", "Digital_Software", "Digital_Video_Download", "Digital_Video_Games",
        "Electronics", "Furniture", "Gift_Card", "Grocery", "Health_Personal_Care", "Home_Entertainment",
        "Home_Improvement", "Home", "Jewelry", "Kitchen", "Lawn_and_Garden", "Luggage",
        "Major_Appliances", "Mobile_Apps", "Mobile_Electronics", "Musical_Instruments", "Music",
        "Office_Products", "Outdoors", "PC", "Personal_Care_Appliances", "Pet_Products", "Shoes",
        "Software", "Sports", "Tools", "Toys", "Video_DVD", "Video_Games", "Video", "Watches", "Wireless" ]

#=======================================================================================================================
def scoreAI(username, itemCategory, itemQuantity, msgID):
        tnsr_name = "tensor:{}:{}".format(username,msgID)
        tnsr = ["AI.TENSORSET", tnsr_name, "FLOAT", "1", len(CATEGORIES), "VALUES"]
        p = execute("HGETALL", "user:profile:{}".format(username))
        profile = {p[0::2][i]: p[1::2][i] for i in range(len(p[1::2]))}
        profile[itemCategory] += int(itemQuantity)
        for c in CATEGORIES:
                tnsr.append(float(profile[c]))
        execute(*tnsr)
        runmodel = ['AI.MODELRUN', 'classifier_model', 'INPUTS', tnsr_name, 'OUTPUTS', "{}:results".format(tnsr_name) ]
        execute(*runmodel)
        scmd = ['AI.TENSORGET', "{}:results".format(tnsr_name),"VALUES"]
        s = execute(*scmd)
        return(float(s[0]))

#=======================================================================================================================
def checkAI(msg):

    score = scoreAI(msg['value']['user'], msg['value']['category'], msg['value']['quantity'], msg['value']['cart_id'])
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
