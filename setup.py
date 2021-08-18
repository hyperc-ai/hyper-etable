import os
import sys
import platform
import compileall
import glob
from setuptools import setup
from setuptools import find_packages
from wheel.bdist_wheel import bdist_wheel
import shutil

PACKAGE_NAME = 'hyperc'

def get_readme():
    return open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r').read()


class MyBuilder(bdist_wheel):

    def get_tag(self):
        python, abi, plat = bdist_wheel.get_tag(self)
        if 'linux' == plat.split('_')[0]:
            plat = 'manylinux1_{0}'.format('_'.join(plat.split('_')[1:]))
        python, abi = 'py3', 'none'
        return python, abi, plat

    def run(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        #cleanup
        try:
            shutil.rmtree(os.path.join(cur_dir, "build"))
        except:
            pass
        try:
            shutil.rmtree(os.path.join(cur_dir, "dist"))
        except:
            pass
        package_dir = os.path.join(cur_dir, PACKAGE_NAME)

        #Remove old pyc files 
        fileList = glob.glob(cur_dir+'/*.pyc')
        for filePath in fileList:
            try:
                os.remove(filePath)
            except:
                print("Error while deleting file : ", filePath)

        # Build
        compileall.compile_dir(os.path.join(cur_dir, PACKAGE_NAME),legacy=True)
        compileall.compile_dir(os.path.join(cur_dir, "tests"), legacy=True)

        # Delete source
        fileList = glob.glob(package_dir + '/*.py')
        fileList.extend(glob.glob(package_dir + '/examples/*.py'))
        fileList.extend(glob.glob(cur_dir + '/tests/*.py'))
        fileList.extend(glob.glob(cur_dir + '/examples/*.py'))

        for filePath in fileList:
            if '__init__' in filePath or "setup.py" in filePath:
                print("init ", filePath)
                continue
            print("rm ", filePath)
            try:
                os.remove(filePath)
            except:
                print("Error while deleting file : ", filePath)
        self.root_is_pure = False
        bdist_wheel.run(self)


setup(
    name=PACKAGE_NAME,
    packages=find_packages(),
    include_package_data=True,
    cmdclass={'bdist_wheel': MyBuilder},
    version='0.0.1',
    author='"Andrew Gree, Kuznetsov Andrey A. ',
    author_email='andrew@criticalhop.com, andreykyz@gmail.com',
    license='Proprietary License',
    description="Python AI Planning and automated programming",
    long_description=get_readme(),
    keywords='python pddl hyperc planner ai ai-planning constraint-programming automated-planning optimization compilers',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Other',
        'Environment :: Console',
        'License:: Other/Proprietary License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
