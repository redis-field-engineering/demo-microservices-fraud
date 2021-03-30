#=======================================================================================================================
def cartAdd(msg):

    newmsg = ['HMSET', "SHOPPING_CART:%s" %(msg['value']['cart_id']) ]
    [newmsg.extend([k,v]) for k,v in msg['value'].items()]
    execute(*newmsg)

    execute(
            'XADD', 'microservice-logs', '*',
            'microservice', 'cart',
            'user', 'system',
            'message', "User: %s added item: %s to cart" %( msg['value']['user'], msg['value']['product_name'])
            )


#=======================================================================================================================
gb = GearsBuilder(
        reader = 'StreamReader',
        desc   = "Add items to the shopping cart")

gb.map(cartAdd)
gb.register('CART-ADD')
