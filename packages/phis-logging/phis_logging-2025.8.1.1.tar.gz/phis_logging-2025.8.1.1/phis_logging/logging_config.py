import logging
import os
from datetime import datetime
import sys


def 配置日志(
    level=None,
    old_dir_compat=True,
    show_logger_name=True,
    show_filename=False,
    filename_color='cyan',
):
    """
    设置日志同时输出到控制台和文件
    """
    if level is None:
        level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_folder = '执行日志'
    if old_dir_compat:
        from phis_logging.dir_switch import setup_dir

        setup_dir()
    os.makedirs(log_folder, exist_ok=True)

    log_filename = os.path.join(
        log_folder, f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
    )

    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Prevent adding duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # 根据选项构建格式字符串
    file_fmt_parts = ['%(asctime)s']
    console_fmt_parts = ['%(asctime)s']

    if show_logger_name:
        file_fmt_parts.append('%(name)s')
        console_fmt_parts.append('%(name)s')

    if show_filename:
        file_fmt_parts.append('[%(filename)s:%(lineno)d]')
        console_fmt_parts.append('[%(filename)s:%(lineno)d]')

    file_fmt_parts.extend(['%(levelname)s', '%(message)s'])
    console_fmt_parts.extend(['%(levelname)s', '%(message)s'])

    file_format = ' - '.join(file_fmt_parts)
    console_format = ' '.join(console_fmt_parts)

    # Create a file handler
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_formatter = logging.Formatter(
        file_format,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Create a console handler
    try:
        import coloredlogs

        # Use coloredlogs for prettier console output
        field_styles = coloredlogs.DEFAULT_FIELD_STYLES
        if show_filename and filename_color:
            field_styles['filename'] = {'color': filename_color}
            field_styles['lineno'] = {'color': filename_color}

        coloredlogs.install(
            level=level,
            logger=logger,
            stream=sys.stdout,
            fmt=console_format,
            field_styles=field_styles,
        )
    except ImportError:
        # Fallback to standard StreamHandler if coloredlogs is not available
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(console_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    logging.info(
        '日志已配置同时输出到控制台和文件 %s 中', str(log_filename).replace('\\', '/')
    )
