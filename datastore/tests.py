import factory
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from rest_framework.status import (HTTP_200_OK, HTTP_401_UNAUTHORIZED,
                                   HTTP_403_FORBIDDEN)
from rest_framework.test import APIClient


from django.contrib.auth import get_user_model
from datastore.models import DataStore, DataStorePermission

UserModel = get_user_model()


class TerraUserFactory(factory.DjangoModelFactory):

    class Meta:
        model = UserModel

    email = factory.Faker('email')
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs.update({'password': kwargs.get('password', '123456')})
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class DataStoreTestCase(TestCase):
    def setUp(self):

        examples = [{
            'key': 'terracommon.test.data.store',
            'value': {'key': 'value', }
        }, {
            'key': 'terracommon.test.data.new_store',
            'value': {}
        }, {
            'key': 'terracommon.prefix.dot.com',
            'value': {}
        }]

        for example in examples:
            DataStore.objects.create(**example)

        self.client = APIClient()
        self.user = TerraUserFactory()
        self.client.force_authenticate(user=self.user)

    def test_not_authenticated(self):
        client = APIClient()
        response = client.get(reverse('datastore:datastore-list'))
        self.assertEqual(HTTP_401_UNAUTHORIZED, response.status_code)

    def test_no_permission(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get(reverse('datastore:datastore-list'))

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(0, response.json()['count'])

    def test_can_readonly(self):
        # Add the user to a group
        group = Group.objects.create(name='can_read')
        self.user.groups.add(group)
        self.user.save()

        # Allow this group to read the terracommon.prefix prefix
        perm = Permission.objects.get(codename='can_read_datastore')
        DataStorePermission.objects.create(
            group=group,
            permission=perm,
            prefix='terracommon.prefix',
        )

        response = self.client.get(reverse('datastore:datastore-list'))
        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.json()['count'])

        # test that write is not allowed
        test_value = {'a': 'TEST'}
        ds = DataStore.objects.get(key='terracommon.prefix.dot.com')
        response = self.client.put(reverse('datastore:datastore-detail',
                                           args=[ds.key]),
                                   data={'value': test_value})

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)
        self.user.groups.clear()

    def test_can_readwrite(self):
        # Add the user to a group
        group = Group.objects.create(name='can_readwrite')
        self.user.groups.add(group)

        # Allow this group to read the terracommon.prefix prefix
        perm = Permission.objects.get(codename='can_readwrite_datastore')
        DataStorePermission.objects.get_or_create(
            group=group,
            permission=perm,
            prefix='terracommon.prefix',
        )

        response = self.client.get(reverse('datastore:datastore-list'))
        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.json()['count'])

        # Test writing
        test_value = {'a': 'b'}
        ds = DataStore.objects.get(key='terracommon.prefix.dot.com')
        response = self.client.put(reverse('datastore:datastore-detail',
                                           args=[ds.key]),
                                   data=test_value)

        self.assertEqual(HTTP_200_OK, response.status_code)

        ds.refresh_from_db()
        self.assertDictEqual(ds.value, test_value)

        self.user.groups.clear()

    def test_create_item(self):
        # Add the user to a group
        group = Group.objects.create(name='can_readwrite')
        self.user.groups.add(group)

        # Allow this group to read the terracommon.prefix prefix
        perm = Permission.objects.get(codename='can_readwrite_datastore')
        DataStorePermission.objects.get_or_create(
            group=group,
            permission=perm,
            prefix='terracommon.prefix',
        )

        test_value = {'test_key': 'test value'}
        response = self.client.post(reverse('datastore:datastore-detail', args=['terracommon.prefix.blurp']),
                                    data=test_value)
        self.assertEqual(response.status_code, HTTP_200_OK)

        self.assertTrue(DataStore.objects.filter(key='terracommon.prefix.blurp').exists())
        self.assertDictEqual(response.json(), test_value)

    def test_forbidden_create_item(self):
        user = TerraUserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(reverse('datastore:datastore-detail',
                                       args=['terracommon.prefix.forbidden_creation']),
                               data={'test_key': 'test value'})
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        self.assertFalse(DataStore.objects.filter(key='terracommon.prefix.forbidden_creation').exists())

    def test_perms(self):
        # Add the user to a group
        group = Group.objects.create(name='can_readwrite')
        self.user.groups.add(group)

        # Allow this group to read the terracommon.prefix prefix
        perm = Permission.objects.get(codename='can_readwrite_datastore')
        DataStorePermission.objects.get_or_create(
            group=group,
            permission=perm,
            prefix='terracommon.testprefix',
        )

        test_value = {'test_key': 'test value'}
        response = self.client.post(reverse('datastore:datastore-detail', args=['terracommon.testprefix.blurp']),
                                    data=test_value)
        self.assertEqual(response.status_code, HTTP_200_OK)

        response = self.client.post(reverse('datastore:datastore-detail', args=['terracommon.forbiddenprefix']),
                                    data=test_value)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
