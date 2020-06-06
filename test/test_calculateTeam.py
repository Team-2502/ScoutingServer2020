import unittest

from calculations import calculateTeam


class TestCalculateTIMDStandard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.timd1 = "A1B2499CaDahEgFfUfWt|GkI1J0K0L4M4NqTaq,GkI1J1K1L2M4NlTaq,GkI1J0K0L4M4NlTan,GkI0J0K5L0M5NqTan,GafT4,GagQtRamSak|test"
        cls.timd2 = "A2B2499CbDahEgFtUfWf|GkI1J0K3L1M4NmTan,GkI1J0K2L1M3NoTan,GkI1J0K2L1M3NpTan,GadOw,GagQtRamSak|test2"
        cls.timd3 = "A3B2499CbDahEcFtUfWt|GkI2J0K1L0M1NpTaq,GkI0J0K3L1M4NlTan,GkI2J0K1L0M1NnTan,GjHaaT10,GagRap|test3"
        cls.timd4 = "A4B2499CbDahEcFtUfWt|GkI1J0K2L0M2NsTaq,GkI0J0K2L1M3NaoTaq,GkI1J0K2L0M2NlTan,GkI0J2K0L0M2NmTan,GafT7,GagRah|test4"
        cls.team = calculateTeam.calculate_team("test", [cls.timd1, cls.timd2, cls.timd3, cls.timd4], test=True)

    def testTeamCreated(self):
        self.assertEqual(self.team['teamNumber'], "test")

    def testTotalCellsScoredHighTeleop(self):
        self.assertEqual(self.team['totals']['cellsScoredHighTeleop'], 26)

    def testTotalTimeDefending(self):
        self.assertEqual(self.team['totals']['timeDefending'], 11)

    def testAvgCellsScoredTele(self):
        self.assertEqual(self.team['totals']['avgCellsScoredTele'], 7)

    def testMaxCellsScored(self):
        self.assertEqual(self.team['maxes']['maxCellsScored'], 10)

    def testClimbPercentage(self):
        self.assertEqual(self.team['percentages']['climbSuccessRate'], 67)

    def testShootingPercentage(self):
        self.assertEqual(self.team['percentages']['shootingPercentageHighTeleop'], 79)

    def testl3mCellsScored(self):
        self.assertEqual(self.team['l3ms']['l3mAvgCellsScored'], 6.3)

    def testp75CellsScored(self):
        self.assertEqual(self.team['p75s']['p75CellsScored'], 9.5)


if __name__ == '__main__':
    unittest.main()
