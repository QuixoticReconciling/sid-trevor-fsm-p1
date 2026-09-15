from setuptools import find_packages, setup

package_name = 'siddhant-trevor-fsm-pkg'

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
            'fsm_node = siddhant_trevor_fsm_pkg.fsm_node:main',
            'draw_shape_node = siddhant_trevor_fsm_pkg.draw_shape_node:main',
            'obj_detector_node = siddhant_trevor_fsm_pkg.obj_detector_node:main',
            'p_follow_node = siddhant_trevor_fsm_pkg.p_follow_node:main',
            'w_follow_node = siddhant_trevor_fsm_pkg.w_follow_node:main',
        ],
    },
)
