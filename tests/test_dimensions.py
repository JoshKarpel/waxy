import wax


def test_dimension_length():
    d = wax.Dimension.length(100.0)
    assert not d.is_auto()


def test_dimension_percent():
    d = wax.Dimension.percent(0.5)
    assert not d.is_auto()


def test_dimension_auto():
    d = wax.Dimension.auto()
    assert d.is_auto()


def test_dimension_eq():
    assert wax.Dimension.length(10.0) == wax.Dimension.length(10.0)
    assert wax.Dimension.length(10.0) != wax.Dimension.length(20.0)
    assert wax.Dimension.auto() == wax.Dimension.auto()
    assert wax.Dimension.auto() != wax.Dimension.length(0.0)


def test_dimension_repr():
    assert repr(wax.Dimension.auto())


def test_length_percentage():
    lp = wax.LengthPercentage.length(50.0)
    assert repr(lp)


def test_length_percentage_percent():
    lp = wax.LengthPercentage.percent(0.5)
    assert repr(lp)


def test_length_percentage_eq():
    assert wax.LengthPercentage.length(10.0) == wax.LengthPercentage.length(10.0)
    assert wax.LengthPercentage.length(10.0) != wax.LengthPercentage.percent(10.0)


def test_length_percentage_auto():
    lpa = wax.LengthPercentageAuto.auto()
    assert lpa.is_auto()


def test_length_percentage_auto_length():
    lpa = wax.LengthPercentageAuto.length(50.0)
    assert not lpa.is_auto()


def test_length_percentage_auto_eq():
    assert wax.LengthPercentageAuto.auto() == wax.LengthPercentageAuto.auto()
    assert wax.LengthPercentageAuto.length(10.0) == wax.LengthPercentageAuto.length(10.0)


def test_helpers():
    assert wax.auto().is_auto()
    assert not wax.length(10.0).is_auto()
    assert not wax.percent(0.5).is_auto()
    assert repr(wax.zero())
