import vidtoolz_hum_hai_rahi as w

from argparse import Namespace, ArgumentParser


def test_create_parser():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser is not None

    result = parser.parse_args(["hello"])
    assert result.input == "hello"
    assert result.output is None
    assert result.start_time == 1.0
    assert result.intro is False
    assert result.subscribe_voice is False
    assert result.subscribe is False
    assert result.consider is False
    assert result.apna_desh is False
    assert result.like is False
    assert result.watching is False
    assert result.part_of_series is False
    assert result.stay_tuned is False


def test_plugin(capsys):
    w.h2r_plugin.hello(None)
    captured = capsys.readouterr()
    assert "Hello! This is an example ``vidtoolz`` plugin." in captured.out
