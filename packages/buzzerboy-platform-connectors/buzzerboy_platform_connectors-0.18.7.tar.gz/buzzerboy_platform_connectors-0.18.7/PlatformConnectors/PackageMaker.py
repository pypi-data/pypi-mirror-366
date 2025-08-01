from setuptools import setup, find_packages
import os, toml, json, subprocess

class PackageAutomation:

    def __init__(self, filepath=None):

        if filepath:
            self.filepath = filepath
        else:
            self.filepath = os.path.dirname(os.path.abspath(__file__))

        # Read pyproject.toml and gather project metadata
        with open(os.path.join(self.filepath, 'pyproject.toml'), 'r') as f:
            pyproject_data = toml.load(f)

        self.project = pyproject_data.get('project', {})
        self.name = self.project.get('name', 'unknown')
        self.version = self.project.get('version', '0.0.1')
        self.description = self.project.get('description', '')
        self.author = self.project.get('authors', [{}])[0].get('name', '')
        self.license = self.project.get('license', {}).get('file', 'MIT')

    def generate_package_json(self):
        package_json = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "main": "index.js",
            "scripts": {
                "semantic-release": "semantic-release"
            },
            "devDependencies": {
                "@semantic-release/changelog": "*",
                "@semantic-release/commit-analyzer": "*",
                "@semantic-release/git": "*",
                "@semantic-release/gitlab": "*",
                "@semantic-release/github": "*",            
                "@semantic-release/release-notes-generator": "*",
                "semantic-release": "*"
            },
            "release": {
                "branches": ["main"]
            },
            "author": self.author,
            "license": self.license
        }

        with open('package.json', 'w') as f:
            json.dump(package_json, f, indent=2)

    def increment_version(self):
        # Increment version
        major, minor, patch = self.version.split('.')
        patch = int(patch) + 1

        if patch >= 10:
            patch = 0
            minor = int(minor) + 1

        self.version = f'{major}.{minor}.{patch}'
        self.project['version'] = self.version

        # Read the entire pyproject.toml file
        with open('pyproject.toml', 'r') as f:
            pyproject_data = toml.load(f)

        # Update only the version property in the [project] section
        pyproject_data['project']['version'] = self.version

        # Write the updated content back to the file
        with open('pyproject.toml', 'w') as f:
            toml.dump(pyproject_data, f)

    def generate_changelog_from_git_log(self):
        # Get the git log
        git_log = subprocess.check_output(['git', 'log', '--pretty=format:%s']).decode('utf-8')
        commits = git_log.split('\n')

        # reverse commits array with last line being first line, and first line being last line
        commits = commits[::-1]

        # Group commits by version
        changelog = {}
        current_version = self.version
        for commit in commits:
            if 'Merge' in commit:
                # Increment minor version for PR merge commits
                major, minor, patch = current_version.split('.')
                minor = int(minor) + 1
                current_version = f'{major}.{minor}.{patch}'
                self.version = f'{major}.{minor}.{patch}'
                changelog[current_version] = []
            if current_version not in changelog:
                changelog[current_version] = []
            changelog[current_version].append(commit)

        # Write the changelog to CHANGELOG.md
        with open('CHANGELOG.md', 'w') as f:
            for version, changes in sorted(changelog.items(), reverse=True):
                f.write(f'## Version {version}\n')
                for change in changes:
                    f.write(f'- {change}\n')
                f.write('\n')

    def cleanUpMarkdown(self):
        # Remove lines starting with "// filepath:" from CHANGELOG.md
        with open('CHANGELOG.md', 'r') as f:
            lines = f.readlines()
        
        with open('CHANGELOG.md', 'w') as f:
            for line in lines:
                if not line.startswith('// filepath:'):
                    f.write(line)


    @staticmethod
    def auto_package(filepath=None):
        autoPackage = PackageAutomation(filepath=filepath)

        # Generate changelog from git log
        autoPackage.generate_changelog_from_git_log()
        autoPackage.cleanUpMarkdown()

        # Increment version
        autoPackage.increment_version()

        # Generate package.json
        autoPackage.generate_package_json()

        return autoPackage


    def parse_requirements(self, filename):
        absolute_path = os.path.join(self.filepath, filename)
        with open(absolute_path, 'r') as file:
            lines = file.readlines()
            return [line.strip() for line in lines if line.strip() and not line.startswith('#')]

    def ensure_manifest_includes_requirements(self):
        manifest_file = 'MANIFEST.in'
        requirements_line = 'include requirements.txt\n'
        if os.path.exists(manifest_file):
            with open(manifest_file, 'r') as file:
                lines = file.readlines()
            if requirements_line not in lines:
                with open(manifest_file, 'a') as file:
                    file.write(requirements_line)
        else:
            with open(manifest_file, 'w') as file:
                file.write(requirements_line)


    @staticmethod
    def auto_setup(package):

        # Ensure MANIFEST.in includes requirements.txt
        package.ensure_manifest_includes_requirements()


        # Read pyproject.toml
        pyproject = toml.load('pyproject.toml')
        project = pyproject['project']


        setup(
            name=project['name'],
            version=project['version'],
            author=project['authors'][0]['name'],
            author_email=project['authors'][0]['email'],
            description=project['description'],
            long_description=open('README.md').read(),
            long_description_content_type='text/markdown',
            url=project['urls']['Homepage'],
            packages=find_packages(),
            classifiers=project['classifiers'],
            python_requires=project['requires-python'],
            install_requires=package.parse_requirements("requirements.txt"),
            license=project['license']
        )


