'''
Created on Sep 23, 2016

@author: castulo
'''
from tempest.api.compute import base
from tempest import config
from tempest import test

import pickle
import os
import six

CONF = config.CONF


class ComputePersistentResources(base.BaseV2ComputeTest):

    @classmethod
    def resource_setup(cls):
        cls.set_validation_resources()
        super(ComputePersistentResources, cls).resource_setup()
        # List of resources created during the test
        cls.persistent_servers = []
        cls.persistent_credentials = []

    @classmethod
    def resource_cleanup(cls):
        # Override the parent's method to avoid deleting the resources at
        # the end of the test. Store them in a file to be used later instead.
        try:
            os.remove('compute.resource')
        except OSError:
            pass
        with open('compute.resource', 'wb') as f:
            pickle.dump(cls.persistent_servers, f)

    @classmethod
    def clear_credentials(cls):
        # Override the parent's method to avoid deleting the credentials
        # at the end of the test. Store them to later use instead.
        try:
            os.remove('credentials.resource')
        except OSError:
            pass
        for cred in six.itervalues(cls._creds_provider._creds):
            cls.persistent_credentials.append(
                {'user_id': cred.user_id,
                 'username': cred.username,
                 'tenant_id': cred.tenant_id,
                 'tenant_name': cred.tenant_name,
                 'network': cred.network,
                 'router': cred.router,
                 'subnet': cred.subnet})
        with open('credentials.resource', 'wb') as f:
            pickle.dump(cls.persistent_credentials, f)

    @test.attr(type='upgrade')
    def test_create_persistent_server(self):
        server = self.create_test_server(validatable=True,
                                         wait_until='ACTIVE')
        self.assertTrue(server['id'])
        self.persistent_servers.append({'id': server['id']})
