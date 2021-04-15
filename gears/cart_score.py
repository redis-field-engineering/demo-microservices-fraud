def reScore(x):
    itemcount = 0
    fraudscores = []
    items=execute("FT.SEARCH", "ShoppingCart", "@session:{}".format(x[1].replace("-", "")))
    for item in items[2::2]:
        res_dct = {item[i]: item[i + 1] for i in range(0, len(item), 2)}
        itemcount += 1
        fraudscores.append(int(100*( float(res_dct['identity_score']) + float(res_dct['profile_score']) + float(res_dct['ai_score']))/2) )

    if itemcount < 1 or len(fraudscores) < 1:
        return(0, 100)
    else:
        return(itemcount, 100 - min(fraudscores))

bg = GB('CommandReader', desc="Trigger to score the cart")
bg.map(reScore)
bg.register(trigger='score')
