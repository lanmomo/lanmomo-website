import re
import subprocess
import os
import shutil


def cache_bust():
    subprocess.call(['grunt', 'cacheBust'])


def main():
    if os.path.exists('../tmp'):
        shutil.rmtree('../tmp')
    shutil.copytree('../public', '../tmp')
    cache_bust()
    if os.path.exists('../static'):
        shutil.rmtree('../static')
    os.rename('../tmp', '../static')


if __name__ == "__main__":
    main()
