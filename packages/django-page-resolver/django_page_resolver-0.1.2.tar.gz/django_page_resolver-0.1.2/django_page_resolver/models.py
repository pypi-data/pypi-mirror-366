from django.db import models


__all__ = ['PageResolverModel']


class PageResolverModel(models.Model):
    class Meta:
        abstract = True

    def get_page_from_nested_object(
        self,
        target_child_instance,
        siblings_qs=None,
        *,
        related_name: str = None,
        order_by: str = None,
        items_per_page: int,
    ):
        """
        Imagine that we have model Post. And we have to find specific comment's page of its post.

        We can do next steps:
        post = Post.objects.get(pk=pk)
        comment = post.comments.first()
        comment_page = post.get_fk_paginated_page(comment, order_by='created_at', items_per_page=10)
        """
        if not related_name:
            related_name = target_child_instance.__class__._meta.verbose_name_plural.replace(' ', '_')

        if hasattr(self, related_name):
            if not siblings_qs:
                siblings_qs = getattr(self, related_name).all()

            if order_by:
                siblings_qs = siblings_qs.order_by(order_by)

            ids = list(siblings_qs.values_list('id', flat=True))

            try:
                index = ids.index(target_child_instance.id)
            except ValueError:
                return None

            page_number = (index // items_per_page) + 1
            return page_number

    def get_page_from_queryset(self, queryset=None, *, order_by: str = None, items_per_page: int):
        """
        Using:

        comment = Comment.objects.get(pk=pk)
        queryset = Comment.objects.filter(post__pk=125)
        comment.get_page_from_queryset(queryset=queryset, order_by='created_at', paginate_by=10)
        """

        if not queryset:
            queryset = self.__class__.objects.all()

        if order_by:
            queryset = queryset.order_by(order_by)

        ids = list(queryset.values_list('id', flat=True))
        try:
            index = ids.index(self.pk)
        except ValueError:
            return None

        page_number = (index // items_per_page) + 1
        return page_number
