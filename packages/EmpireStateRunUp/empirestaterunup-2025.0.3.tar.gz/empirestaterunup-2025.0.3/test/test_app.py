"""
Unit tests for application
"""
import unittest

from textual.widgets import DataTable, MarkdownViewer

from empirestaterunup.apps import BrowserApp
from empirestaterunup.data import RACE_RESULTS_JSON_FULL_LEVEL, load_json_data


class AppTestCase(unittest.IsolatedAsyncioTestCase):
    """
    Unit tests for application
    """
    async def test_browser_app(self):
        """
        Simulate running browser app, with some commands
        """
        df = load_json_data(data_file=RACE_RESULTS_JSON_FULL_LEVEL[2023])
        app = BrowserApp(df=df)
        self.assertIsNotNone(app)
        async with app.run_test() as pilot:
            await pilot.press("ctrl+\\")
            for char in ["jose"]:
                await pilot.press(char)
            await pilot.press("enter")
            markdown_viewer = app.screen.query(MarkdownViewer).first()
            self.assertTrue(markdown_viewer.document)
            await pilot.click("#close")  # Close the new screen, pop the original one

            table = app.screen.query(DataTable).first()
            coordinate = table.cursor_coordinate
            self.assertTrue(table.is_valid_coordinate(coordinate))
            await pilot.press("enter")
            await pilot.pause()
            markdown_viewer = app.screen.query(MarkdownViewer).first()
            self.assertTrue(markdown_viewer)
            # Quit the app by pressing q
            await pilot.press("q")


if __name__ == '__main__':
    unittest.main()
