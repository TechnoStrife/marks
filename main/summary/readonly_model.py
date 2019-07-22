from django.db.models import Model, Manager, QuerySet


class ReadOnlyError(Exception):
    pass


class ReadOnlyQuerySet(QuerySet):
    def create(self, **kwargs):
        raise ReadOnlyError('create method is not allowed on ReadOnlyQuerySet')

    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        raise ReadOnlyError('bulk_create method is not allowed on ReadOnlyQuerySet')

    def bulk_update(self, objs, fields, batch_size=None):
        raise ReadOnlyError('bulk_update method is not allowed on ReadOnlyQuerySet')

    def get_or_create(self, defaults=None, **kwargs):
        raise ReadOnlyError('get_or_create method is not allowed on ReadOnlyQuerySet')

    def update_or_create(self, defaults=None, **kwargs):
        raise ReadOnlyError('update_or_create method is not allowed on ReadOnlyQuerySet')

    def delete(self):
        raise ReadOnlyError('delete method is not allowed on ReadOnlyQuerySet')

    def update(self, **kwargs):
        raise ReadOnlyError('update method is not allowed on ReadOnlyQuerySet')


ReadOnlyManager = Manager.from_queryset(ReadOnlyQuerySet)


class ReadOnlyModel(Model):
    objects = ReadOnlyManager()

    def save(self, *args, **kwargs):
        raise ReadOnlyError('save is not allowed on ReadOnlyModel instance')

    def delete(self, *args, **kwargs):
        raise ReadOnlyError('delete is not allowed on ReadOnlyModel instance')

    class Meta:
        abstract = True
