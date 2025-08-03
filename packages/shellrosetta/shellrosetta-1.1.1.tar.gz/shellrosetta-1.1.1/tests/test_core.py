# tests/test_core.py

import unittest
from shellrosetta.core import lnx2ps, ps2lnx

class TestShellRosettaCore(unittest.TestCase):
    def test_ls_translation(self):
        self.assertIn("Get-ChildItem", lnx2ps("ls"))
        self.assertIn("Get-ChildItem | Format-List", lnx2ps("ls -l"))
        self.assertIn("-Force", lnx2ps("ls -a"))
        self.assertIn("-Force | Format-List", lnx2ps("ls -la"))

    def test_rm_translation(self):
        self.assertIn("Remove-Item", lnx2ps("rm"))
        self.assertIn("-Recurse -Force", lnx2ps("rm -rf /tmp/test"))
    
    def test_ps2lnx(self):
        self.assertIn("ls", ps2lnx("Get-ChildItem"))
        self.assertIn("ls -a", ps2lnx("Get-ChildItem -Force"))
        self.assertIn("rm -rf", ps2lnx("Remove-Item -Recurse -Force"))

    def test_pipeline_translation(self):
        # Test Linux to PowerShell pipelines
        result = lnx2ps("ls -alh | grep error")
        self.assertIn("Get-ChildItem -Force | Format-List", result)
        self.assertIn("Select-String error", result)
        
        # Test PowerShell to Linux pipelines
        result = ps2lnx("Get-ChildItem -Force | Select-String error")
        self.assertIn("ls -a", result)
        self.assertIn("grep", result)

    def test_complex_flags(self):
        # Test complex flag combinations
        self.assertIn("-Recurse -Force -Verbose", lnx2ps("rm -rfv"))
        self.assertIn("-CaseSensitive:$false", lnx2ps("grep -i"))
        self.assertIn("-Recurse -CaseSensitive:$false", lnx2ps("grep -ri"))

    def test_system_commands(self):
        # Test system information commands
        self.assertIn("Get-Process", lnx2ps("ps aux"))
        self.assertIn("Test-Connection", lnx2ps("ping"))
        self.assertIn("Get-NetIPAddress", lnx2ps("ifconfig"))

    def test_file_operations(self):
        # Test file operation commands
        self.assertIn("Copy-Item", lnx2ps("cp"))
        self.assertIn("Move-Item", lnx2ps("mv"))
        self.assertIn("New-Item -ItemType File", lnx2ps("touch"))

    def test_archive_commands(self):
        # Test archive/compression commands
        result = lnx2ps("tar -czvf backup.tar.gz myfolder/")
        self.assertIn("Compress-Archive", result)
        # Note: The exact note text might vary, so we check for the key part
        self.assertIn("Outputs .zip", result)

    def test_environment_variables(self):
        # Test environment variable handling
        self.assertIn("$env:", lnx2ps("export"))
        self.assertIn("Get-ChildItem Env:", lnx2ps("env"))

    def test_edge_cases(self):
        # Test edge cases and error handling
        self.assertIn("No translation", lnx2ps("nonexistent_command"))
        self.assertIn("No Linux equivalent", ps2lnx("Get-NonexistentCommand"))
        
        # Test empty input
        self.assertEqual(lnx2ps(""), "")
        self.assertEqual(ps2lnx(""), "")
        
        # Test whitespace-only input
        self.assertEqual(lnx2ps("   "), "")
        self.assertEqual(ps2lnx("   "), "")

    def test_special_characters(self):
        # Test commands with special characters
        self.assertIn("Get-ChildItem", lnx2ps("ls 'file with spaces'"))
        self.assertIn("Remove-Item", lnx2ps('rm "quoted file"'))

    def test_multiple_pipes(self):
        # Test multiple pipeline stages
        result = lnx2ps("ls -la | grep error | wc -l")
        self.assertIn("Get-ChildItem -Force | Format-List", result)
        self.assertIn("Select-String error", result)
        self.assertIn("Measure-Object", result)

if __name__ == '__main__':
    unittest.main()
