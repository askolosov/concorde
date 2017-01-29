import notmuch
import re
import subprocess
import os
import shutil
from . import logger

EMAIL_SUBADDR_RE = re.compile(r'[^\s<]+\+([^@\s]+)@[^\s>]+')
LIST_ID_RE = re.compile(r'<([^.]+)\.[^>]+>')
BGF_SPAM_RE = re.compile('X-Bogosity:\s*Spam')
BGF_SPAMICITY_RE = re.compile('spamicity=(\d\.\d+)')

def tag(db, name, args, msg):    
    logger.debug("Adding tags %s to message %s.", args, msg.get_message_id())

    for tag in args:
        msg.add_tag(tag)

def untag(db, name, args, msg):
    logger.debug("Removing tags %s from message %s.", args, msg.get_message_id())

    for tag in args:
        msg.remove_tag(tag)

def tag_by_subaddr(db, name, args, msg):
    subaddr_presence_tag = None
    # If an argument is passed, then it is the tag, that should be set to
    # the message if its recipient address has a subaddress part
    if len(args) > 0:
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

def tag_by_list_headers(db, name, args, msg):
    # First argument - tag for messages in maillists
    if len(args) > 0:
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

def tag_by_spam_status(db, name, args, msgs):
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

def train_bgf(msgs, bgf_arg, tag_to_add, tag_to_remove):
    bgf = subprocess.Popen(['bogofilter', bgf_arg],
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    for m in msgs:
        bgf.stdin.write(bytes(u'%s\n' % m.get_filename()))
        if tag_to_add:
            m.add_tag(tag_to_add)

        if tag_to_remove:
            m.remove_tag(tag_to_remove)

    bgf.stdin.close()

def learn_spam(db, name, args, msgs):
    train_bgf(msgs, '-sb', args[0], None)

def learn_ham(db, name, args, msgs):
    train_bgf(msgs, '-nb', args[0], None)

def unlearn_spam(db, name, args, msgs):
    train_bgf(msgs, '-Sb', None, args[0])

def unlearn_ham(db, name, args, msgs):
    train_bgf(msgs, '-Nb', None, args[0])

def purge(db, name, args, msgs):
    for m in msgs:
        logger.info("Removing file of the message '%s'", m.get_message_id())
        try:
            os.remove(m.get_filename())
        except Exception as e:
            logger.warning("Failed to remove file '%s': %s", m.get_filename(), e)

def move(db, name, args, msgs):
    dest_dir = os.path.join(db.get_path(), args[0])

    for m in msgs:
        logger.info("Moving file of the message '%s' to '%s'", m.get_message_id(), dest_dir)
        try:
            shutil.move(m.get_filename(), dest_dir)
        except Exception as e:
            logger.warning("Failed to move file '%s' to '%s': %s", m.get_filename(), dest_dir, e)
