class Input:
    def __init__(self):
        pass

    def get(self):
        return raw_input()


class Output:
    def __init__(self):
        pass

    def put(self, out):
        print("SYSTEM: {}".format(out))
