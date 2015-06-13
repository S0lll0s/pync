# vim: et:ts=4:sw=4

import os
import shutil
from colorama import Fore, Style
try:
    from os import scandir
except ImportError:
    from scandir import scandir

class Filetree(object):
    S_ALL   = 3
    S_SOME  = 2
    S_SEMI  = 1 # no children none, some children some
    S_NONE  = 0

    states = {0: Fore.RED + "none", 1: Fore.MAGENTA + "semi", 2: Fore.YELLOW + "some", 3: Fore.GREEN + "all "}

    def __init__(self, path):
        self.path       = path
        self.root       = self

        if not os.path.isdir(path):
            raise "Not a directory: {}".format(path)

        self.children = dict((entry.name, Filenode(entry, self)) for entry in scandir(path))

    def append_child(self, child):
        self.children[child.name]   = child

    def size(self):
        return sum(child.size() for child in self)

    def find(self, path):
        while path.endswith("/"):
            path = path[:-1]
        if path == "":
            return self

        if hasattr(self, "children"):
            if path.startswith("..") and hasattr(self, "parent"):
                return self.parent.find(path[3:])
            for child in self:
                if child.name == path:
                    return child
                elif child.match(path):
                    return child.find(path[len(child.name)+1:])

    def match(self, path):
        return path.startswith(self.name + "/")

    def ppfix(self):
        if hasattr(self, "children"):
            return "/"
        return ""

    def compare_to(self, other):
        stats = [child.compare_to(other[child.name]) for child in self]
        if   all(s and s == self.S_ALL for s in stats):
            self.status = self.S_ALL
        elif all(s and s > self.S_SEMI for s in stats):
            self.status = self.S_SEMI
        elif any(s and s > self.S_NONE for s in stats):
            self.status = self.S_SOME
        else:
            self.status = self.S_NONE
        return self.status

    def new_status(self):
        if hasattr(self, "children"):
            stats = [child.new_status() for child in self]
            if   all(s and s == self.S_ALL for s in stats):
                return self.S_ALL
            elif all(s and s > self.S_SEMI for s in stats):
                return self.S_SEMI
            elif any(s and s > self.S_NONE for s in stats):
                return self.S_SOME
            else:
                return self.S_NONE
        else:
            return self._new_status

    def trace(self, stop=(3, 0), override=False):
        print("{} {:<50}       {:20}B".format(self.states[self.status], "- REPO -", self.size()))
        for child in self:
            child.trace(stop=stop)
        print(Fore.RESET, end="")

    def __getitem__(self, name):
        try:
            return self.children[name]
        except KeyError:
            return None

    def __iter__(self):
        for child in self.children:
            yield self.children[child]

    def leaves(self):
        if hasattr(self, "children"):
            for child in self:
                for gc in child.leaves():
                    yield gc
        else:
            yield self

    def itera(self, reverse=False, skip=False):
        if hasattr(self, "children"):
            if reverse and not skip:
                yield self, True
            for child in self:
                for gc, l in child.itera(reverse=reverse):
                    yield gc, l
            if not reverse and not skip:
                yield self, True
        else:
            yield self, False

    def commit(self, dest):
        self.commit_del(dest)
        self.commit_add(dest)

    def commit_del(self, dest):
        for (node, dir) in self.itera(skip=True):
            if node.status != self.S_NONE and  node.new_status() == self.S_NONE:
                if dir:
                    os.rmdir(os.path.join(dest, node.relpath()))
                    print("rmdir {}".format(os.path.join(dest, node.relpath())))
                else:
                    os.remove(os.path.join(dest, node.relpath()))
                    print("rm    {}".format(os.path.join(dest, node.relpath())))

    def commit_add(self, dest):
        for (node, dir) in self.itera(reverse=True, skip=True):
            if node.status == self.S_NONE and node.new_status() != self.S_NONE:
                if dir:
                    os.mkdir(os.path.join(dest, node.relpath()))
                    print("mkdir {}".format(os.path.join(dest, node.relpath())))
                else:
                    shutil.copy(node.path, os.path.join(dest, node.relpath()))
                    print("cp    {}".format(os.path.join(dest, node.relpath())))

    def relpath(self):
        if self.parent == self.root:
            return self.name
        else:
            return "{}/{}".format(self.parent.relpath(), self.name)

class Filenode(Filetree):
    def __init__(self, entry, parent):
        self.path   = entry.path
        self.name   = entry.name
        self.entry  = entry

        self.parent = parent
        self.root   = parent.root

        if self.entry.is_dir():
            self.children = dict((entry.name, Filenode(entry, self)) for entry in scandir(self.path))

    def size(self):
        if self.entry.is_dir():
            return sum(child.size() for child in self)
        return os.path.getsize(self.path)

    def compare_to(self, other):
        self.status = self.S_NONE
        self._new_status = self.S_NONE

        if not other:
            if self.entry.is_dir():
                for child in self:
                    child.compare_to(None) # make sure everyone gets assigned a value
            return

        if self.entry.is_dir():
            stats = [child.compare_to(other[child.name]) for child in self]
            if   all(s and s == self.S_ALL for s in stats):
                self.status = self.S_ALL
            elif all(s and s > self.S_SEMI for s in stats):
                self.status = self.S_SEMI
            elif any(s and s > self.S_NONE for s in stats):
                self.status = self.S_SOME
        else:
            if not other.entry.is_dir() and other.size() == self.size():
                self.status = self.S_ALL
                self._new_status = self.S_ALL

        return self.status

    def trace(self, indent=0, stop=(3, 0), override=False):
        bs = ""
        if self.status != self.new_status():
            bs = Style.BRIGHT

        if self.entry.is_dir():
            if self.new_status() in stop and not override:
                print("{}{} {:<50} <skip>{:20}B{}".format(bs, self.states[self.new_status()], "  "*indent + self.name, self.size(), Style.NORMAL))
            else:
                print("{}{} {:<50}       {:20}B{}".format(bs, self.states[self.new_status()], "  "*indent + self.name, self.size(), Style.NORMAL))
                for child in self:
                    child.trace(indent + 1, stop=stop)
        else:
            print("{}{} {:<50}       {:20}B{}".format(bs, self.states[self.new_status()], "  "*indent + self.name, self.size(), Style.NORMAL))
        print(Fore.RESET, end="")
