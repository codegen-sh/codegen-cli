def test_can_import_cli():
    from codegen.cli.cli import cli

    assert cli is not None
