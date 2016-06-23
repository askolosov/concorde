import re
from . import logger

EMAIL_SUBADDR_RE = re.compile(r'[^\s<]+\+([^@\s]+)@[^\s>]+')

def tag(name, args, msg):    
    logger.debug("Adding tags %s to message %s.", args, msg.get_message_id())

    #map(msg.add_tag, args)
    
    return msg

def untag(name, args, msg):
    logger.debug("Removing tags %s from message %s.", args, msg.get_message_id())
    
    #map(msg.remove_tag, args)
    
    return msg

def tag_by_subaddr(name, args, msg):
    subaddr_presence_tag = None
    # If argument is passed, then it is the tag, that should be set to
    # the message if its recipient address has a subaddress part
    if (len(args) > 0):
        subaddr_presence_tag = args[0]
    
    to = msg.get_header("Delivered-To")
    m = EMAIL_SUBADDR_RE.search(to)

    # Skip the message if the recipient address doesn't have a
    # subaddress part
    if not m:
        return msg

    subaddr_tag = m.group(1)

    logger.debug("Tag message %s with '%s'" %
                 (msg.get_message_id(), subaddr_tag))
        
    # msg.add_tag(subaddr_tag)
    # msg.add_tag(subaddr_presence_tag)

    return msg

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
