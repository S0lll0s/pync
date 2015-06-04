# vim: et:ts=4:sw=4

import os
try:
    from os import scandir
except ImportError:
    from scandir import scandir

class Filetree(object):
    S_ALL   = 3
    S_SOME  = 2
    S_SEMI  = 1 # no children none, some children some
    S_NONE  = 0

    states = {0: "none", 1: "semi", 2: "some", 3: "all "}

    def __init__(self, path):
        self.path       = path
        self.root       = self

        if not os.path.isdir(path):
            raise "Not a directory: {}".format(path)

        self.children = dict((entry.name, Filenode(entry, self)) for entry in scandir(path))

    def append_child(self, child):
        self.children[child.name]   = child

    def size(self):
        return sum(child.size() for name, child in self)

    def compare_to(self, other):
        stats = [child.compare_to(other[name]) for name, child in self]
        if   all(s and s == self.S_ALL for s in stats):
            self.status = self.S_ALL
        elif all(s and s > self.S_SEMI for s in stats):
            self.status = self.S_SEMI
        elif any(s and s > self.S_NONE for s in stats):
            self.status = self.S_SOME
        else:
            self.status = self.S_NONE
        return self.status

    def trace(self, stop=()):
        print("{} - REPO -\t({}B)".format(self.states[self.status], self.size()))
        for name, child in self:
            child.trace(stop=stop)

    def __getitem__(self, name):
        try:
            return self.children[name]
        except KeyError:
            return None

    def __iter__(self):
        for child in self.children:
            yield child, self.children[child]

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
            return sum(child.size() for name, child in self)
        return os.path.getsize(self.path)

    def compare_to(self, other):
        self.status = self.S_NONE

        if not other:
            if self.entry.is_dir():
                for name, child in self:
                    child.compare_to(None) # make sure everyone gets assigned a value
            return

        if self.entry.is_dir():
            stats = [child.compare_to(other[name]) for name, child in self]
            if   all(s and s == self.S_ALL for s in stats):
                self.status = self.S_ALL
            elif all(s and s > self.S_SEMI for s in stats):
                self.status = self.S_SEMI
            elif any(s and s > self.S_NONE for s in stats):
                self.status = self.S_SOME
        else:
            if not other.entry.is_dir() and other.size() == self.size():
                self.status = self.S_ALL
        return self.status

    def trace(self, indent=0, stop=()):
        if self.entry.is_dir():
            if self.status in stop:
                print("{} {}{}: ... <skip>\t({}B)".format(self.states[self.status], "  "*indent, self.name, self.size()))
            else:
                print("{} {}{}:\t({}B)".format(self.states[self.status], "  "*indent, self.name, self.size()))
                for name, child in self:
                    child.trace(indent + 1, stop=stop)
        else:
            print("{} {}{}\t({}B)".format(self.states[self.status], "  "*indent, self.name, self.size()))
