'''
Created on Sep 23, 2016

@author: castulo
'''
from tempest.api.compute import base
from tempest import config
from tempest import test

import pickle
import os

CONF = config.CONF


class DummyTestResources(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class CleanupComputePersistentResources(base.BaseV2ComputeTest):

    credentials = ['primary', 'admin']

    @classmethod
    def resource_setup(cls):
        super(CleanupComputePersistentResources, cls).resource_setup()
        # Read the files that have the existing persistent resources
        with open('compute.resource', 'rb') as f:
            cls.servers = pickle.load(f)
        with open('credentials.resource', 'rb') as f:
            credentials_list = pickle.load(f)
        # Add the retrieved user/projects to the list of resources to be
        # deleted
        for credential in credentials_list:
            cred_obj = DummyTestResources(**credential)
            cls._creds_provider._creds.update({cred_obj.username: cred_obj})

        # Use the admin client instead of the primary user client so it
        # can delete resources from other projects.
        cls.servers_client = cls.os_adm.servers_client

    @classmethod
    def resource_cleanup(cls):
        super(CleanupComputePersistentResources, cls).resource_cleanup()
        os.remove('compute.resource')

    @classmethod
    def clear_credentials(cls):
        # Override the parent's method to avoid deleting the credentials
        # at the end of the test. Store them to later use instead.
        super(CleanupComputePersistentResources, cls).clear_credentials()
        os.remove('credentials.resource')

    @test.attr(type='cleanup')
    def test_dummy(self):
        # Dummy test needed to be able to trigger the tearDownClass
        pass
