import os
from cmd import Cmd
from colorama import init, Fore

class Prompt(Cmd):
    prompt = "pync> "
    intro = "pync 1.0 - enter 'help' for list of commands" # @TODO: bump version

    def __init__(self, root, dest):
        self.root       = root
        self.current    = root
        self.dest       = dest
        self.root.compare_to(dest)

        self.prompt = "{}> ".format(os.path.basename(self.root.path.rstrip("/")))

        init()
        Cmd.__init__(self)

    def perror(self, error):
        print("{}ERROR:{} {}".format(Fore.RED, Fore.RESET, error))

    def do_tree(self, params):
        if len(params.split()) != 0:
            tgt = self.current.find(params)
            if tgt:
                tgt.trace(override=True)
            else:
                self.perror("no such file or direcory: '{}'".format(params))
        else:
            self.current.trace(override=True)

    def complete_tree(self, text, line, begidx, endidx):
        if not text or len(text.split()) == 0:
            print([child.name + child.ppostfix() for child in self.current if hasattr(chil, "children")] + [".."])
            return [child.name + child.ppostfix() for child in self.current if hasattr(chil, "children")] + [".."]

        l = self.current.find(os.path.dirname(text))

        if hasattr(l, "children"):
            return [child.name for child in l if child.name.startswith(os.path.basename(text)) and hasattr(child, "children")]

    def do_cd(self, params):
        if len(params.split()) == 0:
            self.current = self.root
        else:
            if self.current.find(params):
                tgt = self.current.find(params)
                if hasattr(tgt, "children"):
                    self.current = tgt
                else:
                    self.perror("not a directory: '{}'".format(params))
            else:
                self.perror("no such file or directory: '{}'".format(params))

    def complete_cd(self, text, line, begidx, endidx):
        if not text:
            return [child.name + child.ppostfix() for child in self.current if hasattr(child, "children")] + [".."]
        l = self.current.find(os.path.dirname(text))

        if hasattr(l, "children"):
            return [child.name for child in l if child.name.startswith(os.path.basename(text)) and hasattr(child, "children")]

    def do_exit(self, params):
        return True

    def do_commit(self, params):
        pass

    def do_EOF(self, params):
        return True
