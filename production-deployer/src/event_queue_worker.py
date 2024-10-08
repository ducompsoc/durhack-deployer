def handle_event():
    pass
    # Check the event ID (`X-GitHub-Delivery` request header) against persistent storage of 'already processed' events
    # if the event ID is known (i.e. has already been processed), we stop processing the event (as it could be a replay attack)
    
    # we need to decide what to do based on the event type.
    # in practise, the webhook should only ever receive two event types: 
    # - `push` (when commits are pushed) 
    # - `ping` (when the webhook is initially connected)
    # but we shouldn't assume that other event types will never be sent, and act accordingly (e.g. respond 'NOT IMPLEMENTED')
    
    # once the event has been handled, we add the event ID to persistent storage 
