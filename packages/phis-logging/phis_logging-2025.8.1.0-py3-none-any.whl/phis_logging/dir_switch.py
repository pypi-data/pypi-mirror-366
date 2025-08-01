from pathlib import Path
import os
import shutil


def switch_dir():
    cwd = Path.cwd()
    if cwd.joinpath('文档').exists():
        return
    elif cwd.parent.joinpath('文档').exists():
        os.chdir(cwd.parent)


def setup_dir():
    switch_dir()

    if not Path('执行结果').exists():
        Path('执行结果').mkdir(parents=True, exist_ok=True)

    if not Path('执行结果/env.txt').exists():
        shutil.copy(Path('文档/env.txt'), Path('执行结果/env.txt'))
