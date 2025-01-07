def test_can_import_cli():
    from codegen.cli import cli

    assert cli is not None
