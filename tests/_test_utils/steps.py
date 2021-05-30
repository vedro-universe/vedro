__all__ = ("given", "when", "then",)


class Context:
    def __enter__(self):
        pass

    def __exit__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self


class Given(Context):
    pass


class When(Context):
    pass


class Then(Context):
    pass


given = Given()
when = When()
then = Then()
