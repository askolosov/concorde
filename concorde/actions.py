import notmuch
import re
import subprocess
from . import logger

EMAIL_SUBADDR_RE = re.compile(r'[^\s<]+\+([^@\s]+)@[^\s>]+')
LIST_ID_RE = re.compile(r'<([^.]+)\.[^>]+>')
BGF_SPAM_RE = re.compile('X-Bogosity:\s*Spam')
BGF_SPAMICITY_RE = re.compile('spamicity=(\d\.\d+)')

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

    try:
        to = msg.get_header("Delivered-To")
        m = EMAIL_SUBADDR_RE.search(to)
    except notmuch.NullPointerError:
        logger.warning("Couldn't extract header from message '%s' \
due to some internal notmuch problems. Skipping.", msg.get_message_id())
        m = None

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

    try:
        list_id_hdr = msg.get_header("List-Id")
        m = LIST_ID_RE.search(list_id_hdr)
    except notmuch.NullPointerError:
        logger.warning("Couldn't extract header from message '%s' \
due to some internal notmuch problems. Skipping.", msg.get_message_id())
        m = None
    
    if not m:
        return

    list_tag = m.group(1)

    logger.debug("Tag message %s with '%s'" %
                 (msg.get_message_id(), list_tag))
    
    msg.add_tag(list_tag)
    msg.add_tag(maillist_indicator)

def tag_by_spam_status(name, args, msgs):
    # First argument - tag for messages, that was recognized as spam
    if (len(args) > 0):
        spam_tag = args[0]

    bgf = subprocess.Popen(['bogofilter', '-bv'],
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for m in msgs:
        bgf.stdin.write(bytes(u'%s\n' % m.get_filename())) #, 'UTF-8'))
        spam_status = bgf.stdout.readline()
        if BGF_SPAM_RE.search(spam_status):
            logger.debug("Message '%s' recognized as spam", m.get_message_id())
            m.add_tag(spam_tag)
    bgf.stdin.close()

def train_bgf(msgs, bgf_arg, tag1, tag2):
    bgf = subprocess.Popen(['bogofilter', bgf_arg],
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    for m in msgs:
        bgf.stdin.write(bytes(u'%s\n' % m.get_filename()))
        if add_tag:
            m.add_tag(tag1)

        if remove_tag:
            m.remove_tag(tag2)

    bgf.stdin.close()

def learn_spam(name, args, msgs):
    train_bgf(msgs, '-sb', args[0], None)

def learn_ham(name, args, msgs):
    train_bgf(msgs, '-nb', args[0], None)

def unlearn_spam(name, args, msgs):
    train_bgf(msgs, '-Sb', None, args[0])

def unlearn_ham(name, args, msgs):
    train_bgf(msgs, '-Nb', None, args[0])

def purge(name, args, msg):
    # TODO
    pass
