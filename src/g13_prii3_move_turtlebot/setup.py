from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'g13_prii3_move_turtlebot'

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
    description='PRII3 Grupo 13 - Mueve el TurtleBot3 siguiendo el numero del grupo',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'draw_number = g13_prii3_move_turtlebot.draw_number:main',
            'obstacle_stop = g13_prii3_move_turtlebot.obstacle_stop:main',
        ],
    },
)
