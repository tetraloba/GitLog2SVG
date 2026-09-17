import subprocess

# REPO="../databases"
REPO = "./tmp"
OUTFILE = "out.md"

edges = []  # List of edges (child_commit_hash, parent_commit_hash)

all_commit_hashes = subprocess.check_output(['git', '-C', REPO, 'rev-list', '--all'], text=True).strip().split('\n')

for commit_hash in all_commit_hashes:
    try:
        parent_hashes = subprocess.check_output(['git', '-C', REPO, 'rev-list', '--parents', '-n', '1', commit_hash], text=True).strip().split()[1:]
    except subprocess.CalledProcessError:
        break  # No parents for this commit
    for parent_hash in parent_hashes:
        edges.append((commit_hash, parent_hash))  # Add edges from commit to its parents

res = subprocess.check_output(['git', '-C', REPO, 'branch', '--list'], text=True).strip().split('\n')
branches = [branch.lstrip('* ') for branch in res if branch]
print(branches) # debug

for branch in branches:
    commit_hash = subprocess.check_output(['git', '-C', REPO, 'rev-parse', branch], text=True).strip()
    edges.append((branch, commit_hash))  # Add edge from branch to commit

with open(OUTFILE, 'w') as f:
    f.write('```mermaid\ngraph\n')
    for edge in edges:
        f.write(f"    {edge[0]} --> {edge[1]}\n")
    f.write('```\n')
