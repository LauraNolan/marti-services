from . import dagger

def init_values(marti_name,dagger_name,decay=None,dagger_value=None):

    dagger_item = dagger.Dagger()

    item = dagger_item.get_item(marti_name)
    if item:
        dagger_item = item


    dagger_item.marti_name = marti_name
    dagger_item.dagger_name = dagger_name
    dagger_item.decay = decay

    if not item:
        dagger_item.dagger_value = 0
    if dagger_value:
        dagger_item.dagger_value = dagger_value

    dagger_item.save()

def set_value(marti_name,dagger_value):

    dagger_item = dagger.Dagger()

    item = dagger_item.get_item(marti_name)
    if not item:
        print 'not here'
        return False

    if dagger_value == 1:
        dagger_value = dagger_value + item.decay
    if dagger_value < 0:
        dagger_value = 0

    item.dagger_value = dagger_value

    item.save()

def decay_value(marti_name):

    dagger_item = dagger.Dagger()

    item = dagger_item.get_item(marti_name)
    if not item:
        print 'item not here'
        return False

    set_value(marti_name,(item.dagger_value-item.decay))