import unittest
from unittest.mock import patch
from auto_coder_chat_lite.common.utils import print_unmerged_blocks
from rich.console import Console

class TestUtils(unittest.TestCase):

    @patch.object(Console, 'print')
    def test_print_unmerged_blocks(self, mock_console_print):
        unmerged_blocks = [
            ("file1.py", "head1", "update1", 0.9),
            ("file2.py", "head2", "update2", 0.85),
        ]
        print_unmerged_blocks(unmerged_blocks)

        # Check if the console.print method was called with the expected arguments
        expected_calls = [
            "\n[bold red]Unmerged Blocks:[/bold red]",
            f"\n[bold blue]File:[/bold blue] {unmerged_blocks[0][0]}",
            f"\n[bold green]Search Block({unmerged_blocks[0][3]}):[/bold green]",
            "\n[bold yellow]Replace Block:[/bold yellow]",
            f"\n[bold blue]File:[/bold blue] {unmerged_blocks[1][0]}",
            f"\n[bold green]Search Block({unmerged_blocks[1][3]}):[/bold green]",
            "\n[bold yellow]Replace Block:[/bold yellow]",
            f"\n[bold red]Total unmerged blocks: {len(unmerged_blocks)}[/bold red]",
        ]

        # Check if the console.print method was called with the expected arguments
        actual_calls = [call[0][0] for call in mock_console_print.call_args_list]
        for expected_call in expected_calls:
            self.assertIn(expected_call, actual_calls)

if __name__ == '__main__':
    unittest.main()