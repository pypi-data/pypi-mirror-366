from setuptools import setup, find_packages

setup(
    name="browser-use-web-ui",
    version="0.1.5",
    description="Gradio Web UI for the browser-use AI agent",
    author="Suleman",
    author_email="sulemanmuhammad049@gmail.com",
    url="https://github.com/yourname/browser-use-web-ui",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "gradio",
        "playwright",
        "openai",
        "anthropic",
        "python-dotenv",
        "browser-use-agent"
    ],
    entry_points={
        "console_scripts": [
            "browser-webui = browser_use_web_ui.webui:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.8"
)
