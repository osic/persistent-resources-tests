'''
Created on Sep 23, 2016

@author: castulo
'''
from tempest.api.compute import base
from tempest import config
from tempest import test

import os
import pickle

CONF = config.CONF


class ComputePersistentResources(base.BaseV2ComputeTest):

    @classmethod
    def resource_setup(cls):
        cls.set_validation_resources()
        super(ComputePersistentResources, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        # Override the parent's method to avoid deleting the resources at
        # the end of the test. Store them in a file to be used later instead.
        try:
            compute_base_path = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(compute_base_path, 'persistent.resource')
            os.remove(file_path)
        except OSError:
            pass
        cred = cls._creds_provider._creds['primary']
        resources = {
            'user_id': cred.user_id,
            'username': cred.username,
            'tenant_id': cred.tenant_id,
            'tenant_name': cred.tenant_name,
            'password': cred.password,
            'network': cred.network,
            'router': cred.router,
            'subnet': cred.subnet,
            'validation_resources': cls.validation_resources,
            'servers': [{'id': server['id']} for server in cls.servers]}
        with open(file_path, 'wb') as f:
            pickle.dump(resources, f)

    @classmethod
    def clear_credentials(cls):
        # Override the parent's method to avoid deleting the credentials
        # at the end of the test.
        pass

    @test.attr(type='upgrade-create')
    def test_create_persistent_server(self):
        server = self.create_test_server(validatable=True,
                                         wait_until='ACTIVE')
        self.assertTrue(server['id'])
