from setuptools import setup, find_packages

setup(
    name="maze_generator_for_algorithm",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["pyautogui", "Pillow"],
    author="Chandramouli Ramesh",
    author_email="aravind2377@gmail.com",
    description="Maze generation tool with turtle graphics and JSON override support.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
)
