'''
Created on Sep 23, 2016

@author: castulo
'''
from tempest.api.compute import base
from tempest.common.dynamic_creds import DynamicCredentialProvider
from tempest.common.cred_provider import TestResources
from tempest import config
from tempest import test

import os
import pickle

CONF = config.CONF


def _use_existing_creds(self, admin):
    """Create credentials with an existing user.

    :return: Readonly Credentials with network resources
    """
    # Read the files that have the existing persistent resources
    compute_base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(compute_base_path, 'persistent.resource')
    with open(file_path, 'rb') as f:
        resources = pickle.load(f)
    user = {'name': resources['username'], 'id': resources['user_id']}
    project = {'name': resources['tenant_name'], 'id': resources['tenant_id']}
    user_password = resources['password']
    creds = self.creds_client.get_credentials(user, project, user_password)
    return TestResources(creds)


class CleanupComputePersistentResources(base.BaseV2ComputeTest):

    @classmethod
    def setup_credentials(cls):
        # Monkey patch the method for creating new credentials to use
        # existing credentials instead
        DynamicCredentialProvider._create_creds = _use_existing_creds
        super(CleanupComputePersistentResources, cls).setup_credentials()

    @classmethod
    def resource_setup(cls):
        super(CleanupComputePersistentResources, cls).resource_setup()
        # Read the files that have the existing persistent resources
        compute_base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(compute_base_path, 'persistent.resource')
        with open(file_path, 'rb') as f:
            resources = pickle.load(f)
        cls.servers.extend(resources['servers'])
        # Remove the file with the persistent resources
        os.remove(file_path)

    @test.attr(type='upgrade-cleanup')
    def test_dummy(self):
        # Dummy test needed to be able to trigger the tearDownClass
        pass
