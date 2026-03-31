messageStack = []

def add(message):
    messageStack.append(message)

def pop():
    if not messageStack:
        return None
    return messageStack.pop(0)

def isEmpty():
    if len(messageStack) == 0:
        return True
    else:
        return False