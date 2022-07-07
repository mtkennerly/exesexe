from invoke import task
import shutil


@task
def build(context):
    context.run("pyinstaller exesexe.py --onefile --specpath build --workpath build")


@task
def dist(context):
    shutil.rmtree("./dist", ignore_errors=True)
    context.run("python setup.py sdist")
    context.run("python setup.py bdist_wheel")


@task
def test(context):
    context.run("pytest tests")
