"""
Simple and intuitive command-line interface for structlint.
"""

import sys

import click

from .checks import (
    check_docs_structure,
    check_imports,
    check_method_order,
    check_tests_structure,
)
from .collection import (
    collect_docs_objects,
    collect_source_objects,
)
from .configuration import Configuration


def main():
    problems = structlint_cli(standalone_mode=False)
    sys.exit(int(problems))


@click.group(invoke_without_command=True)
@click.pass_context
def structlint_cli(ctx: click.Context):
    ctx.ensure_object(dict)["CFG"] = Configuration.read()  # TODO: support passing explicit config

    if ctx.invoked_subcommand is None:
        return ctx.invoke(run_all)


@structlint_cli.command(name="all", help="Run all checks: methods, docs, tests, imports.")
@click.pass_context
def run_all(ctx: click.Context) -> bool:
    cfg: Configuration = ctx.obj["CFG"]

    source_objects = collect_source_objects(cfg.module_root_dir, cfg.root_dir)
    tests_objects = collect_source_objects(cfg.tests.unit_dir, cfg.root_dir)
    docs_objects = collect_docs_objects(cfg.docs.md_dir, cfg.root_dir)

    mo_report, mo_problems = check_method_order(cfg, source_objects)
    docs_report, docs_problems = check_docs_structure(cfg, source_objects, docs_objects)
    tests_report, tests_problems = check_tests_structure(cfg, source_objects, tests_objects)
    imports_report, imports_problems = check_imports(cfg.imports, cfg.module_name)

    click.echo(mo_report)
    click.echo(docs_report)
    click.echo(tests_report)
    click.echo(imports_report)
    click.echo()

    return any((mo_problems, docs_problems, tests_problems, imports_problems))


@structlint_cli.command(help="Verify documentation presence and formatting.")
@click.pass_context
def docs(ctx: click.Context) -> bool:
    cfg: Configuration = ctx.obj["CFG"]
    source_objects = collect_source_objects(cfg.module_root_dir, cfg.root_dir)
    docs_objects = collect_docs_objects(cfg.docs.md_dir, cfg.root_dir)

    report, problems = check_docs_structure(cfg, source_objects, docs_objects)
    click.echo(report)
    click.echo()

    return problems


@structlint_cli.command(help="Inspect import structures and dependencies.")
@click.pass_context
def imports(ctx: click.Context) -> bool:
    cfg = ctx.obj["CFG"]
    report, problems = check_imports(cfg.imports, cfg.module_name)
    click.echo(report)
    click.echo()

    return problems


@structlint_cli.command(help="Check method structure and naming conventions.")
@click.pass_context
def methods(ctx: click.Context) -> bool:
    cfg: Configuration = ctx.obj["CFG"]
    source_objects = collect_source_objects(cfg.module_root_dir, cfg.root_dir)
    report, problems = check_method_order(cfg, source_objects)
    click.echo(report)
    click.echo()

    return problems


@structlint_cli.command(name="tests", help="Check test organization and conventions.")
@click.pass_context
def tsts(ctx: click.Context) -> bool:
    cfg: Configuration = ctx.obj["CFG"]
    source_objects = collect_source_objects(cfg.module_root_dir, cfg.root_dir)
    tests_objects = collect_source_objects(cfg.tests.unit_dir, cfg.root_dir)

    report, problems = check_tests_structure(cfg, source_objects, tests_objects)
    click.echo(report)
    click.echo()

    return problems


@structlint_cli.command(name="show-config", help="Display current configuration.")
@click.pass_context
def show_config(ctx: click.Context) -> bool:
    cfg: Configuration = ctx.obj["CFG"]

    click.echo(str(cfg))
    click.echo()

    return False


@structlint_cli.command(name="show-default-config", help="Display default configuration.")
@click.pass_context
def show_default_config(ctx: click.Context) -> bool:
    click.echo(str(Configuration()))
    click.echo()

    return False


# import re
# import subprocess

# from structlint.cli import (
#     main,
# )


# def test_main(capsys):
#     main()
#     text = capsys.readouterr().out
#     assert len(re.findall("Hello", text)) == 4
#     assert len(re.findall(r"[a-z-_]+ version: \d+\.\d+", text)) == 3


# def test_structlint_cli(capsys):
#     result = subprocess.run(["structlint"], capture_output=True, check=False).stdout
#     assert "No problems detected." in result


# def test_run_all(capsys):
#     result = subprocess.run(["structlint", "all"], capture_output=True, check=False).stdout
#     assert "No problems detected." in result


# def test_docs(capsys):
#     result = subprocess.run(["structlint", "docs"], capture_output=True, check=False).stdout
#     assert "No problems detected." in result


# def test_imports(capsys):
#     result = subprocess.run(["structlint", "imports"], capture_output=True, check=False).stdout
#     assert "No problems detected." in result


# def test_methods(capsys):
#     result = subprocess.run(["structlint", "methods"], capture_output=True, check=False).stdout
#     assert "No problems detected." in result


# def test_tests(capsys):
#     result = subprocess.run(["structlint", "tests"], capture_output=True, check=False).stdout
#     assert "No problems detected." in result
