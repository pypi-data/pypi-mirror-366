from setuptools import setup, find_packages

setup(
    name="chitram",
    version="0.1.0",
    author="Aman Mishra",
    author_email="jarvisbyaman@gmail.com",
    description="🎨 Chitram: Generate images from text prompts using AI",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",  # ✅ this is now valid
    include_package_data=True,
    project_urls={
        "YouTube": "https://www.youtube.com/channel/UCuYpMYOiuQyGgdM9LXupLEg",
        "Telegram": "https://t.me/jarvisbyamanchannel"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests",
        "Pillow",
        "rich"
    ],
)
