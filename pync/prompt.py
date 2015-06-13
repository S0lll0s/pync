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

        import readline
        readline.set_completer_delims(" \t")

        init()
        Cmd.__init__(self)

    def perror(self, error):
        print("{}ERROR:{} {}".format(Fore.RED, Fore.RESET, error))

    def do_tree(self, params):
        tgt = self.current.find(params)
        if tgt:
            tgt.trace(override=True)
        else:
            self.perror("no such file or direcory: '{}'".format(params))

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

    def do_del(self, params):
        tgt = self.current.find(params)
        if tgt:
            for desc in tgt.leaves():
                desc._new_status = desc.S_NONE
        else:
            self.perror("no such file or direcory: '{}'".format(params))

    def do_add(self, params):
        tgt = self.current.find(params)
        if tgt:
            for desc in tgt.leaves():
                desc._new_status = desc.S_ALL
        else:
            self.perror("no such file or direcory: '{}'".format(params))

    def do_commit(self, params):
        self.root.commit(self.dest.path)

    def do_exit(self, params):
        return True

    def do_EOF(self, params):
        return True

    def complete_dirs(self, text, line, begidx, endidx):
        if self.current != self.root and not text or len(text.split()) == 0:
            return [child.name + "/" for child in self.current if hasattr(child, "children")] + ["../"]
        elif not os.path.dirname(text):
            return [child.name + "/" for child in self.current if child.name.startswith(text) and hasattr(child, "children")]

        l = self.current.find(os.path.dirname(text))

        if hasattr(l, "children"):
            return ["{}/{}/".format(os.path.dirname(text), child.name) for child in l if child.name.startswith(os.path.basename(text)) and hasattr(child, "children")]

    def complete_files(self, text, line, begidx, endidx):
        if self.current != self.root and not text or len(text.split()) == 0:
            return [child.name + "/" for child in self.current if hasattr(child, "children")] + ["../"] + [child.name for child in self.current if not hasattr(child, "children")]
        elif not os.path.dirname(text):
            return [child.name + "/" for child in self.current if child.name.startswith(text) and hasattr(child, "children")] + [child.name for child in self.current if not hasattr(child, "children") and child.name.startswith(text)]

        l = self.current.find(os.path.dirname(text))

        if hasattr(l, "children"):
            return ["{}/{}/".format(os.path.dirname(text), child.name) for child in l if child.name.startswith(os.path.basename(text)) and hasattr(child, "children")] + ["{}/{}".format(os.path.dirname(text), child.name) for child in l if child.name.startswith(os.path.basename(text)) and not hasattr(child, "children")]


    complete_tree   = complete_dirs
    complete_cd     = complete_dirs
    complete_add    = complete_files
    complete_del    = complete_files
