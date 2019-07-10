from dataclasses import dataclass
from typing import Type, Callable, List, Dict

from django.db.models import Model
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer

from main.models import BaseMark


@dataclass
class RelatedSerializerCollector:
    model: Type[Model]
    serializer: Type[ModelSerializer]


@dataclass
class RelatedTarget:
    objects: List[Model]
    serializer: Type[ModelSerializer]
    collect: Dict[str, Callable[[BaseMark], int]]


class RelatedSerializer:
    def __init__(self, **collectors: RelatedSerializerCollector):
        self.collectors: Dict[str, RelatedSerializerCollector] = collectors

    def serialize(self, request: Request, **targets: RelatedTarget):
        res = {}
        collected_ids = {}
        for target_name, target in targets.items():
            res[target_name] = target.serializer(
                target.objects,
                many=True,
                context={'request': request}
            ).data
            for name, id_getter in target.collect.items():
                ids = set(id_getter(mark) for mark in target.objects)
                collected_ids.setdefault(name, set()).update(ids)

        for name, ids in collected_ids.items():
            collector = self.collectors[name]
            objects = collector.model.objects.filter(id__in=list(ids))
            serialized = collector.serializer(objects, many=True, context={'request': request})
            res[name] = serialized.data

        return res
