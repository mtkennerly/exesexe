from invoke import task


@task
def build(context):
    context.run("poetry run pyinstaller exesexe.py --onefile --specpath build --workpath build")
