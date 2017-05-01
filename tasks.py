from invoke import task


@task
def build(context):
    context.run("pyinstaller exesexe.py --onefile --specpath build --workpath build")


@task
def dist(context):
    context.run("python setup.py bdist_wheel")


@task
def test(context):
    context.run("tox")
