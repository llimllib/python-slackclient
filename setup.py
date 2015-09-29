#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='slackrtm',
    version='0.2.0',
    description='Python client for Slack.com',
    url='http://github.com/llimllib/slackrtm',
    author='Bill Mill',
    author_email='ryan@slack-corp.com',
    license='MIT',
    packages=['slackrtm'],
    install_requires=[
        'websocket-client',
    ],
    zip_safe=False,
)
