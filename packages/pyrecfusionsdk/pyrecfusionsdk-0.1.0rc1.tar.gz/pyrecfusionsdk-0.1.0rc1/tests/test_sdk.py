from pyRecFusionSDK import build_version, major_version, minor_version


class TestRecFusionSDK:

    def test_version(self):
        assert major_version() == 2
        assert minor_version() == 2
        assert build_version() == 0
