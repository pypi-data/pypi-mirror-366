import helics as h

def destroy_federate(fed):
    h.helicsFederateDisconnect(fed)
    h.helicsFederateDestroy(fed)