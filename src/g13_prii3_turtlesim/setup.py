from setuptools import find_packages, setup
import os
from glob import glob
package_name = 'g13_prii3_turtlesim'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
	(os.path.join('share', package_name, 'launch'), glob('launch/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='teo',
    maintainer_email='tvergut@upv.edu.es',
    description='PRII3 Grupo 13 - Nodo que dibuja el número del grupo en turtlesim',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
		'my_node = g13_prii3_turtlesim.my_node:main',
		'draw_number = g13_prii3_turtlesim.draw_number:main',
        ],
    },


)
