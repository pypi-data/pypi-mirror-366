import sysconfig
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as build_py_orig
import shutil
from pathlib import Path
import site
import sys
import os
import platform

PTH_FILE = "docoreai_autopatch.pth"

class build_py(build_py_orig):
    def run(self):
        # First do the normal build
        super().run()

        # Now copy the .pth file into the build directory where .py files are placed
        if not os.path.exists(PTH_FILE):
            print(f"ℹ️ {PTH_FILE} not found. Creating blank file.")
            with open(PTH_FILE, "w") as f1:
                 f1.write("")
        # Define target path in build directory                 
        target = os.path.join(self.build_lib, PTH_FILE)
        print("build_lib path:", self.build_lib)
        # Copy (overwrite if exists)
        shutil.copyfile(PTH_FILE, target)
        print(f"Copied {PTH_FILE} to {target}")

        site_packages_path = sysconfig.get_paths()["purelib"]
        with open("site_path.txt", "w") as f:
            f.write(site_packages_path)

        # Save current working directory (where install command was run)
        try:
            cwd_path = os.getcwd()
            with open("docoreai_cwd.txt", "w", encoding="utf-8") as f:
                f.write(cwd_path)
            print(f"docoreai_cwd.txt written to install path: {cwd_path}")
        except Exception as e:
            print(f"Failed to write docoreai_cwd.txt: {e}")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setup(
    name="docoreai",
    version="1.0.0b1",
    author="Saji John Miranda",
    author_email="info@docoreai.com",
    license="CC BY-NC-ND 4.0",
    packages=find_packages(
        include=["docore_ai", "docore_ai.*", "api", "api.*"],
        exclude=["docore_ai.Tests", "docore_ai.Tests.*"],
    ),
    cmdclass={"build_py": build_py},
    package_data={
            "": ["LICENSE.md"],
                "docore_ai.prompt_updates": ["data/*.enc", "data/*.sig"],  # Include encrypted prompt files
        },
description="DoCoreAI is an AI prompt optimization tool for developers and teams to reduce LLM cost, improve output, and analyze GPT prompt efficiency—no fine-tuning needed.",
    long_description_content_type="text/markdown",
    url="https://docoreai.com",
    project_urls={
        "Homepage": "https://docoreai.com",
        "Documentation": "https://docoreai.com/docs/",
        "Source Code": "https://github.com/SajiJohnMiranda/DoCoreAI",
        "Blog Post": "https://mobilights.medium.com/intelligent-prompt-optimization-bac89b64fa84",
        "Funding": "https://docoreai.com/pricing/",
        "Support": "https://docoreai.com/contact-us",
    },
    install_requires=[
        "uvicorn",
        "pydantic",
        "fastapi",  
        "python-dotenv",
        "openai",# dynamic installation of the correct openai version based on the user environment
        #"openai>=0.28.1",       # or latest tested version like 1.9.0
        #"httpx==0.27.2",        # pinned to avoid proxy-related crash
        "groq",
        "requests",
        "tiktoken",
        "typer",
        "rich",          # typer[all] pulls this in
        "click",         # typer needs this to run CLI
        "setuptools>=40.0.0",  # Optional but safe
        "psutil>=5.9.0",
        "importlib-metadata; python_version < '3.8'",
        "packaging>=20.0",
        "streamlit",
        "pandas",
        "streamlit-aggrid",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: Other/Proprietary License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="openai, groq, prompt optimization, llm cost reduction, ai development, prompt tuning, gpt efficiency, docoreai",

    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "docoreai=docore_ai.cli:app",
        ],
    },
    include_package_data=True,
    zip_safe=False,    
    data_files=[(sysconfig.get_paths()["purelib"], [PTH_FILE])], #31-Jul helps remove pth file in pip uninstall

)