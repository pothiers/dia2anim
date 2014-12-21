'# EXAMPLE:
#   cd $sb/dia2anim
#   python setup.py sdist
#
#   cd ~/tmp
#   tar xvf $sb/dia2anim/dist/dia2anim-0.3.0.tar.gz
#   cd dia2anim-0.3.0
#   python setup.py install --prefix=/swl
#   prepend PATH ~/tmp/swl
#   cd
#   dia2anim.py ~/tmp/swl/test-data/test-2path.dia anim/test-2path
#   animate anim/test-2path/Background.gif

from distutils.core import setup
import glob


DESCRIPTION = '''
This tool was built to support research into automatic perception.  For
instance, it might be used to generate data for the "Numenta Platform for
Intelligent Computing" (NuPIC, http://www.numenta.com/)'''

setup(name='dia2anim',
      version='0.3.1',
      license='GPL',
      description='dia2anim creates a GIF animation from a schematic of a scene (drawn using Dia).',
      long_description=DESCRIPTION,
      author='Steve Pothier',
      author_email='b4ape@users.sourceforge.net',
      url='http://dia2anim.sourceforge.net/',
      keywords=['dia','gif','animate','movie'],
      package_dir  = {'dia2anim':'python'},
      scripts = glob.glob('python/dia2*.py'),
      data_files = [('test-data', glob.glob('test-data/*.dia')),
                    ('dia2anim-doc',glob.glob('doc/derived/*')),
                    ('xsl',glob.glob('xsl/*.xsl')),
                    ]
      )
