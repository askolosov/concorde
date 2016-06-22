import re
import notmuch
import sys
import actions
from . import logger

COMMENT_RE = re.compile('\s*#')
EMPTYLINE_RE = re.compile('^\s*$')
INSTR_RE = re.compile('(.+)\s+--\s+(.+)')
ACTION_RE = re.compile(r'([^(]+)(\(([^)]*)\))?')

known_actions = {
    '+': actions.tag,
    '-': actions.untag,
    '=': {
        'by-subaddr': actions.tag_by_subaddr,
        'by-list-info': actions.tag_by_list_headers,
        'by-spam-status': actions.tag_by_spam_status
    },
    '%': {
        'learn-spam': actions.learn_spam,
        'learn-ham': actions.learn_ham,
        'purge': actions.purge
    }
}

class Error(Exception):
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class TransitionError(Error):
    """Raised when an operation attempts a state transition that's not
    allowed.

    Attributes:
        prev -- state at beginning of transition
        next -- attempted new state
        msg  -- explanation of why the specific transition is not allowed
    """

    def __init__(self, prev, next, msg):
        self.prev = prev
        self.next = next
        self.msg = msg

def perform_action(action, msgs):
    return map(lambda m: action['func'](action['name'], action['args'], m),
               msgs)

def parse_action_token(action_token):
    action_char = action_token[0]

    if not action_char in known_actions:
        # TODO: raise exception
        return

    # Parse action token
    m = ACTION_RE.match(action_token[1:])
    if not m:
        # TODO: raise exception
        return

    action_func = known_actions[action_char]
    if not type(action_func) is dict:
        # If corresponding action is a simple action, then action token
        # contains only action arguments

        action_name = None
        action_args = re.split('\s*,\s*', m.group(1))
    else:
        # TODO: parse complex action token here
        
        # If it is an action with a name, then action token contains
        # action name and argument list in parethesis
        
        action_name = m.group(1)
        action_args = re.split('\s*,\s*', m.group(3))
        action_func = action_func[action_name]

    return dict(name=action_name, args=action_args, func=action_func)

def run_actions(db, action_tokens, query_str):
    actions = map(parse_action_token, action_tokens)
    
    query = notmuch.Query(db, query_str)
    msgs = query.search_messages()

    # Sequentially perform given actions on queried messages
    reduce(lambda m, a: perform_action(a, m), actions, msgs)
    
def run_instructions(db, instrs):
    lines_counter = 0
    
    for line in instrs:
        lines_counter += 1
        
        # Skip comment lines
        if COMMENT_RE.match(line):
            continue

        # Skip empty lines
        if EMPTYLINE_RE.match(line):
            continue

        # Try to parse instruction in the line
        m = INSTR_RE.match(line)

        # Skip the line If it doesn't look like an instruction
        if not m:
            logger.warning("Line %d couldn't be parsed. Skipping." % lines_counter)
            continue

        # Extract actions and query from the instruction
        actions = re.split('\s+', m.group(1))
        query = m.group(2)

        # Run actions, listed in the instruction
        run_actions(db, actions, query)

def process_file(filename):
    logger.debug("Processing instructions file '%s'", filename)
    
    with notmuch.Database(mode=notmuch.Database.MODE.READ_WRITE) as db:
        with open(filename, 'r') as f:
            run_instructions(db, f)
