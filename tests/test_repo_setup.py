import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]/'repo_setup.py'

class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.p=Path(self.tmp.name)/'repo'
        self.p.mkdir()
        subprocess.run(['git','init',str(self.p)],capture_output=True,check=True)
        (self.p/'package.json').write_text(json.dumps({'name':'sample','scripts':{'lint':'eslint .'}}))
        (self.p/'README.md').write_text('Sample project')
    def tearDown(self):
        self.tmp.cleanup()
    def execute(self,*args):
        return subprocess.run([sys.executable,str(CODE),str(self.p),*args],text=True,capture_output=True)
    def test_prepare_idempotent_and_preserve(self):
        (self.p/'AGENTS.md').write_text('# Original guidance\nDo not erase me!\n')
        run=self.execute('--hooks','--ci')
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        contents=(self.p/'AGENTS.md').read_text()
        self.assertIn('Do not erase me!',contents)
        self.assertIn('repo-setup:begin',contents)
        self.assertTrue((self.p/'.agent-bootstrap/project-map.md').exists())
        self.assertTrue((self.p/'.githooks/pre-commit').exists())
        self.assertTrue((self.p/'.github/workflows/agent-quality.yml').exists())
        self.assertTrue((self.p/'.github/dependabot.yml').exists())
        self.assertIn('npm', (self.p/'.github/dependabot.yml').read_text())
        another=self.execute('--hooks','--ci')
        self.assertEqual(another.returncode,0,another.stdout+another.stderr)
        self.assertEqual(contents,(self.p/'AGENTS.md').read_text())
    def test_dry_run_no_changes(self):
        self.assertEqual(self.execute('--dry-run','--ci','--hooks').returncode,0)
        self.assertFalse((self.p/'AGENTS.md').exists())
        self.assertFalse((self.p/'.agent-bootstrap').exists())
    def test_preserves_existing_ci_and_husky(self):
        f=self.p/'.github/workflows/current.yml'
        f.parent.mkdir(parents=True)
        f.write_text('name: current\n')
        (self.p/'.husky').mkdir()
        self.assertEqual(self.execute('--ci','--hooks').returncode,0)
        self.assertFalse((self.p/'.github/workflows/agent-quality.yml').exists())
        self.assertTrue((self.p/'.github/dependabot.yml').exists())
        self.assertFalse((self.p/'.githooks').exists())
        self.assertEqual(f.read_text(),'name: current\n')
    def test_full_dry_run_does_not_install_or_change_files(self):
        p = self.execute('--full', '--dry-run')
        self.assertEqual(p.returncode, 0, p.stdout+p.stderr)
        self.assertFalse((self.p/'AGENTS.md').exists())
        self.assertFalse((self.p/'.githooks').exists())

    def test_doctor_is_read_only(self):
        p = self.execute('--doctor')
        self.assertEqual(p.returncode, 0, p.stdout+p.stderr)
        self.assertIn('DIAGNÓSTICO', p.stdout)
        self.assertFalse((self.p/'AGENTS.md').exists())

    def test_refuse_non_git_directory(self):
        (self.p/'.git').rename(self.p/'_git')
        self.assertNotEqual(self.execute().returncode,0)

if __name__=='__main__': unittest.main()
