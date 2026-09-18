from setuptools import find_packages, setup

package_name = 'siddhant_trevor_fsm_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='siddhant',
    maintainer_email='glorb458@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'fsm = siddhant_trevor_fsm_pkg.fsm:main',
            'draw_shape = siddhant_trevor_fsm_pkg.draw_shape:main',
            'obj_detect = siddhant_trevor_fsm_pkg.obj_detect:main',
            'person_follow = siddhant_trevor_fsm_pkg.person_follow:main',
            'wall_follow = siddhant_trevor_fsm_pkg.wall_follow:main',
            'detect_wall = siddhant_trevor_fsm_pkg.detect_wall:main',
        ],
    },
)
