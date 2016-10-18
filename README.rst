====================================
OpenStack Persistent Resources Tests
====================================

The OpenStack tempest plugin for testing persistent resources during an upgrade

Description
-----------
The purpose of these tests is to verify that resources created in an OpenStack environment are not corrupted after upgrading OpenStack to a newer release.

The resources to be validated include the following:
 - VMs
 - Containers
 - Objects
 - Volumes (Not yet supported)
 
These tests are  provided as a Tempest plugin, this way we can take advantage of all the features and capabilities of Tempest without having to  merge these tests into the Tempest tree.

Installation
------------
1.  Install Tempest 
2.  Configure Tempest configuration file according to your OpenStack deployment
3.  Clone the  repository into the system where you installed Tempest: git clone https://github.com/osic/persistent-resources-tests.git
4. cd openstack-upgrade-tests
5. pip install -e .

To verify the installation was successfull, go to your tempest directory and run the following command:
 *ostestr --list | grep persistent*
You should see the list of tests from the plugin.

How the plugin works
-------------
These tests work pretty much the same as any other Tempest test, where the test starts by doing some setup, then it runs the actual validation and finishes by tearing down whatever it was created during the test. The one big difference with the tests in this plugin is that each test is split up in three different modules: one for the setup, one for the validation, and one for the tear down, whereas in Tempest all those three stages are part of the same module.

The module that creates the resources (user, tenant, network, vm, etc.) is nothing but a Tempest-like test that has the tear down methods overwritten so the resources created during the test are not deleted, instead of that, the resources are added to a dictionary and then saved into a file so we can use them later.

The module that validates the resources is another Tempest-like test  that has the methods for seting up the resources overwritten so no new resources get created, instead, we read the existing resources from the file where we store them earlier and load them in the test as if they had been created there. This module also has the methods for tearing down the resources overwritten so we don't clean them up after runnig the test, this way we can run it multiple times with the same persistent resources.

The module that tears down the resources is a Tempest-like module that has the setup method overwritten the same way as the validation module so we don't create new resources, and same as the validation module it loads the existing ones instead from the file. This module does not actually run any test, all it does is to run the normal tear down that any other Tempest test runs, which then effectively deletes all our persisten resources. 

Running the tests
-----------------
To create  test resources run this command:
 *ostestr --regex persistent-create*

To validate the test reources run:
 *ostestr --regex persistent-verify*

To delete the test reources run:
 *ostestr --regex persistent-cleanup*
