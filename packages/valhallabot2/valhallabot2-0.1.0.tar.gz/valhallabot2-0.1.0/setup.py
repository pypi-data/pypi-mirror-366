from setuptools import setup, find_packages

setup(
    name='valhallabot2',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pyTelegramBotAPI',
    ],
    author='valhalla',
    description='مكتبة بايثون لإرسال ملفات من مجلد معين عبر بوت تليجرام',
    long_description='مكتبة بسيطة لإرسال الملفات من مجلد عبر بوت تليجرام مع إرسال الأخطاء كرسائل.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
