'''
Created on Oct 5, 2016

@author: castulo
'''
from tempest.api.object_storage import base
from tempest.lib.common.utils import data_utils
from tempest import config
from tempest import test
from unittest.suite import TestSuite

import os
import pickle

CONF = config.CONF


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(ObjectStoragePersistentResources(
        "test_create_persistent_container"))
    suite.addTest(ObjectStoragePersistentResources(
        "test_create_persistent_object"))
    return suite


class ObjectStoragePersistentResources(base.BaseObjectTest):

    @classmethod
    def resource_setup(cls):
        super(ObjectStoragePersistentResources, cls).resource_setup()
        cls.objects = []
        cls.object_data = []

    @classmethod
    def resource_cleanup(cls):
        # Override the parent's method to avoid deleting the resources at
        # the end of the test. Store them in a file to be used later instead.
        try:
            obj_stg_base_path = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(obj_stg_base_path, 'persistent.resource')
            os.remove(file_path)
        except OSError:
            pass
        cred = cls._creds_provider._creds[
            str([CONF.object_storage.operator_role])]
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
            'containers': cls.containers,
            'objects': cls.objects,
            'data': cls.object_data
            }
        with open(file_path, 'wb') as f:
            pickle.dump(resources, f)

    @classmethod
    def clear_credentials(cls):
        # Override the parent's method to avoid deleting the credentials
        # at the end of the test.
        pass

    @test.attr(type='upgrade-create')
    def test_create_persistent_container(self):
        container_name = data_utils.rand_name(name='TestContainer')
        resp, _ = self.container_client.create_container(container_name)
        self.containers.append(container_name)
        self.assertHeaders(resp, 'Container', 'PUT')

    @test.attr(type='upgrade-create')
    def test_create_persistent_object(self):
        object_name = data_utils.rand_name(name='TestObject')
        data = data_utils.arbitrary_string(15)
        resp, _ = self.object_client.create_object(self.containers[0],
                                                   object_name, data)
        self.assertHeaders(resp, 'Object', 'PUT')
        self.objects.append(object_name)
        self.object_data.append(data)
