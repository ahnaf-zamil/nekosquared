#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Got sick and tired of trying to get stuff to work with pip automatically, and
dependencies being a pain in the backside.

This is an absolutely horriffic brute force attempt to install stuff. This
generates service and run scripts, and installs a virtual environment and
all depencencies.

./install.py onlydeps   -- Only install dependencies
./install.py update     -- Update any dependencies already satisfied.
"""
import getpass
import inspect
import os
import pip
import shutil
import subprocess
import sys
import time
import traceback

# Maps import name to pypi name.
dependencies = {
    # Async file io
    'aiofiles': 'aiofiles',
    # Async http io
    'aiohttp': 'aiohttp',
    # Async postgresql wrapper.
    'asyncpg': 'asyncpg',
    # Beautiful soup 4 HTML parser
    'bs4': 'beautifulsoup4',
    # Cached property
    'cached_property': 'cached_property',
    # Youtube streaming
    'youtube_dl': 'youtube_dl',
    # Python3.7 cached property backport.
    'dataclasses': 'dataclasses',
    # PILLOW image manip lib
    'PIL': 'pillow',
    'wordnik': 'wordnik-py3',
    'yaml': 'pyyaml',
    # Used by the `py` cog.
    'docutils': 'docutils',
    'sphinx': 'sphinx',
    # These are used only for caching purposes in the Py module :)
    # Intentionally is incorrect. Don't alter until Danny releases
    # the rewrite properly.
    'discord.py': 'git+https://github.com/rapptz/discord.py@rewrite#egg'
                  '=discord.py[voice]',
    # My pagination utilities I have outsourced to a separate repository.
    'discomaton': 'git+https://github.com/neko404notfound/discomaton',
}

python_command = 'python3'

# Should we force update?
args = sys.argv[1:]
if args and any(args[0] == x for x in ('-h', '--help', 'help', '-?')):
    print('Args:')
    print('  update - updates all dependencies')
    print('  onlydeps - does not set up a virtual environment, nor clone the '
          'repo.')
    exit(0)

update_flag = '-U' if 'update' in args or 'upgrade' in args else None
just_deps = '-D' if 'onlydeps' in args else None


def shell_do(command):
    print(command)
    subprocess.check_call(command,
                          universal_newlines=True, shell=True)


# Ensure python3.6 or 3.7 for now.
try:
    assert sys.version_info[0] == 3, 'Must be Python3.6 or Python3.7'
    assert sys.version_info[1] in (6, 7), 'Must be Python3.6 or Python3.7'
    if sys.version_info[1] == 7:
        print('Python3.7: This is experimental support only')
        python_command += '.7'
    else:
        python_command += '.6'

except AssertionError:
    traceback.print_exc()
    exit(2)

if not just_deps:
    # Try to get virtualenv package, install it if it does not exist.
    print('I will create a venv in this directory, and then clone the repo.')

    i = 5
    while i >= 0:
        print(f'You have {i}s to cancel the operation...', end='')
        time.sleep(1)
        i -= 1
        print('\r', end='')
    print()

    try:
        import venv
    except ImportError:
        print('Attempting to install venv')
        try:
            assert getpass.getuser() == 'root', 'You must be root to install ' \
                                                'venv '
            pip.main(['install', '-U', 'python3-venv'])
            import venv
            print('Now reinvoke this command again, but not as root!')
            exit(0)
        except BaseException as ex:
            traceback.print_exception(type(ex), ex, ex.__traceback__)
            print('Please install venv (virtualenv) manually.')
            exit(3 if type(ex) == AssertionError else 4)

    # First git clone
    if os.path.exists('nekosquared'):
        print('Nekosquared directory already exists...')
        exit(5)

    shell_do('git clone https://github.com/espeonageon/nekosquared')
    os.chdir('./nekosquared')

    # Make the VENV if needbe.
    if os.path.exists('venv'):
        try:
            assert os.path.isdir('venv'), 'venv exists, but it isn\'t a ' \
                                          'directory! '
        except AssertionError:
            exit(6)
        else:
            print('venv directory already exists.')
    else:
        try:
            print('Creating venv...')
            venv.create('venv',
                        prompt='neko²',
                        system_site_packages=True)
            assert os.path.isdir('venv'), 'Unknown error'
        except BaseException as ex:
            traceback.print_exception(type(ex), ex, ex.__traceback__)
            exit(7)

    # Ensure bash is installed. Atm I cba to try and get this to work on Windows
bash_path = shutil.which('bash')

try:
    assert bash_path is not None, 'Bash must be installed and accessible.'
except AssertionError:
    exit(8)

# Generate a shell script to install the stuff we need in the venv.

with open('temp-install-script.sh', 'w') as script_file:
    script = f'''
        #!/bin/bash
        function main() {{
            source venv/bin/activate
            python3.6 -m pip install --upgrade pip
        '''.lstrip()
    for dep, pkg in dependencies.items():
        script += f'''
            if {python_command} -c "import {dep}" > /dev/null 2>&1; then
        '''
        if update_flag is not None:
            script += f'        python3.6 -m pip install {update_flag} {pkg}\n'
        else:
            script += f'        echo Already installed {pkg}\n'

        script += f'''
            else
                {python_command} -m pip install {pkg}
            fi'''

    script += '''
        }

        time main
        '''

    script = inspect.cleandoc(script)
    print('Script:')
    print(script)
    script_file.write(script)
    shell_do('chmod -v +x temp-install-script.sh')

shell_do(f'./temp-install-script.sh && rm -v temp-install-script.sh')

print('Completed.')

if not just_deps:
    print('Generating run script and sample service script.')

    run_script = f'''#!/bin/bash
    source venv/bin/activate
    {python_command} -m neko2
    '''

    service_script = f'''[Unit]
    Description=Nekozilla^2 generated systemd Service
    
    [Service]
    Type=simple
    PIDFile=/var/run/neko2.pid
    ExecStart={os.path.join(os.getcwd(), "neko2.sh")}
    Restart=always
    User={getpass.getuser()}
    WorkingDirectory={os.getcwd()}
    
    [Install]
    WantedBy=multi-user.target
    '''

    enable_script = '''#!/bin/bash
    sudo cp neko2.service /etc/systemd/system -v
    sudo systemctl daemon-reload
    sudo systemctl enable neko2
    
    echo "Run 'sudo systemctl start neko2' to start the service."
    '''

    update_script = '''#!/bin/bash
    git fetch --all && git reset --hard origin/master
    '''

    with open('neko2.sh', 'w') as run_file:
        print(f'Run script: {os.path.join(os.getcwd(), "neko2.sh")}')
        print(run_script)
        run_file.write(run_script)

    with open('neko2.service', 'w') as service_file:
        print(f'Sample service: {os.path.join(os.getcwd(), "neko2.service")}')
        print(service_script)
        service_file.write(service_script)

    with open('enable.sh', 'w') as enable_file:
        print(f'Enable script: {os.path.join(os.getcwd(), "enable.sh")}')
        print(enable_script)
        enable_file.write(enable_script)

    with open('update.sh', 'w') as update_file:
        print(f'Update script: {os.path.join(os.getcwd(), "update.sh")}')
        print(update_script)
        update_file.write(update_script)

    shell_do('chmod -v +x neko2.sh enable.sh update.sh')

print(
    'Done. All you need to do now is add your configurations into the config '
    'dir inside `nekosquared\'. See the `example-config\' '
    'directory for examples.'
)
