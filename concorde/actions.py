import re
from . import logger

EMAIL_SUBADDR_RE = re.compile(r'[^\s<]+\+([^@\s]+)@[^\s>]+')
LIST_ID_RE = re.compile(r'<([^.]+)\.[^>]+>')

def tag(name, args, msg):    
    logger.debug("Adding tags %s to message %s.", args, msg.get_message_id())

    for tag in args:
        msg.add_tag(tag)

def untag(name, args, msg):
    logger.debug("Removing tags %s from message %s.", args, msg.get_message_id())

    for tag in args:
        msg.remove_tag(tag)

def tag_by_subaddr(name, args, msg):
    subaddr_presence_tag = None
    # If an argument is passed, then it is the tag, that should be set to
    # the message if its recipient address has a subaddress part
    if (len(args) > 0):
        subaddr_presence_tag = args[0]

    to = msg.get_header("Delivered-To")
    m = EMAIL_SUBADDR_RE.search(to)

    # Skip the message if the recipient address doesn't have a
    # subaddress part
    if not m:
        return

    subaddr_tag = m.group(1)

    logger.debug("Tag message %s with '%s'" %
                 (msg.get_message_id(), subaddr_tag))
        
    msg.add_tag(subaddr_tag)
    msg.add_tag(subaddr_presence_tag)

def tag_by_list_headers(name, args, msg):
    # First argument - tag for messages in maillists
    if (len(args) > 0):
        maillist_indicator = args[0]
    
    list_id_hdr = msg.get_header("List-Id")
    if not list_id_hdr:
        return

    m = LIST_ID_RE.search(list_id_hdr)
    if not m:
        return

    list_tag = m.group(1)

    logger.debug("Tag message %s with '%s'" %
                 (msg.get_message_id(), list_tag))
    
    msg.add_tag(list_tag)
    msg.add_tag(maillist_indicator)

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
