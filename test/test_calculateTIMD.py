import unittest

from calculations import calculateTIMD


class TestCalculateTIMDStandard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compressed_timd = "A1B2499CaDahEgFfUfWt|GkI1J0K0L4M4NqTaq,GkI1J1K1L2M4NlTaq,GkI1J0K0L4M4NlTan,GkI0J0K5L0M5NqTan,GafT4,GagQtRamSak|test"
        cls.timd_name = "test1"
        cls.timd = calculateTIMD.calculate_timd(cls.compressed_timd, cls.timd_name, test=True)

    def testHeaderDecompression(self):
        self.assertEqual(self.timd['header']['matchNumber'], 1)

    def testCalcCellsShotAuto(self):
        self.assertEqual(self.timd['calculated']['cellsShotAuto'], 10)

    def testCalcCellsShotTeleop(self):
        self.assertEqual(self.timd['calculated']['cellsShotTeleop'], 10)

    def testCalcCellsScoredHighTeleop(self):
        self.assertEqual(self.timd['calculated']['cellsScoredHighTeleop'], 9)

    def testCalcCellsScoredTrenchTeleop(self):
        self.assertEqual(self.timd['calculated']['cellsScoredTrenchTeleop'], 4)

    def testCalcCellsMissedTeleop(self):
        self.assertEqual(self.timd['calculated']['cellsMissedTeleop'], 1)

    def testCalcTotalCycles(self):
        self.assertEqual(self.timd['calculated']['totalCycles'], 2)

    def testCalcShootingPercentageTeleop(self):
        self.assertEqual(self.timd['calculated']['shootingPercentageTeleop'], 90)

    def testCalcTimeDefending(self):
        self.assertEqual(self.timd['calculated']['timeDefending'], 4)

    def testCalcTimeTOC(self):
        self.assertEqual(self.timd['calculated']['trueOffensiveContribution'], 109)


if __name__ == '__main__':
    unittest.main()

