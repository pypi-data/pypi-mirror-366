from setuptools import setup, find_packages

setup(
      name="nt_PyTgram_bot",
      version="0.1.0",
      author="Latipova Sevara",
      description="Python Telegram Bot",
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown",
      url="https://github.com/sevapova/py-gram-bot/PyTgram_bot",
      packages=find_packages(),
      classifiers=[
          "Programming Language :: Python",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires=">=3.11",
  )