class Input:
    def __init__(self):
        pass

    def get(self):
        return raw_input("USER:")


class Output:
    def __init__(self):
        pass

    def put(self, out):
        print("ROBOT:{}".format(out))
