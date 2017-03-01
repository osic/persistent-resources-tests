'''
Created on Oct 7, 2016

@author: castulo
'''
from tempest.api.object_storage import base
from tempest.common.dynamic_creds import DynamicCredentialProvider
from tempest import config
from tempest import test

# Version 14 of tempest moves cred_provider library, this allows older
# Tempest versions to use this plugin. Older versions may be required
# in environments using mirrored packaging repos
try:
    from tempest.lib.common.cred_provider import TestResources
except ImportError:
    from tempest.common.cred_provider import TestResources

import os
import pickle

CONF = config.CONF


def _use_existing_creds(self, roles):
    """Create credentials with an existing user.

    :return: Readonly Credentials with network resources
    """
    # Read the files that have the existing persistent resources
    test_base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(test_base_path, 'persistent.resource')
    with open(file_path, 'rb') as f:
        resources = pickle.load(f)
    user = {'name': resources['username'], 'id': resources['user_id']}
    project = {'name': resources['tenant_name'], 'id': resources['tenant_id']}
    user_password = resources['password']
    creds = self.creds_client.get_credentials(user, project, user_password)
    return TestResources(creds)


class CleanupObjectStoragePersistentResources(base.BaseObjectTest):

    @classmethod
    def setup_credentials(cls):
        # Monkey patch the method for creating new credentials to use
        # existing credentials instead
        DynamicCredentialProvider._create_creds = _use_existing_creds
        super(CleanupObjectStoragePersistentResources, cls).setup_credentials()

    @classmethod
    def resource_setup(cls):
        super(CleanupObjectStoragePersistentResources, cls).resource_setup()
        # Read the files that have the existing persistent resources
        test_base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(test_base_path, 'persistent.resource')
        with open(file_path, 'rb') as f:
            resources = pickle.load(f)
        # Hack to use plugin in older version of tempest
        # in repo locked environment
        try:
            cls.containers.extend(resources['containers'])
        except AttributeError:
            cls.containers = resources["containers"]
        # Remove the file with the persistent resources
        os.remove(file_path)

    @classmethod
    def resource_cleanup(cls):
        # Remove the created containers
        cls.delete_containers()
        super(CleanupObjectStoragePersistentResources, cls).resource_cleanup()

    @test.attr(type='persistent-cleanup')
    def test_cleanup_object_storage_resources(self):
        # Dummy test needed to be able to trigger the tearDownClass
        pass
