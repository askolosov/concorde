from . import logger

def tag(name, args, msg):
    logger.debug("Adding tag %s to message %s." % (tag, msg.get_message_id()))
        
    #msg.add_tag(tag)

    return msg

def untag(name, args, msg):
    logger.debug( "Removing tag %s from message %s." % (tag, msg.get_message_id()))
    return msg

def tag_by_subaddr(name, args, msg):
    # TODO
    pass

def tag_by_list_headers(name, args, msg):
    # TODO
    pass

def tag_by_spam_status(name, args, msg):
    # TODO
    pass

def learn_spam(name, args, msg):
    # TODO
    pass

def learn_ham(name, args, msg):
    # TODO
    pass


def purge(name, args, msg):
    # TODO
    pass
