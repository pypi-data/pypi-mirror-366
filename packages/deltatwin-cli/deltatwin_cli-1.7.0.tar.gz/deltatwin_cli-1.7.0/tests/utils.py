import os


def remove_conf():
    if os.path.exists("conf.ini"):
        os.remove("conf.ini")


class TagObjMock:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


class RemoteObjMock:
    def __init__(self, url, push_obj):
        self._url = url
        self._push_obj = push_obj

    @property
    def url(self):
        return self._url

    def push(self, version=None):
        return [self._push_obj]


class FailPushObjMock:
    def __init__(self):
        self._flags = 8

    @property
    def flags(self):
        return self._flags


class GoodPushObjMock:
    def __init__(self):
        self._flags = 1

    @property
    def flags(self):
        return self._flags


class RepoMock:
    def __init__(self, version, url, push_obj):
        self._tags = [
            TagObjMock(version)
        ]
        self._remotes = [
            RemoteObjMock(url, push_obj)
        ]

    @property
    def tags(self):
        return self._tags

    def create_tag(self, version):
        pass

    @property
    def remotes(self):
        return self._remotes
