from django.db.models import *

__all__ = ['MyModel', 'PersonModel']


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


class PersonModel(MyModel):
    full_name = CharField(max_length=255, verbose_name='ФИО')

    birthday = DateField(verbose_name='День рождения', null=True)
    tel = CharField(max_length=15, verbose_name='Телефон', null=True)
    email = EmailField(verbose_name='Email', null=True)
    dnevnik_id = BigIntegerField(verbose_name='ID пользователя в dnevnik.ru', unique=True, null=True)
    dnevnik_person_id = BigIntegerField(verbose_name='ID в dnevnik.ru', unique=True, null=True)

    @property
    def name(self):
        surname, name, patronymic = self.full_name.split()
        name = f'{surname} {name[0]}. {patronymic[0]}.'
        return name

    @name.setter
    def name(self, value):
        self.full_name = value

    @property
    def first_name(self):
        surname, name, patronymic = self.full_name.split()
        return name

    @property
    def patronymic(self):
        surname, name, patronymic = self.full_name.split()
        return patronymic

    @property
    def middle_name(self):
        return self.patronymic

    @property
    def surname(self):
        surname, name, patronymic = self.full_name.split()
        return surname

    def check_name(self, check_name: str):
        check_name = check_name.split()
        return all(name in check_name for name in self.full_name.split())

    def dnevnik_user_link(self):
        if self.dnevnik_id:
            return 'https://dnevnik.ru/user/user.aspx?user=' + str(self.dnevnik_id)
        else:
            return None

    class Meta:
        abstract = True

