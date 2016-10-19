'''
Created on Sep 26, 2016

@author: castulo
'''
from tempest.api.compute import base
from tempest.common.dynamic_creds import DynamicCredentialProvider
from tempest.common.utils.linux import remote_client
from tempest.common import waiters
from tempest import config
from tempest.lib.common.cred_provider import TestResources
from tempest import test
from unittest.suite import TestSuite

import os
import pickle
import testtools

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


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(VerifyComputePersistentResources(
        "test_verify_persistent_servers_existance"))
    suite.addTest(VerifyComputePersistentResources(
        "test_can_ssh_into_persistent_servers"))
    suite.addTest(VerifyComputePersistentResources(
        "test_suspend_resume_persistent_server"))
    return suite


class VerifyComputePersistentResources(base.BaseV2ComputeTest):

    @classmethod
    def setup_credentials(cls):
        # Monkey patch the method for creating new credentials to use
        # existing credentials instead
        DynamicCredentialProvider._create_creds = _use_existing_creds
        super(VerifyComputePersistentResources, cls).setup_credentials()

    @classmethod
    def resource_setup(cls):
        super(VerifyComputePersistentResources, cls).resource_setup()
        # Read the files that have the existing persistent resources
        compute_base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(compute_base_path, 'persistent.resource')
        with open(file_path, 'rb') as f:
            cls.resources = pickle.load(f)
        cls.validation_resources = cls.resources['validation_resources']

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
    def test_verify_persistent_servers_existance(self):
        """ The persisted server(s) still exist in the environment."""
        servers = self.resources['servers']
        for server in servers:
            fetched_server = self.servers_client.show_server(
                server['id'])['server']
            self.assertEqual(server['id'], fetched_server['id'])

    @test.attr(type='persistent-verify')
    @testtools.skipUnless(CONF.validation.run_validation,
                          'Instance validation tests are disabled.')
    def test_can_ssh_into_persistent_servers(self):
        """ User(s) can still SSH to the persisted server(s)."""
        servers = self.resources['servers']
        for server in servers:
            fetched_server = self.servers_client.show_server(
                server['id'])['server']
            linux_client = remote_client.RemoteClient(
                self.get_server_ip(fetched_server),
                self.ssh_user,
                CONF.validation.image_ssh_password,
                self.validation_resources['keypair']['private_key'],
                server=fetched_server,
                servers_client=self.servers_client)
            linux_client.validate_authentication()
            hostname = linux_client.get_hostname()
            self.assertEqual(fetched_server['name'].lower(), hostname)

    @test.attr(type='persistent-verify')
    @testtools.skipUnless(CONF.compute_feature_enabled.suspend,
                          'Suspend is not available.')
    def test_suspend_resume_persistent_server(self):
        servers = self.resources['servers']
        for server in servers:
            self.servers_client.suspend_server(server['id'])
            waiters.wait_for_server_status(self.servers_client, server['id'],
                                           'SUSPENDED')
            self.servers_client.resume_server(server['id'])
            waiters.wait_for_server_status(self.servers_client, server['id'],
                                           'ACTIVE')
