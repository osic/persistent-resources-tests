'''
Created on Oct 7, 2016

@author: castulo
'''
from tempest.api.object_storage import base
from tempest.common.dynamic_creds import DynamicCredentialProvider
from tempest import config
from tempest import test
from unittest.suite import TestSuite

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


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(VerifyObjectStoragePersistentResources(
        "test_verify_persistent_container_existance"))
    suite.addTest(VerifyObjectStoragePersistentResources(
        "test_list_persistent_container_contents"))
    suite.addTest(VerifyObjectStoragePersistentResources(
        "test_get_persistent_object"))
    return suite


class VerifyObjectStoragePersistentResources(base.BaseObjectTest):

    @classmethod
    def setup_credentials(cls):
        # Monkey patch the method for creating new credentials to use
        # existing credentials instead
        DynamicCredentialProvider._create_creds = _use_existing_creds
        super(VerifyObjectStoragePersistentResources, cls).setup_credentials()

    @classmethod
    def resource_setup(cls):
        super(VerifyObjectStoragePersistentResources, cls).resource_setup()
        # Read the files that have the existing persistent resources
        test_base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(test_base_path, 'persistent.resource')
        with open(file_path, 'rb') as f:
            cls.resources = pickle.load(f)

    @classmethod
    def resource_cleanup(cls):
        # Override the parent's method to avoid deleting the resources at
        # the end of the test.
        pass

    @classmethod
    def clear_credentials(cls):
        # Override the parent's method to avoid deleting the credentials
        # at the end of the test.
        pass

    @test.attr(type='persistent-verify')
    def test_verify_persistent_container_existance(self):
        """ The persisted container(s) still exist in the environment."""
        self.assertTrue(self.resources['containers'],
                        'No containers were found in the file.')
        container = self.resources['containers'][0]
        resp, _ = self.container_client.list_container_contents(
            container)
        self.assertHeaders(resp, 'Container', 'GET')

    @test.attr(type='persistent-verify')
    def test_list_persistent_container_contents(self):
        self.assertTrue(self.resources['containers'],
                        'No containers were found in the file.')
        container = self.resources['containers'][0]
        object_name = self.resources['objects'][0]
        _, object_list = self.container_client.list_container_contents(
            container)
        self.assertEqual(object_name, object_list.strip('\n'))

    @test.attr(type='persistent-verify')
    def test_get_persistent_object(self):
        self.assertTrue(self.resources['containers'],
                        'No containers were found in the file.')
        container = self.resources['containers'][0]
        self.assertTrue(self.resources['objects'],
                        'No objects were found in the file.')
        object_name = self.resources['objects'][0]
        self.assertTrue(self.resources['data'],
                        'No object data was found in the file.')
        data = self.resources['data'][0]
        # get object
        resp, object_data = self.object_client.get_object(container,
                                                          object_name)
        self.assertHeaders(resp, 'Object', 'GET')
        self.assertEqual(object_data, data)
