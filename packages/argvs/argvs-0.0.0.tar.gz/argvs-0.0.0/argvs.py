import sys

class argvs:
    def __init__(self):
        self.params = {}
        self.version='1.1.0'
        self.author='Bob Robertson'
        self.email='coderdude2000@proton.me'
    def help(self):
        return f'For help, just email {self.email}, or search the internet'
    def add_param(self, argv_num, param_name, command):
        '''Add a param to the list'''
        self.params[param_name] = [argv_num, command]

    def init_param(self, param_name):
        '''Initialize a specific param'''
        if not self.params:
            raise Exception("Error code: 1. No params in list")
        
        if param_name not in self.params:
            raise Exception(f"Param '{param_name}' not registered.")

        index, command = self.params[param_name]
        if len(sys.argv) > index:
            if sys.argv[index] == param_name:
                return command()
            else:
                return f"Param '{param_name}' not found at position {index} (got '{sys.argv[index]}')"
        else:
            return f"Not enough arguments passed. Expected index {index}, got {len(sys.argv) - 1}"

    def init_all(self):
        '''Initialize all registered params'''
        if not self.params:
            raise Exception("Error code: 1. No params in list")
        for param_name in self.params:
            self.init_param(param_name)

    def add_param_list(self, list_name):
        '''
        Add a param list.
        Example format: [[param_name, argv_num, command], ...]
        '''
        for param_name, argv_num, command in list_name:
            self.add_param(argv_num, param_name, command)


        
            



# === Usage ===

if __name__ == "__main__":
    ar = argvs()
    def greet():
        print("Hello! 👋")

    def show_version():
        print(f"Version {ar.version}")

    def say_goodbye():
        print("Goodbye! 👋")
    
    ar.add_param_list([
        ['greet', 1, greet],
        ['version', 1, show_version],
        ['bye', 1, say_goodbye]
    ])

    ar.init_all()
