def return_products_to_warehouse(lianiki_order):
    #gets all the order items and adds the qty in warehouse
    order_items = lianiki_order.lianikiorderitem_set.all()
    for item in order_items:
        item.title.reserve += item.qty
        item.title.save()
        if item.color:
            item.color.qty += item.qty
            item.color.save()
        if item.size:
            item.size.qty += item.qty
            item.size.save()

def remove_products_from_warehouse(lianiki_order):
    #gets all the order items and remove the qty in warehouse
    order_items = lianiki_order.lianikiorderitem_set.all()
    for item in order_items:
        item.title.reserve -= item.qty
        item.title.save()
        if item.color:
            item.color.qty -= item.qty
            item.color.save()
        if item.size:
            item.size.qty -= item.qty
            item.size.save()

def change_order_status(lianiki_order, old_id, new_id):
    if int(old_id) in [1,2,3,4,5]:
        print('new_order')
        if int(new_id) in [6,7]:
            lianiki_order.paid_value = lianiki_order.value
            lianiki_order.save()
            lianiki_order.costumer_account.paid_value += lianiki_order.value
            lianiki_order.costumer_account.save()
        if int(new_id) in [8,9]:
            lianiki_order.costumer_account.balance -= lianiki_order.value
            lianiki_order.costumer_account.save()
            return_products_to_warehouse(lianiki_order)

    elif int(old_id) in [6,7]:
        if int(new_id) in [1,2,3,4,5]:
            lianiki_order.paid_value = 0
            lianiki_order.costumer_account.paid_value -= lianiki_order.value
            lianiki_order.save()
            lianiki_order.costumer_account.save()

        if int(new_id) in [8,9]:
            lianiki_order.paid_value -= lianiki_order.value
            lianiki_order.save()
            lianiki_order.costumer_account.balance -= lianiki_order.value
            lianiki_order.costumer_account.paid_value -= lianiki_order.value
            lianiki_order.costumer_account.save()
            return_products_to_warehouse(lianiki_order)

    elif int(old_id) in [8,9]:
        if int(new_id) in [1, 2, 3, 4, 5]:
            lianiki_order.costumer_account.balance += lianiki_order.value
            lianiki_order.costumer_account.save()
            remove_products_from_warehouse(lianiki_order)
        if int(new_id) in [6,7]:
            lianiki_order.paid_value += lianiki_order.value
            lianiki_order.save()
            remove_products_from_warehouse(lianiki_order)
            lianiki_order.costumer_account.balance += lianiki_order.value
            lianiki_order.costumer_account.paid_value += lianiki_order.value
            remove_products_from_warehouse(lianiki_order)

