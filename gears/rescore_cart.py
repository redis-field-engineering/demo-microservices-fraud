def reScore(x):
    rescore = []
    items=execute("FT.SEARCH", "ShoppingCart", "@session:{}".format(x[1]))
    for item in items[2::2]:
        res_dct = {item[i]: item[i + 1] for i in range(0, len(item), 2)}
        res_dct['user'] = x[2]
        res_dct["action"] = "enhance"
        newmsg = ['XADD', 'CHECK-IDENTITY', '*']
        [newmsg.extend([k,v]) for k,v in res_dct.items()]
        execute(*newmsg)
    return("resubmitted")

bg = GB('CommandReader', desc="Trigger to rescore the cart")
bg.map(reScore)
bg.register(trigger='rescore')
