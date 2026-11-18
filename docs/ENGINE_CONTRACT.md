# Engine contract

Python owns game rules and outcomes. The frontend replays the engine's ordered
book events and must not invent the authoritative outcome.

For the current Lines example, consult these authoritative local files:

- math/src/state/books.py: book serialization and payout multiplier units.
- math/games/0_0_lines/: official sample rules and event generation.
- frontend/apps/lines/src/game/typesBookEvent.ts: discriminated event types.
- frontend/apps/lines/src/game/bookEventHandlerMap.ts: event playback.
- frontend/apps/lines/src/stories/data/: example books used without an RGS.

The SDK book contains id, payoutMultiplier, ordered events, criteria,
baseGameWins and freeGameWins. payoutMultiplier is serialized as an integer
at 100 units per multiplier. Event monetary fields must follow the SDK's
actual serializer; do not infer units from a variable name. Validate IDs,
event indexes and board dimensions against the actual generated data.

Engine publish data includes compressed JSONL books, matching CSV lookup
tables and an index/manifest. The small development smoke output uses unit
weights only to inspect IDs and payouts. It is not optimized, published or
qualified as a production distribution.

Storybook uses local books and does not require an RGS login. The ordinary
Vite development app may show an authentication error without an RGS session.
An RGS account, hosting, production certification and release are outside
this setup. Custom event changes require explicit math/frontend agreement.
