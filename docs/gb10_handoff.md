# GB10 handoff — how this sandbox and the DGX Spark cooperate

## Topology (verified 2026-07-07)
- This Cowork sandbox: Linux VM, no GPU, internet egress OK (github read), **no route to the Spark**
  (tailnet 100.98.74.5 unreachable, mDNS unresolvable) and **no push credentials**.
- The Spark (GB10): has the GitHub-authenticated session that created SharathSPhD/prabodha.
- Shared file channel: the projects drive (SMB). Git must NOT run over it (lock semantics); it carries
  a file mirror + `prabodha.bundle` (full history) only.

## Enable direct native work (preferred — one-time, operator action)
Authorize this sandbox's key on the Spark, then Claude here can ssh in, build docker, run jobs, push:
```
# on the Spark (or via your GB10 session):
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKHJ7bHUCg8CSUmtGtO0f1CnHuUjdHGt0ip+YCtFYq48 prabodha-cowork-sandbox" >> ~/.ssh/authorized_keys
```
Then tell Claude the Spark's **LAN IP** (192.168.0.x — tailnet IPs don't route from the sandbox).

## Until then: bundle handoff (each cycle, one command on the Spark)
```
# first time:
git clone /path/to/mounted/projects/prabodha/prabodha.bundle ~/projects/prabodha
cd ~/projects/prabodha && git remote set-url origin https://github.com/SharathSPhD/prabodha.git && git push -u origin main
# subsequent cycles:
cd ~/projects/prabodha && git fetch /path/to/mounted/projects/prabodha/prabodha.bundle main && git merge FETCH_HEAD && git push
# run L1:
docker compose run l1
```
After any GB10-side commits are pushed, the sandbox pulls from the public repo (read needs no auth).
