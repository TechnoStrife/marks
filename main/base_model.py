from django.db.models import Model


class MyModel(Model):
    def update_or_create(self, search_attr):
        try:
            obj = self.objects.only('id').get(**{search_attr: getattr(self, search_attr)})
        except self.DoesNotExist:
            pass
        else:
            self.id = obj.id
        return self.save()

    class Meta:
        abstract = True
