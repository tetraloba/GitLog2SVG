import subprocess
from typing import override

# REPO="../databases"
REPO = "./tmp"
OUTFILE = "out.md"

class Node:
    def __init__(self, name = None, title = None, description = None):
        self._name = name
        self._title = title
        self._description = description
    def name(self):
        return self._name
    def title(self):
        return self._title
    def description(self):
        return self._description
class Edge:
    def __init__(self, source: Node = None, target: Node = None):
        self._source = source
        self._target = target
    def __str__(self):
        return f"{self._source.name()} --> {self._target.name()}"

class Commit(Node):
    def __init__(self, hash = None, tree = None, parents = [], author = None, committer = None, message = None):
        self._hash = hash
        self._tree = tree
        self._parents = parents
        self._author = author
        self._committer = committer
        self._message = message
    def hash(self):
        return self._hash
    def short_hash(self):
        return self._hash[:7]
    def __str__(self):
        return self.hash()
    @override
    def name(self):
        return self.short_hash()
    @override
    def title(self):
        return "\n".join(f"parent {parent}" for parent in self._parents) + f"\nauthor {self._author}\n\n{self._message}"
    @override
    def description(self):
        return f"tree {self._tree}\n" + "\n".join(f"parent {parent}" for parent in self._parents) + f"\nauthor {self._author}\ncommitter {self._committer}\n\n{self._message}"
class Branch(Node):
    def __init__(self, name = None, commit = None):
        self._name = name
        self._commit = commit
    def commit(self):
        return self._commit
    @override
    def name(self):
        return self._name
    @override
    def title(self):
        return f"branch {self._name}\ncommit {self._commit}"
    @override
    def description(self):
        return f"branch {self._name}\ncommit {self._commit}"

edges: list[Edge] = []

all_commit_hashes = subprocess.check_output(['git', '-C', REPO, 'rev-list', '--all'], text=True).strip().split('\n')
commits: dict[str, Commit] = {commit_hash : Commit(hash=commit_hash) for commit_hash in all_commit_hashes}

for commit in commits.values():
    #TODO Commitオブジェクトの生成とEdgeの生成を分ける
    try:
        parent_hashes = subprocess.check_output(['git', '-C', REPO, 'rev-list', '--parents', '-n', '1', commit.hash()], text=True).strip().split()[1:]
    except subprocess.CalledProcessError:
        break  # No parents for this commit
    for parent_hash in parent_hashes:
        edges.append(Edge(source=commit, target=commits[parent_hash]))  # Add edges from commit to its parents

res = subprocess.check_output(['git', '-C', REPO, 'branch', '--list'], text=True).strip().split('\n')
branch_names = [r.lstrip('* ') for r in res if r]
branches: dict[str, Branch] = {branch_name: Branch(name=branch_name) for branch_name in branch_names}
print(branches) # debug

for branch in branches.values():
    #TODO Branchオブジェクトの生成とEdgeの生成を分ける
    commit_hash = subprocess.check_output(['git', '-C', REPO, 'rev-parse', branch.name()], text=True).strip()
    edges.append(Edge(source=branch, target=commits[commit_hash]))  # Add edge from branch to commit

with open(OUTFILE, 'w') as f:
    f.write('```mermaid\ngraph\n')
    for edge in edges:
        f.write(f"    {edge}\n")
    f.write('```\n')
