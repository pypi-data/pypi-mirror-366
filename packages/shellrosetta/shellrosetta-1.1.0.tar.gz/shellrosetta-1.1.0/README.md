# ShellRosetta

**Translate Linux/Bash commands to PowerShell and vice versa—flags, pipes, networking, and more.**

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)
[![Shell](https://img.shields.io/badge/shell-interactive-blue)](#interactive-shell-mode)
[![Tested](https://img.shields.io/badge/Tests-passing-brightgreen)](tests/)
[![PyPI version](https://badge.fury.io/py/shellrosetta.svg)](https://pypi.org/project/shellrosetta/)

---

## What is ShellRosetta?

ShellRosetta is a cross-platform CLI tool for developers, sysadmins, and anyone switching between Windows and Linux.

It instantly translates commands—including flags and arguments—between Linux/Bash and PowerShell. No more flipping between cheat sheets or Stack Overflow!

---

## Features

- 🖥️ **Interactive Shell Mode!** Open ShellRosetta as a REPL and translate commands live, just like in a real shell.
- 🔄 **Bi-directional translation:** Linux ↔ PowerShell, with accurate mappings for real-world scenarios.
- 🏷️ **Flag and multi-flag aware:** Understands combos like `ls -alh`, `rm -rf`, etc.
- 🔗 **Pipeline support:** Handles piped commands (e.g. `ls -l | grep foo`).
- 🌐 **Networking and system commands:** Supports `ping`, `curl`, `Get-NetTCPConnection`, and many more.
- 📋 **Extensive mappings:** Permissions, archiving, users, process management, environment variables, I/O redirection, and more.
- 🚦 **Helpful notes:** Outputs usage tips or warnings if there's no direct translation or if a flag behaves differently.
- 🧩 **Easily extensible:** Add or edit mappings in `mappings.py`—grow as you learn!
- ⚡ **Ready for shell aliases & tab-completion:** Bash/Zsh completion script included.

---

## Quickstart

**Clone and install locally:**


git clone https://github.com/sdirishguy/shellrosetta.git
cd shellrosetta
pip install .
Usage:

shellrosetta lnx2ps "ls -alh | grep error"
shellrosetta ps2lnx "Get-ChildItem -Force | Select-String error"
Or test before installing:

python -m shellrosetta.cli lnx2ps "ls -alh | grep error"
python -m shellrosetta.cli ps2lnx "Get-ChildItem -Force | Select-String error"
(Optional) Add aliases to your shell:

echo "alias lnx2ps='shellrosetta lnx2ps'" >> ~/.bashrc
echo "alias ps2lnx='shellrosetta ps2lnx'" >> ~/.bashrc
source ~/.bashrc
(Optional) Enable tab-completion:
Copy shellrosetta/autocomplete.sh somewhere (or use directly from the repo), then add this to your ~/.bashrc or ~/.zshrc:

source /path/to/shellrosetta/autocomplete.sh
Reload your shell:

source ~/.bashrc
# or
source ~/.zshrc
Now you get tab completion for commands and flags!

## Interactive Shell Mode
Run with no arguments for a live translation shell!

```shellrosetta```

You'll be prompted for your translation mode (lnx2ps or ps2lnx). Enter commands and see translations instantly, switching modes at any time with mode or exit with exit.

Example session:
```
$ shellrosetta
=================================================================
ShellRosetta: Linux ↔ PowerShell CLI Command Translator
Author: David Donohue
Repo: github.com/sdirishguy/shellrosetta
=================================================================
Welcome to ShellRosetta Interactive Mode!
Type 'exit' to quit, or 'mode' to switch translation direction.
Mode [lnx2ps/ps2lnx] (or 'exit'): lnx2ps
Type your LNX2PS commands below. Type 'mode' to switch, 'exit' to quit.

> ls -alh | grep foo

--- Translation ---
PowerShell Equivalent:
  Get-ChildItem -Force | Format-List # [Human-readable file sizes not natively available.] | Select-String foo
-------------------

> rm -rf /tmp
--- Translation ---
PowerShell Equivalent:
  Remove-Item -Recurse -Force /tmp
-------------------

> mode
Mode [lnx2ps/ps2lnx] (or 'exit'): ps2lnx
Switched to PS2LNX mode.

> Get-Process
--- Translation ---
Linux Equivalent:
  ps aux
-------------------

> exit
Goodbye!
```

## Bash/Zsh Tab Completion

Speed up your workflow with tab-completion for top-level commands and common flags.

1. Copy shellrosetta/autocomplete.sh into your home directory, or reference it from your project.

2. Add this to your ~/.bashrc or ~/.zshrc:

```source /path/to/shellrosetta/autocomplete.sh```
Reload your shell:

```source ~/.bashrc      # or source ~/.zshrc```

Now, typing lnx2ps l<TAB> or ps2lnx G<TAB> will auto-complete common commands and flags!

## Example autocomplete script (shellrosetta/autocomplete.sh):
```
# Bash/Zsh completion for ShellRosetta
_shellrosetta_complete() {
  local cur prev opts lnxflags psflags
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD-1]}"
  opts="ls rm cp mv grep find cat ping ifconfig netstat traceroute curl wget hostname nslookup dig"
  lnxflags="-a -l -h -R -r -f -v"
  psflags="-Force -Recurse -Verbose | Format-List -CaseSensitive:\$false"

  if [[ ${COMP_CWORD} -eq 1 ]]; then
    COMPREPLY=( $(compgen -W "lnx2ps ps2lnx" -- "${cur}") )
    return 0
  fi
  if [[ ${COMP_CWORD} -eq 2 ]]; then
    COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
    return 0
  fi
  if [[ ${COMP_WORDS[1]} == "lnx2ps" ]]; then
    if [[ ${COMP_WORDS[2]} == "ls" || ${COMP_WORDS[2]} == "rm" || ${COMP_WORDS[2]} == "cp" || ${COMP_WORDS[2]} == "mv" ]]; then
      COMPREPLY=( $(compgen -W "${lnxflags}" -- "${cur}") )
      return 0
    fi
  elif [[ ${COMP_WORDS[1]} == "ps2lnx" ]]; then
    if [[ ${COMP_WORDS[2]} =~ (Get-ChildItem|Remove-Item|Copy-Item|Move-Item|Select-String) ]]; then
      COMPREPLY=( $(compgen -W "${psflags}" -- "${cur}") )
      return 0
    fi
  fi
}
complete -F _shellrosetta_complete lnx2ps
complete -F _shellrosetta_complete ps2lnx
```

Examples

shellrosetta lnx2ps "ls -alh | grep foo"
# ➔ Get-ChildItem -Force | Format-List # [Human-readable file sizes not natively available.] | Select-String foo

shellrosetta lnx2ps "rm -rf /var/tmp"
# ➔ Remove-Item -Recurse -Force /var/tmp

shellrosetta lnx2ps "tar -czvf backup.tar.gz myfolder/"
# ➔ Compress-Archive # [Outputs .zip, not .tar.gz. For gzip, use third-party modules or 7-Zip.]

shellrosetta ps2lnx "Get-ChildItem -Force | Format-List"
# ➔ ls -la
Supported Command Areas
Filesystem: ls, rm, cp, mv, touch, cat, ln, mkdir, cd, pwd, etc.

Permissions & Ownership: chmod, chown, chgrp, icacls, etc.

Archiving/Compression: tar, gzip, gunzip, zip, unzip, Compress-Archive, Expand-Archive.

Processes: ps, top, kill, pkill, pgrep, Get-Process, Stop-Process.

System Info: uname, whoami, df, du, free, uptime, lscpu, lspci, lsusb, etc.

Networking: ifconfig, ping, netstat, ss, ssh, scp, wget, curl, Test-Connection, Get-NetIPAddress.

Environment Variables: export, unset, env, printenv, $env:, etc.

Users/Groups: adduser, userdel, passwd, usermod, New-LocalUser, Remove-LocalUser, etc.

History, clearing, date, man/help.

I/O Redirection: >, >>, <, 2>, &>, 2>&1.

See mappings.py for full details.

How the Logic Works
Checks for an exact command or command+flag mapping first (fast and accurate).

If not found, falls back to a flexible per-command flag parser for real-world combos.

Provides notes or warnings if there is no direct translation or usage caveat.

Handles piped commands and reconstructs them for the target shell.

## Project Structure:

shellrosetta/
  shellrosetta/
    __init__.py
    cli.py
    core.py
    mappings.py
    autocomplete.sh
  tests/
    test_core.py
  setup.py
  README.md
  LICENSE
  .gitignore

## Contribution Guidelines
We welcome all contributions!

Bug Reports:
Open a GitHub issue describing the bug and how to reproduce it.

Feature Requests:
Open a GitHub issue with [Feature] in the title, and explain your use-case and preferred UX.

Pull Requests:
Fork the repo, then clone your fork.

Create a new branch: git checkout -b feature/your-feature

Add your feature or bugfix.

Write or update tests in tests/ as appropriate.

Update README.md and/or mappings.py as needed.

Push to your fork and submit a PR—describe your changes!


Adding New Command Mappings:
Edit shellrosetta/mappings.py. Include both directions if possible (Linux ↔ PowerShell). Add a test if it’s a core mapping.


Coding Style:
Keep code PEP8-compliant.

Use clear, descriptive comments.

Prefer modular, testable code.

By contributing, you agree to license your work under the MIT License.

Questions? Open an issue or email David Donohue.



## License
MIT License



## Author
David Donohue
github.com/sdirishguy




## Tests
Run all tests:


python -m unittest discover -s tests

Example test coverage in tests/test_core.py:
```
import unittest
from shellrosetta.core import lnx2ps, ps2lnx

class TestShellRosettaCore(unittest.TestCase):
    def test_basic_ls(self):
        self.assertIn("Get-ChildItem", lnx2ps("ls"))

    def test_ls_with_flags(self):
        self.assertIn("-Force", lnx2ps("ls -a"))
        self.assertIn("Format-List", lnx2ps("ls -l"))
        self.assertIn("-Force | Format-List", lnx2ps("ls -al"))

    def test_rm_rf(self):
        self.assertIn("-Recurse -Force", lnx2ps("rm -rf mydir"))

    def test_pipeline(self):
        out = lnx2ps("ls -alh | grep foo")
        self.assertIn("Get-ChildItem -Force | Format-List", out)
        self.assertIn("Select-String foo", out)

    def test_ps2lnx_get_childitem(self):
        self.assertEqual(ps2lnx("Get-ChildItem"), "ls")
        self.assertEqual(ps2lnx("Get-ChildItem -Force"), "ls -a")

    def test_ps2lnx_with_pipeline(self):
        out = ps2lnx("Get-ChildItem -Force | Select-String foo")
        self.assertIn("ls -a", out)
        self.assertIn("grep", out)

    def test_unmapped(self):
        self.assertIn("No translation", lnx2ps("foo"))

    def test_chmod_pattern(self):
        out = lnx2ps("chmod 755 file.txt")
        self.assertIn("icacls", out)
        self.assertIn("755", out)

if __name__ == '__main__':
    unittest.main()

```