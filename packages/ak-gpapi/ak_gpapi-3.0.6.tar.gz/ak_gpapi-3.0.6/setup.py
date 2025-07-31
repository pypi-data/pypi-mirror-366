from setuptools import setup
from setuptools.command.build_py import build_py as _build


import os.path
import subprocess
import shutil

PROTOC_EXEC = "protoc"

CURRENT_DIR = os.path.abspath( os.path.dirname( __file__ ) )

__VERSION__ = '3.0.6'

class ProtobufBuilder(_build):

    def run(self):
        # check if protobuf is installed
        exec_path = shutil.which(PROTOC_EXEC)
        if exec_path is None:
            raise Exception("You should install protobuf compiler")

        print("Building protobuf file")
        subprocess.run([exec_path,
            "--proto_path=" + CURRENT_DIR,
            "--python_out=" + CURRENT_DIR + "/gpapi/",
            CURRENT_DIR + "/googleplay.proto"])
        super().run()

setup(name='ak-gpapi',
      version=__VERSION__,
      description='Unofficial python api for google play',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      url='https://github.com/appknox/googleplay-api',
      author='appknox',
      author_email='engineering@appknox.com',
      license='GPL3',
      packages=['gpapi'],
      package_data={
          'gpapi': [
              'config.py'
              'device.properties',
              'googleplay_pb2.py',
              'googleplay.py',
              'utils.py'
          ]},
      include_package_data=True,
      cmdclass={'build_py': ProtobufBuilder},
      install_requires=['cryptography<41',
                        'protobuf==3.19.0',
                        'requests==2.31.0',
                        'urllib3 < 1.26.0'])
