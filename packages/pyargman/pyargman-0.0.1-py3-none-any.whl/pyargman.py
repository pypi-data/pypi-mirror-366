
"""
author = its_me_abi
date = 1/8/2025

"""
class ArgManager:
    """
    commandline argument manager , get ,set values and produce command list"
    alternative to inbuilt argument parser
    """
    def __init__(self, exename = "" ):
        self.exe_name = exename  # prefix of command usualy "java" like executable name
        self.args = {}

    def set_arg(self, key, val):
        if key in self.args.keys():
            if isinstance(self.args[key],list):
                self.args[key].append(val)
            else:
                oldval = self.args[key]
                self.args[key] = [oldval, val]
        else:
            self.args[key]=val

    def get_arg(self, key):
        if key in self.args.keys():
           return self.args[key]

    def toString(self):
        return " ".join(self.tolist())

    def tolist(self):
        cli = []
        for key, value in self.args.items():
            if isinstance(value, bool):
                if value:
                    cli.append(f"{key}")
            elif isinstance(value, list):
                for v in value:
                    cli.extend([f"{key}", str(v)])
            elif value is not None:
                cli.extend([f"{key}", str(value)])
        if self.exe_name:
            cli = [self.exe_name] + cli
        return cli


if __name__ == "__main__":
    a = ArgManager()
    a.set_arg("--helo_duplicate", 1)
    a.set_arg("--helo_duplicate", 2)
    a.set_arg("--helo_boolean_value", True) # arguemnt without values
    a.set_arg("script_path_like", True)
    print(" converted to cli list " ,a.tolist())
    print(" converted to cli string ", a.toString())