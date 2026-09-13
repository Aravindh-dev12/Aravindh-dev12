# VECTOR//STORM README-native game

The profile game is rendered directly as Markdown in `README.md` between `VECTOR_STORM_GAME_START` and `VECTOR_STORM_GAME_END` markers.

Each control is a GitHub link that opens a pre-filled `storm: <move>` issue. The `VECTOR STORM README Game` workflow handles that issue, advances persistent JSON state, rewrites the Markdown board, comments the result, and closes the move issue.

This intentionally follows the same interaction pattern used by well-known README chess games: the board itself is Markdown, while GitHub Issues + Actions provide stateful moves.
