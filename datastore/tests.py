from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.shortcuts import resolve_url
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
)
from rest_framework.test import APITestCase

from .models import DataStore, DataStorePermission

User = get_user_model()


class DataStoreTestCase(APITestCase):
    def setUp(self):

        examples = [{
            'key': 'test.data.store',
            'value': {'key': 'value', }
        }, {
            'key': 'test.data.new_store',
            'value': {}
        }, {
            'key': 'test.prefix.dot.com',
            'value': {}
        }]

        for example in examples:
            DataStore.objects.create(**example)

        self.user = User.objects.create(username="bar")
        self.client.force_authenticate(user=self.user)

    def test_not_authenticated(self):
        self.client.force_authenticate()
        response = self.client.get(reverse('datastore:datastore-list'))
        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_no_permission(self):
        response = self.client.get(reverse('datastore:datastore-list'))

        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(0, response.json()['count'])

    def test_can_readonly(self):
        # Add the user to a group
        group = Group.objects.create(name='can_read')
        self.user.groups.add(group)
        self.user.save()

        # Allow this group to read the test.prefix prefix
        perm = Permission.objects.get(codename='can_read_datastore')
        DataStorePermission.objects.create(
            group=group,
            permission=perm,
            prefix='test.prefix',
        )

        response = self.client.get(reverse('datastore:datastore-list'))
        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.json()['count'])

        # test that write is not allowed
        test_value = {'a': 'TEST'}
        ds = DataStore.objects.get(key='test.prefix.dot.com')
        response = self.client.put(
            resolve_url('datastore:datastore-detail', ds.key),
            data={'value': test_value},
            format='json',
        )

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)
        self.user.groups.clear()

    def test_can_readwrite(self):
        # Add the user to a group
        group = Group.objects.create(name='can_readwrite')
        self.user.groups.add(group)

        # Allow this group to read the test.prefix prefix
        perm = Permission.objects.get(codename='can_readwrite_datastore')
        DataStorePermission.objects.get_or_create(
            group=group,
            permission=perm,
            prefix='test.prefix',
        )

        response = self.client.get(reverse('datastore:datastore-list'))
        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.json()['count'])

        # Test writing
        test_value = {'a': 'b'}
        ds = DataStore.objects.get(key='test.prefix.dot.com')
        response = self.client.put(
            resolve_url('datastore:datastore-detail', ds.key),
            data=test_value,
            format='json',
        )

        self.assertEqual(HTTP_200_OK, response.status_code)

        ds.refresh_from_db()
        self.assertDictEqual(ds.value, test_value)

        self.user.groups.clear()

    def test_create_item(self):
        # Add the user to a group
        group = Group.objects.create(name='can_readwrite')
        self.user.groups.add(group)

        # Allow this group to read the test.prefix prefix
        perm = Permission.objects.get(codename='can_readwrite_datastore')
        DataStorePermission.objects.get_or_create(
            group=group,
            permission=perm,
            prefix='test.prefix',
        )

        test_value = {'test_key': 'test value'}
        prefix = 'test.prefix.blurp'
        response = self.client.post(
            resolve_url('datastore:datastore-detail', prefix),
            data=test_value,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

        self.assertTrue(DataStore.objects.filter(key=prefix).exists())
        self.assertDictEqual(response.json(), test_value)

    def test_forbidden_create_item(self):
        user = User.objects.create(username="foo")
        self.client.force_authenticate(user=user)

        prefix = 'test.prefix.forbidden_creation'
        response = self.client.post(
            resolve_url('datastore:datastore-detail', prefix),
            data={'test_key': 'test value'},
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        self.assertFalse(DataStore.objects.filter(key=prefix).exists())

    def test_perms(self):
        # Add the user to a group
        group = Group.objects.create(name='can_readwrite')
        self.user.groups.add(group)

        # Allow this group to read the test.prefix prefix
        perm = Permission.objects.get(codename='can_readwrite_datastore')
        DataStorePermission.objects.get_or_create(
            group=group,
            permission=perm,
            prefix='test.testprefix',
        )

        test_value = {'test_key': 'test value'}
        response = self.client.post(
            resolve_url('datastore:datastore-detail', 'test.testprefix.blurp'),
            data=test_value,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

        response = self.client.post(
            resolve_url('datastore:datastore-detail', 'test.forbiddenprefix'),
            data=test_value,
            format='json',
        )
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
