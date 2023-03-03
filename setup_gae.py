# Copyright 2019 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS-IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Python execution environment setup for scripts that require GAE."""

from __future__ import annotations

import argparse
import os
import subprocess
import ssl
import sys
import tarfile
from urllib import error as urlerror
from urllib import request as urlrequest

from typing import Optional, Sequence

CURR_DIR = os.path.abspath(os.getcwd())
OPPIA_TOOLS_DIR = os.path.join(CURR_DIR, os.pardir, 'oppia_tools')
OPPIA_TOOLS_DIR_ABS_PATH = os.path.abspath(OPPIA_TOOLS_DIR)
GOOGLE_CLOUD_SDK_HOME = os.path.join(
    OPPIA_TOOLS_DIR_ABS_PATH, 'google-cloud-sdk-364.0.0', 'google-cloud-sdk')
GOOGLE_APP_ENGINE_SDK_HOME = os.path.join(
    GOOGLE_CLOUD_SDK_HOME, 'platform', 'google_appengine')
GOOGLE_CLOUD_SDK_HOME = os.path.join(
    OPPIA_TOOLS_DIR_ABS_PATH, 'google-cloud-sdk-364.0.0', 'google-cloud-sdk')
GOOGLE_APP_ENGINE_SDK_HOME = os.path.join(
    GOOGLE_CLOUD_SDK_HOME, 'platform', 'google_appengine')
GOOGLE_CLOUD_SDK_BIN = os.path.join(GOOGLE_CLOUD_SDK_HOME, 'bin')
GCLOUD_PATH = os.path.join(GOOGLE_CLOUD_SDK_BIN, 'gcloud')

_PARSER = argparse.ArgumentParser(
    description="""
Python execution environment setup for scripts that require GAE.
""")

GAE_DOWNLOAD_ZIP_PATH = os.path.join('.', 'gae-download.zip')


def url_retrieve(
        url: str, output_path: str, max_attempts: int = 2,
        enforce_https: bool = True
) -> None:
    """Retrieve a file from a URL and write the file to the file system.

    Note that we use Python's recommended default settings for verifying SSL
    connections, which are documented here:
    https://docs.python.org/3/library/ssl.html#best-defaults.

    Args:
        url: str. The URL to retrieve the data from.
        output_path: str. Path to the destination file where the data from the
            URL will be written.
        max_attempts: int. The maximum number of attempts that will be made to
            download the data. For failures before the maximum number of
            attempts, a message describing the error will be printed. Once the
            maximum is hit, any errors will be raised.
        enforce_https: bool. Whether to require that the provided URL starts
            with 'https://' to ensure downloads are secure.

    Raises:
        Exception. Raised when the provided URL does not use HTTPS but
            enforce_https is True.
    """
    failures = 0
    success = False
    if enforce_https and not url.startswith('https://'):
        raise Exception(
            'The URL %s should use HTTPS.' % url)
    while not success and failures < max_attempts:
        try:
            with urlrequest.urlopen(
                url, context=ssl.create_default_context()
            ) as response:
                with open(output_path, 'wb') as output_file:
                    output_file.write(response.read())
        except (urlerror.URLError, ssl.SSLError) as exception:
            failures += 1
            print('Attempt %d of %d failed when downloading %s.' % (
                failures, max_attempts, url))
            if failures >= max_attempts:
                raise exception
            print('Error: %s' % exception)
            print('Retrying download.')
        else:
            success = True


def main(args: Optional[Sequence[str]] = None) -> None:
    """Runs the script to setup GAE."""
    unused_parsed_args = _PARSER.parse_args(args=args)

    sys.path.append('.')
    sys.path.append(GOOGLE_APP_ENGINE_SDK_HOME)

    # Delete old *.pyc files.
    for directory, _, files in os.walk('.'):
        for file_name in files:
            if file_name.endswith('.pyc'):
                filepath = os.path.join(directory, file_name)
                os.remove(filepath)

    print(
        'Checking whether google-cloud-sdk is installed in %s'
        % GOOGLE_CLOUD_SDK_HOME)
    if not os.path.exists(GOOGLE_CLOUD_SDK_HOME):
        print('Downloading Google Cloud SDK (this may take a little while)...')
        os.makedirs(GOOGLE_CLOUD_SDK_HOME)
        try:
            # If the google cloud version is updated here, the corresponding
            # lines (GAE_DIR and GCLOUD_PATH) in assets/release_constants.json
            # should also be updated.
            url_retrieve(
                'https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/'
                'google-cloud-sdk-364.0.0-linux-x86_64.tar.gz',
                'gcloud-sdk.tar.gz')
        except Exception as e:
            print('Error downloading Google Cloud SDK. Exiting.')
            raise Exception('Error downloading Google Cloud SDK.') from e
        print('Download complete. Installing Google Cloud SDK...')
        tar = tarfile.open(name='gcloud-sdk.tar.gz')
        tar.extractall(
            path=os.path.join(
                OPPIA_TOOLS_DIR, 'google-cloud-sdk-364.0.0/'))
        tar.close()

        os.remove('gcloud-sdk.tar.gz')

    # This command installs specific google cloud components for the google
    # cloud sdk to prevent the need for developers to install it themselves when
    # the app engine development server starts up. The --quiet parameter
    # specifically tells the gcloud program to autofill all prompts with default
    # values. In this case, that means accepting all installations of gcloud
    # packages.
    subprocess.call([
        GCLOUD_PATH,
        'components', 'install', 'beta', 'cloud-datastore-emulator',
        'app-engine-python', 'app-engine-python-extras', '--quiet'])


# The 'no coverage' pragma is used as this line is un-testable. This is because
# it will only be called when setup_gae.py is used as a script.
if __name__ == '__main__': # pragma: no cover
    main()
