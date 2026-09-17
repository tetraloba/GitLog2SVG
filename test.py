import subprocess
from collections import defaultdict

class Commit:
    def __init__(self):
        self.parents = []
        self.children = []
        self.branches = []

# REPO="../databases"
REPO="./tmp"

commits = defaultdict(Commit)  # commit_hash -> Commit object

res = subprocess.check_output(['git', '-C', REPO, 'branch', '--list'], text=True).strip().split('\n')
branches = [branch.lstrip('* ') for branch in res if branch]
print(branches) # debug

for branch in branches:
    commit_hash = subprocess.check_output(['git', '-C', REPO, 'rev-parse', branch], text=True).strip()
    while True:
        if commit_hash in commits:
            continue
        # Get parent commits
        try:
            parents = subprocess.check_output(['git', '-C', REPO, 'rev-list', '--parents', '-n', '1', commit_hash], text=True).strip().split()[1:]
        except subprocess.CalledProcessError:
            break  # No parents for this commit

        if not commits[commit_hash].parents:
            commits[commit_hash].parents = parents
        for parent in parents:
            commits[parent].children.append(commit_hash)
    res = subprocess.check_output(['git', '-C', REPO, 'rev-parse', branch], text=True).strip()
    print(f"Branch: {branch}, Commit: {res}") # debug
    commits[res].branches.append(branch)


"""
いや無理だわ。あるGitRepositoryを決定論的にMermaidのGitGraphの形にするのは無理。
merge commitを，mergeされた側がmergeした時点で過去のチェーン(commitの連鎖)が元々どのbranchだったかは特定不可能。
例えば以下の場合，`ea6fff5`と`535b0ee`のどっちのチェーンが`main`, `branch1`だったか見分けつかない。
code:txt
 tetraloba@Niobe:~/projects/GitLog2SVG/tmp$ git log --oneline --graph
 *   f99941f (HEAD -> branch1, main) Merge branch 'branch1' (Niobe)
 |\
 | * ea6fff5 file2.txt (Niobe)
 * | 535b0ee file3 (Niobe)
 |/
 * fb7c47b file1 (Niobe)
 * 994e49b initiali commit (Niobe)

MermaidのGtGraphはあくまでGitのコミットの説明用であって，実際のGitの構造を表現できるものではなさそう。
単なるグラフで十分。
"""
