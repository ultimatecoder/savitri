#! /usr/bin/env python

from rest_framework import status
from rest_framework.test import APITestCase

from blog import models
from . import dummy
from . import mocks


class TestComment(APITestCase):

    def setUp(self):
        self._create_dummy_records()

    def _create_dummy_records(self):
        self.author = dummy.create_author()
        self.post = dummy.create_post(self.author)
        self.comments = [
            dummy.create_comment(self.author, self.post),
            dummy.create_comment(self.author, self.post)
        ]

    def _serialize_comment(self, comment, post, author):
        serialized_comment = {
            "id": comment.id,
            "post": post.id,
            "author": author.id,
            "body": comment.body,
            "created_date": mocks.MockedDateTime.timezoned
        }
        return serialized_comment

    def test_that_it_is_possible_to_read_a_comment(self):
        response = self.client.get('/comments/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = self._serialize_comment(
            self.comments[0], self.author, self.post
        )
        self.assertDictEqual(response.data, expected_data)

    def test_that_it_is_possible_to_read_list_of_comments(self):
        response = self.client.get('/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_response = []
        for comment in self.comments:
            serialized_comment = self._serialize_comment(
                comment, self.author, self.post
            )
            expected_response.append(serialized_comment)
        self.assertListEqual(response.data, expected_response)

    def test_that_it_is_possible_to_create_new_comment(self):
        new_comment = {
            "post": self.post.id,
            "author": self.author.id,
            "body": "You are wrong here.",
        }
        response = self.client.post("/comments/", new_comment)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        is_new_record_exists = models.Comment.objects.filter(
            post=self.post.id,
            author=self.author.id,
            body="You are wrong here."
        ).exists()
        self.assertTrue(is_new_record_exists)

    def test_that_it_is_possible_to_update_comment(self):
        new_body = "I have updated my comment"
        comment = {
            "body": new_body
        }
        response = self.client.patch("/comments/2/", comment)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        is_updated_record_exists = models.Comment.objects.filter(
            body=new_body
        ).exists()
        self.assertTrue(is_updated_record_exists)
        total_comments = models.Comment.objects.count()
        self.assertEqual(total_comments, len(self.comments))

    def test_that_it_is_possible_to_delete_comment(self):
        response = self.client.delete("/comments/1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        total_comments = models.Comment.objects.count()
        expected_comments = len(self.comments) - 1
        self.assertEqual(total_comments, expected_comments)
