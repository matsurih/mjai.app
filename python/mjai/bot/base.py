import json
import sys

from mjai.bot.tools import (
    convert_tehai_vec34_as_tenhou,
    vec34_index_to_mjai_tile,
)
from mjai.mlibriichi.state import ActionCandidate, PlayerState  # type: ignore
from mjai.mlibriichi.tools import find_improving_tiles  # type: ignore


class Bot:
    def __init__(self, player_id: int = 0):
        self.player_id = player_id
        self.player_state = PlayerState(player_id)
        self.action_candidate: ActionCandidate | None = None

    # ==========================================================
    # action_candidate properties

    @property
    def can_discard(self) -> bool:
        """
        Whether the player can discard a tile.
        """
        assert self.action_candidate is not None
        return self.action_candidate.can_discard

    @property
    def can_riichi(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_riichi

    @property
    def can_agari(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_agari

    @property
    def can_tsumo_agari(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_tsumo_agari

    @property
    def can_ron_agari(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_ron_agari

    @property
    def can_ryukyoku(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_ryukyoku

    @property
    def can_kakan(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_kakan

    @property
    def can_daiminkan(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_daiminkan

    @property
    def can_kan(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_kan

    @property
    def can_ankan(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_ankan

    @property
    def can_pon(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_pon

    @property
    def can_chi(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_chi

    @property
    def can_chi_low(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_chi_low

    @property
    def can_chi_mid(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_chi_mid

    @property
    def can_chi_high(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_chi_high

    @property
    def can_act(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_act

    @property
    def can_pass(self) -> bool:
        assert self.action_candidate is not None
        return self.action_candidate.can_pass

    @property
    def target_actor(self) -> int:
        assert self.action_candidate is not None
        return self.action_candidate.target_actor

    # ==========================================================
    # player state properties

    """
    PS
    ['ankan_candidates', 'kakan_candidates',
    'validate_reaction', 'brief_info',
    'can_w_riichi', 'last_cans', 'at_furiten',
    'minkans', 'ankans', 'pons', 'kyotaku',
    'self_riichi_accepted', 'chis', 'akas_in_hand',
    'player_id', 'at_turn']
    """

    @property
    def is_oya(self) -> bool:
        return self.player_state.is_oya

    @property
    def honba(self) -> int:
        return self.player_state.honba

    @property
    def kyoku(self) -> int:
        """
        Current kyoku as 1-indexed number.
        East 1 is 1, East 2 is 2, ..., South 4 is 4.

        Example:
            >>> bot.kyoku
            2
        """
        return self.player_state.kyoku + 1

    @property
    def last_self_tsumo(self) -> str:
        """
        Last tile that the player drew by itself.
        """
        return self.player_state.last_self_tsumo()

    @property
    def last_kawa_tile(self) -> str:
        return self.player_state.last_kawa_tile()

    @property
    def self_riichi_declared(self) -> bool:
        return self.player_state.self_riichi_declared

    @property
    def tehai_vec34(self) -> list[int]:
        """
        Player's hand as a list of tile counts.
        Aka dora is not distinguished.
        For identifying aka dora, use `self.player_akas_in_hand`.

        Example:
            >>> bot.tehai_vec34
            [1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1,
             1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0]
        """
        return self.player_state.tehai

    @property
    def tehai_mjai(self) -> list[str]:
        """
        Player's hand as a list of tile strings in mjai format.

        Example:
            >>> bot.tehai_mjai
            ["1m", "2m", "6m", "9m", "1p", "3p", "4p", "3s", "4s", "5s",
             "7s", "9s", "5z", "6z"]
        """
        zi_map = ["E", "S", "W", "N", "P", "F", "C"]
        ms, ps, ss, zis, akas = [], [], [], [], []
        tiles = []
        for tile_idx, tile_count in enumerate(self.player_state.tehai):
            if tile_count and tile_idx == 4:
                akas.append("5mr")
            elif tile_count and tile_idx == 4 + 9:
                akas.append("5pr")
            elif tile_count and tile_idx == 4 + 18:
                akas.append("5sr")
            elif tile_count and tile_idx < 9:
                ms += [f"{tile_idx + 1}m"] * tile_count
            elif tile_count and tile_idx < 18:
                ps += [f"{tile_idx - 9 + 1}p"] * tile_count
            elif tile_count and tile_idx < 27:
                ss += [f"{tile_idx - 18 + 1}s"] * tile_count
            else:
                for _ in range(tile_count):
                    zis.append(zi_map[tile_idx - 27])

        tiles = ms + ps + ss + zis + akas
        return tiles

    @property
    def tehai_tenhou(self) -> str:
        """
        Player's hand with tenhou.net/2 format (like 123m0456p789s111z)

        TODO: handling called tiles

        Example:
            >>> bot.tehai_tenhou
            "1269m134p34579s56z"

            >>> bot.tehai_tenhou
            "012346789m11122z"
        """
        return convert_tehai_vec34_as_tenhou(
            self.player_state.tehai, self.player_state.akas_in_hand
        )

    @property
    def akas_in_hand(self) -> list[bool]:
        """
        List of aka dora indices in the player's hand.

        Example:
            >>> bot.player_akas_in_hand
            [False, False, False]
        """
        return self.player_state.akas_in_hand

    @property
    def shanten(self) -> int:
        """
        Shanten of the player's hand.
        """
        return self.player_state.shanten

    # ==========================================================
    # table state properties
    # TODO: kawa, called tiles, remaining_tiles, etc...

    # ==========================================================
    # actions

    def action_discard(self, tile_str: str) -> str:
        """
        Return a dahai event as a JSON string.
        """
        last_self_tsumo = self.player_state.last_self_tsumo()
        return json.dumps(
            {
                "type": "dahai",
                "pai": tile_str,
                "actor": self.player_id,
                "tsumogiri": tile_str == last_self_tsumo,
            },
            separators=(",", ":"),
        )

    def action_nothing(self) -> str:
        """
        Return a none event as a JSON string.
        """
        return json.dumps(
            {
                "type": "none",
            },
            separators=(",", ":"),
        )

    def action_tsumo_agari(self) -> str:
        return json.dumps(
            {
                "type": "hora",
                "actor": self.player_id,
                "target": self.target_actor,
                "pai": self.last_self_tsumo,
            },
            separators=(",", ":"),
        )

    def action_ron_agari(self) -> str:
        return json.dumps(
            {
                "type": "hora",
                "actor": self.player_id,
                "target": self.target_actor,
                "pai": self.last_kawa_tile,
            },
            separators=(",", ":"),
        )

    def action_riichi(self) -> str:
        return json.dumps(
            {
                "type": "reach",
                "actor": self.player_id,
            },
            separators=(",", ":"),
        )

    def think(self) -> str:
        """
        Logic part of the bot.

        Override this method to implement your own logic!
        Default logic is tsumogiri: discard the last tile that the player drew.
        """
        if self.can_discard:
            tile_str = self.last_self_tsumo
            return self.action_discard(tile_str)
        else:
            return self.action_nothing()

    def react(self, input_str: str) -> str:
        try:
            events = json.loads(input_str)
            if len(events) == 0:
                raise ValueError("Empty events")
            for event in events:
                self.action_candidate = self.player_state.update(
                    json.dumps(event)
                )
            resp = self.think()
            return resp

        except Exception as e:
            print(
                "===========================================", file=sys.stderr
            )
            print(f"Exception: {str(e)}", file=sys.stderr)
            print("Brief info:", file=sys.stderr)
            print(self.player_state.brief_info(), file=sys.stderr)
            print("", file=sys.stderr)

        return json.dumps({"type": "none"}, separators=(",", ":"))

    def start(self, player_id: int) -> None:
        self.player_id = player_id

        while True:
            line = sys.stdin.readline().strip()
            resp = self.react(line)
            sys.stdout.write(resp + "\n")
            sys.stdout.flush()

    def find_improving_tiles(self) -> list[tuple[str, list[str]]]:
        """
        Find tiles that improve the hand.

        Example:
            >>> bot.tehai_tenhou
            1269m134p34579s56z

            >>> ret = bot.find_improving_tiles()
            >>> len(ret)
            6

            >>> discard_tile, improving_tiles = ret[0]
            >>> discard_tile
            6m
            >>> improving_tiles
            [
                "3m",
                "9m",
                "1p",
                "2p",
                "4p",
                "5p",
                "8s",
                "P",
                "F",
            ]

        """

        def _aka(tile: str) -> str:
            # Use aka if needeed
            if (
                tile == "5s"
                and self.tehai_vec34[4] == 1
                and self.akas_in_hand[0]
            ):
                return "5sr"
            if (
                tile == "5p"
                and self.tehai_vec34[4 + 9] == 1
                and self.akas_in_hand[1]
            ):
                return "5pr"
            if (
                tile == "5p"
                and self.tehai_vec34[4 + 18] == 1
                and self.akas_in_hand[2]
            ):
                return "5pr"
            return tile

        candidates = find_improving_tiles(self.tehai_tenhou)
        candidates = list(
            sorted(candidates, key=lambda x: len(x[1]), reverse=True)
        )
        return [
            (
                _aka(vec34_index_to_mjai_tile(discard_tile_idx)),
                [
                    vec34_index_to_mjai_tile(tile_idx)
                    for tile_idx in improving_tile_indices
                ],
            )
            for discard_tile_idx, improving_tile_indices in candidates
        ]
