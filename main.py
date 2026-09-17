import subprocess
from typing import override

from bs4 import BeautifulSoup

# REPO="../databases"
REPO = "./tmp"
OUT_MD = "out.md"
OUT_MMD = "out.mmd"
OUT_SVG = "out.svg"
OUT_SVG_WITH_TITLE = "out_with_title.svg"
USER_ID = subprocess.check_output(['id', '-u'], text=True).strip()
GROUP_ID = subprocess.check_output(['id', '-g'], text=True).strip()
DOCKER_MMDC = ["docker", "run", "--rm", "-u", f"{USER_ID}:{GROUP_ID}", "-v", ".:/data", "minlag/mermaid-cli"]

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
    def __init__(self, hash = None, tree = None, parents = None, author = None, committer = None, message = None):
        self._hash = hash
        self._tree = tree
        self._parents = parents if parents else []
        self._author = author
        self._committer = committer
        self._message = message
    def hash(self):
        return self._hash
    def short_hash(self):
        return self._hash[:7]
    def __str__(self):
        return self.hash()
    def set_tree(self, tree):
        self._tree = tree
    def add_parent(self, parent):
        if parent in self._parents:
            return
        self._parents.append(parent)
    def set_author(self, author):
        self._author = author
    def set_committer(self, commiter):
        self._commiter = commiter
    def set_message(self, message):
        self._message = message
    def get_parents(self):
        return self._parents
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
    def set_commit(self, commit):
        self._commit = commit
    def get_commit(self):
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

# generate commits
for commit in commits.values():
    res_lines = subprocess.check_output(['git', '-C', REPO, 'cat-file', '-p', commit.hash()], text=True).strip().split('\n')
    for i, res_line in enumerate(res_lines):
        if res_line[0:5] == 'tree ':
            commit.set_tree(res_line[5:])
        elif res_line[0:7] == 'parent ':
            commit.add_parent(res_line[7:])
        elif res_line[0:7] == 'author ':
            commit.set_author(res_line[7:])
        elif res_line[0:10] == 'committer ':
            commit.set_committer(res_line[10:])
        elif res_line == '':
            commit.set_message("\n".join(res_lines[i+1:]))
            break
        else:
            print(f"attribute not found for line ({res_line}).")

# generate branches
res = subprocess.check_output(['git', '-C', REPO, 'branch', '--list'], text=True).strip().split('\n')
branch_names = [r.lstrip('* ') for r in res if r]
branches: dict[str, Branch] = {branch_name: Branch(name=branch_name) for branch_name in branch_names}
print(branches) # debug
for branch in branches.values():
    commit_hash = subprocess.check_output(['git', '-C', REPO, 'rev-parse', branch.name()], text=True).strip()
    branch.set_commit(commit_hash)


# generate edges
for commit in commits.values():
    for parent_hash in commit.get_parents():
        edges.append(Edge(source=commit, target=commits[parent_hash]))  # Add edges from commit to its parents
for branch in branches.values():
    edges.append(Edge(source=branch, target=commits[branch.get_commit()]))  # Add edge from branch to commit

# Generate Mermaid text

mermaid_text = 'graph\n'
for edge in edges:
    mermaid_text += f"    {edge}\n"

with open(OUT_MD, 'w') as f:
    f.write('```mermaid\n')
    f.write(mermaid_text)
    f.write('```\n')

with open(OUT_MMD, 'w') as f:
    header = """---
config:
  htmlLabels: false
---
"""
    f.write(header)
    f.write(mermaid_text)

# Generate SVG from Mermaid using Docker

subprocess.run(DOCKER_MMDC + ['-i', OUT_MMD, '-o', OUT_SVG])

# Add title tags to the generated SVG

name2title = {node.name(): node.title() for node in list(commits.values()) + list(branches.values())}
with open(OUT_SVG, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'xml')
# classに "node" を持つ <g> 要素をすべて抽出
for node_g in soup.find_all('g', class_=lambda c: c and 'node' in c.split()):
    # 内包する全テキスト（ネストされたtspanなど）を透過的に結合取得
    commit_id = node_g.get_text(strip=True)
    if commit_id in name2title:
        if not node_g.find('title'):
            # titleタグを生成して挿入
            title_tag = soup.new_tag('title')
            title_tag.string = name2title[commit_id]
            node_g.append(title_tag)
with open(OUT_SVG_WITH_TITLE, 'w', encoding='utf-8') as f:
    f.write(str(soup))
